"""HTTP plumbing: one place that knows about sockets, status codes, and retries.

Nothing above this layer touches httpx, and nothing in this layer knows what a
customer or an invoice is.
"""

from __future__ import annotations

import email.utils
import re
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

import httpx

from minimax_api.auth import Authenticator
from minimax_api.errors import (
    AmbiguousWriteError,
    ConcurrencyError,
    NotFoundError,
    RateBudgetExceeded,
    TransportError,
    ValidationError,
)
from minimax_api.region import Region

if TYPE_CHECKING:
    from minimax_api.budget import Budget

_LOCATION_ID = re.compile(r"/(\d+)\s*$")

# UNVERIFIED: the vendor's Swagger only says "Row version is used for
# concurrency check" -- we have never captured the actual wording of a live
# RowVersion conflict response. The single literal "concurrency error" this
# used to match came from an invented test fixture, not a real one. These are
# best-effort guesses at plausible wordings; replace this with a real
# captured response the moment one exists, and narrow the match again.
#
# One second-hand data point, from Minimax support (2026-09-21) describing the
# behaviour to a sibling Odoo integration: "the second call fails with an error
# saying it does not hold the latest record". That paraphrase contains none of
# the words a naive guess would pick, which is why "latest record" is matched
# too -- and why this whole list should be treated as a stopgap. Failing to
# recognise a conflict is the expensive direction: the caller then sees a
# plain ValidationError and may replay a stale write over someone else's edit.
_CONCURRENCY_MARKERS = ("concurrency", "rowversion", "row version", "latest record")

#: Methods whose repetition cannot create a duplicate side effect. Retrying
#: any other method (POST, PATCH, ...) after an ambiguous outcome risks
#: creating the same document twice, so those are never retried here.
_IDEMPOTENT_METHODS = frozenset({"GET", "HEAD", "PUT", "DELETE"})

#: httpx errors raised before a connection was ever established. The request
#: never left this process, so it cannot have spent any of the organisation's
#: request budget.
_CONNECT_ERRORS = (httpx.ConnectError, httpx.ConnectTimeout)

_DEFAULT_RETRY_AFTER = 3600.0


def _parse_retry_after(raw: str | None) -> float:
    """Parse a `Retry-After` header: delta-seconds or an HTTP-date (RFC 7231).

    Falls back to the default on anything unparseable. A malformed header
    must never escape as an untyped exception -- that would skip
    `RateBudgetExceeded` (and `Budget.penalize`) entirely, leaving the client
    free to keep hammering an organisation Minimax has already rate-limited.
    """
    if not raw:
        return _DEFAULT_RETRY_AFTER

    raw = raw.strip()
    try:
        return float(raw)
    except ValueError:
        pass

    try:
        parsed = email.utils.parsedate_to_datetime(raw)
    except (TypeError, ValueError, IndexError):
        return _DEFAULT_RETRY_AFTER
    if parsed is None:
        return _DEFAULT_RETRY_AFTER

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return max((parsed - datetime.now(UTC)).total_seconds(), 0.0)


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
        # Remove query string and fragment, then strip trailing slashes
        path = location.split("?")[0].split("#")[0].rstrip("/")
        match = _LOCATION_ID.search(path)
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
        attempts = 0
        refreshed = False
        idempotent = method.upper() in _IDEMPOTENT_METHODS

        while True:
            if attempts >= self._max_transport_retries:
                raise TransportError(
                    f"{method} {path} exhausted {self._max_transport_retries} transport attempts"
                )

            if self._budget is not None:
                self._budget.check()

            headers = {
                "Authorization": f"Bearer {self._auth.access_token()}",
                "Accept": "application/json",
            }
            try:
                raw = self._http.request(method, url, params=params, json=json, headers=headers)
            except httpx.HTTPError as error:
                # A connect error never reached the server, so it never spent
                # any of the organisation's budget. Anything past that point
                # (a timeout waiting for a reply, a dropped read, ...) may
                # well have -- Minimax could have received and even committed
                # the request before the connection died.
                if not isinstance(error, _CONNECT_ERRORS) and self._budget is not None:
                    self._budget.record()

                if not idempotent:
                    # Never retry a write whose outcome we cannot see. The
                    # request may have already committed; sending it again
                    # would risk a duplicate document, and this library has
                    # no durable log to tell a retry from a duplicate.
                    raise AmbiguousWriteError(
                        f"{method} {path} failed with {error!r} before a response was "
                        "received; whether it reached Minimax is unknown, so it was not "
                        "retried. Reconcile by searching for the record using its "
                        "business reference before creating it again -- do not resend "
                        "this payload."
                    ) from error

                self._sleep(self._backoff_base * (2**attempts))
                attempts += 1
                continue

            if self._budget is not None:
                self._budget.record()

            if raw.status_code == 401:
                if not refreshed:
                    # The token expired mid-flight. This is not a credential
                    # rejection: the token endpoint is the only place that judges
                    # credentials, and it has its own terminal handling.
                    # This path does NOT consume a transport attempt.
                    #
                    # It is also the ONE place a non-idempotent request is sent
                    # twice, and deliberately so: a 401 is a definitive refusal
                    # from the server, not an unknown outcome -- the request was
                    # received and rejected, so nothing was written and a resend
                    # cannot duplicate a document. Bounded to a single retry;
                    # a second 401 raises below.
                    refreshed = True
                    self._auth.invalidate()
                    continue
                else:
                    # Already refreshed once, don't loop forever
                    raise TransportError(f"{method} {path} returned HTTP 401 after token refresh")

            if raw.status_code >= 500:
                if not idempotent:
                    raise AmbiguousWriteError(
                        f"{method} {path} returned HTTP {raw.status_code}; whether Minimax "
                        "committed the write before failing is unknown, so it was not "
                        "retried. Reconcile by searching for the record using its "
                        "business reference before creating it again -- do not resend "
                        "this payload."
                    )
                self._sleep(self._backoff_base * (2**attempts))
                attempts += 1
                continue

            return self._interpret(method, path, raw)

    def _interpret(self, method: str, path: str, raw: httpx.Response) -> Response:
        payload = self._decode(raw)

        if raw.status_code == 429:
            retry_after = _parse_retry_after(raw.headers.get("Retry-After"))
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
            lowered = message.lower()
            if any(marker in lowered for marker in _CONCURRENCY_MARKERS):
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
