"""Critical 1: a shared MinimaxClient must survive concurrent worker threads.

httpx.Client is thread-safe, so sharing one MinimaxClient across a worker
pool is the natural deployment. Before the fix, Authenticator.access_token()
and Budget.check()/record() were an unsynchronised read-check-request-store
sequence: four threads racing a wrong password each saw "no cached token,
not latched" and each sent their own request to the token endpoint -- the
exact burst that locks a customer's Minimax application.
"""

from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor

import httpx
import pytest

from minimax_api import MinimaxClient
from minimax_api.auth import Credentials
from minimax_api.errors import MinimaxAuthError
from minimax_api.models import Country

BAD_CREDENTIALS = Credentials(
    client_id="client", client_secret="secret", username="user", password="wrong"
)
GOOD_CREDENTIALS = Credentials(
    client_id="client", client_secret="secret", username="user", password="right"
)

THREAD_COUNT = 4


def test_four_threads_one_bad_password_send_exactly_one_token_request() -> None:
    token_calls = 0
    calls_lock = threading.Lock()
    barrier = threading.Barrier(THREAD_COUNT)

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/oauth20/token"):
            with calls_lock:
                nonlocal token_calls
                token_calls += 1
            # Widen the race window: without the fix, this gives every other
            # thread time to also decide "no token yet, let's request one".
            time.sleep(0.02)
            return httpx.Response(400, json={"error": "invalid_grant"})
        raise AssertionError("must never reach the API with no valid token")

    http = httpx.Client(transport=httpx.MockTransport(handler))
    client = MinimaxClient(credentials=BAD_CREDENTIALS, organisation_id=97271, http=http)

    def worker() -> None:
        barrier.wait()
        with pytest.raises(MinimaxAuthError) as raised:
            client.codelists.countries()
        assert raised.value.terminal is True

    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as pool:
        futures = [pool.submit(worker) for _ in range(THREAD_COUNT)]
        for future in futures:
            future.result()

    # One bad password, one request, ever -- regardless of how many threads
    # asked for a token at once.
    assert token_calls == 1


def test_four_threads_one_good_password_share_one_token_and_all_succeed() -> None:
    token_calls = 0
    calls_lock = threading.Lock()
    barrier = threading.Barrier(THREAD_COUNT)

    countries_payload = {
        "Rows": [{"CountryId": 3, "Code": "RS", "Name": "Serbia"}],
        "TotalRows": 1,
        "CurrentPageNumber": 1,
        "PageSize": 300,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/oauth20/token"):
            with calls_lock:
                nonlocal token_calls
                token_calls += 1
            time.sleep(0.02)  # widen the race window, same reasoning as above
            return httpx.Response(200, json={"access_token": "abc", "expires_in": 3600})
        return httpx.Response(200, json=countries_payload)

    http = httpx.Client(transport=httpx.MockTransport(handler))
    client = MinimaxClient(credentials=GOOD_CREDENTIALS, organisation_id=97271, http=http)

    results: list[list[Country]] = []
    results_lock = threading.Lock()

    def worker() -> None:
        barrier.wait()
        countries = client.codelists.countries()
        with results_lock:
            results.append(countries)

    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as pool:
        futures = [pool.submit(worker) for _ in range(THREAD_COUNT)]
        for future in futures:
            future.result()

    assert token_calls == 1
    assert len(results) == THREAD_COUNT
    for countries in results:
        assert [c.code for c in countries] == ["RS"]


def test_budget_state_survives_concurrent_check_and_record() -> None:
    """Budget's internal store must not corrupt under concurrent access.

    Each of many threads performs one check()+record() pair through a shared
    Budget. Without a lock, concurrent list mutation in InMemoryBudgetStore
    can lose updates (or, on other store implementations, corrupt state);
    with the lock, every recorded call must show up.
    """
    from minimax_api.budget import Budget

    now = [1000.0]
    budget = Budget(clock=lambda: now[0], daily_limit=10_000)
    thread_count = 50
    barrier = threading.Barrier(thread_count)

    def worker() -> None:
        barrier.wait()
        budget.check()
        budget.record()

    with ThreadPoolExecutor(max_workers=thread_count) as pool:
        futures = [pool.submit(worker) for _ in range(thread_count)]
        for future in futures:
            future.result()

    assert len(budget._store.since(0.0)) == thread_count
