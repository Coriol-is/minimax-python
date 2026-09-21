from collections.abc import Callable

import httpx
import pytest

from minimax_api.auth import Authenticator, Credentials, InMemoryTokenStore, Token, TokenStore
from minimax_api.errors import MinimaxAuthError, TransportError
from minimax_api.region import RS

CREDENTIALS = Credentials(
    client_id="client", client_secret="secret", username="user", password="password"
)


def make_auth(
    handler: Callable[[httpx.Request], httpx.Response],
    *,
    clock: Callable[[], float] | None = None,
    store: TokenStore | None = None,
) -> Authenticator:
    http = httpx.Client(transport=httpx.MockTransport(handler))
    return Authenticator(
        credentials=CREDENTIALS,
        region=RS,
        http=http,
        store=store,
        clock=clock or (lambda: 1000.0),
    )


def test_token_is_requested_once_and_then_cached() -> None:
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(
            200,
            json={"access_token": "abc", "expires_in": 3600, "token_type": "bearer"},
        )

    auth = make_auth(handler)
    assert auth.access_token() == "abc"
    assert auth.access_token() == "abc"
    assert len(calls) == 1


def test_token_request_sends_the_password_grant_form() -> None:
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["body"] = request.content.decode()
        return httpx.Response(200, json={"access_token": "abc", "expires_in": 3600})

    make_auth(handler).access_token()
    assert seen["url"] == RS.token_url
    for field in (
        "grant_type=password",
        "client_id=client",
        "client_secret=secret",
        "username=user",
        "password=password",
        "scope=minimax.rs",
    ):
        assert field in seen["body"]


def test_expired_token_is_refreshed_once() -> None:
    calls = []
    now = [1000.0]

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, json={"access_token": f"token-{len(calls)}", "expires_in": 3600})

    auth = make_auth(handler, clock=lambda: now[0])
    assert auth.access_token() == "token-1"
    now[0] += 3600  # past expiry once the 60 s skew is applied
    assert auth.access_token() == "token-2"
    assert auth.access_token() == "token-2"
    assert len(calls) == 2


def test_credential_rejection_is_terminal_and_never_reaches_the_network_twice() -> None:
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(400, json={"error": "invalid_grant"})

    auth = make_auth(handler)
    with pytest.raises(MinimaxAuthError) as first:
        auth.access_token()
    assert first.value.terminal is True

    with pytest.raises(MinimaxAuthError) as second:
        auth.access_token()
    assert second.value.terminal is True

    # The latch is the whole point: one bad password, one request, ever.
    assert len(calls) == 1


def test_401_from_the_token_endpoint_is_also_terminal() -> None:
    auth = make_auth(lambda request: httpx.Response(401, json={"error": "invalid_client"}))
    with pytest.raises(MinimaxAuthError) as raised:
        auth.access_token()
    assert raised.value.terminal is True


def test_server_error_is_a_transport_error_and_does_not_latch() -> None:
    responses = [httpx.Response(503, text="unavailable"),
                 httpx.Response(200, json={"access_token": "abc", "expires_in": 3600})]

    def handler(request: httpx.Request) -> httpx.Response:
        return responses.pop(0)

    auth = make_auth(handler)
    with pytest.raises(TransportError):
        auth.access_token()
    assert auth.access_token() == "abc"


def test_connection_failure_is_a_transport_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    with pytest.raises(TransportError):
        make_auth(handler).access_token()


def test_a_shared_store_prevents_a_second_worker_from_requesting_a_token() -> None:
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, json={"access_token": "abc", "expires_in": 3600})

    store = InMemoryTokenStore()
    first = make_auth(handler, store=store)
    second = make_auth(handler, store=store)
    assert first.access_token() == "abc"
    assert second.access_token() == "abc"
    assert len(calls) == 1


def test_invalidate_forces_one_refresh() -> None:
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, json={"access_token": f"token-{len(calls)}", "expires_in": 3600})

    auth = make_auth(handler)
    assert auth.access_token() == "token-1"
    auth.invalidate()
    assert auth.access_token() == "token-2"
    assert len(calls) == 2


def test_store_round_trips_a_token() -> None:
    store = InMemoryTokenStore()
    assert store.get() is None
    token = Token(access_token="abc", expires_at=4600.0)
    store.set(token)
    assert store.get() == token


def test_credentials_repr_hides_secrets() -> None:
    creds = Credentials(
        client_id="my-client",
        client_secret="super-secret",
        username="user123",
        password="password-secret",
    )
    creds_repr = repr(creds)
    assert "my-client" in creds_repr
    assert "user123" in creds_repr
    assert "super-secret" not in creds_repr
    assert "password-secret" not in creds_repr


def test_token_repr_hides_access_token() -> None:
    token = Token(access_token="secret-token", expires_at=5000.0)
    token_repr = repr(token)
    assert "5000" in token_repr
    assert "secret-token" not in token_repr


def test_credential_rejection_error_message_hides_credentials() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"error": "invalid_grant"})

    auth = make_auth(handler)
    with pytest.raises(MinimaxAuthError) as raised:
        auth.access_token()
    error_message = str(raised.value)
    assert "password" not in error_message.lower()
    assert "secret" not in error_message.lower()
    assert "invalid_grant" not in error_message
