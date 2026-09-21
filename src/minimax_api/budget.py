"""Request accounting against the published per-organisation limits.

Minimax publishes 1,000 requests per organisation per rolling 24 hours and
20,000 per month. This module decides whether a request may be sent; it never
waits. The caller owns a scheduler and a database, and a library that blocks a
worker for an unknown number of hours is a bug.

The count is an estimate. Other processes and the Minimax web UI spend from
the same budget, so a server-side rejection always outranks local state.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Protocol

from minimax_api.errors import RateBudgetExceeded

DAY_SECONDS = 24 * 60 * 60
MONTH_SECONDS = 30 * DAY_SECONDS


class BudgetStore(Protocol):
    """Where request timestamps live. Implement over a table to share a budget."""

    def append(self, timestamp: float) -> None: ...

    def since(self, timestamp: float) -> list[float]: ...

    def prune(self, before: float) -> None: ...


class InMemoryBudgetStore:
    """Default store. Process-local, lost on restart."""

    def __init__(self) -> None:
        self._timestamps: list[float] = []

    def append(self, timestamp: float) -> None:
        self._timestamps.append(timestamp)

    def since(self, timestamp: float) -> list[float]:
        return [value for value in self._timestamps if value > timestamp]

    def prune(self, before: float) -> None:
        self._timestamps = [value for value in self._timestamps if value > before]


class Budget:
    """Answers one question: may another request be sent right now?"""

    def __init__(
        self,
        *,
        store: BudgetStore | None = None,
        daily_limit: int = 1000,
        monthly_limit: int = 20000,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self._store: BudgetStore = store if store is not None else InMemoryBudgetStore()
        self._daily_limit = daily_limit
        self._monthly_limit = monthly_limit
        self._clock = clock
        self._blocked_until: float = 0.0

    def check(self) -> None:
        """Raise RateBudgetExceeded if sending now would exceed a limit."""
        now = self._clock()

        if now < self._blocked_until:
            raise RateBudgetExceeded(
                "the server rejected a recent request as rate limited",
                retry_after=self._blocked_until - now,
            )

        self._store.prune(before=now - MONTH_SECONDS)

        daily = self._store.since(now - DAY_SECONDS)
        if len(daily) >= self._daily_limit:
            raise RateBudgetExceeded(
                f"daily budget of {self._daily_limit} requests is spent",
                retry_after=daily[0] + DAY_SECONDS - now,
            )

        monthly = self._store.since(now - MONTH_SECONDS)
        if len(monthly) >= self._monthly_limit:
            raise RateBudgetExceeded(
                f"monthly budget of {self._monthly_limit} requests is spent",
                retry_after=monthly[0] + MONTH_SECONDS - now,
            )

    def record(self) -> None:
        """Count a request that actually reached Minimax."""
        self._store.append(self._clock())

    def penalize(self, retry_after: float) -> None:
        """Accept a server-side rate-limit verdict, overriding the local count."""
        self._blocked_until = self._clock() + retry_after
