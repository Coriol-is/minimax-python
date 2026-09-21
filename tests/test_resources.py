from collections.abc import Callable

import httpx
import pytest

from minimax_api import MinimaxClient
from minimax_api.auth import Credentials
from minimax_api.errors import AmbiguousWriteError, ConcurrencyError, ValidationError

CREDENTIALS = Credentials(
    client_id="client", client_secret="secret", username="user", password="password"
)

TOKEN = {"access_token": "abc", "expires_in": 3600}

Route = httpx.Response | Callable[[httpx.Request], httpx.Response]


def make_client(routes: dict[tuple[str, str], Route]) -> MinimaxClient:
    """routes: dict mapping (method, path) -> httpx.Response or callable."""

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/oauth20/token"):
            return httpx.Response(200, json=TOKEN)
        key = (request.method, request.url.path)
        route = routes[key]
        return route(request) if callable(route) else route

    http = httpx.Client(transport=httpx.MockTransport(handler))
    return MinimaxClient(credentials=CREDENTIALS, organisation_id=12345, http=http)


def test_currencies_are_read_from_the_organisation_not_a_global_endpoint() -> None:
    seen: list[str] = []

    def route(request: httpx.Request) -> httpx.Response:
        seen.append(request.url.path)
        return httpx.Response(
            200,
            json={
                "Rows": [{"CurrencyId": 2, "Code": "RSD", "Name": "Serbian dinar"}],
                "TotalRows": 1,
                "CurrentPageNumber": 1,
                "PageSize": 300,
            },
        )

    client = make_client({("GET", "/RS/API/api/orgs/12345/currencies"): route})
    currencies = client.codelists.currencies()

    assert seen == ["/RS/API/api/orgs/12345/currencies"]
    assert currencies[0].code == "RSD"
    assert currencies[0].currency_id == 2


def test_currency_by_code_resolves_rather_than_assuming_an_id() -> None:
    # The vendor's samples say Currency.ID 7 is the default; in the Serbian
    # organisation 7 is CZK and RSD is 2. Nothing may be assumed.
    rows = {
        "Rows": [
            {"CurrencyId": 7, "Code": "CZK"},
            {"CurrencyId": 2, "Code": "RSD"},
        ],
        "TotalRows": 2,
        "CurrentPageNumber": 1,
        "PageSize": 300,
    }
    response = httpx.Response(200, json=rows)
    client = make_client({("GET", "/RS/API/api/orgs/12345/currencies"): response})
    currency = client.codelists.currency_by_code("RSD")
    assert currency is not None
    assert currency.currency_id == 2


def test_country_by_code_returns_none_when_absent() -> None:
    rows = {
        "Rows": [{"CountryId": 3, "Code": "RS"}],
        "TotalRows": 1,
        "CurrentPageNumber": 1,
        "PageSize": 300,
    }
    response = httpx.Response(200, json=rows)
    client = make_client({("GET", "/RS/API/api/orgs/12345/countries"): response})
    assert client.codelists.country_by_code("XX") is None


def test_creating_a_customer_returns_the_id_from_the_location_header() -> None:
    location = {"Location": "https://moj.minimax.rs/RS/API/api/orgs/12345/customers/4242"}
    captured: dict[str, str] = {}

    def route(request: httpx.Request) -> httpx.Response:
        captured["body"] = request.content.decode()
        return httpx.Response(201, headers=location)

    client = make_client({("POST", "/RS/API/api/orgs/12345/customers"): route})
    from minimax_api.models import Customer

    new_id = client.customers.create(Customer(name="ACME", address="Example Street 1"))
    assert new_id == 4242
    # Vendor spelling on the wire, snake_case in Python.
    assert '"Name": "ACME"' in captured["body"] or '"Name":"ACME"' in captured["body"]


def test_creating_a_customer_with_no_location_header_is_ambiguous_not_invalid() -> None:
    # The write succeeded -- Minimax just didn't say what the new ID is. That
    # must not be reported as ValidationError: a caller who sees that type and
    # "fixes the payload" would resubmit an identical customer, duplicating it.
    client = make_client({("POST", "/RS/API/api/orgs/12345/customers"): httpx.Response(201)})
    from minimax_api.models import Customer

    with pytest.raises(AmbiguousWriteError):
        client.customers.create(Customer(name="ACME"))


def test_creating_an_issued_invoice_without_a_location_header_is_ambiguous() -> None:
    client = make_client(
        {("POST", "/RS/API/api/orgs/12345/issuedinvoices"): httpx.Response(201)}
    )
    from minimax_api.models import IssuedInvoice

    with pytest.raises(AmbiguousWriteError):
        client.issued_invoices.create(IssuedInvoice())


def test_updating_without_a_row_version_is_refused_before_the_request() -> None:
    calls: list[httpx.Request] = []

    def route(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200)

    client = make_client({("PUT", "/RS/API/api/orgs/12345/customers/1"): route})
    from minimax_api.models import Customer

    with pytest.raises(ValidationError):
        client.customers.update(Customer(customer_id=1, name="ACME"))
    assert calls == []


def test_a_row_version_conflict_surfaces_as_concurrency_error() -> None:
    body = {"Message": "Concurrency error - record changed by another action (RowVersion)"}
    response = httpx.Response(400, json=body)
    client = make_client({("PUT", "/RS/API/api/orgs/12345/customers/1"): response})
    from minimax_api.models import Customer

    with pytest.raises(ConcurrencyError):
        client.customers.update(Customer(customer_id=1, name="ACME", row_version="AAAAA8OTDPw="))


def test_customers_list_walks_pages() -> None:
    pages = {
        "1": {"Rows": [{"CustomerId": 1}], "TotalRows": 2, "CurrentPageNumber": 1, "PageSize": 1},
        "2": {"Rows": [{"CustomerId": 2}], "TotalRows": 2, "CurrentPageNumber": 2, "PageSize": 1},
    }

    def route(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=pages[request.url.params.get("CurrentPage", "1")])

    client = make_client({("GET", "/RS/API/api/orgs/12345/customers"): route})
    customers = client.customers.list(page_size=1)
    assert [c.customer_id for c in customers] == [1, 2]
