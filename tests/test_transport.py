from collections.abc import Callable
from typing import Any

import httpx
import pytest

from minimax_api.errors import (
    AmbiguousWriteError,
    ConcurrencyError,
    NotFoundError,
    RateBudgetExceeded,
    TransportError,
    ValidationError,
)
from minimax_api.region import RS
from minimax_api.transport import Response, Transport, _parse_retry_after


class StubAuth:
    """Stands in for Authenticator; counts how often the token was invalidated."""

    def __init__(self) -> None:
        self.invalidations: int = 0
        self.tokens: list[str] = ["token-1", "token-2"]

    def access_token(self) -> str:
        return self.tokens[min(self.invalidations, len(self.tokens) - 1)]

    def invalidate(self) -> None:
        self.invalidations += 1


def make_transport(
    handler: Callable[[httpx.Request], httpx.Response], **kwargs: Any
) -> Transport:
    http = httpx.Client(transport=httpx.MockTransport(handler))
    return Transport(
        region=RS,
        authenticator=StubAuth(),  # type: ignore[arg-type]
        http=http,
        sleep=lambda seconds: None,
        **kwargs,
    )


def test_get_builds_the_url_and_sends_the_bearer_token() -> None:
    seen: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["auth"] = request.headers["Authorization"]
        return httpx.Response(200, json={"Rows": []})

    transport = make_transport(handler)
    response = transport.request("GET", "/api/orgs/12345/customers", params={"PageSize": 300})

    assert seen["url"] == "https://moj.minimax.rs/RS/API/api/orgs/12345/customers?PageSize=300"
    assert seen["auth"] == "Bearer token-1"
    assert response.status_code == 200
    assert response.json == {"Rows": []}


def test_404_becomes_not_found() -> None:
    transport = make_transport(
        lambda request: httpx.Response(404, json={"Message": "no such thing"})
    )
    with pytest.raises(NotFoundError):
        transport.request("GET", "/api/orgs/12345/customers/999")


def test_concurrency_message_becomes_concurrency_error() -> None:
    body = {"Message": "Concurrency error - record changed by another action (RowVersion)"}
    transport = make_transport(lambda request: httpx.Response(400, json=body))
    with pytest.raises(ConcurrencyError):
        transport.request("PUT", "/api/orgs/12345/customers/1", json={})


def test_other_4xx_becomes_validation_error_carrying_the_server_text() -> None:
    body = {"Message": "Name is required"}
    transport = make_transport(lambda request: httpx.Response(400, json=body))
    with pytest.raises(ValidationError) as raised:
        transport.request("POST", "/api/orgs/12345/customers", json={})
    assert raised.value.status_code == 400
    assert raised.value.payload == body


def test_5xx_is_retried_then_succeeds() -> None:
    responses = [httpx.Response(503, text="try later"), httpx.Response(200, json={"ok": True})]
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return responses.pop(0)

    transport = make_transport(handler)
    assert transport.request("GET", "/api/orgs/12345/customers").json == {"ok": True}
    assert len(calls) == 2


def test_5xx_gives_up_after_the_retry_budget() -> None:
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(500, text="boom")

    transport = make_transport(handler, max_transport_retries=3)
    with pytest.raises(TransportError):
        transport.request("GET", "/api/orgs/12345/customers")
    assert len(calls) == 3


def test_401_on_an_api_call_refreshes_the_token_once() -> None:
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.headers["Authorization"])
        if len(calls) == 1:
            return httpx.Response(401, text="expired")
        return httpx.Response(200, json={"ok": True})

    transport = make_transport(handler)
    assert transport.request("GET", "/api/orgs/12345/customers").json == {"ok": True}
    assert calls == ["Bearer token-1", "Bearer token-2"]


def test_repeated_401_does_not_loop_forever() -> None:
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(401, text="expired")

    transport = make_transport(handler)
    with pytest.raises(TransportError):
        transport.request("GET", "/api/orgs/12345/customers")
    assert len(calls) == 2


def test_connection_error_is_a_transport_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("timed out")

    transport = make_transport(handler, max_transport_retries=2)
    with pytest.raises(TransportError):
        transport.request("GET", "/api/orgs/12345/customers")


def test_location_header_yields_the_created_id() -> None:
    headers = {"Location": "https://moj.minimax.rs/RS/API/api/orgs/12345/customers/4242"}
    transport = make_transport(lambda request: httpx.Response(201, headers=headers))
    response = transport.request("POST", "/api/orgs/12345/customers", json={})
    assert response.location_id == 4242


def test_missing_location_header_yields_none() -> None:
    assert Response(status_code=200, json=None, headers={}).location_id is None


