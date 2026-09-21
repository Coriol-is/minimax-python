import httpx

from minimax_api import MinimaxClient
from minimax_api.auth import Credentials

CREDENTIALS = Credentials(
    client_id="client", client_secret="secret", username="user", password="password"
)


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


def test_organisations_lists_what_the_credentials_can_reach() -> None:
    http = httpx.Client(transport=httpx.MockTransport(handler))
    client = MinimaxClient(credentials=CREDENTIALS, organisation_id=97271, http=http)
    organisations = client.organisations()
    assert [org.id for org in organisations] == [97271]


def test_client_works_as_a_context_manager() -> None:
    http = httpx.Client(transport=httpx.MockTransport(handler))
    with MinimaxClient(credentials=CREDENTIALS, organisation_id=97271, http=http) as client:
        assert client.organisations()[0].name == "ACME"


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
    ):
        assert hasattr(minimax_api, name), name
