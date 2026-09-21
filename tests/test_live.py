"""Read-only tests against a real Minimax organisation.

Run with: uv run pytest -m live -v

These pin the facts that the vendor's own documentation gets wrong. If one of
them fails, either the organisation's configuration changed or Minimax changed
the API — investigate before touching the assertion.
"""

from __future__ import annotations

import pytest

from minimax_api import MinimaxClient

pytestmark = pytest.mark.live


def test_credentials_reach_exactly_the_expected_organisation(live_client: MinimaxClient) -> None:
    organisations = live_client.organisations()
    ids = [org.id for org in organisations]
    assert live_client.organisation_id in ids
    # A broader grant than intended is a security finding, not a convenience.
    assert len(ids) == 1, f"credentials reach more organisations than expected: {ids}"


def test_serbia_is_country_id_3_not_the_documented_192(live_client: MinimaxClient) -> None:
    serbia = live_client.codelists.country_by_code("RS")
    assert serbia is not None
    assert serbia.country_id == 3


def test_rsd_is_currency_id_2_and_7_is_not_it(live_client: MinimaxClient) -> None:
    currencies = live_client.codelists.currencies()
    by_code = {row.code: row.currency_id for row in currencies}
    assert by_code["RSD"] == 2
    # Vendor samples present 7 as the default currency. It is the Czech koruna.
    assert by_code["RSD"] != 7


def test_standard_vat_rate_is_twenty_percent(live_client: MinimaxClient) -> None:
    rates = {row.code: row for row in live_client.codelists.vat_rates()}
    s_rate = rates["S"]
    assert s_rate.percent == 20.0
    # VatRateId and VatRatePercentage.ID are separate ID spaces.
    assert s_rate.vat_rate_percentage is not None
    assert s_rate.vat_rate_id != s_rate.vat_rate_percentage.id


def test_code_lists_paginate_in_one_request(live_client: MinimaxClient) -> None:
    countries = live_client.codelists.countries()
    assert len(countries) > 200
