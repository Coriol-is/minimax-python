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
- Non-idempotent writes are never retried: a `POST` whose outcome is unknown raises
  `AmbiguousWriteError` telling the caller to reconcile by search, rather than risking a
  duplicate document. Token acquisition and budget accounting are thread-safe, so a pool of
  workers sharing one client cannot turn one bad password into a burst of rejected token
  requests.
- Ships a `py.typed` marker (PEP 561): the wheel is typed, so a consumer's own mypy checks
  against `minimax_api`'s public models and client instead of treating the package as untyped.
- Packaging follows current standards: PEP 639 licence expression, Trove classifiers, and an
  sdist carrying the vendored spec and the generator, so the client can be regenerated from a
  source release alone.
- CI builds and installs the wheel on every change, validates package metadata, and checks
  weekly whether Minimax's live API surface still matches the committed spec.

API surface as of **2026-09-21** (`spec/swagger-2026-09-21.json`): 120 paths, 178 operations,
127 definitions.
