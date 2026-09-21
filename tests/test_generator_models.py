import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from generate import build_models, class_name, snake_case  # noqa: E402


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ("CustomerId", "customer_id"),
        ("Name", "name"),
        ("VATIdentificationNumber", "vat_identification_number"),
        ("EInvoiceIssuing", "e_invoice_issuing"),
        ("GLN", "gln"),
        ("RowVersion", "row_version"),
        ("ID", "id"),
    ],
)
def test_snake_case_handles_acronyms(given: str, expected: str) -> None:
    assert snake_case(given) == expected


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ("SAOP.API.Models.Customer.Customer", "Customer"),
        ("SAOP.API.Models.Customer.CustomerSearch", "CustomerSearch"),
        ("SAOP.API.Common.mMApiFkField", "FkField"),
    ],
)
def test_class_name_strips_the_namespace(given: str, expected: str) -> None:
    assert class_name(given, collisions=set()) == expected


def test_colliding_leaf_names_get_their_parent_segment() -> None:
    collisions = {"Chart"}
    assert class_name("SAOP.API.Models.Dashboard.Chart", collisions=collisions) == "DashboardChart"
    assert class_name("SAOP.API.Models.Report.Chart", collisions=collisions) == "ReportChart"


MINI_SPEC: dict[str, Any] = {
    "definitions": {
        "SAOP.API.Common.mMApiFkField": {
            "type": "object",
            "properties": {
                "ID": {"type": "integer", "format": "int64"},
                "Name": {"type": "string", "readOnly": True},
                "ResourceUrl": {"type": "string", "readOnly": True},
            },
        },
        "SAOP.API.Models.Customer.Customer": {
            "type": "object",
            "properties": {
                "CustomerId": {
                    "type": "integer",
                    "format": "int64",
                    "description": '"Customer id."',
                },
                "Name": {"type": "string"},
                "Country": {"$ref": "#/definitions/SAOP.API.Common.mMApiFkField"},
                "RebatePercent": {"type": "number", "format": "double"},
                "Usage": {"type": "string"},
                "RowVersion": {"type": "string", "format": "byte"},
                "Contacts": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/SAOP.API.Common.mMApiFkField"},
                },
            },
        },
        "SAOP.API.Models.SearchResult[SAOP.API.Models.Customer.Customer]": {
            "type": "object",
            "properties": {"Rows": {"type": "array"}},
        },
    }
}


def test_generated_source_declares_the_expected_classes() -> None:
    source = build_models(MINI_SPEC)
    assert "class FkField(MinimaxModel):" in source
    assert "class Customer(MinimaxModel):" in source
    # The envelope is hand-written once; its 37 generic instantiations are skipped.
    assert "SearchResult" not in source


def test_generated_fields_carry_types_and_aliases() -> None:
    source = build_models(MINI_SPEC)
    assert 'customer_id: int | None = Field(default=None, alias="CustomerId")' in source
    assert 'name: str | None = Field(default=None, alias="Name")' in source
    assert 'country: FkField | None = Field(default=None, alias="Country")' in source
    assert 'rebate_percent: float | None = Field(default=None, alias="RebatePercent")' in source
    assert 'contacts: list[FkField] | None = Field(default=None, alias="Contacts")' in source


def test_generated_source_is_importable_and_round_trips_a_payload() -> None:
    namespace: dict[str, object] = {}
    exec(compile(build_models(MINI_SPEC), "<generated>", "exec"), namespace)  # noqa: S102
    customer = namespace["Customer"].model_validate(  # type: ignore[attr-defined]
        {"CustomerId": 1, "Name": "ACME", "Country": {"ID": 3, "Name": "RS"}}
    )
    assert customer.customer_id == 1
    assert customer.country.id == 3
    # Round-tripping must produce the vendor's spelling, not Python's.
    assert customer.model_dump(by_alias=True, exclude_none=True)["CustomerId"] == 1


def test_generated_header_warns_against_editing() -> None:
    source = build_models(MINI_SPEC)
    assert "do not edit" in source.lower()
