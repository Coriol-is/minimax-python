"""Walking a collection endpoint.

The Swagger document does not describe the paging query parameters, but the
live API honours them: `PageSize` sets the page length and `CurrentPage`
selects the page. Both were verified against organisation 97271 on 2026-09-21.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Any, TypeVar

from minimax_api.envelope import MinimaxModel, SearchResult
from minimax_api.transport import Transport

T = TypeVar("T", bound=MinimaxModel)

#: Large enough that most code lists arrive in one request, which matters when
#: the whole organisation gets 1,000 requests a day.
DEFAULT_PAGE_SIZE = 300


def paginate(  # noqa: UP047
    transport: Transport,
    path: str,
    model: type[T],
    *,
    params: Mapping[str, Any] | None = None,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> Iterator[T]:
    """Yield every row of a collection endpoint, one request per page."""
    page_number = 1
    seen = 0

    while True:
        query: dict[str, Any] = dict(params or {})
        query["PageSize"] = page_size
        query["CurrentPage"] = page_number

        payload = transport.request("GET", path, params=query).json

        if isinstance(payload, list):
            # A few endpoints answer with a bare array rather than an envelope.
            for item in payload:
                yield model.model_validate(item)
            return

        result = SearchResult[model].model_validate(payload)  # type: ignore[valid-type]
        if not result.rows:
            return

        yield from result.rows
        seen += len(result.rows)

        if seen >= result.total_rows:
            return
        page_number += 1
