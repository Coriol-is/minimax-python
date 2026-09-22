# Contributing

Thanks for looking. This library talks to a real accounting system, so a few of
its rules are stricter than they would be elsewhere — the ones below exist
because getting them wrong costs somebody money or locks their account.

## Setup

```bash
uv sync --all-groups
uv run pytest          # offline, no network, ~0.2s
uv run ruff check .
uv run mypy src tests
```

CI runs exactly those on Python 3.12 and 3.13, plus a build check and a
staleness check on the generated code.

## The generated layer

`src/minimax_api/_generated/` is machine-written from the vendor's Swagger
document and **must never be hand-edited**. If its output is wrong, fix
`scripts/generate.py` and regenerate:

```bash
uv run python scripts/generate.py          # rewrite _generated/
uv run python scripts/generate.py --check  # fail if the committed output is stale (CI runs this)
```

The generated output is committed on purpose. A regenerated diff is then a
readable report on what Minimax changed, consumers do not need the generator
installed, and IDE navigation works.

## When Minimax changes its API

```bash
uv run python scripts/refresh_spec.py --check  # has the live surface moved?
uv run python scripts/refresh_spec.py          # write a new dated spec/ file and show the diff
```

A weekly CI job runs the `--check` form, so drift shows up as a red build.

Refreshing the spec and regenerating belongs in **its own commit**, separate
from hand-written changes, so that the diff reads as a report on the vendor.

## Things this library will not do

Keep these in mind before proposing a change; each is a deliberate decision, not
an oversight:

- **A rejected credential is never retried.** Several consecutive credential
  failures lock the customer's Minimax application, and recovery means deleting
  and recreating it. The first rejection latches the client permanently.
- **`POST` is never retried automatically.** A write whose response was lost may
  or may not have happened; resending it would duplicate an invoice in someone's
  ledger. Such an outcome surfaces as `AmbiguousWriteError`, which tells the
  caller to reconcile by search. (The single exception — one resend after a
  `401` — is commented where it happens: a 401 is a definitive refusal, so
  nothing was written.)
- **The library never sleeps for the rate budget.** It raises
  `RateBudgetExceeded(retry_after=...)` and lets the caller schedule, because
  the caller has a scheduler and this does not.
- **No reference ID is hardcoded.** The vendor's own examples give Serbia as
  `Country.ID` 192 and 7 as the default currency; in a real Serbian organisation
  Serbia is 3, RSD is 2, and 7 is the Czech koruna. Every ID is resolved from
  the organisation's own code list.

## Tests

Three tiers:

- **Offline** — `httpx.MockTransport`, no network, run on every push. This is
  where almost everything belongs.
- **Contract** — recorded real responses, sanitised of personal data. This tier
  does not exist yet; it needs a populated organisation. Adding it is welcome.
- **Live** — marked `live`, excluded by default, requires real credentials in
  `.env`.

```bash
uv run pytest -m live
```

**Read this before running live tests.** They issue real API calls against a
real organisation and spend from its budget of 1,000 requests per rolling 24
hours. If a credential is wrong, the token request that fails counts toward
locking the API application. Run them deliberately, never in a loop, and never
in CI.

Coverage has a floor of 95% on the hand-written layers (`uv run pytest --cov`).

## Style

Line length 100, `ruff` for lint and import order, `mypy --strict`. Comments
explain *why*, not *what* — if a line looks odd, the comment should say which
vendor behaviour forced it.
