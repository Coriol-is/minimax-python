import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from generate import build_operations, operation_names  # noqa: E402

_CUSTOMER = "SAOP.API.Models.Customer.Customer"
_CUSTOMER_SEARCH = "SAOP.API.Models.Customer.CustomerSearch"
_CUSTOMER_SEARCH_RESULT = f"SAOP.API.Models.SearchResult[{_CUSTOMER_SEARCH}]"

MINI_SPEC: dict[str, Any] = {
    "definitions": {
        _CUSTOMER: {
            "type": "object",
            "properties": {"CustomerId": {"type": "integer"}},
        },
        _CUSTOMER_SEARCH: {
            "type": "object",
            "properties": {"CustomerId": {"type": "integer"}},
        },
        _CUSTOMER_SEARCH_RESULT: {
            "type": "object",
            "properties": {
                "Rows": {"type": "array", "items": {"$ref": f"#/definitions/{_CUSTOMER_SEARCH}"}}
            },
        },
    },
    "paths": {
        "/api/orgs/{organisationId}/customers": {
            "get": {
                "operationId": "Customer_Get",
                "parameters": [
                    {"name": "organisationId", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"schema": {"$ref": f"#/definitions/{_CUSTOMER_SEARCH_RESULT}"}}
                },
            },
            "post": {
                "operationId": "Customer_Post",
                "parameters": [
                    {"name": "organisationId", "in": "path", "required": True, "type": "integer"},
                    {
                        "name": "customer",
                        "in": "body",
                        "schema": {"$ref": f"#/definitions/{_CUSTOMER}"},
                    },
                ],
                "responses": {"200": {"description": "OK"}},
            },
        },
        "/api/orgs/{organisationId}/customers/{customerId}": {
            "get": {
                "operationId": "Customer_Get",
                "parameters": [
                    {"name": "organisationId", "in": "path", "required": True, "type": "integer"},
                    {"name": "customerId", "in": "path", "required": True, "type": "integer"},
                ],
                "responses": {"200": {"schema": {"$ref": f"#/definitions/{_CUSTOMER}"}}},
            },
            "put": {
                "operationId": "Customer_Put",
                "parameters": [
                    {"name": "organisationId", "in": "path", "required": True, "type": "integer"},
                    {"name": "customerId", "in": "path", "required": True, "type": "integer"},
                    {
                        "name": "customer",
                        "in": "body",
                        "schema": {"$ref": f"#/definitions/{_CUSTOMER}"},
                    },
                ],
                "responses": {"200": {"description": "OK"}},
            },
        },
        "/api/orgs/{organisationId}/customers/code({code})": {
            "get": {
                "operationId": "Customer_Get",
                "parameters": [
                    {"name": "organisationId", "in": "path", "required": True, "type": "integer"},
                    {"name": "code", "in": "path", "required": True, "type": "string"},
                ],
                "responses": {"200": {"schema": {"$ref": f"#/definitions/{_CUSTOMER}"}}},
            },
        },
    },
}


def test_colliding_operation_ids_are_disambiguated_by_path() -> None:
    names = set(operation_names(MINI_SPEC))
    assert {"customer_get", "customer_get_by_customer_id", "customer_get_by_code"} <= names


def test_every_generated_name_is_unique() -> None:
    names = list(operation_names(MINI_SPEC))
    assert len(names) == len(set(names))


def test_collection_get_returns_the_envelope() -> None:
    source = build_operations(MINI_SPEC)
    assert "def customer_get(" in source
    assert "-> SearchResult[CustomerSearch]:" in source


def test_single_get_returns_the_model() -> None:
    source = build_operations(MINI_SPEC)
    assert "def customer_get_by_customer_id(" in source
    assert "customer_id: int," in source
    assert "-> Customer:" in source


def test_post_without_a_response_schema_returns_the_location_id() -> None:
    source = build_operations(MINI_SPEC)
    assert "def customer_post(" in source
    assert "body: Customer," in source
    assert "-> int | None:" in source
    assert "return response.location_id" in source


def test_put_returns_none() -> None:
    source = build_operations(MINI_SPEC)
    assert "def customer_put_by_customer_id(" in source
    assert "-> None:" in source


def test_paths_are_interpolated_with_the_python_parameter_names() -> None:
    source = build_operations(MINI_SPEC)
    assert 'f"/api/orgs/{organisation_id}/customers/{customer_id}"' in source
    assert 'f"/api/orgs/{organisation_id}/customers/code({code})"' in source


def test_body_is_serialised_with_vendor_field_names() -> None:
    source = build_operations(MINI_SPEC)
    assert "body.model_dump(by_alias=True, exclude_none=True)" in source


def test_generated_operations_compile() -> None:
    compile(build_operations(MINI_SPEC), "<generated>", "exec")
