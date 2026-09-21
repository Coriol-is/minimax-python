"""Exceptions raised by the client.

Every exception answers one question for the caller: may this be retried,
and if so, when? That distinction is load-bearing. Retrying a rejected
credential locks the customer's Minimax application, and replaying a write
that lost a RowVersion race silently overwrites another actor's change.
"""

from __future__ import annotations


class MinimaxError(Exception):
    """Base class for every error this library raises."""

    #: Whether re-issuing the same call unchanged is a legitimate response.
    retryable: bool = False


class MinimaxAuthError(MinimaxError):
    """The token endpoint rejected the request.

    ``terminal`` marks a credential rejection. Several consecutive credential
    rejections lock the Minimax application, and recovery means deleting and
    recreating it, so a terminal failure must never be retried.
    """

    def __init__(self, message: str, *, terminal: bool) -> None:
        super().__init__(message)
        self.terminal = terminal

    @property
    def retryable(self) -> bool:  # type: ignore[override]
        return not self.terminal


class RateBudgetExceeded(MinimaxError):
    """The request was not sent: the organisation's request budget is spent."""

    retryable = True

    def __init__(self, message: str, *, retry_after: float) -> None:
        super().__init__(message)
        #: Seconds to wait before the budget allows another request.
        self.retry_after = retry_after


class ConcurrencyError(MinimaxError):
    """The record changed between the read and the write (RowVersion conflict).

    Re-read the record, decide whether the change is still wanted, and
    re-apply it. Never replay the original payload.
    """


class NotFoundError(MinimaxError):
    """The requested record or endpoint does not exist."""


class ValidationError(MinimaxError):
    """Minimax rejected the payload and explained why."""

    def __init__(self, message: str, *, status_code: int, payload: object) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class TransportError(MinimaxError):
    """A timeout, connection failure, or 5xx. Safe to retry."""

    retryable = True