def test_unparseable_location_yields_none() -> None:
    response = Response(status_code=201, json=None, headers={"Location": "/customers/not-a-number"})
    assert response.location_id is None


def test_empty_body_parses_as_none() -> None:
    transport = make_transport(lambda request: httpx.Response(204))
    assert transport.request("DELETE", "/api/orgs/12345/customers/1").json is None


def test_401_refresh_does_not_consume_transport_retry_budget() -> None:
    """With max_transport_retries=1, 401 followed by 200 succeeds (401 doesn't consume attempt)."""
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.headers["Authorization"])
        if len(calls) == 1:
            return httpx.Response(401, text="expired")
        return httpx.Response(200, json={"ok": True})

    transport = make_transport(handler, max_transport_retries=1)
    assert transport.request("GET", "/api/orgs/12345/customers").json == {"ok": True}
    assert len(calls) == 2
    assert calls == ["Bearer token-1", "Bearer token-2"]


def test_401_refresh_does_not_add_extra_transport_attempts() -> None:
    """A 401 followed by two 5xx with max_transport_retries=2 still exhausts and raises."""
    responses = [
        httpx.Response(401, text="expired"),
        httpx.Response(500, text="error1"),
        httpx.Response(500, text="error2"),
    ]
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return responses.pop(0)

    transport = make_transport(handler, max_transport_retries=2)
    with pytest.raises(TransportError):
        transport.request("GET", "/api/orgs/12345/customers")
    assert len(calls) == 3


def test_location_id_from_trailing_slash_url() -> None:
    headers = {"Location": "https://moj.minimax.rs/RS/API/api/orgs/12345/customers/4242/"}
    response = Response(status_code=201, json=None, headers=headers)
    assert response.location_id == 4242


def test_location_id_from_query_string_url() -> None:
    headers = {"Location": "https://moj.minimax.rs/RS/API/api/orgs/12345/customers/4242?foo=bar"}
    response = Response(status_code=201, json=None, headers=headers)
    assert response.location_id == 4242


def test_location_id_from_relative_path() -> None:
    headers = {"Location": "/RS/API/api/orgs/12345/customers/4242"}
    response = Response(status_code=201, json=None, headers=headers)
    assert response.location_id == 4242


def test_location_id_with_fragment() -> None:
    headers = {"Location": "https://example.com/customers/4242#section"}
    response = Response(status_code=201, json=None, headers=headers)
    assert response.location_id == 4242


def test_location_id_from_path_with_no_digits() -> None:
    response = Response(status_code=201, json=None, headers={"Location": "/customers/created"})
    assert response.location_id is None


def test_transport_refuses_to_send_when_the_budget_is_spent() -> None:
    from minimax_api.budget import Budget
    from minimax_api.errors import RateBudgetExceeded

    now = [1000.0]
    budget = Budget(clock=lambda: now[0], daily_limit=1)
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, json={"ok": True})

    transport = make_transport(handler, budget=budget)
    transport.request("GET", "/api/orgs/12345/customers")

    with pytest.raises(RateBudgetExceeded):
        transport.request("GET", "/api/orgs/12345/customers")
    assert len(calls) == 1


# -- Critical 2: non-idempotent writes are never retried automatically -----


def test_post_with_a_connection_error_is_not_retried_and_raises_ambiguous_write() -> None:
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        raise httpx.ConnectTimeout("server committed, reply lost")

    transport = make_transport(handler, max_transport_retries=3)
    with pytest.raises(AmbiguousWriteError) as raised:
        transport.request("POST", "/api/orgs/12345/issuedinvoices", json={"Name": "x"})

    assert len(calls) == 1  # never resent
    assert raised.value.retryable is False


def test_post_with_a_502_is_not_retried_and_raises_ambiguous_write() -> None:
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(502, text="bad gateway")

    transport = make_transport(handler, max_transport_retries=3)
    with pytest.raises(AmbiguousWriteError):
        transport.request("POST", "/api/orgs/12345/issuedinvoices", json={})

    assert len(calls) == 1  # never resent


def test_get_with_a_502_still_retries() -> None:
    responses = [httpx.Response(502, text="bad gateway"), httpx.Response(200, json={"ok": True})]
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return responses.pop(0)

    transport = make_transport(handler)
    assert transport.request("GET", "/api/orgs/12345/customers").json == {"ok": True}
    assert len(calls) == 2


# -- Important 3: an HTTP-date Retry-After must not crash -------------------


def test_parse_retry_after_accepts_delta_seconds() -> None:
    assert _parse_retry_after("120") == 120.0


