"""The pydantic base and the collection envelope every list endpoint returns."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class MinimaxModel(BaseModel):
    """Base for every model, generated or hand-written.

    Minimax field names are PascalCase; Python attributes are snake_case. Wire
    names are always declared explicitly using `Field(alias=...)` on every field
    — never inferred. Unknown fields are kept rather than rejected: the vendor
    adds fields without warning, and a strict model would turn that into a
    caller's outage.
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")


class SearchResult(MinimaxModel, Generic[T]):  # noqa: UP046
    """`{Rows, TotalRows, CurrentPageNumber, PageSize}` — every collection response."""

    rows: list[T] = Field(default_factory=list, alias="Rows")
    #: `None` means the server did not say -- treat that as unknown, not zero.
    #: Defaulting this to 0 used to make `paginate` stop after the first page
    #: whenever an endpoint omitted `TotalRows`, silently truncating the
    #: collection.
    total_rows: int | None = Field(default=None, alias="TotalRows")
    current_page_number: int = Field(default=1, alias="CurrentPageNumber")
    page_size: int = Field(default=0, alias="PageSize")
