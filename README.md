# minimax-api

Python client for the **Minimax** (Saop) accounting REST API — the ERP used in Serbia, Slovenia,
Croatia, Bosnia and Montenegro.

> This is **not** the MiniMax AI platform. If you are looking for the Chinese LLM vendor, you
> want a different package.

Serbia is the verified deployment. Other countries are a configuration change, not a code
change, but they are untested here.

## Install

Not on PyPI yet — install from the repository:

```bash
pip install git+https://github.com/Coriol-is/minimax-python@v0.1.0
```

or take the wheel attached to a [release](https://github.com/Coriol-is/minimax-python/releases).

## Use

```python
from minimax_api import Credentials, MinimaxClient
from minimax_api.models import Customer, FkField

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
    if rsd is None or serbia is None:
        raise RuntimeError("this organisation's code lists do not contain RSD or RS")

    customer_id = client.customers.create(
        Customer(
            name="ACME d.o.o.",
            address="Example Street 1",
            postal_code="11000",
            city="Beograd",
            country=FkField(id=serbia.country_id),
            currency=FkField(id=rsd.currency_id),
            subject_to_vat="D",
            e_invoice_issuing="SeNePripravlja",
        )
    )
```

Models are pydantic: their fields take Python names (`customer_id`, `subject_to_vat`), never the
wire's PascalCase (`CustomerId`, `SubjectToVAT`) as keyword arguments — that spelling is rejected
by both pydantic's runtime validation and, by design, by mypy. Nested references such as
`country` and `currency` are typed `FkField | None`, not a plain `dict`; construct them with
`FkField(id=...)` rather than `{"ID": ...}`.

## Credentials

Minimax splits credentials in two, and both halves arrive through different channels:

| Half | Contents | Who creates it |
|---|---|---|
| Client | `client_id`, `client_secret` | Minimax support, on request — there is no self-service |
| User | `username`, `password` | The subscriber, in *Moj profil → Lozinke za pristup spoljnim aplikacijama* |

A third thing is required: the subscriber's administrator must grant the API right to that user
**on the target organisation**. Without it, authentication succeeds and `organisations()` returns
an empty list.

## Behaviours worth knowing

**A wrong password is never retried.** Several consecutive credential rejections lock the Minimax
application, and recovery means deleting and recreating it. The first rejection latches the
client: every later call raises without touching the network.

**The request budget is a typed outcome, not a failure.** Minimax allows 1,000 requests per
organisation per rolling 24 hours (and 20,000 per month). When the budget is spent, the client
raises `RateBudgetExceeded` carrying `retry_after` — it never sleeps. Scheduling is yours.

**Nothing is assumed about IDs.** The vendor's published examples give `Country.ID` 192 for
Serbia and `Currency.ID` 7 as a default. In a real Serbian organisation, Serbia is 3, RSD is 2,
and **7 is the Czech koruna**. Resolve every reference from the organisation's own code lists.

**The lockout latch and the rate-limit penalty are both process-local.** The credential-rejection
latch lives on one `Authenticator` instance, and the 429 penalty lives on one `Budget` instance —
neither travels through a shared `TokenStore` or `BudgetStore`. If you run multiple workers or
processes against the same organisation, a bad password or a spent budget known to one process is
invisible to the others: a separate process constructing its own client with the same bad
password will issue its own token request (and can contribute to the same lockout), and a sibling
process can keep sending requests after another process has been told to back off. Sharing a
`TokenStore`/`BudgetStore` implementation across processes (e.g. backed by a database) avoids
racing to refresh a token, but it does not make the lockout latch or the rate-limit penalty
itself shared — read the docstrings on `TokenStore` and `Budget.penalize` before deploying more
than one worker.

## What this library does not do

Idempotency keys, queues, persistence, reconciliation, and webhook handling. A created record's
ID arrives only in the `Location` header, so if your process dies between Minimax committing and
you persisting that ID, the record exists with no local trace. Record the intent to write before
calling and reconcile by search after an unknown outcome — that needs a database, which a client
library has no business owning.

One thing to know before you rely on that reconciliation: **Minimax's search methods filter on
fewer fields than you might assume.** `GetIssuedInvoicePostings`, for instance, filters only on
`DateFrom`, `DateTo`, `Description`, `Status` and `AnalyticID` — there is no document-number
filter. So a reference you intend to search by later has to be written into a field the search
actually accepts, typically `Description`. Decide that before your first write, not after your
first lost response.

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

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow, and
[SECURITY.md](SECURITY.md) for how credentials are handled and what to report privately.

A weekly CI job asks the vendor's public Swagger endpoint whether the API surface still matches
the document in `spec/`, so drift arrives as a failed build rather than as a production surprise.

## Versioning

SemVer, with one caveat: before 1.0 the public facade may change. The generated layer is
versioned with the spec it came from — see `spec/` and the CHANGELOG.

## Licence

MIT.
