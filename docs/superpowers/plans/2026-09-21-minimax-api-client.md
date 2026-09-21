# minimax-api Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `minimax-api`, a Python client for the Minimax accounting REST API whose authentication cannot lock the customer's account, whose rate budget is a typed outcome rather than a failure, and whose full 178-operation surface is generated from the vendor's own Swagger document.

**Architecture:** Three hand-written layers with no knowledge of each other's concerns — `auth` (token lifecycle and the lockout latch), `transport` (httpx, retries, error mapping), `budget` (request accounting) — plus a machine-generated layer (`_generated/models.py`, `_generated/operations.py`) produced from a committed Swagger artifact, and a thin hand-written `resources/` facade over the modules the connector actually uses.

**Tech Stack:** Python 3.12+, httpx, pydantic v2, uv, hatchling, pytest with `httpx.MockTransport`, ruff, mypy.

**Spec:** `docs/superpowers/specs/2026-09-21-minimax-python-design.md`

## Global Constraints

- PyPI package name `minimax-api`; import name `minimax_api`; repository `Coriol-is/minimax-python`.
- Python `>=3.12`. Runtime dependencies are exactly `httpx` and `pydantic>=2` — no others.
- All documentation, comments, docstrings, and commit messages in English.
- Licence MIT. README's first line must state this is **not** the MiniMax AI platform.
- The library never calls `time.sleep` for rate-budget waits and never retries a credential failure.
- No Serbian constant (country ID, currency ID, VAT rate ID) may appear anywhere in `src/`.
- `src/minimax_api/_generated/` is machine-written. Never hand-edit it; regenerate instead.
- Offline tests must not touch the network. Live tests carry the `live` marker and are excluded by default.
- Source layout is `src/minimax_api/`; tests in `tests/`.

## Facts established against the live API on 2026-09-21

These are measured, not assumed. Tasks below depend on them.

| Fact | Value |
|---|---|
| Token endpoint | `POST https://moj.minimax.rs/RS/AUT/oauth20/token`, password grant, `scope=minimax.rs` |
| Token lifetime | 3600 s |
| API base | `https://moj.minimax.rs/RS/API` + Swagger paths like `/api/orgs/{organisationId}/customers` |
| Collection envelope | `{Rows, TotalRows, CurrentPageNumber, PageSize}`; default `PageSize` 100 |
| Paging parameters | **Not in the Swagger document** — `?PageSize=300` is honoured by the live API regardless |
| Swagger | `GET https://moj.minimax.rs/RS/API/swagger/docs/v1` — Swagger 2.0, public, no auth |
| Swagger size | 120 paths, 178 operations, 127 definitions of which **90 are real models** (37 are `SearchResult[...]` envelopes) |
| `operationId` uniqueness | **178 operations share only 131 distinct `operationId` values** — names must be disambiguated by path |
| Definition naming | `SAOP.API.Models.Customer.Customer`, generics as `SAOP.API.Models.SearchResult[SAOP.API.Models.Customer.CustomerSearch]` |
| Leaf-name collisions | `Chart` ×3, `PaymentMethodSearch` ×3, `ListResult` ×2 |
| OData-style paths | 12, e.g. `/api/orgs/{organisationId}/customers/code({code})` |
| Reference fields | `SAOP.API.Common.mMApiFkField` = `{ID, Name, ResourceUrl}` |

---

## File Structure

| File | Responsibility |
|---|---|
| `pyproject.toml` | Packaging, dependencies, pytest markers, ruff/mypy config |
| `src/minimax_api/errors.py` | Exception hierarchy; every error answers "may I retry, and when?" |
| `src/minimax_api/region.py` | `Region` dataclass and the `RS` preset (base URL, token URL, scope) |
| `src/minimax_api/auth.py` | `Credentials`, `Token`, `TokenStore`, `Authenticator` — including the lockout latch |
| `src/minimax_api/transport.py` | `Transport`, `Response`; httpx calls, 5xx backoff, HTTP-status-to-error mapping |
| `src/minimax_api/budget.py` | `Budget`, `BudgetStore` — rolling 24 h and monthly accounting |
| `src/minimax_api/envelope.py` | `SearchResult[T]` pydantic model and `MinimaxModel` base |
| `src/minimax_api/pagination.py` | `paginate()` — walks `Rows` to `TotalRows` |
| `src/minimax_api/_generated/models.py` | 90 generated pydantic models |
| `src/minimax_api/_generated/operations.py` | 178 generated operation functions |
| `src/minimax_api/resources/codelists.py` | Countries, currencies, VAT rates, accounts |
| `src/minimax_api/resources/customers.py` | Customer read/create/update with `RowVersion` handling |
| `src/minimax_api/resources/issued_invoices.py` | Issued-invoice read/create |
| `src/minimax_api/client.py` | `MinimaxClient` — wires the layers, owns the httpx client |
| `src/minimax_api/__init__.py` | Public surface re-exports |
| `scripts/generate.py` | Swagger → `_generated/` |
| `scripts/refresh_spec.py` | Re-download the spec, show the diff |
| `spec/swagger-2026-09-21.json` | Committed API surface artifact |

---

### Task 1: Package skeleton and the error hierarchy

**Files:**
- Create: `pyproject.toml`, `.gitignore`, `LICENSE`, `src/minimax_api/__init__.py`, `src/minimax_api/errors.py`, `tests/test_errors.py`, `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: nothing.
- Produces: `MinimaxError`, `MinimaxAuthError(message, *, terminal: bool)`, `RateBudgetExceeded(message, *, retry_after: float)`, `ConcurrencyError`, `NotFoundError`, `ValidationError(message, *, status_code: int, payload: object)`, `TransportError`. Every exception exposes `.retryable: bool`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_errors.py
import pytest

from minimax_api.errors import (
    ConcurrencyError,
    MinimaxAuthError,
    MinimaxError,
    NotFoundError,
    RateBudgetExceeded,
    TransportError,
    ValidationError,
)


def test_every_error_descends_from_minimax_error():
    for cls in (
        MinimaxAuthError,
        RateBudgetExceeded,
        ConcurrencyError,
        NotFoundError,
        ValidationError,
        TransportError,
    ):
        assert issubclass(cls, MinimaxError)


def test_terminal_auth_error_is_not_retryable():
    error = MinimaxAuthError("bad password", terminal=True)
    assert error.terminal is True
    assert error.retryable is False


def test_non_terminal_auth_error_is_retryable():
    assert MinimaxAuthError("token expired", terminal=False).retryable is True


def test_transport_error_is_retryable():
    assert TransportError("connection reset").retryable is True


def test_rate_budget_exceeded_carries_retry_after_and_is_retryable():
    error = RateBudgetExceeded("daily budget spent", retry_after=3600.0)
    assert error.retry_after == 3600.0
    assert error.retryable is True


def test_concurrency_error_is_not_retryable_by_replay():
    # A RowVersion conflict must be re-read and re-evaluated, never replayed.
    assert ConcurrencyError("RowVersion conflict").retryable is False


def test_validation_error_keeps_the_server_explanation():
    error = ValidationError("Name is required", status_code=400, payload={"Message": "Name is required"})
    assert error.status_code == 400
    assert error.payload == {"Message": "Name is required"}
    assert error.retryable is False


def test_not_found_is_not_retryable():
    assert NotFoundError("no such customer").retryable is False


def test_errors_can_be_caught_by_base_class():
    with pytest.raises(MinimaxError):
        raise NotFoundError("no such customer")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_errors.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'minimax_api'`

- [ ] **Step 3: Write the packaging files**

```toml
# pyproject.toml
[project]
name = "minimax-api"
version = "0.1.0"
description = "Python client for the Minimax (Saop) accounting REST API"
readme = "README.md"
requires-python = ">=3.12"
license = { text = "MIT" }
authors = [{ name = "Coriolis" }]
keywords = ["minimax", "saop", "accounting", "serbia", "erp"]
dependencies = ["httpx>=0.27", "pydantic>=2.6"]

[project.urls]
Homepage = "https://github.com/Coriol-is/minimax-python"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/minimax_api"]

[dependency-groups]
dev = ["pytest>=8.0", "mypy>=1.9", "ruff>=0.4"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
# The default run is offline. Live tests need real credentials and spend
# from the organisation's daily request budget, so they are opt-in.
addopts = ["-m", "not live"]
markers = ["live: makes real calls to moj.minimax.rs using credentials from .env"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.mypy]
python_version = "3.12"
strict = true
files = ["src", "tests"]

[[tool.mypy.overrides]]
# Generated code is checked, but its dynamic construction defeats some inference.
module = "minimax_api._generated.*"
disallow_any_explicit = false
```

```gitignore
# .gitignore
__pycache__/
*.py[cod]
.venv/
dist/
build/
*.egg-info/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.env
```

`LICENSE`: the standard MIT licence text, copyright `2026 Coriolis`.

- [ ] **Step 4: Write the error module**

```python
# src/minimax_api/errors.py
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

    @property  # type: ignore[override]
    def retryable(self) -> bool:
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
```

```python
# src/minimax_api/__init__.py
"""Python client for the Minimax (Saop) accounting REST API."""

from minimax_api.errors import (
    ConcurrencyError,
    MinimaxAuthError,
    MinimaxError,
    NotFoundError,
    RateBudgetExceeded,
    TransportError,
    ValidationError,
)

__all__ = [
    "ConcurrencyError",
    "MinimaxAuthError",
    "MinimaxError",
    "NotFoundError",
    "RateBudgetExceeded",
    "TransportError",
    "ValidationError",
]
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/test_errors.py -v`
Expected: PASS, 8 tests.

Note on `MinimaxAuthError`: `retryable` is a class attribute on the base and a property on this subclass. Run `uv run mypy src` and, if it objects, keep the `# type: ignore[override]` comment shown above.

- [ ] **Step 6: Add CI**

