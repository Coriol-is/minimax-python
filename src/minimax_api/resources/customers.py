"""Customer records."""

from __future__ import annotations

from minimax_api._generated.models import Customer, CustomerSearch
from minimax_api.errors import ValidationError
from minimax_api.pagination import DEFAULT_PAGE_SIZE, paginate
from minimax_api.transport import Transport


class Customers:
    def __init__(self, transport: Transport, organisation_id: int) -> None:
        self._transport = transport
        self._organisation_id = organisation_id
        self._base = f"/api/orgs/{organisation_id}/customers"

    def list(
        self, *, search: str | None = None, page_size: int = DEFAULT_PAGE_SIZE
    ) -> list[CustomerSearch]:
        params = {"SearchString": search} if search else None
        rows = paginate(
            self._transport, self._base, CustomerSearch, params=params, page_size=page_size
        )
        return list(rows)

    def get(self, customer_id: int) -> Customer:
        response = self._transport.request("GET", f"{self._base}/{customer_id}")
        return Customer.model_validate(response.json)

    def create(self, customer: Customer) -> int:
        """Create a customer and return its new ID.

        The ID exists only in the response's `Location` header. If this process
        dies before persisting the returned value, the record exists in Minimax
        with no local trace — record the intent to write before calling, and
        reconcile by search after an unknown outcome. This library deliberately
        does not manage idempotency: it has no durable storage.
        """
        payload = customer.model_dump(by_alias=True, exclude_none=True)
        response = self._transport.request("POST", self._base, json=payload)
        created = response.location_id
        if created is None:
            raise ValidationError(
                "customer was created but Minimax returned no Location header, so its ID is "
                "unknown; reconcile by search before retrying",
                status_code=response.status_code,
                payload=response.json,
            )
        return created

    def update(self, customer: Customer) -> None:
        """Update a customer read moments ago.

        Pass the object as returned by `get`, with its `row_version` intact. A
        stale `row_version` raises ConcurrencyError: re-read, re-evaluate, and
        re-apply — never replay.
        """
        if customer.customer_id is None:
            raise ValidationError(
                "customer_id is required to update a customer",
                status_code=0,
                payload=None,
            )
        if not customer.row_version:
            raise ValidationError(
                "row_version is required to update a customer; read the record first so "
                "Minimax can detect a concurrent change",
                status_code=0,
                payload=None,
            )
        payload = customer.model_dump(by_alias=True, exclude_none=True)
        self._transport.request("PUT", f"{self._base}/{customer.customer_id}", json=payload)
