"""Reference data — the records documents point at by ID.

Every ID here is organisation-specific. The vendor's published samples give
`Country.ID` 192 for Serbia and `Currency.ID` 7 as a default; in the Serbian
organisation 97271, Serbia is 3, RSD is 2, and 7 is the Czech koruna. That is
why this module resolves and never assumes, and why no ID constant appears
anywhere in this library.
"""

from __future__ import annotations

from minimax_api._generated.models import Account, Country, Currency, VatRate
from minimax_api.pagination import DEFAULT_PAGE_SIZE, paginate
from minimax_api.transport import Transport


class CodeLists:
    """Read access to an organisation's reference data."""

    def __init__(self, transport: Transport, organisation_id: int) -> None:
        self._transport = transport
        self._organisation_id = organisation_id

    def _base(self, module: str) -> str:
        return f"/api/orgs/{self._organisation_id}/{module}"

    def countries(self, *, page_size: int = DEFAULT_PAGE_SIZE) -> list[Country]:
        path = self._base("countries")
        return list(paginate(self._transport, path, Country, page_size=page_size))

    def currencies(self, *, page_size: int = DEFAULT_PAGE_SIZE) -> list[Currency]:
        path = self._base("currencies")
        return list(paginate(self._transport, path, Currency, page_size=page_size))

    def vat_rates(self, *, page_size: int = DEFAULT_PAGE_SIZE) -> list[VatRate]:
        return list(paginate(self._transport, self._base("vatrates"), VatRate, page_size=page_size))

    def accounts(self, *, page_size: int = DEFAULT_PAGE_SIZE) -> list[Account]:
        return list(paginate(self._transport, self._base("accounts"), Account, page_size=page_size))

    def country_by_code(self, code: str) -> Country | None:
        """Find a country by its ISO code, e.g. `RS`. Returns None if absent."""
        return next((row for row in self.countries() if row.code == code), None)

    def currency_by_code(self, code: str) -> Currency | None:
        """Find a currency by its ISO code, e.g. `RSD`. Returns None if absent."""
        return next((row for row in self.currencies() if row.code == code), None)
