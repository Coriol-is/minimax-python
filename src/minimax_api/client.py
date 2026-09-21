"""The object callers construct."""

from __future__ import annotations

from types import TracebackType

import httpx

from minimax_api._generated.models import FkField
from minimax_api.auth import Authenticator, Credentials, TokenStore
from minimax_api.budget import Budget
from minimax_api.pagination import paginate
from minimax_api.region import RS, Region
from minimax_api.resources.codelists import CodeLists
from minimax_api.resources.customers import Customers
from minimax_api.resources.issued_invoices import IssuedInvoices
from minimax_api.transport import Transport

DEFAULT_TIMEOUT = httpx.Timeout(30.0, connect=10.0)


class MinimaxClient:
    """A client bound to one organisation.

    ```python
    from minimax_api import Credentials, MinimaxClient

    with MinimaxClient(
        credentials=Credentials(client_id=..., client_secret=..., username=..., password=...),
        organisation_id=97271,
    ) as client:
        rsd = client.codelists.currency_by_code("RSD")
    ```
    """

    def __init__(
        self,
        *,
        credentials: Credentials,
        organisation_id: int,
        region: Region = RS,
        http: httpx.Client | None = None,
        token_store: TokenStore | None = None,
        budget: Budget | None = None,
    ) -> None:
        self._owns_http = http is None
        self._http = http if http is not None else httpx.Client(timeout=DEFAULT_TIMEOUT)
        self.region = region
        self.organisation_id = organisation_id

        self.authenticator = Authenticator(
            credentials=credentials, region=region, http=self._http, store=token_store
        )
        self.budget = budget if budget is not None else Budget()
        self.transport = Transport(
            region=region,
            authenticator=self.authenticator,
            http=self._http,
            budget=self.budget,
        )

        self.codelists = CodeLists(self.transport, organisation_id)
        self.customers = Customers(self.transport, organisation_id)
        self.issued_invoices = IssuedInvoices(self.transport, organisation_id)

    def organisations(self) -> list[FkField]:
        """Every organisation these credentials can reach.

        Worth calling first on any new deployment: an organisation in this list
        that you did not expect means the API right was granted more broadly
        than intended.
        """
        rows = paginate(self.transport, "/api/currentuser/orgs", FkField)
        result = []
        for row in rows:
            nested = row.model_extra.get("Organisation") if row.model_extra else None
            result.append(FkField.model_validate(nested) if isinstance(nested, dict) else row)
        return result

    def close(self) -> None:
        if self._owns_http:
            self._http.close()

    def __enter__(self) -> MinimaxClient:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()