def test_parse_retry_after_accepts_an_http_date() -> None:
    from datetime import UTC, datetime, timedelta
    from email.utils import format_datetime

    future = datetime.now(UTC) + timedelta(seconds=90)
    header = format_datetime(future, usegmt=True)
    result = _parse_retry_after(header)
    assert 60 <= result <= 120  # generous window around the 90s offset


def test_parse_retry_after_falls_back_to_default_on_garbage() -> None:
    assert _parse_retry_after("not a valid retry-after value") == 3600.0


def test_parse_retry_after_falls_back_to_default_when_missing() -> None:
    assert _parse_retry_after(None) == 3600.0


def test_429_with_an_http_date_retry_after_does_not_crash_and_penalizes_budget() -> None:
    # The literal case that used to raise a bare ValueError instead of
    # RateBudgetExceeded, leaving budget.penalize() unreached.
    from minimax_api.budget import Budget

    budget = Budget()
    headers = {"Retry-After": "Wed, 21 Oct 2026 07:28:00 GMT"}
    transport = make_transport(
        lambda request: httpx.Response(429, headers=headers, json={"Message": "slow down"}),
        budget=budget,
    )
    with pytest.raises(RateBudgetExceeded) as raised:
        transport.request("GET", "/api/orgs/12345/customers")
    assert raised.value.retry_after >= 0

    # The penalty was actually applied to the budget: a second call is
    # refused locally, with no second network request required.
    with pytest.raises(RateBudgetExceeded):
        transport.request("GET", "/api/orgs/12345/customers")


def test_429_drives_the_budget_penalty_through_transport() -> None:
    # Previously only exercised by calling Budget directly; this is the path
    # that would have caught the HTTP-date crash above.
    from minimax_api.budget import Budget

    now = [1000.0]
    budget = Budget(clock=lambda: now[0])
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(429, headers={"Retry-After": "60"}, json={"Message": "slow down"})

    transport = make_transport(handler, budget=budget)
    with pytest.raises(RateBudgetExceeded) as raised:
        transport.request("GET", "/api/orgs/12345/customers")
    assert raised.value.retry_after == pytest.approx(60.0)
    assert len(calls) == 1

    now[0] += 30
    with pytest.raises(RateBudgetExceeded):
        transport.request("GET", "/api/orgs/12345/customers")
    assert len(calls) == 1  # still refused locally, no second request


# -- Important 5: broaden the (unverified) concurrency-error match ----------


def test_concurrency_match_covers_rowversion_wording() -> None:
    body = {"Message": "RowVersion mismatch: the record has been modified"}
    transport = make_transport(lambda request: httpx.Response(400, json=body))
    with pytest.raises(ConcurrencyError):
        transport.request("PUT", "/api/orgs/12345/customers/1", json={})


def test_concurrency_match_covers_row_version_with_a_space() -> None:
    body = {"Message": "Row version conflict: please reload and try again"}
    transport = make_transport(lambda request: httpx.Response(400, json=body))
    with pytest.raises(ConcurrencyError):
        transport.request("PUT", "/api/orgs/12345/customers/1", json={})


# -- Budget undercounts retries: connect vs. read/timeout errors ------------


class _CountingBudgetStore:
    """Records every timestamp it is given, in insertion order, for assertions."""

    def __init__(self) -> None:
        self.timestamps: list[float] = []

    def append(self, timestamp: float) -> None:
        self.timestamps.append(timestamp)

    def since(self, timestamp: float) -> list[float]:
        return [value for value in self.timestamps if value > timestamp]

    def prune(self, before: float) -> None:
        self.timestamps = [value for value in self.timestamps if value > before]


def test_a_connect_error_never_reached_the_server_and_is_not_counted() -> None:
    from minimax_api.budget import Budget

    store = _CountingBudgetStore()
    budget = Budget(store=store, clock=lambda: 1000.0)

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    transport = make_transport(handler, budget=budget, max_transport_retries=2)
    with pytest.raises(TransportError):
        transport.request("GET", "/api/orgs/12345/customers")

    assert store.timestamps == []


def test_a_read_timeout_may_have_reached_the_server_and_is_counted() -> None:
    from minimax_api.budget import Budget

    store = _CountingBudgetStore()
    budget = Budget(store=store, clock=lambda: 1000.0)

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out waiting for a reply")

    transport = make_transport(handler, budget=budget, max_transport_retries=2)
    with pytest.raises(TransportError):
        transport.request("GET", "/api/orgs/12345/customers")

    # Each of the two exhausted attempts may have reached Minimax.
    assert len(store.timestamps) == 2
