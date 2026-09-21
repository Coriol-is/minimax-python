import httpx
import pytest

from minimax_api import MinimaxClient
from minimax_api.auth import Credentials

CREDENTIALS = Credentials(
    client_id="client", client_secret="secret", username="user", password="password"
)

TOKEN = {"access_token": "abc", "expires_in": 3600}


def handler(request: httpx.Request) -> httpx.Response:
    if request.url.path.endswith("/oauth20/token"):
        return httpx.Response(200, json={"access_token": "abc", "expires_in": 3600})
    if request.url.path == "/RS/API/api/currentuser/orgs":
        return httpx.Response(
            200,
            json={
                "Rows": [{"Organisation": {"ID": 97271, "Name": "ACME"}}],
                "TotalRows": 1,
                "CurrentPageNumber": 1,
                "PageSize": 300,
            },
        )
    raise AssertionError(f"unexpected request: {request.url}")


def make_client_with_orgs_response(orgs_response: httpx.Response) -> MinimaxClient:
    def route(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/oauth20/token"):
            return httpx.Response(200, json=TOKEN)
        if request.url.path == "/RS/API/api/currentuser/orgs":
            return orgs_response
        raise AssertionError(f"unexpected request: {request.url}")

    http = httpx.Client(transport=httpx.MockTransport(route))
    return MinimaxClient(credentials=CREDENTIALS, organisation_id=97271, http=http)


def test_organisations_lists_what_the_credentials_can_reach() -> None:
    http = httpx.Client(transport=httpx.MockTransport(handler))
    client = MinimaxClient(credentials=CREDENTIALS, organisation_id=97271, http=http)
    organisations = client.organisations()
    assert [org.id for org in organisations] == [97271]


def test_organisations_skips_a_row_whose_nested_organisation_is_null() -> None:
    # {"Organisation": None, "APIAccess": "D"} carries no usable reference at
    # all: not a nested object, and no ID on the row itself. A caller verifying
    # "credentials reach exactly what I expect" must not see a phantom entry.
    rows = {
        "Rows": [{"Organisation": None, "APIAccess": "D"}],
        "TotalRows": 1,
        "CurrentPageNumber": 1,
        "PageSize": 300,
    }
    client = make_client_with_orgs_response(httpx.Response(200, json=rows))
    assert client.organisations() == []


def test_organisations_accepts_a_bare_reference_row() -> None:
    # No "Organisation" wrapper at all, just the reference object itself.
    rows = {
        "Rows": [{"ID": 97271, "Name": "ACME"}],
        "TotalRows": 1,
        "CurrentPageNumber": 1,
        "PageSize": 300,
    }
    client = make_client_with_orgs_response(httpx.Response(200, json=rows))
    organisations = client.organisations()
    assert [org.id for org in organisations] == [97271]


def test_client_works_as_a_context_manager() -> None:
    http = httpx.Client(transport=httpx.MockTransport(handler))
    with MinimaxClient(credentials=CREDENTIALS, organisation_id=97271, http=http) as client:
        assert client.organisations()[0].name == "ACME"


def test_close_does_not_close_an_injected_http_client() -> None:
    # An injected client is owned by its caller; MinimaxClient must not close
    # something it did not create, or it would break other users of that client.
    http = httpx.Client(transport=httpx.MockTransport(handler))
    client = MinimaxClient(credentials=CREDENTIALS, organisation_id=97271, http=http)
    client.close()
    assert not http.is_closed
    http.close()


def test_context_manager_closes_an_owned_client_even_when_the_body_raises() -> None:
    # No `http=` is passed, so the client constructs and owns its own httpx.Client.
    # `_http` is an implementation detail inspected here only to confirm cleanup.
    with pytest.raises(RuntimeError):
        with MinimaxClient(credentials=CREDENTIALS, organisation_id=97271) as client:
            owned_http = client._http
            raise RuntimeError("boom")
    assert owned_http.is_closed


def test_public_surface_is_importable_from_the_package_root() -> None:
    import minimax_api

    for name in (
        "MinimaxClient",
        "Credentials",
        "Region",
        "RS",
        "MinimaxError",
        "MinimaxAuthError",
        "RateBudgetExceeded",
        "ConcurrencyError",
        "NotFoundError",
        "ValidationError",
        "TransportError",
        "AmbiguousWriteError",
        "paginate",
        "DEFAULT_PAGE_SIZE",
    ):
        assert hasattr(minimax_api, name), name
