import httpx
import pytest

from minimax_api.auth import Authenticator, Credentials, Token
from minimax_api.errors import (
    ConcurrencyError,
    NotFoundError,
    TransportError,
    ValidationError,
)
from minimax_api.region import RS
from minimax_api.transport import Response, Transport


class StubAuth:
    """Stands in for Authenticator; counts how often the token was invalidated."""

    def __init__(self) -> None:
        self.invalidations = 0
        self.tokens = ["token-1", "token-2"]

    def access_token(self) -> str:
        return self.tokens[min(self.invalidations, len(self.tokens) - 1)]

    def invalidate(self) -> None:
        self.invalidations += 1


def make_transport(handler, **kwargs):
    http = httpx.Client(transport=httpx.MockTransport(handler))
    return Transport(
        region=RS,
        authenticator=StubAuth(),
        http=http,
        sleep=lambda seconds: None,
        **kwargs,
    )


def test_get_builds_the_url_and_sends_the_bearer_token():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["auth"] = request.headers["Authorization"]
        return httpx.Response(200, json={"Rows": []})

    transport = make_transport(handler)
    response = transport.request("GET", "/api/orgs/97271/customers", params={"PageSize": 300})

    assert seen["url"] == "https://moj.minimax.rs/RS/API/api/orgs/97271/customers?PageSize=300"
    assert seen["auth"] == "Bearer token-1"
    assert response.status_code == 200
    assert response.json == {"Rows": []}


def test_404_becomes_not_found() -> None:
    transport = make_transport(lambda request: httpx.Response(404, json={"Message": "no such thing"}))
    with pytest.raises(NotFoundError):
        transport.request("GET", "/api/orgs/97271/customers/999")


def test_concurrency_message_becomes_concurrency_error() -> None:
    body = {"Message": "Concurrency error - record changed by another action (RowVersion)"}
    transport = make_transport(lambda request: httpx.Response(400, json=body))
    with pytest.raises(ConcurrencyError):
        transport.request("PUT", "/api/orgs/97271/customers/1", json={})


def test_other_4xx_becomes_validation_error_carrying_the_server_text() -> None:
    body = {"Message": "Name is required"}
    transport = make_transport(lambda request: httpx.Response(400, json=body))
    with pytest.raises(ValidationError) as raised:
        transport.request("POST", "/api/orgs/97271/customers", json={})
    assert raised.value.status_code == 400
    assert raised.value.payload == body


def test_5xx_is_retried_then_succeeds() -> None:
    responses = [httpx.Response(503, text="try later"), httpx.Response(200, json={"ok": True})]
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return responses.pop(0)

    transport = make_transport(handler)
    assert transport.request("GET", "/api/orgs/97271/customers").json == {"ok": True}
    assert len(calls) == 2


def test_5xx_gives_up_after_the_retry_budget() -> None:
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(500, text="boom")

    transport = make_transport(handler, max_transport_retries=3)
    with pytest.raises(TransportError):
        transport.request("GET", "/api/orgs/97271/customers")
    assert len(calls) == 3


def test_401_on_an_api_call_refreshes_the_token_once() -> None:
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.headers["Authorization"])
        if len(calls) == 1:
            return httpx.Response(401, text="expired")
        return httpx.Response(200, json={"ok": True})

    transport = make_transport(handler)
    assert transport.request("GET", "/api/orgs/97271/customers").json == {"ok": True}
    assert calls == ["Bearer token-1", "Bearer token-2"]


def test_repeated_401_does_not_loop_forever() -> None:
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(401, text="expired")

    transport = make_transport(handler)
    with pytest.raises(TransportError):
        transport.request("GET", "/api/orgs/97271/customers")
    assert len(calls) == 2


def test_connection_error_is_a_transport_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("timed out")

    transport = make_transport(handler, max_transport_retries=2)
    with pytest.raises(TransportError):
        transport.request("GET", "/api/orgs/97271/customers")


def test_location_header_yields_the_created_id() -> None:
    headers = {"Location": "https://moj.minimax.rs/RS/API/api/orgs/97271/customers/4242"}
    transport = make_transport(lambda request: httpx.Response(201, headers=headers))
    response = transport.request("POST", "/api/orgs/97271/customers", json={})
    assert response.location_id == 4242


def test_missing_location_header_yields_none() -> None:
    assert Response(status_code=200, json=None, headers={}).location_id is None


def test_unparseable_location_yields_none() -> None:
    response = Response(status_code=201, json=None, headers={"Location": "/customers/not-a-number"})
    assert response.location_id is None


def test_empty_body_parses_as_none() -> None:
    transport = make_transport(lambda request: httpx.Response(204))
    assert transport.request("DELETE", "/api/orgs/97271/customers/1").json is None
