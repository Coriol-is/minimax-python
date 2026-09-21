# Design: `minimax-api` — a Python client for the Minimax accounting API

**Date:** 2026-09-21
**Repository:** `Coriol-is/minimax-python` (public)
**Distribution:** PyPI package `minimax-api`, import name `minimax_api`
**Status:** approved design, not yet implemented

## Purpose

Minimax is a Slovenian/Serbian accounting SaaS (Saop) with a REST API. This library is the
transport and resource layer for talking to it from Python: authentication, request budgeting,
pagination, typed payloads, and errors that say what a caller is allowed to do next.

It exists for two reasons, in this order:

1. **A clean boundary for the connector.** The `minimax-connectors` project delivers commerce
   documents into Minimax. HTTP, OAuth, rate budget, and payload shape belong outside its
   business logic. Extracting them makes both sides testable in isolation.
2. **Public, because the boundary is generic.** Nothing about "a Shopify order becomes an
   invoice" lives here, so there is no cost to opening it — and an open client is the cheapest
   credible proof of Minimax expertise on the Serbian market. Marketing is a side effect, not a
   driver: the library ships when it serves the connector, not when it would make a good post.

**Not the MiniMax AI platform.** The name collides with a Chinese LLM vendor whose unofficial SDK
occupies `minimax-client` on PyPI. The README's first line must say so.

## Scope

**In scope:** authentication with lockout protection, request budgeting against the published
per-organisation limits, pagination, typed models for the full API surface, an ergonomic facade
over the modules the connector uses, and errors that distinguish retryable from terminal.

**Out of scope:** idempotency keys, outbox/queue, persistence, reconciliation, webhook handling,
and every piece of Serbian commerce logic. Those stay in the connector, which owns a database.
The library never sleeps, never retries a business write on its own, and never decides *when*
work should happen — it reports, the caller schedules.

**Region:** Serbia now. `base_url` and `scope` are client parameters with an `RS` preset, so
SI/HR/BA/ME are a configuration change rather than a rewrite. No other region is claimed as
supported, because we have credentials for exactly one organisation and cannot test the rest.

## Verified facts this design rests on

Established against the live API on 2026-09-21 with organisation `97271`:

| Fact | Value |
|---|---|
| Token endpoint | `POST /RS/AUT/oauth20/token`, password grant, `scope=minimax.rs` |
| Token lifetime | 3600 s |
| Collection base | `/RS/api/api/orgs/{orgId}/<module>` |
| Code lists | Per organisation. `/RS/api/api/currencies` returns 404; `/RS/api/api/orgs/{org}/currencies` works |
| Collection envelope | `{Rows, TotalRows, CurrentPageNumber, PageSize}`, default `PageSize` 100, `?PageSize=` honoured |
| Machine-readable schema | `GET /RS/API/swagger/docs/v1` — Swagger 2.0, public, no auth: 120 paths, 178 operations, 127 definitions |
| Published limits | 1,000 requests per organisation per rolling 24 h; 20,000 per month |

Three ID facts contradict the vendor's own published samples and are the reason the library
resolves every reference from the organisation's own code lists instead of shipping constants:

- Serbia is `CountryId` **3**, not the 192 that vendor examples use. No country with ID 192 exists
  in the 244-row list.
- RSD is `CurrencyId` **2**. **ID 7 is CZK** — the value vendor samples present as the default
  currency. Hardcoding it bills invoices in Czech crowns.
- `VatRateId` and `VatRatePercentage.ID` are separate ID spaces: the 20% rate `S` is `VatRateId` 4
  carrying `VatRatePercentage.ID` 6.

## Approach: generated core, hand-written facade

The Swagger document is committed to the repository as a dated artifact. A repo-local generator
turns it into pydantic models and low-level operation functions, and **the generated output is
committed too**.

This is deliberate. Committed generated code means `git diff` after a spec refresh *is* the
diff of Minimax's API — a free breakage detector. It also keeps the generator out of consumers'
dependency trees and keeps IDE navigation working. The cost is a few thousand lines of code in
the repo that must never be hand-edited.

Rejected alternatives: generating at build time (hides API drift, breaks if the spec host is
down, worse IDE experience); using `openapi-python-client` as-is (foreign ergonomics, and the
lockout and budget rules still have to be written by hand); hand-writing only the modules we
need (leaves 112 paths unreachable and turns every new module into manual work).

## Structure

```
src/minimax_api/
  __init__.py        # MinimaxClient, errors, Region — the entire public surface
  auth.py            # token request, cache, expiry, terminal-failure latch
  transport.py       # httpx wrapper: timeouts, 5xx backoff, the seam for async later
  budget.py          # rolling 24 h / monthly accounting, defer decisions, no sleeping
  errors.py          # exception hierarchy
  pagination.py      # Rows/TotalRows/PageSize envelope -> iterator
  region.py          # RS preset (base_url, scope); seam for SI/HR/BA/ME
  resources/         # hand-written facade: customers, items, issued_invoices, codelists
  _generated/        # models.py, operations.py — machine-written, never hand-edited
spec/swagger-2026-09-21.json   # dated, committed
scripts/generate.py      # spec -> _generated/
scripts/refresh_spec.py  # re-download spec, show the diff
tests/
```