```yaml
# .github/workflows/ci.yml
name: ci
on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv python install ${{ matrix.python-version }}
      - run: uv sync --all-groups
      - run: uv run ruff check .
      - run: uv run mypy src tests
      - run: uv run pytest -v
```

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml .gitignore LICENSE src/minimax_api tests/test_errors.py .github/workflows/ci.yml
git commit -m "feat: package skeleton and error hierarchy"
```

---

### Task 2: Region preset and the authenticator

**Files:**
- Create: `src/minimax_api/region.py`, `src/minimax_api/auth.py`, `tests/test_auth.py`

**Interfaces:**
- Consumes: `minimax_api.errors.MinimaxAuthError`, `TransportError`.
- Produces:
  - `Region(code: str, base_url: str, token_url: str, scope: str)` and the module constant `RS`.
  - `Credentials(client_id: str, client_secret: str, username: str, password: str)`.
  - `Token(access_token: str, expires_at: float)`.
  - `TokenStore` protocol with `get() -> Token | None` and `set(token: Token) -> None`; `InMemoryTokenStore`.
  - `Authenticator(credentials, region, http: httpx.Client, store=None, clock=time.time, expiry_skew=60.0)` with `access_token() -> str` and `invalidate() -> None`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_auth.py
import httpx
import pytest

from minimax_api.auth import Authenticator, Credentials, InMemoryTokenStore, Token
from minimax_api.errors import MinimaxAuthError, TransportError
from minimax_api.region import RS

CREDENTIALS = Credentials(
    client_id="client", client_secret="secret", username="user", password="password"
)


def make_auth(handler, *, clock=None, store=None):
    http = httpx.Client(transport=httpx.MockTransport(handler))
    return Authenticator(
        credentials=CREDENTIALS,
        region=RS,
        http=http,
        store=store,
        clock=clock or (lambda: 1000.0),
    )


def test_token_is_requested_once_and_then_cached():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, json={"access_token": "abc", "expires_in": 3600, "token_type": "bearer"})

    auth = make_auth(handler)
    assert auth.access_token() == "abc"
    assert auth.access_token() == "abc"
    assert len(calls) == 1


def test_token_request_sends_the_password_grant_form():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["body"] = request.content.decode()
        return httpx.Response(200, json={"access_token": "abc", "expires_in": 3600})

    make_auth(handler).access_token()
    assert seen["url"] == RS.token_url
    for field in (
        "grant_type=password",
        "client_id=client",
        "client_secret=secret",
        "username=user",
        "password=password",
        "scope=minimax.rs",
    ):
        assert field in seen["body"]


def test_expired_token_is_refreshed_once():
    calls = []
    now = [1000.0]

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, json={"access_token": f"token-{len(calls)}", "expires_in": 3600})

    auth = make_auth(handler, clock=lambda: now[0])
    assert auth.access_token() == "token-1"
    now[0] += 3600  # past expiry once the 60 s skew is applied
    assert auth.access_token() == "token-2"
    assert auth.access_token() == "token-2"
    assert len(calls) == 2


def test_credential_rejection_is_terminal_and_never_reaches_the_network_twice():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(400, json={"error": "invalid_grant"})

    auth = make_auth(handler)
    with pytest.raises(MinimaxAuthError) as first:
        auth.access_token()
    assert first.value.terminal is True

    with pytest.raises(MinimaxAuthError) as second:
        auth.access_token()
    assert second.value.terminal is True

    # The latch is the whole point: one bad password, one request, ever.
    assert len(calls) == 1


def test_401_from_the_token_endpoint_is_also_terminal():
    auth = make_auth(lambda request: httpx.Response(401, json={"error": "invalid_client"}))
    with pytest.raises(MinimaxAuthError) as raised:
        auth.access_token()
    assert raised.value.terminal is True


def test_server_error_is_a_transport_error_and_does_not_latch():
    responses = [httpx.Response(503, text="unavailable"),
                 httpx.Response(200, json={"access_token": "abc", "expires_in": 3600})]

    def handler(request: httpx.Request) -> httpx.Response:
        return responses.pop(0)

    auth = make_auth(handler)
    with pytest.raises(TransportError):
        auth.access_token()
    assert auth.access_token() == "abc"


def test_connection_failure_is_a_transport_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    with pytest.raises(TransportError):
        make_auth(handler).access_token()


def test_a_shared_store_prevents_a_second_worker_from_requesting_a_token():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, json={"access_token": "abc", "expires_in": 3600})

    store = InMemoryTokenStore()
    first = make_auth(handler, store=store)
    second = make_auth(handler, store=store)
    assert first.access_token() == "abc"
    assert second.access_token() == "abc"
    assert len(calls) == 1


def test_invalidate_forces_one_refresh():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, json={"access_token": f"token-{len(calls)}", "expires_in": 3600})

    auth = make_auth(handler)
    assert auth.access_token() == "token-1"
    auth.invalidate()
    assert auth.access_token() == "token-2"
    assert len(calls) == 2


def test_store_round_trips_a_token():
    store = InMemoryTokenStore()
    assert store.get() is None
    token = Token(access_token="abc", expires_at=4600.0)
    store.set(token)
    assert store.get() == token
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_auth.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'minimax_api.auth'`

- [ ] **Step 3: Write the region module**

```python
# src/minimax_api/region.py
"""Per-country Minimax deployments.

Minimax runs one code base behind several national deployments, each with its
own host and OAuth scope. Only the Serbian preset is verified: it is the only
organisation these authors can reach. Other countries are a configuration
change, not a code change, but they are not claimed as supported.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Region:
    """A national Minimax deployment."""

    code: str
    base_url: str
    token_url: str
    scope: str


#: Serbia. Verified against a live RS organisation on 2026-09-21.
RS = Region(
    code="RS",
    base_url="https://moj.minimax.rs/RS/API",
    token_url="https://moj.minimax.rs/RS/AUT/oauth20/token",
    scope="minimax.rs",
)
```

- [ ] **Step 4: Write the authenticator**

```python
# src/minimax_api/auth.py
"""Token lifecycle, including the rule that keeps customers out of lockout.

Minimax locks an API application after several consecutive token requests
carrying a wrong password. Recovery is not a cooldown: the application must be
deleted and recreated, which issues new credentials and requires a redeploy.

So a credential rejection latches this authenticator. The first rejection is
the only request that ever reaches the network; every later call raises the
same error without a socket being opened. Transport failures are a different
class entirely and leave the latch untouched.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

import httpx

from minimax_api.errors import MinimaxAuthError, TransportError
from minimax_api.region import Region

#: Status codes from the token endpoint that mean "these credentials are wrong".
_TERMINAL_STATUSES = frozenset({400, 401, 403})


@dataclass(frozen=True)
class Credentials:
    """Both halves of Minimax authentication.

    The client half is issued by Minimax support; the user half is created by
    the subscriber in *Moj profil*. Both are secrets.
    """

    client_id: str
    client_secret: str
    username: str
    password: str


@dataclass(frozen=True)
class Token:
    """An access token and the moment it stops being usable."""

    access_token: str
    expires_at: float


class TokenStore(Protocol):
    """Where a token lives between uses.

    Implement this over a database so concurrent workers share one token. They
    would otherwise race to refresh, and a single bad stored password
    multiplied across workers reaches the lockout threshold in one burst.
    """

    def get(self) -> Token | None: ...

    def set(self, token: Token) -> None: ...


class InMemoryTokenStore:
    """Default store. Process-local, lost on restart."""

    def __init__(self) -> None:
        self._token: Token | None = None

    def get(self) -> Token | None:
        return self._token

    def set(self, token: Token) -> None:
        self._token = token


class Authenticator:
    """Obtains and caches an access token."""

    def __init__(
        self,
        *,
        credentials: Credentials,
        region: Region,
        http: httpx.Client,
        store: TokenStore | None = None,
        clock: Callable[[], float] = time.time,
        expiry_skew: float = 60.0,
    ) -> None:
        self._credentials = credentials
        self._region = region
        self._http = http
        self._store: TokenStore = store if store is not None else InMemoryTokenStore()
        self._clock = clock
        self._expiry_skew = expiry_skew
        self._latched: MinimaxAuthError | None = None

    def access_token(self) -> str:
        """Return a usable token, requesting one only when necessary."""
        if self._latched is not None:
            raise self._latched

        token = self._store.get()
        if token is not None and token.expires_at - self._expiry_skew > self._clock():
            return token.access_token

        token = self._request_token()
        self._store.set(token)
        return token.access_token

    def invalidate(self) -> None:
        """Drop the cached token, e.g. after an API call answered 401."""
        self._store.set(Token(access_token="", expires_at=0.0))

    def _request_token(self) -> Token:
        form = {
            "grant_type": "password",
            "client_id": self._credentials.client_id,
            "client_secret": self._credentials.client_secret,
            "username": self._credentials.username,
            "password": self._credentials.password,
            "scope": self._region.scope,
        }
        try:
            response = self._http.post(
                self._region.token_url,
                data=form,
                headers={"Accept": "application/json"},
            )
        except httpx.HTTPError as error:
            # No response means the credentials were never judged. Retrying is
            # safe and does not count towards lockout.
            raise TransportError(f"token request failed to complete: {error}") from error

        if response.status_code in _TERMINAL_STATUSES:
            latched = MinimaxAuthError(
                f"token request rejected with HTTP {response.status_code}; "
                "not retrying, because repeated credential failures lock the "
                "Minimax application",
                terminal=True,
            )
            self._latched = latched
            raise latched

        if response.status_code >= 500:
            raise TransportError(f"token endpoint returned HTTP {response.status_code}")

        payload = response.json()
        access_token = payload.get("access_token")
        if response.status_code != 200 or not access_token:
            raise TransportError(
                f"token endpoint returned HTTP {response.status_code} without an access token"
            )

        expires_in = float(payload.get("expires_in", 3600))
        return Token(access_token=access_token, expires_at=self._clock() + expires_in)
```

Note: the token request never appears in an exception message. The form carries the client secret and the user password, and exception text ends up in logs.

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/test_auth.py -v`
Expected: PASS, 10 tests.

- [ ] **Step 6: Commit**

```bash
git add src/minimax_api/region.py src/minimax_api/auth.py tests/test_auth.py
git commit -m "feat: region preset and authenticator with lockout latch"
```

---

### Task 3: Transport

**Files:**
- Create: `src/minimax_api/transport.py`, `tests/test_transport.py`

**Interfaces:**
- Consumes: `Authenticator`, `Region`, the error hierarchy.
- Produces:
  - `Response(status_code: int, json: object, headers: Mapping[str, str])` with property `location_id: int | None`.
  - `Transport(region, authenticator, http, budget=None, max_transport_retries=3, backoff_base=0.5, sleep=time.sleep)` with `request(method: str, path: str, *, params=None, json=None) -> Response`.

`budget` is typed `Budget | None` and left `None` until Task 4 lands; the parameter exists now so Task 4 does not have to change this signature.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_transport.py
import httpx
import pytest

from minimax_api.auth import Authenticator, Credentials, Token
from minimax_api.errors import (
    ConcurrencyError,
    NotFoundError,
    TransportError,
    ValidationError,
)
from minimax_api.region import RS
from minimax_api.transport import Response, Transport


class StubAuth:
    """Stands in for Authenticator; counts how often the token was invalidated."""

    def __init__(self) -> None:
        self.invalidations = 0
        self.tokens = ["token-1", "token-2"]

    def access_token(self) -> str:
        return self.tokens[min(self.invalidations, len(self.tokens) - 1)]

    def invalidate(self) -> None:
        self.invalidations += 1


def make_transport(handler, **kwargs):
    http = httpx.Client(transport=httpx.MockTransport(handler))
    return Transport(
        region=RS,
        authenticator=StubAuth(),
        http=http,
        sleep=lambda seconds: None,
        **kwargs,
    )


def test_get_builds_the_url_and_sends_the_bearer_token():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["auth"] = request.headers["Authorization"]
        return httpx.Response(200, json={"Rows": []})

    transport = make_transport(handler)
    response = transport.request("GET", "/api/orgs/12345/customers", params={"PageSize": 300})

    assert seen["url"] == "https://moj.minimax.rs/RS/API/api/orgs/12345/customers?PageSize=300"
    assert seen["auth"] == "Bearer token-1"
    assert response.status_code == 200
    assert response.json == {"Rows": []}


def test_404_becomes_not_found():
    transport = make_transport(lambda request: httpx.Response(404, json={"Message": "no such thing"}))
    with pytest.raises(NotFoundError):
        transport.request("GET", "/api/orgs/12345/customers/999")


def test_concurrency_message_becomes_concurrency_error():
    body = {"Message": "Concurrency error - record changed by another action (RowVersion)"}
    transport = make_transport(lambda request: httpx.Response(400, json=body))
    with pytest.raises(ConcurrencyError):
        transport.request("PUT", "/api/orgs/12345/customers/1", json={})


def test_other_4xx_becomes_validation_error_carrying_the_server_text():
    body = {"Message": "Name is required"}
    transport = make_transport(lambda request: httpx.Response(400, json=body))
    with pytest.raises(ValidationError) as raised:
        transport.request("POST", "/api/orgs/12345/customers", json={})
    assert raised.value.status_code == 400
    assert raised.value.payload == body


def test_5xx_is_retried_then_succeeds():
    responses = [httpx.Response(503, text="try later"), httpx.Response(200, json={"ok": True})]
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return responses.pop(0)

    transport = make_transport(handler)
    assert transport.request("GET", "/api/orgs/12345/customers").json == {"ok": True}
    assert len(calls) == 2


def test_5xx_gives_up_after_the_retry_budget():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(500, text="boom")

    transport = make_transport(handler, max_transport_retries=3)
    with pytest.raises(TransportError):
        transport.request("GET", "/api/orgs/12345/customers")
    assert len(calls) == 3


def test_401_on_an_api_call_refreshes_the_token_once():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.headers["Authorization"])
        if len(calls) == 1:
            return httpx.Response(401, text="expired")
        return httpx.Response(200, json={"ok": True})

    transport = make_transport(handler)
    assert transport.request("GET", "/api/orgs/12345/customers").json == {"ok": True}
    assert calls == ["Bearer token-1", "Bearer token-2"]


def test_repeated_401_does_not_loop_forever():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(401, text="expired")

    transport = make_transport(handler)
    with pytest.raises(TransportError):
        transport.request("GET", "/api/orgs/12345/customers")
    assert len(calls) == 2


def test_connection_error_is_a_transport_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("timed out")

    transport = make_transport(handler, max_transport_retries=2)
    with pytest.raises(TransportError):
        transport.request("GET", "/api/orgs/12345/customers")


def test_location_header_yields_the_created_id():
    headers = {"Location": "https://moj.minimax.rs/RS/API/api/orgs/12345/customers/4242"}
    transport = make_transport(lambda request: httpx.Response(201, headers=headers))
    response = transport.request("POST", "/api/orgs/12345/customers", json={})
    assert response.location_id == 4242


def test_missing_location_header_yields_none():
    assert Response(status_code=200, json=None, headers={}).location_id is None


def test_unparseable_location_yields_none():
    response = Response(status_code=201, json=None, headers={"Location": "/customers/not-a-number"})
    assert response.location_id is None


def test_empty_body_parses_as_none():
    transport = make_transport(lambda request: httpx.Response(204))
    assert transport.request("DELETE", "/api/orgs/12345/customers/1").json is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_transport.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'minimax_api.transport'`

