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
- Ships a `py.typed` marker (PEP 561): the wheel is typed, so a consumer's own mypy checks
  against `minimax_api`'s public models and client instead of treating the package as untyped.

API surface as of **2026-09-21** (`spec/swagger-2026-09-21.json`): 120 paths, 178 operations,
127 definitions.
