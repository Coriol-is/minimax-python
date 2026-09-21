"""HTTP plumbing: one place that knows about sockets, status codes, and retries.

Nothing above this layer touches httpx, and nothing in this layer knows what a
customer or an invoice is.
"""

from __future__ import annotations

import re
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import httpx

from minimax_api.auth import Authenticator
from minimax_api.errors import (
    ConcurrencyError,
    NotFoundError,
    RateBudgetExceeded,
    TransportError,
    ValidationError,
)
from minimax_api.region import Region

if TYPE_CHECKING:
    from minimax_api.budget import Budget  # type: ignore[import-untyped]

_LOCATION_ID = re.compile(r"/(\d+)\s*$")
_CONCURRENCY_MARKER = "concurrency error"


@dataclass(frozen=True)
class Response:
    """What came back, decoded but not interpreted."""

    status_code: int
    json: Any
    headers: Mapping[str, str]

    @property
    def location_id(self) -> int | None:
        """The created record's ID, which write methods return only in a header."""
        location = self.headers.get("Location") or self.headers.get("location")
        if not location:
            return None
        match = _LOCATION_ID.search(location)
        return int(match.group(1)) if match else None


class Transport:
    """Issues authenticated requests and turns HTTP outcomes into typed errors."""

    def __init__(
        self,
        *,
        region: Region,
        authenticator: Authenticator,
        http: httpx.Client,
        budget: Budget | None = None,
        max_transport_retries: int = 3,
        backoff_base: float = 0.5,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._region = region
        self._auth = authenticator
        self._http = http
        self._budget = budget
        self._max_transport_retries = max_transport_retries
        self._backoff_base = backoff_base
        self._sleep = sleep

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
    ) -> Response:
        url = f"{self._region.base_url}{path}"
        refreshed = False

        for attempt in range(self._max_transport_retries):
            if self._budget is not None:
                self._budget.check()

            headers = {
                "Authorization": f"Bearer {self._auth.access_token()}",
                "Accept": "application/json",
            }
            try:
                raw = self._http.request(method, url, params=params, json=json, headers=headers)
            except httpx.HTTPError as error:
                if attempt == self._max_transport_retries - 1:
                    raise TransportError(f"{method} {path} failed: {error}") from error
                self._sleep(self._backoff_base * (2**attempt))
                continue

            if self._budget is not None:
                self._budget.record()

            if raw.status_code == 401:
                if not refreshed:
                    # The token expired mid-flight. This is not a credential
                    # rejection: the token endpoint is the only place that judges
                    # credentials, and it has its own terminal handling.
                    refreshed = True
                    self._auth.invalidate()
                    continue
                else:
                    # Already refreshed once, don't loop forever
                    raise TransportError(f"{method} {path} returned HTTP 401 after token refresh")

            if raw.status_code >= 500:
                if attempt == self._max_transport_retries - 1:
                    raise TransportError(f"{method} {path} returned HTTP {raw.status_code}")
                self._sleep(self._backoff_base * (2**attempt))
                continue

            return self._interpret(method, path, raw)

        raise TransportError(f"{method} {path} exhausted {self._max_transport_retries} attempts")

    def _interpret(self, method: str, path: str, raw: httpx.Response) -> Response:
        payload = self._decode(raw)

        if raw.status_code == 429:
            retry_after = float(raw.headers.get("Retry-After", 3600))
            if self._budget is not None:
                self._budget.penalize(retry_after)
            raise RateBudgetExceeded(
                f"{method} {path} was rejected by the server's rate limit",
                retry_after=retry_after,
            )

        if raw.status_code == 404:
            raise NotFoundError(f"{method} {path} returned HTTP 404")

        if 400 <= raw.status_code < 500:
            message = self._message(payload) or raw.text[:300]
            if _CONCURRENCY_MARKER in message.lower():
                raise ConcurrencyError(
                    f"{method} {path}: {message}. Re-read the record and re-evaluate the "
                    "change; do not replay this payload."
                )
            raise ValidationError(
                f"{method} {path}: {message}", status_code=raw.status_code, payload=payload
            )

        return Response(status_code=raw.status_code, json=payload, headers=dict(raw.headers))

    @staticmethod
    def _decode(raw: httpx.Response) -> Any:
        if not raw.content:
            return None
        try:
            return raw.json()
        except ValueError:
            return raw.text

    @staticmethod
    def _message(payload: Any) -> str:
        if isinstance(payload, dict):
            for key in ("Message", "message", "error_description", "error"):
                value = payload.get(key)
                if isinstance(value, str):
                    return value
        return ""