- [ ] **Step 3: Write the transport**

```python
# src/minimax_api/transport.py
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
    from minimax_api.budget import Budget

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

            if raw.status_code == 401 and not refreshed:
                # The token expired mid-flight. This is not a credential
                # rejection: the token endpoint is the only place that judges
                # credentials, and it has its own terminal handling.
                refreshed = True
                self._auth.invalidate()
                continue

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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_transport.py -v`
Expected: PASS, 13 tests.

- [ ] **Step 5: Commit**

```bash
git add src/minimax_api/transport.py tests/test_transport.py
git commit -m "feat: transport with typed error mapping and bounded retries"
```

---

### Task 4: Request budget

**Files:**
- Create: `src/minimax_api/budget.py`, `tests/test_budget.py`
- Modify: `tests/test_transport.py` (add one test proving the transport consults the budget)

**Interfaces:**
- Consumes: `RateBudgetExceeded`.
- Produces:
  - `BudgetStore` protocol: `append(timestamp: float) -> None`, `since(timestamp: float) -> list[float]`, `prune(before: float) -> None`.
  - `InMemoryBudgetStore`.
  - `Budget(store=None, daily_limit=1000, monthly_limit=20000, clock=time.time)` with `check() -> None`, `record() -> None`, `penalize(retry_after: float) -> None`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_budget.py
import pytest

from minimax_api.budget import Budget, InMemoryBudgetStore
from minimax_api.errors import RateBudgetExceeded

DAY = 24 * 60 * 60


def make_budget(now, **kwargs):
    return Budget(clock=lambda: now[0], **kwargs)


def test_a_fresh_budget_allows_requests():
    now = [1000.0]
    budget = make_budget(now)
    budget.check()  # does not raise


def test_the_daily_limit_blocks_and_reports_when_to_come_back():
    now = [1000.0]
    budget = make_budget(now, daily_limit=3)
    for _ in range(3):
        budget.check()
        budget.record()

    with pytest.raises(RateBudgetExceeded) as raised:
        budget.check()
    # The oldest of the three requests ages out of the window in exactly a day.
    assert raised.value.retry_after == pytest.approx(DAY)


def test_the_window_rolls():
    now = [1000.0]
    budget = make_budget(now, daily_limit=2)
    budget.check(); budget.record()
    budget.check(); budget.record()
    with pytest.raises(RateBudgetExceeded):
        budget.check()

    now[0] += DAY + 1
    budget.check()  # both recorded calls have aged out


def test_the_monthly_limit_also_blocks():
    now = [1000.0]
    budget = make_budget(now, daily_limit=1000, monthly_limit=2)
    budget.check(); budget.record()
    budget.check(); budget.record()
    with pytest.raises(RateBudgetExceeded) as raised:
        budget.check()
    assert raised.value.retry_after > DAY


def test_a_server_penalty_overrides_the_local_count():
    now = [1000.0]
    budget = make_budget(now)
    budget.check()  # local state says there is plenty left
    budget.penalize(120.0)

    with pytest.raises(RateBudgetExceeded) as raised:
        budget.check()
    assert raised.value.retry_after == pytest.approx(120.0)

    now[0] += 121
    budget.check()  # the penalty has expired


def test_store_prunes_old_entries():
    store = InMemoryBudgetStore()
    store.append(100.0)
    store.append(200.0)
    assert store.since(150.0) == [200.0]
    store.prune(before=150.0)
    assert store.since(0.0) == [200.0]


def test_a_shared_store_is_counted_once_across_clients():
    now = [1000.0]
    store = InMemoryBudgetStore()
    first = make_budget(now, store=store, daily_limit=2)
    second = make_budget(now, store=store, daily_limit=2)

    first.check(); first.record()
    second.check(); second.record()
    with pytest.raises(RateBudgetExceeded):
        first.check()
```

Add to `tests/test_transport.py`:

```python
def test_transport_refuses_to_send_when_the_budget_is_spent():
    from minimax_api.budget import Budget

    now = [1000.0]
    budget = Budget(clock=lambda: now[0], daily_limit=1)
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, json={"ok": True})

    transport = make_transport(handler, budget=budget)
    transport.request("GET", "/api/orgs/12345/customers")

    from minimax_api.errors import RateBudgetExceeded

    with pytest.raises(RateBudgetExceeded):
        transport.request("GET", "/api/orgs/12345/customers")
    assert len(calls) == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_budget.py tests/test_transport.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'minimax_api.budget'`

- [ ] **Step 3: Write the budget**

```python
# src/minimax_api/budget.py
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_budget.py tests/test_transport.py -v`
Expected: PASS, 7 budget tests and 14 transport tests.

- [ ] **Step 5: Commit**

```bash
git add src/minimax_api/budget.py tests/test_budget.py tests/test_transport.py
git commit -m "feat: rolling request budget with server-penalty override"
```

---

### Task 5: Envelope and pagination

**Files:**
- Create: `src/minimax_api/envelope.py`, `src/minimax_api/pagination.py`, `tests/test_pagination.py`

**Interfaces:**
- Consumes: `Transport`, `Response`.
- Produces:
  - `MinimaxModel` — the pydantic base every generated model inherits.
  - `SearchResult[T]` with fields `rows: list[T]` (alias `Rows`), `total_rows: int` (alias `TotalRows`), `current_page_number: int` (alias `CurrentPageNumber`), `page_size: int` (alias `PageSize`).
  - `paginate(transport, path, model, *, params=None, page_size=DEFAULT_PAGE_SIZE) -> Iterator[T]`.
  - `DEFAULT_PAGE_SIZE = 300`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_pagination.py
import httpx
import pytest

from minimax_api.envelope import MinimaxModel, SearchResult
from minimax_api.pagination import DEFAULT_PAGE_SIZE, paginate
from minimax_api.region import RS
from minimax_api.transport import Transport


class Row(MinimaxModel):
    id: int
    name: str | None = None


class StubAuth:
    def access_token(self) -> str:
        return "token"

    def invalidate(self) -> None:
        pass


def make_transport(handler):
    http = httpx.Client(transport=httpx.MockTransport(handler))
    return Transport(region=RS, authenticator=StubAuth(), http=http, sleep=lambda s: None)


def test_envelope_maps_pascal_case_aliases():
    result = SearchResult[Row].model_validate(
        {"Rows": [{"ID": 1}], "TotalRows": 1, "CurrentPageNumber": 1, "PageSize": 100}
    )
    assert result.total_rows == 1
    assert result.rows[0].id == 1


def test_model_accepts_unexpected_fields():
    # Minimax adds fields without warning; a caller must not break mid-invoice.
    row = Row.model_validate({"ID": 1, "SomethingNew": "value"})
    assert row.id == 1


def test_pagination_requests_the_large_page_size():
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(dict(request.url.params))
        return httpx.Response(200, json={"Rows": [], "TotalRows": 0, "CurrentPageNumber": 1, "PageSize": DEFAULT_PAGE_SIZE})

    list(paginate(make_transport(handler), "/api/orgs/12345/customers", Row))
    assert seen[0]["PageSize"] == str(DEFAULT_PAGE_SIZE)


def test_pagination_walks_every_page():
    pages = {
        "1": {"Rows": [{"ID": 1}, {"ID": 2}], "TotalRows": 5, "CurrentPageNumber": 1, "PageSize": 2},
        "2": {"Rows": [{"ID": 3}, {"ID": 4}], "TotalRows": 5, "CurrentPageNumber": 2, "PageSize": 2},
        "3": {"Rows": [{"ID": 5}], "TotalRows": 5, "CurrentPageNumber": 3, "PageSize": 2},
    }

    def handler(request: httpx.Request) -> httpx.Response:
        page = request.url.params.get("CurrentPage", "1")
        return httpx.Response(200, json=pages[page])

    rows = list(paginate(make_transport(handler), "/api/orgs/12345/customers", Row, page_size=2))
    assert [row.id for row in rows] == [1, 2, 3, 4, 5]


def test_pagination_keeps_caller_parameters():
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(dict(request.url.params))
        return httpx.Response(200, json={"Rows": [], "TotalRows": 0, "CurrentPageNumber": 1, "PageSize": 300})

    list(paginate(make_transport(handler), "/api/orgs/12345/customers", Row, params={"SearchString": "acme"}))
    assert seen[0]["SearchString"] == "acme"


def test_pagination_stops_when_a_page_comes_back_empty():
    # Defensive: a server that reports a TotalRows it cannot deliver must not
    # send us round the loop forever.
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, json={"Rows": [], "TotalRows": 99, "CurrentPageNumber": 1, "PageSize": 300})

    rows = list(paginate(make_transport(handler), "/api/orgs/12345/customers", Row))
    assert rows == []
    assert len(calls) == 1


def test_pagination_handles_a_bare_list_response():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[{"ID": 7}])

    rows = list(paginate(make_transport(handler), "/api/orgs/12345/countries", Row))
    assert [row.id for row in rows] == [7]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_pagination.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'minimax_api.envelope'`

- [ ] **Step 3: Write the envelope**

```python
# src/minimax_api/envelope.py
"""The pydantic base and the collection envelope every list endpoint returns."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class MinimaxModel(BaseModel):
    """Base for every model, generated or hand-written.

    Minimax field names are PascalCase; Python attributes are snake_case, and
    aliases bridge the two. Unknown fields are kept rather than rejected: the
    vendor adds fields without warning, and a strict model would turn that into
    a caller's outage.
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")


class SearchResult(MinimaxModel, Generic[T]):
    """`{Rows, TotalRows, CurrentPageNumber, PageSize}` — every collection response."""

    rows: list[T] = Field(default_factory=list, alias="Rows")
    total_rows: int = Field(default=0, alias="TotalRows")
    current_page_number: int = Field(default=1, alias="CurrentPageNumber")
    page_size: int = Field(default=0, alias="PageSize")
```

