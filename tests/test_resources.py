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


# -- Read paths the earlier tests never exercised ---------------------------


def _envelope(rows: list[dict[str, object]]) -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "Rows": rows,
            "TotalRows": len(rows),
            "CurrentPageNumber": 1,
            "PageSize": 300,
        },
    )


def test_vat_rates_keep_the_two_id_spaces_apart() -> None:
    # VatRateId and VatRatePercentage.ID are different numbers for the same
    # rate. Reading the wrong one silently applies a different VAT rate, so the
    # facade must not conflate them.
    rows = [
        {"VatRateId": 4, "Code": "S", "Percent": 20.0, "VatRatePercentage": {"ID": 6}},
        {"VatRateId": 3, "Code": "P", "Percent": 8.0, "VatRatePercentage": {"ID": 7}},
    ]
    client = make_client({("GET", "/RS/API/api/orgs/12345/vatrates"): _envelope(rows)})

    rates = {rate.code: rate for rate in client.codelists.vat_rates()}

    assert rates["S"].percent == 20.0
    assert rates["S"].vat_rate_id == 4
    assert rates["S"].vat_rate_percentage is not None
    assert rates["S"].vat_rate_percentage.id == 6


def test_accounts_are_read_from_the_organisation() -> None:
    rows = [{"AccountId": 1, "Code": "2040", "Name": "Kupci u zemlji"}]
    client = make_client({("GET", "/RS/API/api/orgs/12345/accounts"): _envelope(rows)})

    accounts = client.codelists.accounts()

    assert [account.code for account in accounts] == ["2040"]


def test_getting_one_customer_reads_it_by_id() -> None:
    seen: list[str] = []

    def route(request: httpx.Request) -> httpx.Response:
        seen.append(request.url.path)
        return httpx.Response(200, json={"CustomerId": 7, "Name": "ACME", "RowVersion": "AAA="})

    client = make_client({("GET", "/RS/API/api/orgs/12345/customers/7"): route})

    customer = client.customers.get(7)

    assert seen == ["/RS/API/api/orgs/12345/customers/7"]
    assert customer.customer_id == 7
    # The RowVersion must survive the read: an update without it is refused.
    assert customer.row_version == "AAA="


def test_issued_invoices_list_and_get() -> None:
    rows = [{"IssuedInvoiceId": 11, "Status": "O"}]
    client = make_client(
        {
            ("GET", "/RS/API/api/orgs/12345/issuedinvoices"): _envelope(rows),
            ("GET", "/RS/API/api/orgs/12345/issuedinvoices/11"): httpx.Response(
                200, json={"IssuedInvoiceId": 11, "Status": "O"}
            ),
        }
    )

    listed = client.issued_invoices.list()
    one = client.issued_invoices.get(11)

    assert [invoice.issued_invoice_id for invoice in listed] == [11]
    # Documents created through the API arrive as drafts ("O"): an accepted
    # write is not yet a business event.
    assert one.status == "O"


def test_creating_an_invoice_returns_the_id_from_the_location_header() -> None:
    location = {"Location": "https://moj.minimax.rs/RS/API/api/orgs/12345/issuedinvoices/909"}
    client = make_client(
        {("POST", "/RS/API/api/orgs/12345/issuedinvoices"): httpx.Response(201, headers=location)}
    )

    from minimax_api.models import IssuedInvoice

    assert client.issued_invoices.create(IssuedInvoice(date_issued=None)) == 909


def test_updating_a_customer_without_an_id_is_refused_before_the_request() -> None:
    calls: list[httpx.Request] = []

    def route(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200)

    client = make_client({("PUT", "/RS/API/api/orgs/12345/customers/1"): route})
    from minimax_api.models import Customer

    with pytest.raises(ValidationError):
        client.customers.update(Customer(name="ACME", row_version="AAA="))

    assert calls == []
