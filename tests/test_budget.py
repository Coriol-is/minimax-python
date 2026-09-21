from typing import Any

import pytest

from minimax_api.budget import Budget, InMemoryBudgetStore
from minimax_api.errors import RateBudgetExceeded

DAY = 24 * 60 * 60


def make_budget(now: list[float], **kwargs: Any) -> Budget:
    return Budget(clock=lambda: now[0], **kwargs)


def test_a_fresh_budget_allows_requests() -> None:
    now = [1000.0]
    budget = make_budget(now)
    budget.check()  # does not raise


def test_the_daily_limit_blocks_and_reports_when_to_come_back() -> None:
    now = [1000.0]
    budget = make_budget(now, daily_limit=3)
    for _ in range(3):
        budget.check()
        budget.record()

    with pytest.raises(RateBudgetExceeded) as raised:
        budget.check()
    # The oldest of the three requests ages out of the window in exactly a day.
    assert raised.value.retry_after == pytest.approx(DAY)


def test_the_window_rolls() -> None:
    now = [1000.0]
    budget = make_budget(now, daily_limit=2)
    budget.check()
    budget.record()
    budget.check()
    budget.record()
    with pytest.raises(RateBudgetExceeded):
        budget.check()

    now[0] += DAY + 1
    budget.check()  # both recorded calls have aged out


def test_the_monthly_limit_also_blocks() -> None:
    now = [1000.0]
    budget = make_budget(now, daily_limit=1000, monthly_limit=2)
    budget.check()
    budget.record()
    budget.check()
    budget.record()
    with pytest.raises(RateBudgetExceeded) as raised:
        budget.check()
    assert raised.value.retry_after > DAY


def test_a_server_penalty_overrides_the_local_count() -> None:
    now = [1000.0]
    budget = make_budget(now)
    budget.check()  # local state says there is plenty left
    budget.penalize(120.0)

    with pytest.raises(RateBudgetExceeded) as raised:
        budget.check()
    assert raised.value.retry_after == pytest.approx(120.0)

    now[0] += 121
    budget.check()  # the penalty has expired


def test_store_prunes_old_entries() -> None:
    store = InMemoryBudgetStore()
    store.append(100.0)
    store.append(200.0)
    assert store.since(150.0) == [200.0]
    store.prune(before=150.0)
    assert store.since(0.0) == [200.0]


def test_a_shared_store_is_counted_once_across_clients() -> None:
    now = [1000.0]
    store = InMemoryBudgetStore()
    first = make_budget(now, store=store, daily_limit=2)
    second = make_budget(now, store=store, daily_limit=2)

    first.check()
    first.record()
    second.check()
    second.record()
    with pytest.raises(RateBudgetExceeded):
        first.check()