- [ ] **Step 4: Write pagination**

```python
# src/minimax_api/pagination.py
"""Walking a collection endpoint.

The Swagger document does not describe the paging query parameters, but the
live API honours them: `PageSize` sets the page length and `CurrentPage`
selects the page. Both were verified against a live RS organisation on 2026-09-21.
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


def paginate(
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
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/test_pagination.py -v`
Expected: PASS, 7 tests.

If `SearchResult[model]` trips mypy, keep the `# type: ignore[valid-type]` shown; parametrising a generic with a runtime variable is correct here and unexpressible in the type system.

- [ ] **Step 6: Commit**

```bash
git add src/minimax_api/envelope.py src/minimax_api/pagination.py tests/test_pagination.py
git commit -m "feat: collection envelope and pagination"
```

---

### Task 6: Vendor the Swagger document

**Files:**
- Create: `spec/swagger-2026-09-21.json`, `scripts/refresh_spec.py`, `tests/test_spec_artifact.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `spec/swagger-2026-09-21.json` (committed) and `scripts/refresh_spec.py` as a CLI.

- [ ] **Step 1: Download the spec**

```bash
mkdir -p spec
curl -s -o spec/swagger-2026-09-21.json https://moj.minimax.rs/RS/API/swagger/docs/v1
python3 -c "import json;d=json.load(open('spec/swagger-2026-09-21.json'));print(len(d['paths']),'paths',len(d['definitions']),'definitions')"
```

Expected: `120 paths 127 definitions`. If the numbers differ, the API has changed since 2026-09-21 — record the new counts in the commit message and carry on; the generator is driven by the file, not by these numbers.

- [ ] **Step 2: Write the failing test**

```python
# tests/test_spec_artifact.py
import json
from pathlib import Path

SPEC = Path(__file__).resolve().parent.parent / "spec" / "swagger-2026-09-21.json"


def test_the_spec_is_committed_and_parses():
    assert SPEC.exists(), "the Swagger artifact must be committed, not downloaded at build time"
    document = json.loads(SPEC.read_text())
    assert document["swagger"] == "2.0"
    assert document["basePath"] == "/RS/API"


def test_the_spec_still_contains_the_operations_the_facade_relies_on():
    document = json.loads(SPEC.read_text())
    for path in (
        "/api/orgs/{organisationId}/customers",
        "/api/orgs/{organisationId}/customers/{customerId}",
        "/api/orgs/{organisationId}/currencies",
        "/api/orgs/{organisationId}/countries",
        "/api/orgs/{organisationId}/vatrates",
        "/api/orgs/{organisationId}/issuedinvoices",
    ):
        assert path in document["paths"], path
```

- [ ] **Step 3: Run test to verify it passes**

Run: `uv run pytest tests/test_spec_artifact.py -v`
Expected: PASS, 2 tests. (This test guards an artifact rather than driving new code, so it passes as soon as Step 1's download is in place.)

- [ ] **Step 4: Write the refresh script**

```python
#!/usr/bin/env python3
"""Re-download the Swagger document and show what changed.

Running this is how API drift becomes visible. Regenerating the client from a
refreshed spec always belongs in its own commit, never mixed with hand-written
changes, so that `git diff` of `_generated/` reads as a report on Minimax.

Usage:
    uv run python scripts/refresh_spec.py            # write a new dated file and diff it
    uv run python scripts/refresh_spec.py --check    # exit 1 if the live spec differs
"""

from __future__ import annotations

import argparse
import datetime as dt
import difflib
import json
import sys
import urllib.request
from pathlib import Path

SPEC_URL = "https://moj.minimax.rs/RS/API/swagger/docs/v1"
SPEC_DIR = Path(__file__).resolve().parent.parent / "spec"


def newest_spec() -> Path:
    candidates = sorted(SPEC_DIR.glob("swagger-*.json"))
    if not candidates:
        raise SystemExit("no committed spec found in spec/")
    return candidates[-1]


def fetch() -> str:
    with urllib.request.urlopen(SPEC_URL, timeout=60) as response:
        document = json.loads(response.read().decode("utf-8"))
    return json.dumps(document, ensure_ascii=False, indent=1, sort_keys=True) + "\n"