Layering rule: `auth`, `budget`, and `transport` know nothing about business modules;
`resources` knows nothing about HTTP. A reader should be able to understand any one of these
files without opening the others.

## Authentication and the lockout rule

Several consecutive token requests with a wrong password **lock the API application** in
Minimax. Recovery is not a cooldown — the application must be deleted and recreated, which
issues new credentials and requires a redeploy. Retry behaviour is therefore a correctness
requirement, not a politeness one.

- A `400`/`401` from the token endpoint raises `MinimaxAuthError(terminal=True)` and **latches**
  the client: every subsequent call raises the same error without touching the network. Only
  constructing a new client with new credentials clears it.
- Transport failures (timeout, connection reset, 5xx) are a different class and are retryable.
  The distinction is explicit in the code, not implied by an exception type the caller might
  conflate.
- The token cache stores `expires_at = now + expires_in - 60`. The default store is in-process;
  a `TokenStore` protocol (`get`/`set`) lets the connector persist it so concurrent workers
  share one token instead of racing to refresh — a race that multiplies a single bad stored
  password into a lockout in one burst.

## Request budget

The library counts requests against the 1,000-per-rolling-24h and 20,000-per-month limits and,
before issuing a call, either allows it or raises `RateBudgetExceeded(retry_after)`.

It does not sleep. The caller has a database and a scheduler; the library has neither, and a
library that blocks a worker thread for an unknown number of hours is a bug. The counter is
pluggable through the same shape as the token store, defaulting to in-process.

The local counter is an **estimate**, never the truth: other processes and the Minimax UI share
the same organisation budget. A `429` or a server-side rejection always wins and corrects local
state.

## Writes, concurrency, and created IDs

`RowVersion` guards updates. The facade requires the object as just read and raises
`ConcurrencyError` when Minimax rejects the write, with a message stating that the correct
response is re-read and re-evaluate, never a blind replay — a replay silently overwrites
whatever the other actor did.

Create operations return an empty body and the new record's URL in the `Location` header. The
facade parses the ID out and returns it. **Idempotency stays with the caller:** if a process
dies between Minimax committing and the caller persisting that ID, the record exists with no
local trace, and only the caller's intent log can tell a retry from a duplicate.

## Errors

```
MinimaxError
├── MinimaxAuthError(terminal: bool)   # token rejected; terminal=True latches the client
├── RateBudgetExceeded(retry_after)    # local budget or a 429
├── ConcurrencyError                   # RowVersion conflict
├── NotFoundError                      # 404
├── ValidationError                    # 4xx the server explains
└── TransportError                     # timeout, reset, 5xx — retryable
```

Every exception answers one question: may the caller retry this, and when?

## Testing

**Offline core** — `httpx.MockTransport`, no network, runs in CI on every push. It covers the
behaviour where the bugs live: a terminal token failure does not reach the network a second
time; transport failures retry but credential failures do not; an expired token refreshes once
rather than per request; pagination walks `Rows` to `TotalRows`; the budget returns `retry_after`
instead of issuing a request; a `429` overrides the local counter; a `RowVersion` conflict raises
`ConcurrencyError`; the created ID is parsed out of `Location`.

**Contract** — recorded real responses, sanitised of personal data (tax numbers, registration
numbers, addresses, names), replayed through the pydantic models. These catch the spec promising
a field the live API does not return.

**Live** — marked `live`, excluded by default, require a populated `.env`, and issue read-only
code-list calls only. They pin the Serbian ID facts (Serbia = 3, RSD = 2, `S` = 20%) against the
real organisation and cost a handful of the daily 1,000. Run by hand, never in CI.

Pydantic models are permissive (`extra` allowed, non-strict coercion): a response carrying an
unexpected field must not break a caller mid-invoice.

## Packaging and release

`uv` + `hatchling`, src layout, Python 3.12+, matching `limits-watcher` in this organisation.
Runtime dependencies: `httpx`, `pydantic>=2`. CI on 3.12 and 3.13: `ruff`, `mypy`, offline tests.

SemVer, with the README stating plainly that the public facade may change before 1.0. The
generated layer is versioned with its spec: `spec/swagger-<date>.json` plus a CHANGELOG line
recording the API surface date. `scripts/refresh_spec.py` re-downloads and shows the diff;
regenerating is always its own commit, never mixed with hand-written changes. PyPI publication
is manual, triggered by a tag.

MIT licence, matching the other public Coriolis repositories. All documentation in this
repository is written in English.

## Success criteria

1. The connector can authenticate, read code lists, and create a document through this library
   without importing `httpx` or knowing a URL.
2. A wrong password produces exactly one network request, ever.
3. Exceeding the daily budget is a typed, scheduleable outcome rather than a failed write.
4. Refreshing the spec shows API drift as a reviewable diff.
5. No Serbian constant is hardcoded anywhere in the library.
