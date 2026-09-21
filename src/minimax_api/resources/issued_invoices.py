"""Issued invoices.

An accepted write is a draft, not a business event. Documents created through
the API arrive with status `O` (nacrt); an invoice becomes real only after the
corresponding custom action succeeds and the result is read back. This library
creates and reads; deciding when to issue belongs to the caller.
"""

from __future__ import annotations

from minimax_api._generated.models import IssuedInvoice
from minimax_api.errors import AmbiguousWriteError
from minimax_api.pagination import DEFAULT_PAGE_SIZE, paginate
from minimax_api.transport import Transport


class IssuedInvoices:
    def __init__(self, transport: Transport, organisation_id: int) -> None:
        self._transport = transport
        self._organisation_id = organisation_id
        self._base = f"/api/orgs/{organisation_id}/issuedinvoices"

    def list(self, *, page_size: int = DEFAULT_PAGE_SIZE) -> list[IssuedInvoice]:
        return list(paginate(self._transport, self._base, IssuedInvoice, page_size=page_size))

    def get(self, invoice_id: int) -> IssuedInvoice:
        response = self._transport.request("GET", f"{self._base}/{invoice_id}")
        return IssuedInvoice.model_validate(response.json)

    def create(self, invoice: IssuedInvoice) -> int:
        """Create a draft invoice and return its ID from the `Location` header."""
        payload = invoice.model_dump(by_alias=True, exclude_none=True)
        response = self._transport.request("POST", self._base, json=payload)
        created = response.location_id
        if created is None:
            # The invoice was created -- Minimax just didn't tell us the new
            # ID. Never surface this as ValidationError: a caller with the
            # obvious handler for "the server rejected my payload" would fix
            # nothing and resubmit, duplicating the invoice in the ledger.
            raise AmbiguousWriteError(
                "invoice was created but Minimax returned no Location header, so its ID "
                "is unknown. Reconcile by searching for the invoice (e.g. by document "
                "number or the customer's order reference) before creating it again -- "
                "do not resend this payload."
            )
        return created