def normalise(path: Path) -> str:
    return json.dumps(json.loads(path.read_text()), ensure_ascii=False, indent=1, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="only report whether the spec changed")
    args = parser.parse_args()

    current = newest_spec()
    live = fetch()
    diff = list(
        difflib.unified_diff(
            normalise(current).splitlines(keepends=True),
            live.splitlines(keepends=True),
            fromfile=str(current.name),
            tofile="live",
        )
    )

    if not diff:
        print(f"No change: {current.name} matches the live API surface.")
        return 0

    sys.stdout.writelines(diff[:400])
    if len(diff) > 400:
        print(f"... {len(diff) - 400} more diff lines")

    if args.check:
        return 1

    target = SPEC_DIR / f"swagger-{dt.date.today().isoformat()}.json"
    target.write_text(live)
    print(f"\nWrote {target.name}. Next: regenerate and commit that on its own.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Verify the script runs**

Run: `uv run python scripts/refresh_spec.py --check`
Expected: `No change: swagger-2026-09-21.json matches the live API surface.` and exit 0. A non-empty diff is also an acceptable outcome — it means Minimax changed the API and the artifact should be refreshed in its own commit.

- [ ] **Step 6: Commit**

```bash
git add spec/swagger-2026-09-21.json scripts/refresh_spec.py tests/test_spec_artifact.py
git commit -m "chore: vendor Swagger 2.0 spec as of 2026-09-21"
```

---

### Task 7: Generate the models

**Files:**
- Create: `scripts/generate.py`, `tests/test_generator_models.py`
- Create (by running the generator): `src/minimax_api/_generated/__init__.py`, `src/minimax_api/_generated/models.py`

**Interfaces:**
- Consumes: `MinimaxModel` from `envelope.py`.
- Produces:
  - `scripts/generate.py` exposing `snake_case(name: str) -> str`, `class_name(definition: str) -> str`, `build_models(document: dict) -> str`.
  - `minimax_api._generated.models` containing 90 classes, including `Customer`, `CustomerSearch`, `Country`, `Currency`, `VatRate`, and `FkField`.

**Naming rules this task locks in:**

| Swagger definition | Generated class |
|---|---|
| `SAOP.API.Models.Customer.Customer` | `Customer` |
| `SAOP.API.Models.Customer.CustomerSearch` | `CustomerSearch` |
| `SAOP.API.Common.mMApiFkField` | `FkField` (special case, documented in the file header) |
| `SAOP.API.Models.SearchResult[...]` | not generated — `envelope.SearchResult` covers all 37 |
| `SAOP.API.Models.Dashboard.Chart` vs `SAOP.API.Models.Report.Chart` | leaf collides, so prefix the preceding segment: `DashboardChart`, `ReportChart` |

- [ ] **Step 1: Write the failing test**

```python
# tests/test_generator_models.py
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from generate import build_models, class_name, snake_case  # noqa: E402


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ("CustomerId", "customer_id"),
        ("Name", "name"),
        ("VATIdentificationNumber", "vat_identification_number"),
        ("EInvoiceIssuing", "e_invoice_issuing"),
        ("GLN", "gln"),
        ("RowVersion", "row_version"),
        ("ID", "id"),
    ],
)
def test_snake_case_handles_acronyms(given, expected):
    assert snake_case(given) == expected


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ("SAOP.API.Models.Customer.Customer", "Customer"),
        ("SAOP.API.Models.Customer.CustomerSearch", "CustomerSearch"),
        ("SAOP.API.Common.mMApiFkField", "FkField"),
    ],
)
def test_class_name_strips_the_namespace(given, expected):
    assert class_name(given, collisions=set()) == expected


def test_colliding_leaf_names_get_their_parent_segment():
    collisions = {"Chart"}
    assert class_name("SAOP.API.Models.Dashboard.Chart", collisions=collisions) == "DashboardChart"
    assert class_name("SAOP.API.Models.Report.Chart", collisions=collisions) == "ReportChart"


MINI_SPEC = {
    "definitions": {
        "SAOP.API.Common.mMApiFkField": {
            "type": "object",
            "properties": {
                "ID": {"type": "integer", "format": "int64"},
                "Name": {"type": "string", "readOnly": True},
                "ResourceUrl": {"type": "string", "readOnly": True},
            },
        },
        "SAOP.API.Models.Customer.Customer": {
            "type": "object",
            "properties": {
                "CustomerId": {"type": "integer", "format": "int64", "description": '"Customer id."'},
                "Name": {"type": "string"},
                "Country": {"$ref": "#/definitions/SAOP.API.Common.mMApiFkField"},
                "RebatePercent": {"type": "number", "format": "double"},
                "Usage": {"type": "string"},
                "RowVersion": {"type": "string", "format": "byte"},
                "Contacts": {"type": "array", "items": {"$ref": "#/definitions/SAOP.API.Common.mMApiFkField"}},
            },
        },
        "SAOP.API.Models.SearchResult[SAOP.API.Models.Customer.Customer]": {
            "type": "object",
            "properties": {"Rows": {"type": "array"}},
        },
    }
}


def test_generated_source_declares_the_expected_classes():
    source = build_models(MINI_SPEC)
    assert "class FkField(MinimaxModel):" in source
    assert "class Customer(MinimaxModel):" in source
    # The envelope is hand-written once; its 37 generic instantiations are skipped.
    assert "SearchResult" not in source


def test_generated_fields_carry_types_and_aliases():
    source = build_models(MINI_SPEC)
    assert 'customer_id: int | None = Field(default=None, alias="CustomerId")' in source
    assert 'name: str | None = Field(default=None, alias="Name")' in source
    assert 'country: FkField | None = Field(default=None, alias="Country")' in source
    assert 'rebate_percent: float | None = Field(default=None, alias="RebatePercent")' in source
    assert 'contacts: list[FkField] | None = Field(default=None, alias="Contacts")' in source


def test_generated_source_is_importable_and_round_trips_a_payload():
    namespace: dict[str, object] = {}
    exec(compile(build_models(MINI_SPEC), "<generated>", "exec"), namespace)  # noqa: S102
    customer = namespace["Customer"].model_validate(  # type: ignore[attr-defined]
        {"CustomerId": 1, "Name": "ACME", "Country": {"ID": 3, "Name": "RS"}}
    )
    assert customer.customer_id == 1
    assert customer.country.id == 3
    # Round-tripping must produce the vendor's spelling, not Python's.
    assert customer.model_dump(by_alias=True, exclude_none=True)["CustomerId"] == 1


def test_generated_header_warns_against_editing():
    source = build_models(MINI_SPEC)
    assert "do not edit" in source.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_generator_models.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'generate'`

- [ ] **Step 3: Write the generator's model half**

```python
#!/usr/bin/env python3
"""Generate `minimax_api._generated` from the committed Swagger document.

The output is committed. That is deliberate: a regenerated diff is a readable
report on what Minimax changed, consumers do not need this script installed,
and IDE navigation works. Never hand-edit the output — change this script and
regenerate.

Usage:
    uv run python scripts/generate.py
    uv run python scripts/generate.py --check   # exit 1 if the committed output is stale
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SPEC_DIR = ROOT / "spec"
OUT_DIR = ROOT / "src" / "minimax_api" / "_generated"

#: `mMApiFkField` is the reference object every foreign key uses. Its vendor
#: name is unreadable, and it appears in almost every model, so it is the one
#: name this generator renames.
SPECIAL_CLASS_NAMES = {"SAOP.API.Common.mMApiFkField": "FkField"}

_ACRONYM_BOUNDARY = re.compile(r"(.)([A-Z][a-z]+)")
_LOWER_UPPER_BOUNDARY = re.compile(r"([a-z0-9])([A-Z])")

_PRIMITIVES: dict[tuple[str, str | None], str] = {
    ("integer", "int32"): "int",
    ("integer", "int64"): "int",
    ("integer", None): "int",
    ("number", "double"): "float",
    ("number", "float"): "float",
    ("number", None): "float",
    ("string", "date-time"): "str",
    ("string", "byte"): "str",
    ("string", None): "str",
    ("boolean", None): "bool",
}


def snake_case(name: str) -> str:
    """`VATIdentificationNumber` -> `vat_identification_number`."""
    first = _ACRONYM_BOUNDARY.sub(r"\1_\2", name)
    return _LOWER_UPPER_BOUNDARY.sub(r"\1_\2", first).lower()


def leaf(definition: str) -> str:
    return definition.split("[")[0].split(".")[-1]


def class_name(definition: str, *, collisions: set[str]) -> str:
    """Map a Swagger definition name to a Python class name."""
    if definition in SPECIAL_CLASS_NAMES:
        return SPECIAL_CLASS_NAMES[definition]

    name = leaf(definition)
    if name in collisions:
        segments = definition.split("[")[0].split(".")
        parent = segments[-2] if len(segments) > 1 else ""
        return f"{parent}{name}"
    return name


def find_collisions(definitions: dict[str, Any]) -> set[str]:
    counts = Counter(
        leaf(name)
        for name in definitions
        if not name.startswith("SAOP.API.Models.SearchResult[")
        and name not in SPECIAL_CLASS_NAMES
    )
    return {name for name, count in counts.items() if count > 1}


def python_type(schema: dict[str, Any], collisions: set[str]) -> str:
    ref = schema.get("$ref")
    if ref:
        return class_name(ref.rsplit("/", 1)[-1], collisions=collisions)

    kind = schema.get("type")
    if kind == "array":
        return f"list[{python_type(schema.get('items', {}), collisions)}]"

    mapped = _PRIMITIVES.get((kind, schema.get("format"))) or _PRIMITIVES.get((kind, None))
    # Anything unmapped stays `Any`: guessing a narrower type would reject
    # payloads the live API actually sends.
    return mapped or "Any"


def field_line(prop: str, schema: dict[str, Any], collisions: set[str]) -> str:
    annotation = python_type(schema, collisions)
    attribute = snake_case(prop)
    if attribute in {"id", "type", "format"} and prop != "ID":
        attribute = f"{attribute}_"
    return f'    {attribute}: {annotation} | None = Field(default=None, alias="{prop}")'


def build_models(document: dict[str, Any]) -> str:
    definitions = document["definitions"]
    collisions = find_collisions(definitions)

    lines = [
        '"""Models generated from the Minimax Swagger document. Do not edit.',
        "",
        "Regenerate with `uv run python scripts/generate.py`.",
        "",
        "`SearchResult[...]` definitions are skipped: `minimax_api.envelope.SearchResult`",
        "covers every one of them generically. `mMApiFkField` is renamed `FkField`.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "from typing import Any",
        "",
        "from pydantic import Field",
        "",
        "from minimax_api.envelope import MinimaxModel",
        "",
    ]

    for definition in sorted(definitions):
        if definition.startswith("SAOP.API.Models.SearchResult["):
            continue
        schema = definitions[definition]
        name = class_name(definition, collisions=collisions)
        properties: dict[str, Any] = schema.get("properties", {})

        lines.append("")
        lines.append(f"class {name}(MinimaxModel):")
        lines.append(f'    """`{definition}`"""')
        lines.append("")
        if not properties:
            lines.append("    pass")
            continue
        for prop, prop_schema in properties.items():
            lines.append(field_line(prop, prop_schema, collisions))

    lines.append("")
    return "\n".join(lines)


def newest_spec() -> Path:
    candidates = sorted(SPEC_DIR.glob("swagger-*.json"))
    if not candidates:
        raise SystemExit("no committed spec found in spec/")
    return candidates[-1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    document = json.loads(newest_spec().read_text())
    outputs = {OUT_DIR / "models.py": build_models(document)}

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    init = OUT_DIR / "__init__.py"
    if not init.exists() and not args.check:
        init.write_text('"""Generated code. Do not edit; run scripts/generate.py."""\n')

    stale = []
    for path, source in outputs.items():
        if args.check:
            if not path.exists() or path.read_text() != source:
                stale.append(path.name)
            continue
        path.write_text(source)
        print(f"wrote {path.relative_to(ROOT)} ({len(source.splitlines())} lines)")

    if args.check and stale:
        print(f"stale generated files: {', '.join(stale)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_generator_models.py -v`
Expected: PASS, 15 tests.

- [ ] **Step 5: Generate and sanity-check the real models**

```bash
uv run python scripts/generate.py
uv run python -c "
import minimax_api._generated.models as m
import inspect
classes = [n for n, o in vars(m).items() if inspect.isclass(o) and n[0].isupper()]
print(len(classes), 'classes')
print(m.Customer.model_validate({'CustomerId': 1, 'Country': {'ID': 3}}).country.id)
"
```

Expected: `90 classes` (or whatever the current spec holds — the count must match the non-`SearchResult` definition count) and `3`.

- [ ] **Step 6: Commit**

```bash
git add scripts/generate.py src/minimax_api/_generated tests/test_generator_models.py
git commit -m "feat: generate pydantic models from the vendored spec"
```

---

### Task 8: Generate the operations

**Files:**
- Modify: `scripts/generate.py` (add `build_operations`, wire it into `main`)
- Create: `tests/test_generator_operations.py`
- Create (by running the generator): `src/minimax_api/_generated/operations.py`

**Interfaces:**
- Consumes: `Transport`, `Response`, `SearchResult`, the generated models.
- Produces: `build_operations(document: dict) -> str` and 178 module-level functions in `minimax_api._generated.operations`, each with the shape:

```python
def customer_get(transport: Transport, *, organisation_id: int, params: Mapping[str, Any] | None = None) -> SearchResult[CustomerSearch]: ...
def customer_get_by_customer_id(transport: Transport, *, organisation_id: int, customer_id: int) -> Customer: ...
def customer_post(transport: Transport, *, organisation_id: int, body: Customer) -> int | None: ...
def customer_put_by_customer_id(transport: Transport, *, organisation_id: int, customer_id: int, body: Customer) -> None: ...
def customer_delete_by_customer_id(transport: Transport, *, organisation_id: int, customer_id: int) -> None: ...
```

**The naming problem this task must solve:** 178 operations share only 131 distinct `operationId` values, so `operationId` alone cannot name a function. The rule is two-pass and deterministic:

1. Candidate name = `snake_case(operationId)` with the `_` separator preserved (`Customer_Get` → `customer_get`).
2. Group operations by candidate. Any group with more than one member gets a suffix built from the path segments after the collection segment: `{customerId}` → `by_customer_id`, `code({code})` → `by_code`, a literal segment → that segment (`synccandidates`).
3. After disambiguation the generator asserts every name is unique and raises if not, so a future spec cannot silently produce two functions with one name.

**Return-type rules:**
- Response schema is `SearchResult[X]` → return `SearchResult[X]`.
- Response schema is a plain definition → return that model.
- `POST` with no response schema → return `response.location_id` typed `int | None`.
- `PUT`/`DELETE` with no response schema → return `None`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_generator_operations.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from generate import build_operations, operation_names  # noqa: E402

MINI_SPEC = {
    "definitions": {
        "SAOP.API.Models.Customer.Customer": {"type": "object", "properties": {"CustomerId": {"type": "integer"}}},
        "SAOP.API.Models.Customer.CustomerSearch": {"type": "object", "properties": {"CustomerId": {"type": "integer"}}},
        "SAOP.API.Models.SearchResult[SAOP.API.Models.Customer.CustomerSearch]": {
            "type": "object",
            "properties": {"Rows": {"type": "array", "items": {"$ref": "#/definitions/SAOP.API.Models.Customer.CustomerSearch"}}},
        },
    },
    "paths": {
        "/api/orgs/{organisationId}/customers": {
            "get": {
                "operationId": "Customer_Get",
                "parameters": [{"name": "organisationId", "in": "path", "required": True, "type": "integer"}],
                "responses": {"200": {"schema": {"$ref": "#/definitions/SAOP.API.Models.SearchResult[SAOP.API.Models.Customer.CustomerSearch]"}}},
            },
            "post": {
                "operationId": "Customer_Post",
                "parameters": [
                    {"name": "organisationId", "in": "path", "required": True, "type": "integer"},
                    {"name": "customer", "in": "body", "schema": {"$ref": "#/definitions/SAOP.API.Models.Customer.Customer"}},
                ],
                "responses": {"200": {"description": "OK"}},
            },
        },
        "/api/orgs/{organisationId}/customers/{customerId}": {
            "get": {
                "operationId": "Customer_Get",
                "parameters": [
                    {"name": "organisationId", "in": "path", "required": True, "type": "integer"},
                    {"name": "customerId", "in": "path", "required": True, "type": "integer"},
                ],
                "responses": {"200": {"schema": {"$ref": "#/definitions/SAOP.API.Models.Customer.Customer"}}},
            },
            "put": {
                "operationId": "Customer_Put",
                "parameters": [
                    {"name": "organisationId", "in": "path", "required": True, "type": "integer"},
                    {"name": "customerId", "in": "path", "required": True, "type": "integer"},
                    {"name": "customer", "in": "body", "schema": {"$ref": "#/definitions/SAOP.API.Models.Customer.Customer"}},
                ],
                "responses": {"200": {"description": "OK"}},
            },
        },
        "/api/orgs/{organisationId}/customers/code({code})": {
            "get": {
                "operationId": "Customer_Get",
                "parameters": [
                    {"name": "organisationId", "in": "path", "required": True, "type": "integer"},
                    {"name": "code", "in": "path", "required": True, "type": "string"},
                ],
                "responses": {"200": {"schema": {"$ref": "#/definitions/SAOP.API.Models.Customer.Customer"}}},
            },
        },
    },
}


def test_colliding_operation_ids_are_disambiguated_by_path():
    names = set(operation_names(MINI_SPEC))
    assert {"customer_get", "customer_get_by_customer_id", "customer_get_by_code"} <= names


def test_every_generated_name_is_unique():
    names = list(operation_names(MINI_SPEC))
    assert len(names) == len(set(names))


def test_collection_get_returns_the_envelope():
    source = build_operations(MINI_SPEC)
    assert "def customer_get(" in source
    assert "-> SearchResult[CustomerSearch]:" in source


def test_single_get_returns_the_model():
    source = build_operations(MINI_SPEC)
    assert "def customer_get_by_customer_id(" in source
    assert "customer_id: int," in source
    assert "-> Customer:" in source


def test_post_without_a_response_schema_returns_the_location_id():
    source = build_operations(MINI_SPEC)
    assert "def customer_post(" in source
    assert "body: Customer," in source
    assert "-> int | None:" in source
    assert "return response.location_id" in source


def test_put_returns_none():
    source = build_operations(MINI_SPEC)
    assert "def customer_put_by_customer_id(" in source
    assert "-> None:" in source


def test_paths_are_interpolated_with_the_python_parameter_names():
    source = build_operations(MINI_SPEC)
    assert 'f"/api/orgs/{organisation_id}/customers/{customer_id}"' in source
    assert 'f"/api/orgs/{organisation_id}/customers/code({code})"' in source


def test_body_is_serialised_with_vendor_field_names():
    source = build_operations(MINI_SPEC)
    assert "body.model_dump(by_alias=True, exclude_none=True)" in source


def test_generated_operations_compile():
    compile(build_operations(MINI_SPEC), "<generated>", "exec")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_generator_operations.py -v`
Expected: FAIL — `ImportError: cannot import name 'build_operations' from 'generate'`

- [ ] **Step 3: Extend the generator**

Add to `scripts/generate.py`:

```python
_PATH_PARAM = re.compile(r"\{([A-Za-z0-9_]+)\}")
_HTTP_METHODS = ("get", "post", "put", "delete", "patch")


def _operations(document: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten the Swagger paths into one record per operation, path order preserved."""
    found = []
    for path in document["paths"]:
        item = document["paths"][path]
        for method in _HTTP_METHODS:
            if method in item:
                found.append({"path": path, "method": method, "spec": item[method]})
    return found


def _path_suffix(path: str) -> str:
    """The distinguishing tail of a path, e.g. `by_customer_id` or `by_code`."""
    parts = []
    # Everything after the collection segment (the one following `{organisationId}`).
    segments = [s for s in path.split("/") if s]
    for segment in segments[3:]:
        match = _PATH_PARAM.fullmatch(segment)
        if match:
            parts.append(f"by_{snake_case(match.group(1))}")
            continue
        odata = re.fullmatch(r"([A-Za-z0-9]+)\(\{[A-Za-z0-9_]+\}\)", segment)
        if odata:
            parts.append(f"by_{snake_case(odata.group(1))}")
            continue
        parts.append(snake_case(segment))
    return "_".join(parts)


def operation_names(document: dict[str, Any]) -> list[str]:
    """Deterministic function names, disambiguated where operationIds collide."""
    operations = _operations(document)
    candidates = [snake_case(op["spec"]["operationId"]) for op in operations]
    counts = Counter(candidates)

    names = []
    for operation, candidate in zip(operations, candidates, strict=True):
        if counts[candidate] == 1:
            names.append(candidate)
            continue
        suffix = _path_suffix(operation["path"])
        names.append(f"{candidate}_{suffix}" if suffix else candidate)

    duplicates = [name for name, count in Counter(names).items() if count > 1]
    if duplicates:
        raise SystemExit(f"operation names are not unique: {duplicates}")
    return names


def _response_type(spec: dict[str, Any], collisions: set[str]) -> str | None:
    for status in ("200", "201"):
        schema = spec.get("responses", {}).get(status, {}).get("schema")
        if not schema:
            continue
        ref = schema.get("$ref", "")
        definition = ref.rsplit("/", 1)[-1]
        envelope = re.fullmatch(r"SAOP\.API\.Models\.SearchResult\[(.+)\]", definition)
        if envelope:
            return f"SearchResult[{class_name(envelope.group(1), collisions=collisions)}]"
        if definition:
            return class_name(definition, collisions=collisions)
    return None


def build_operations(document: dict[str, Any]) -> str:
    collisions = find_collisions(document["definitions"])
    operations = _operations(document)
    names = operation_names(document)

    used_models: set[str] = set()
    bodies: list[str] = []

    for operation, name in zip(operations, names, strict=True):
        path, method, spec = operation["path"], operation["method"], operation["spec"]
        parameters = spec.get("parameters", [])

        signature = ["transport: Transport", "*"]
        for parameter in parameters:
            if parameter["in"] != "path":
                continue
            annotation = python_type(parameter, collisions)
            signature.append(f"{snake_case(parameter['name'])}: {annotation}")

        body_type = None
        for parameter in parameters:
            if parameter["in"] == "body":
                body_type = python_type(parameter.get("schema", {}), collisions)
                signature.append(f"body: {body_type}")
                used_models.add(body_type)

        has_query = any(parameter["in"] == "query" for parameter in parameters)
        if method == "get":
            signature.append("params: Mapping[str, Any] | None = None")
        elif has_query:
            signature.append("params: Mapping[str, Any] | None = None")

        return_type = _response_type(spec, collisions)
        if return_type:
            inner = return_type.removeprefix("SearchResult[").removesuffix("]")
            used_models.add(inner)
        elif method == "post":
            return_type = "int | None"
        else:
            return_type = "None"

        interpolated = _PATH_PARAM.sub(lambda m: "{" + snake_case(m.group(1)) + "}", path)

        call = [f'    response = transport.request("{method.upper()}", f"{interpolated}"']
        if "params" in " ".join(signature):
            call.append(", params=params")
        if body_type:
            call.append(", json=body.model_dump(by_alias=True, exclude_none=True)")
        call.append(")")

        lines = [
            "",
            "",
            f"def {name}(",
            "    " + ",\n    ".join(signature) + ",",
            f") -> {return_type}:",
            f'    """`{method.upper()} {path}` (operationId `{spec["operationId"]}`)."""',
            "".join(call),
        ]

        if return_type.startswith("SearchResult["):
            lines.append(f"    return {return_type}.model_validate(response.json)")
        elif return_type == "int | None":
            lines.append("    return response.location_id")
        elif return_type == "None":
            lines.append("    return None")
        else:
            lines.append(f"    return {return_type}.model_validate(response.json)")

        bodies.extend(lines)

    imports = ", ".join(sorted(name for name in used_models if name != "Any"))
    header = [
        '"""Operations generated from the Minimax Swagger document. Do not edit.',
        "",
        "One function per Swagger operation. Names come from the operationId; where",
        "several operations share one operationId, the path tail disambiguates them",
        "(`customer_get`, `customer_get_by_customer_id`, `customer_get_by_code`).",
        "",
        "Regenerate with `uv run python scripts/generate.py`.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "from collections.abc import Mapping",
        "from typing import Any",
        "",
        "from minimax_api.envelope import SearchResult",
        "from minimax_api.transport import Transport",
    ]
    if imports:
        header.append(f"from minimax_api._generated.models import {imports}")
    return "\n".join(header + bodies) + "\n"
```

Wire it into `main` by replacing the `outputs` assignment:

```python
    outputs = {
        OUT_DIR / "models.py": build_models(document),
        OUT_DIR / "operations.py": build_operations(document),
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_generator_operations.py -v`
Expected: PASS, 9 tests.

- [ ] **Step 5: Generate and verify the real operations**

```bash
uv run python scripts/generate.py
uv run python -c "
import minimax_api._generated.operations as ops
import inspect
functions = [n for n, o in vars(ops).items() if inspect.isfunction(o)]
print(len(functions), 'operations')
print(sorted(n for n in functions if n.startswith('customer_')))
"
uv run ruff check src/minimax_api/_generated
uv run mypy src
```

Expected: `178 operations`, the customer list showing the disambiguated names, and both linters clean. If ruff reports formatting complaints about the generated file, fix the generator's emitted text — never the output.

- [ ] **Step 6: Add a staleness guard to CI**

Add to `.github/workflows/ci.yml`, after the mypy step:

```yaml
      - run: uv run python scripts/generate.py --check
```

- [ ] **Step 7: Commit**

```bash
git add scripts/generate.py src/minimax_api/_generated tests/test_generator_operations.py .github/workflows/ci.yml
git commit -m "feat: generate 178 typed operation functions from the spec"
```

---

### Task 9: The client and the resource facade

**Files:**
- Create: `src/minimax_api/client.py`, `src/minimax_api/resources/__init__.py`, `src/minimax_api/resources/codelists.py`, `src/minimax_api/resources/customers.py`, `src/minimax_api/resources/issued_invoices.py`, `tests/test_client.py`, `tests/test_resources.py`
- Modify: `src/minimax_api/__init__.py`

**Interfaces:**
- Consumes: everything above.
- Produces:
  - `MinimaxClient(credentials, organisation_id, *, region=RS, http=None, token_store=None, budget=None)` with attributes `.codelists`, `.customers`, `.issued_invoices`, `.transport`, and methods `organisations() -> list[FkField]`, `close() -> None`, plus context-manager support.
  - `CodeLists` with `countries()`, `currencies()`, `vat_rates()`, `accounts()`, `country_by_code(code)`, `currency_by_code(code)` — all returning generated models.
  - `Customers` with `list(search=None)`, `get(customer_id)`, `create(customer) -> int`, `update(customer) -> None`.
  - `IssuedInvoices` with `list()`, `get(invoice_id)`, `create(invoice) -> int`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_resources.py
import httpx
import pytest

from minimax_api import MinimaxClient
from minimax_api.auth import Credentials
from minimax_api.errors import ConcurrencyError, ValidationError

CREDENTIALS = Credentials(
    client_id="client", client_secret="secret", username="user", password="password"
)

TOKEN = {"access_token": "abc", "expires_in": 3600}


def make_client(routes):
    """routes: dict mapping (method, path) -> httpx.Response or callable."""

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/oauth20/token"):
            return httpx.Response(200, json=TOKEN)
        key = (request.method, request.url.path)
        route = routes[key]
        return route(request) if callable(route) else route

    http = httpx.Client(transport=httpx.MockTransport(handler))
    return MinimaxClient(credentials=CREDENTIALS, organisation_id=12345, http=http)


def test_currencies_are_read_from_the_organisation_not_a_global_endpoint():
    seen = []

    def route(request: httpx.Request) -> httpx.Response:
        seen.append(request.url.path)
        return httpx.Response(
            200,
            json={
                "Rows": [{"CurrencyId": 2, "Code": "RSD", "Name": "Serbian dinar"}],
                "TotalRows": 1,
                "CurrentPageNumber": 1,
                "PageSize": 300,
            },
        )

    client = make_client({("GET", "/RS/API/api/orgs/12345/currencies"): route})
    currencies = client.codelists.currencies()

    assert seen == ["/RS/API/api/orgs/12345/currencies"]
    assert currencies[0].code == "RSD"
    assert currencies[0].currency_id == 2


def test_currency_by_code_resolves_rather_than_assuming_an_id():
    # The vendor's samples say Currency.ID 7 is the default; in the Serbian
    # organisation 7 is CZK and RSD is 2. Nothing may be assumed.
    rows = {
        "Rows": [
            {"CurrencyId": 7, "Code": "CZK"},
            {"CurrencyId": 2, "Code": "RSD"},
        ],
        "TotalRows": 2,
        "CurrentPageNumber": 1,
        "PageSize": 300,
    }
    client = make_client({("GET", "/RS/API/api/orgs/12345/currencies"): httpx.Response(200, json=rows)})
    assert client.codelists.currency_by_code("RSD").currency_id == 2


def test_country_by_code_returns_none_when_absent():
    rows = {"Rows": [{"CountryId": 3, "Code": "RS"}], "TotalRows": 1, "CurrentPageNumber": 1, "PageSize": 300}
    client = make_client({("GET", "/RS/API/api/orgs/12345/countries"): httpx.Response(200, json=rows)})
    assert client.codelists.country_by_code("XX") is None


def test_creating_a_customer_returns_the_id_from_the_location_header():
    location = {"Location": "https://moj.minimax.rs/RS/API/api/orgs/12345/customers/4242"}
    captured = {}

    def route(request: httpx.Request) -> httpx.Response:
        captured["body"] = request.content.decode()
        return httpx.Response(201, headers=location)

    client = make_client({("POST", "/RS/API/api/orgs/12345/customers"): route})
    from minimax_api.models import Customer

    new_id = client.customers.create(Customer(name="ACME", address="Example Street 1"))
    assert new_id == 4242
    # Vendor spelling on the wire, snake_case in Python.
    assert '"Name": "ACME"' in captured["body"] or '"Name":"ACME"' in captured["body"]


def test_creating_a_customer_without_a_location_header_is_an_error():
    client = make_client({("POST", "/RS/API/api/orgs/12345/customers"): httpx.Response(201)})
    from minimax_api.models import Customer

    with pytest.raises(ValidationError):
        client.customers.create(Customer(name="ACME"))


def test_updating_without_a_row_version_is_refused_before_the_request():
    calls = []

    def route(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200)

    client = make_client({("PUT", "/RS/API/api/orgs/12345/customers/1"): route})
    from minimax_api.models import Customer

    with pytest.raises(ValidationError):
        client.customers.update(Customer(customer_id=1, name="ACME"))
    assert calls == []


def test_a_row_version_conflict_surfaces_as_concurrency_error():
    body = {"Message": "Concurrency error - record changed by another action (RowVersion)"}
    client = make_client({("PUT", "/RS/API/api/orgs/12345/customers/1"): httpx.Response(400, json=body)})
    from minimax_api.models import Customer

    with pytest.raises(ConcurrencyError):
        client.customers.update(Customer(customer_id=1, name="ACME", row_version="AAAAA8OTDPw="))


def test_customers_list_walks_pages():
    pages = {
        "1": {"Rows": [{"CustomerId": 1}], "TotalRows": 2, "CurrentPageNumber": 1, "PageSize": 1},
        "2": {"Rows": [{"CustomerId": 2}], "TotalRows": 2, "CurrentPageNumber": 2, "PageSize": 1},
    }

    def route(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=pages[request.url.params.get("CurrentPage", "1")])

    client = make_client({("GET", "/RS/API/api/orgs/12345/customers"): route})
    customers = client.customers.list(page_size=1)
    assert [c.customer_id for c in customers] == [1, 2]
```

```python
# tests/test_client.py
import httpx

from minimax_api import MinimaxClient
from minimax_api.auth import Credentials

CREDENTIALS = Credentials(
    client_id="client", client_secret="secret", username="user", password="password"
)


def handler(request: httpx.Request) -> httpx.Response:
    if request.url.path.endswith("/oauth20/token"):
        return httpx.Response(200, json={"access_token": "abc", "expires_in": 3600})
    if request.url.path == "/RS/API/api/currentuser/orgs":
        return httpx.Response(
            200,
            json={
                "Rows": [{"Organisation": {"ID": 12345, "Name": "ACME"}}],
                "TotalRows": 1,
                "CurrentPageNumber": 1,
                "PageSize": 300,
            },
        )
    raise AssertionError(f"unexpected request: {request.url}")


def test_organisations_lists_what_the_credentials_can_reach():
    http = httpx.Client(transport=httpx.MockTransport(handler))
    client = MinimaxClient(credentials=CREDENTIALS, organisation_id=12345, http=http)
    organisations = client.organisations()
    assert [org.id for org in organisations] == [12345]


def test_client_works_as_a_context_manager():
    http = httpx.Client(transport=httpx.MockTransport(handler))
    with MinimaxClient(credentials=CREDENTIALS, organisation_id=12345, http=http) as client:
        assert client.organisations()[0].name == "ACME"


def test_public_surface_is_importable_from_the_package_root():
    import minimax_api

    for name in (
        "MinimaxClient",
        "Credentials",
        "Region",
        "RS",
        "MinimaxError",
        "MinimaxAuthError",
        "RateBudgetExceeded",
        "ConcurrencyError",
        "NotFoundError",
        "ValidationError",
        "TransportError",
    ):
        assert hasattr(minimax_api, name), name
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_client.py tests/test_resources.py -v`
Expected: FAIL — `ImportError: cannot import name 'MinimaxClient' from 'minimax_api'`

- [ ] **Step 3: Write the code-list facade**

```python
# src/minimax_api/resources/codelists.py
"""Reference data — the records documents point at by ID.

Every ID here is organisation-specific. The vendor's published samples give
`Country.ID` 192 for Serbia and `Currency.ID` 7 as a default; in the Serbian
a live RS organisation, Serbia is 3, RSD is 2, and 7 is the Czech koruna. That is
why this module resolves and never assumes, and why no ID constant appears
anywhere in this library.
"""

from __future__ import annotations

from minimax_api._generated.models import Account, Country, Currency, VatRate
from minimax_api.pagination import DEFAULT_PAGE_SIZE, paginate
from minimax_api.transport import Transport


class CodeLists:
    """Read access to an organisation's reference data."""

    def __init__(self, transport: Transport, organisation_id: int) -> None:
        self._transport = transport
        self._organisation_id = organisation_id

    def _base(self, module: str) -> str:
        return f"/api/orgs/{self._organisation_id}/{module}"

    def countries(self, *, page_size: int = DEFAULT_PAGE_SIZE) -> list[Country]:
        return list(paginate(self._transport, self._base("countries"), Country, page_size=page_size))

    def currencies(self, *, page_size: int = DEFAULT_PAGE_SIZE) -> list[Currency]:
        return list(paginate(self._transport, self._base("currencies"), Currency, page_size=page_size))

    def vat_rates(self, *, page_size: int = DEFAULT_PAGE_SIZE) -> list[VatRate]:
        return list(paginate(self._transport, self._base("vatrates"), VatRate, page_size=page_size))

    def accounts(self, *, page_size: int = DEFAULT_PAGE_SIZE) -> list[Account]:
        return list(paginate(self._transport, self._base("accounts"), Account, page_size=page_size))

    def country_by_code(self, code: str) -> Country | None:
        """Find a country by its ISO code, e.g. `RS`. Returns None if absent."""
        return next((row for row in self.countries() if row.code == code), None)

    def currency_by_code(self, code: str) -> Currency | None:
        """Find a currency by its ISO code, e.g. `RSD`. Returns None if absent."""
        return next((row for row in self.currencies() if row.code == code), None)
```

If the generated class for VAT rates is not named `VatRate`, use whatever `scripts/generate.py` emitted — check with `uv run python -c "import minimax_api._generated.models as m; print([n for n in vars(m) if 'Vat' in n])"` and adjust the import and annotations here.

- [ ] **Step 4: Write the customer and invoice facades**

```python
# src/minimax_api/resources/customers.py
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
        return list(
            paginate(self._transport, self._base, CustomerSearch, params=params, page_size=page_size)
        )

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
```

```python
# src/minimax_api/resources/issued_invoices.py
"""Issued invoices.

An accepted write is a draft, not a business event. Documents created through
the API arrive with status `O` (nacrt); an invoice becomes real only after the
corresponding custom action succeeds and the result is read back. This library
creates and reads; deciding when to issue belongs to the caller.
"""

from __future__ import annotations

from minimax_api._generated.models import IssuedInvoice
from minimax_api.errors import ValidationError
from minimax_api.pagination import DEFAULT_PAGE_SIZE, paginate
from minimax_api.transport import Transport


class IssuedInvoices:
    def __init__(self, transport: Transport, organisation_id: int) -> None:
        self._transport = transport
        self._organisation_id = organisation_id
        self._base = f"/api/orgs/{organisation_id}/issuedinvoices"

    def list(self, *, page_size: int = DEFAULT_PAGE_SIZE) -> list[IssuedInvoice]:
        return list(paginate(self._transport, self._base, IssuedInvoice, page_size=page_size))

    def get(self, invoice_id: int) -> IssuedInvoice:
        response = self._transport.request("GET", f"{self._base}/{invoice_id}")
        return IssuedInvoice.model_validate(response.json)

    def create(self, invoice: IssuedInvoice) -> int:
        """Create a draft invoice and return its ID from the `Location` header."""
        payload = invoice.model_dump(by_alias=True, exclude_none=True)
        response = self._transport.request("POST", self._base, json=payload)
        created = response.location_id
        if created is None:
            raise ValidationError(
                "invoice was created but Minimax returned no Location header, so its ID is "
                "unknown; reconcile by search before retrying",
                status_code=response.status_code,
                payload=response.json,
            )
        return created
```

The generated class for an issued invoice may be `IssuedInvoice` or a near variant. Confirm with `uv run python -c "import minimax_api._generated.models as m; print([n for n in vars(m) if 'Issued' in n])"` and use the real name.

- [ ] **Step 5: Write the client**

```python
# src/minimax_api/client.py
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
        organisation_id=12345,
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
```

Create `src/minimax_api/resources/__init__.py` containing:

```python
"""Hand-written facades over the modules the connector uses."""
```

Extend `src/minimax_api/__init__.py`:

```python
"""Python client for the Minimax (Saop) accounting REST API."""

from minimax_api._generated import models
from minimax_api.auth import Credentials, InMemoryTokenStore, Token, TokenStore
from minimax_api.budget import Budget, BudgetStore, InMemoryBudgetStore
from minimax_api.client import MinimaxClient
from minimax_api.envelope import MinimaxModel, SearchResult
from minimax_api.errors import (
    ConcurrencyError,
    MinimaxAuthError,
    MinimaxError,
    NotFoundError,
    RateBudgetExceeded,
    TransportError,
    ValidationError,
)
from minimax_api.region import RS, Region

__all__ = [
    "RS",
    "Budget",
    "BudgetStore",
    "ConcurrencyError",
    "Credentials",
    "InMemoryBudgetStore",
    "InMemoryTokenStore",
    "MinimaxAuthError",
    "MinimaxClient",
    "MinimaxError",
    "MinimaxModel",
    "NotFoundError",
    "RateBudgetExceeded",
    "Region",
    "SearchResult",
    "Token",
    "TokenStore",
    "TransportError",
    "ValidationError",
    "models",
]
```

Create `src/minimax_api/models.py` so callers have a stable import path that does not reach into a private package:

```python
"""Re-export of the generated models under a public name.

`from minimax_api.models import Customer` is the supported import. The
`_generated` package is an implementation detail and may be reorganised.
"""

from minimax_api._generated.models import *  # noqa: F403
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `uv run pytest -v`
Expected: PASS — every offline test, including 11 new ones in `test_resources.py` and `test_client.py`.

- [ ] **Step 7: Commit**

```bash
git add src/minimax_api tests/test_client.py tests/test_resources.py
git commit -m "feat: MinimaxClient with code-list, customer, and invoice facades"
```

---

### Task 10: Live tests against the real organisation

**Files:**
- Create: `tests/test_live.py`, `tests/conftest.py`, `.env.example`

**Interfaces:**
- Consumes: `MinimaxClient`, `Credentials`.
- Produces: the `live` pytest marker's fixtures. No source changes.

These tests are the only place that names Serbian ID values, and they name them as **assertions about one organisation**, never as library constants. They issue read-only calls and spend roughly six requests from the daily thousand.

- [ ] **Step 1: Write the env template and fixtures**

```bash
# .env.example
# Copy to .env (gitignored) and fill in. Never commit real values.
# Client half: issued by Minimax support on request.
MINIMAX_CLIENT_ID=
MINIMAX_CLIENT_SECRET=
# User half: Moj profil -> Uredi osnovne podatke ->
# Lozinke za pristup spoljnim aplikacijama -> Nova aplikacija.
MINIMAX_USERNAME=
MINIMAX_PASSWORD=
# The organisation the live tests read.
MINIMAX_ORGANISATION_ID=
```

```python
# tests/conftest.py
"""Fixtures for the opt-in live tests.

Live tests need real credentials and spend from the organisation's daily
request budget of 1,000. They are excluded by default (see `addopts` in
pyproject.toml); run them with `uv run pytest -m live`.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from minimax_api import Credentials, MinimaxClient


def _load_dotenv() -> None:
    path = Path(__file__).resolve().parent.parent / ".env"
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@pytest.fixture(scope="session")
def live_client():
    _load_dotenv()
    required = (
        "MINIMAX_CLIENT_ID",
        "MINIMAX_CLIENT_SECRET",
        "MINIMAX_USERNAME",
        "MINIMAX_PASSWORD",
        "MINIMAX_ORGANISATION_ID",
    )
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        pytest.skip(f"live tests need {', '.join(missing)} in .env")

    client = MinimaxClient(
        credentials=Credentials(
            client_id=os.environ["MINIMAX_CLIENT_ID"],
            client_secret=os.environ["MINIMAX_CLIENT_SECRET"],
            username=os.environ["MINIMAX_USERNAME"],
            password=os.environ["MINIMAX_PASSWORD"],
        ),
        organisation_id=int(os.environ["MINIMAX_ORGANISATION_ID"]),
    )
    yield client
    client.close()
```

- [ ] **Step 2: Write the live tests**

```python
# tests/test_live.py
"""Read-only tests against a real Minimax organisation.

Run with: uv run pytest -m live -v

These pin the facts that the vendor's own documentation gets wrong. If one of
them fails, either the organisation's configuration changed or Minimax changed
the API — investigate before touching the assertion.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.live


def test_credentials_reach_exactly_the_expected_organisation(live_client):
    organisations = live_client.organisations()
    ids = [org.id for org in organisations]
    assert live_client.organisation_id in ids
    # A broader grant than intended is a security finding, not a convenience.
    assert len(ids) == 1, f"credentials reach more organisations than expected: {ids}"


def test_serbia_is_country_id_3_not_the_documented_192(live_client):
    serbia = live_client.codelists.country_by_code("RS")
    assert serbia is not None
    assert serbia.country_id == 3


def test_rsd_is_currency_id_2_and_7_is_not_it(live_client):
    currencies = live_client.codelists.currencies()
    by_code = {row.code: row.currency_id for row in currencies}
    assert by_code["RSD"] == 2
    # Vendor samples present 7 as the default currency. It is the Czech koruna.
    assert by_code["RSD"] != 7


def test_standard_vat_rate_is_twenty_percent(live_client):
    rates = {row.code: row for row in live_client.codelists.vat_rates()}
    assert rates["S"].percent == 20.0
    # VatRateId and VatRatePercentage.ID are separate ID spaces.
    assert rates["S"].vat_rate_id != rates["S"].vat_rate_percentage.id


def test_code_lists_paginate_in_one_request(live_client):
    countries = live_client.codelists.countries()
    assert len(countries) > 200
```

- [ ] **Step 3: Run the offline suite to confirm live tests stay excluded**

Run: `uv run pytest -v`
Expected: PASS with the live tests not collected. Confirm with `uv run pytest --collect-only -q | tail -3`.

- [ ] **Step 4: Run the live suite once, deliberately**

Run: `cp .env.example .env` (fill it in from the connector's `.env`), then `uv run pytest -m live -v`
Expected: PASS, 5 tests. A `MinimaxAuthError` here means the credentials are wrong — **stop, do not rerun**, and check them before trying again.

If `rates["S"].vat_rate_percentage` is spelled differently by the generator, adjust the assertion to the real attribute name rather than changing the model.

- [ ] **Step 5: Commit**

```bash
git add tests/test_live.py tests/conftest.py .env.example
git commit -m "test: opt-in live tests pinning the Serbian code-list facts"
```

---

### Task 11: README and the first release

**Files:**
- Create: `README.md`, `CHANGELOG.md`
- Modify: `pyproject.toml` (no change expected; verify metadata)

**Interfaces:**
- Consumes: the finished public surface.
- Produces: documentation only.

- [ ] **Step 1: Write the README**

````markdown
# minimax-api

Python client for the **Minimax** (Saop) accounting REST API — the ERP used in Serbia, Slovenia,
Croatia, Bosnia and Montenegro.

> This is **not** the MiniMax AI platform. If you are looking for the Chinese LLM vendor, you
> want a different package.

Serbia is the verified deployment. Other countries are a configuration change, not a code
change, but they are untested here.

## Install

```bash
pip install minimax-api
```

## Use

```python
from minimax_api import Credentials, MinimaxClient

with MinimaxClient(
    credentials=Credentials(
        client_id="...",      # issued by Minimax support
        client_secret="...",
        username="...",       # Moj profil -> Lozinke za pristup spoljnim aplikacijama
        password="...",
    ),
    organisation_id=12345,
) as client:
    print([org.name for org in client.organisations()])

    rsd = client.codelists.currency_by_code("RSD")
    serbia = client.codelists.country_by_code("RS")

    from minimax_api.models import Customer

    customer_id = client.customers.create(
        Customer(
            name="ACME d.o.o.",
            address="Example Street 1",
            postal_code="11000",
            city="Beograd",
            country={"ID": serbia.country_id},
            currency={"ID": rsd.currency_id},
            subject_to_vat="D",
            e_invoice_issuing="SeNePripravlja",
        )
    )
```

## Credentials

Minimax splits credentials in two, and both halves arrive through different channels:

| Half | Contents | Who creates it |
|---|---|---|
| Client | `client_id`, `client_secret` | Minimax support, on request — there is no self-service |
| User | `username`, `password` | The subscriber, in *Moj profil → Lozinke za pristup spoljnim aplikacijama* |

A third thing is required: the subscriber's administrator must grant the API right to that user
**on the target organisation**. Without it, authentication succeeds and `organisations()` returns
an empty list.

## Three behaviours worth knowing

**A wrong password is never retried.** Several consecutive credential rejections lock the Minimax
application, and recovery means deleting and recreating it. The first rejection latches the
client: every later call raises without touching the network.

**The request budget is a typed outcome, not a failure.** Minimax allows 1,000 requests per
organisation per rolling 24 hours. When the budget is spent, the client raises
`RateBudgetExceeded` carrying `retry_after` — it never sleeps. Scheduling is yours.

**Nothing is assumed about IDs.** The vendor's published examples give `Country.ID` 192 for
Serbia and `Currency.ID` 7 as a default. In a real Serbian organisation, Serbia is 3, RSD is 2,
and **7 is the Czech koruna**. Resolve every reference from the organisation's own code lists.

## What this library does not do

Idempotency keys, queues, persistence, reconciliation, and webhook handling. A created record's
ID arrives only in the `Location` header, so if your process dies between Minimax committing and
you persisting that ID, the record exists with no local trace. Record the intent to write before
calling and reconcile by search after an unknown outcome — that needs a database, which a client
library has no business owning.

## Coverage

All 178 operations of the Minimax API are generated from the vendor's public Swagger document
and available under `minimax_api._generated.operations`. The hand-written facade
(`client.codelists`, `client.customers`, `client.issued_invoices`) covers what most integrations
need; anything else is one generated call away.

## Development

```bash
uv sync --all-groups
uv run pytest                  # offline, no network
uv run pytest -m live          # real API; needs .env, spends from the daily budget
uv run python scripts/refresh_spec.py --check   # has Minimax changed the API?
uv run python scripts/generate.py               # regenerate after a spec refresh
```

`src/minimax_api/_generated/` is machine-written. Change `scripts/generate.py` and regenerate;
never edit it by hand. Regeneration belongs in its own commit, so that its diff reads as a report
on what Minimax changed.

## Versioning

SemVer, with one caveat: before 1.0 the public facade may change. The generated layer is
versioned with the spec it came from — see `spec/` and the CHANGELOG.

## Licence

MIT.
````

- [ ] **Step 2: Write the changelog**

```markdown
# Changelog

## 0.1.0 — unreleased

First release.

- Authentication with a terminal-failure latch: a rejected credential produces exactly one
  network request, ever.
- Request budget for the 1,000/day and 20,000/month per-organisation limits, raising
  `RateBudgetExceeded(retry_after=...)` instead of sleeping.
- Transport with bounded 5xx retries, one token refresh on a mid-flight 401, and typed errors.
- Pagination over the `{Rows, TotalRows, CurrentPageNumber, PageSize}` envelope.
- 90 generated pydantic models and 178 generated operations.
- Hand-written facades for code lists, customers, and issued invoices.

API surface as of **2026-09-21** (`spec/swagger-2026-09-21.json`): 120 paths, 178 operations,
127 definitions.
```

- [ ] **Step 3: Verify the whole suite and the linters**

```bash
uv run ruff check .
uv run mypy src tests
uv run pytest -v
uv run python scripts/generate.py --check
```

Expected: all clean, generated output not stale.

- [ ] **Step 4: Verify the package builds and imports from a wheel**

```bash
uv build
uv run --isolated --with dist/minimax_api-0.1.0-py3-none-any.whl --no-project \
  python -c "import minimax_api; print(minimax_api.RS.base_url)"
```

Expected: `https://moj.minimax.rs/RS/API`

- [ ] **Step 5: Commit and tag**

```bash
git add README.md CHANGELOG.md
git commit -m "docs: README and changelog for 0.1.0"
git tag v0.1.0
```

Publishing to PyPI is manual and deliberately not automated: `uv publish` once the tag is pushed
and the maintainer has decided to release.

---

## Self-Review

**Spec coverage.** Every section of the spec maps to a task: purpose and naming → Tasks 1 and 11;
scope boundaries → the `create`/`update` docstrings in Task 9 and the README's "what this library
does not do"; region seam → Task 2; verified facts → Tasks 6 and 10; generated-core approach →
Tasks 7 and 8; structure → the file table and Tasks 1–9; lockout rule → Task 2; budget → Task 4;
writes and concurrency → Tasks 3 and 9; errors → Task 1; testing's three levels → Tasks 1–9
(offline), 10 (live); packaging and release → Tasks 1 and 11.

**One spec requirement is deliberately deferred:** the spec's "contract tests — recorded real
responses, sanitised" layer. Recording them requires an organisation with real customers and
invoices, and a live RS organisation is currently empty (`customers` and `items` both return
`TotalRows` 0). Task 10's live tests cover what can be verified today. Add contract fixtures
when the pilot organisation has data — that is a follow-up task, not a gap to paper over.

**Success criteria from the spec, and where each is proven:**

1. Connector authenticates and reads without touching httpx → `tests/test_client.py`, README example.
2. A wrong password produces exactly one network request, ever →
   `test_credential_rejection_is_terminal_and_never_reaches_the_network_twice`.
3. Exceeding the budget is typed and scheduleable → `tests/test_budget.py`,
   `test_transport_refuses_to_send_when_the_budget_is_spent`.
4. Spec refresh shows drift as a diff → `scripts/refresh_spec.py`, CI's `generate.py --check`.
5. No Serbian constant in the library → enforced by review; the only ID literals live in
   `tests/test_live.py` as assertions about one organisation.

**Type consistency.** `Transport.request` keeps one signature from Task 3 onward, with `budget`
present from the start so Task 4 adds no churn. `Response.location_id` is defined in Task 3 and
used in Tasks 8 and 9. `Authenticator.access_token`/`invalidate` are the only methods the
transport calls, which is why `StubAuth` in the tests implements exactly those two.

**Known soft spots the implementer should expect.** Generated class names are predictions:
`VatRate`, `IssuedInvoice`, and `CustomerSearch` are what the definition names imply, but the
generator's collision rule decides the real spelling. Tasks 9 and 10 each carry a command for
checking the real name before writing the import. Treat a mismatch as normal, not as a bug.
