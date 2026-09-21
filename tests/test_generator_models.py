import json
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from generate import (  # noqa: E402
    build_models,
    class_name,
    find_collisions,
    newest_spec,
    snake_case,
)


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


# The real spec has two collision shapes the brief's own naming table didn't
# fully cover: generic definitions (`Base[Param]`) that collide on `Base`
# while sharing the same parent namespace segment too. Disambiguating those
# by the *parent segment* (as non-generic collisions are) would leave them
# colliding; the generator instead uses the type parameter's leaf name. This
# once silently collapsed three `Chart[...]` definitions and two
# `ListResult[...]` definitions onto one class name each — the tests below
# pin the fix so a future change to the rule shows up as a visible diff, and
# `test_build_models_refuses_to_silently_merge_colliding_names` pins the
# fallback (`SystemExit`) for whatever collision shape the rule doesn't cover.
def test_generic_family_collisions_are_disambiguated_by_type_parameter() -> None:
    document = json.loads(newest_spec().read_text())
    definitions = document["definitions"]
    collisions = find_collisions(definitions)

    expected = {
        "SAOP.API.Models.Dashboard.Chart[SAOP.API.Models.Dashboard.AgregateInvoice]": (
            "AgregateInvoiceChart"
        ),
        "SAOP.API.Models.Dashboard.Chart[SAOP.API.Models.Dashboard.DashboardCustomer]": (
            "DashboardCustomerChart"
        ),
        "SAOP.API.Models.Dashboard.Chart[SAOP.API.Models.Dashboard.DashboardMonth]": (
            "DashboardMonthChart"
        ),
        "SAOP.API.Models.IssuedInvoice.PaymentMethodSearch": "IssuedInvoicePaymentMethodSearch",
        "SAOP.API.Models.IssuedInvoicePosting.PaymentMethodSearch": (
            "IssuedInvoicePostingPaymentMethodSearch"
        ),
        "SAOP.API.Models.PaymentMethod.PaymentMethodSearch": "PaymentMethodPaymentMethodSearch",
        "SAOP.API.Models.ListResult[SAOP.API.Models.Item.ItemData]": "ItemDataListResult",
        "SAOP.API.Models.ListResult[SAOP.API.Models.Item.ItemPriceListItem]": (
            "ItemPriceListItemListResult"
        ),
    }
    for definition, expected_name in expected.items():
        assert definition in definitions, (
            f"fixture is stale: {definition!r} not in the committed spec"
        )
        assert class_name(definition, collisions=collisions) == expected_name


def test_real_spec_definitions_map_injectively_to_class_names() -> None:
    """Every non-`SearchResult` definition must get its own, distinct class name.

    This is the general guard behind the specific names pinned above: if the
    naming rule ever regresses on some other collision the current spec
    doesn't exercise, this fails without needing a name added to a fixture.
    """
    document = json.loads(newest_spec().read_text())
    definitions = document["definitions"]
    collisions = find_collisions(definitions)

    non_search = [d for d in definitions if not d.startswith("SAOP.API.Models.SearchResult[")]
    names = [class_name(d, collisions=collisions) for d in non_search]

    assert len(non_search) == 90
    assert len(names) == len(set(names)), "naming rule produced duplicate class names"
    assert len(non_search) == len(set(names))


def test_build_models_refuses_to_silently_merge_colliding_names() -> None:
    """A collision the naming rule cannot break must fail loudly, not merge classes.

    Two generic families in different namespaces sharing both their base leaf
    name and their type parameter's leaf name is the documented, known gap in
    the rule (see the module docstring in `scripts/generate.py`): both
    `Foo.Widget[Foo.Bar]` and `Baz.Widget[Foo.Bar]` resolve to `BarWidget`.
    """
    spec: dict[str, Any] = {
        "definitions": {
            "SAOP.API.Models.Foo.Widget[SAOP.API.Models.Foo.Bar]": {
                "type": "object",
                "properties": {},
            },
            "SAOP.API.Models.Baz.Widget[SAOP.API.Models.Foo.Bar]": {
                "type": "object",
                "properties": {},
            },
        }
    }
    with pytest.raises(SystemExit, match="BarWidget"):
        build_models(spec)


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
