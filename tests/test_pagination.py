from collections.abc import Callable
from typing import Any

import httpx

from minimax_api.envelope import MinimaxModel, SearchResult
from minimax_api.pagination import DEFAULT_PAGE_SIZE, paginate
from minimax_api.region import RS
from minimax_api.transport import Transport


class Row(MinimaxModel):
    id: int
    name: str | None = None


class StubAuth:
    def access_token(self) -> str:
        return "token"

    def invalidate(self) -> None:
        pass


def make_transport(
    handler: Callable[[httpx.Request], httpx.Response]
) -> Transport:
    http = httpx.Client(transport=httpx.MockTransport(handler))
    return Transport(
        region=RS,
        authenticator=StubAuth(),  # type: ignore[arg-type]
        http=http,
        sleep=lambda s: None,
    )


def test_envelope_maps_pascal_case_aliases() -> None:
    result = SearchResult[Row].model_validate(
        {"Rows": [{"ID": 1}], "TotalRows": 1, "CurrentPageNumber": 1, "PageSize": 100}
    )
    assert result.total_rows == 1
    assert result.rows[0].id == 1


def test_model_accepts_unexpected_fields() -> None:
    # Minimax adds fields without warning; a caller must not break mid-invoice.
    row = Row.model_validate({"ID": 1, "SomethingNew": "value"})
    assert row.id == 1


def test_pagination_requests_the_large_page_size() -> None:
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(dict(request.url.params))
        return httpx.Response(
            200,
            json={
                "Rows": [],
                "TotalRows": 0,
                "CurrentPageNumber": 1,
                "PageSize": DEFAULT_PAGE_SIZE,
            },
        )

    list(paginate(make_transport(handler), "/api/orgs/97271/customers", Row))
    assert seen[0]["PageSize"] == str(DEFAULT_PAGE_SIZE)


def test_pagination_walks_every_page() -> None:
    pages = {
        "1": {
            "Rows": [{"ID": 1}, {"ID": 2}],
            "TotalRows": 5,
            "CurrentPageNumber": 1,
            "PageSize": 2,
        },
        "2": {
            "Rows": [{"ID": 3}, {"ID": 4}],
            "TotalRows": 5,
            "CurrentPageNumber": 2,
            "PageSize": 2,
        },
        "3": {
            "Rows": [{"ID": 5}],
            "TotalRows": 5,
            "CurrentPageNumber": 3,
            "PageSize": 2,
        },
    }

    def handler(request: httpx.Request) -> httpx.Response:
        page = request.url.params.get("CurrentPage", "1")
        return httpx.Response(200, json=pages[page])

    rows = list(paginate(make_transport(handler), "/api/orgs/97271/customers", Row, page_size=2))
    assert [row.id for row in rows] == [1, 2, 3, 4, 5]


def test_pagination_keeps_caller_parameters() -> None:
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(dict(request.url.params))
        return httpx.Response(
            200,
            json={
                "Rows": [],
                "TotalRows": 0,
                "CurrentPageNumber": 1,
                "PageSize": 300,
            },
        )

    list(
        paginate(
            make_transport(handler),
            "/api/orgs/97271/customers",
            Row,
            params={"SearchString": "acme"},
        )
    )
    assert seen[0]["SearchString"] == "acme"


def test_pagination_stops_when_a_page_comes_back_empty() -> None:
    # Defensive: a server that reports a TotalRows it cannot deliver must not
    # send us round the loop forever.
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(
            200,
            json={
                "Rows": [],
                "TotalRows": 99,
                "CurrentPageNumber": 1,
                "PageSize": 300,
            },
        )

    rows = list(paginate(make_transport(handler), "/api/orgs/97271/customers", Row))
    assert rows == []
    assert len(calls) == 1


def test_pagination_handles_a_bare_list_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[{"ID": 7}])

    rows = list(paginate(make_transport(handler), "/api/orgs/97271/countries", Row))
    assert [row.id for row in rows] == [7]
