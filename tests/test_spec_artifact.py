import json
from pathlib import Path

SPEC = Path(__file__).resolve().parent.parent / "spec" / "swagger-2026-09-21.json"


def test_the_spec_is_committed_and_parses() -> None:
    assert SPEC.exists(), "the Swagger artifact must be committed, not downloaded at build time"
    document = json.loads(SPEC.read_text())
    assert document["swagger"] == "2.0"
    assert document["basePath"] == "/RS/API"


def test_the_spec_still_contains_the_operations_the_facade_relies_on() -> None:
    document = json.loads(SPEC.read_text())
    for path in (
        "/api/orgs/{organisationId}/customers",
        "/api/orgs/{organisationId}/customers/{customerId}",
        "/api/orgs/{organisationId}/currencies",
        "/api/orgs/{organisationId}/countries",
        "/api/orgs/{organisationId}/vatrates",
        "/api/orgs/{organisationId}/issuedinvoices",
    ):
        assert path in document["paths"], path
