# Security

## Reporting a vulnerability

Report privately through GitHub's [security advisory
form](https://github.com/Coriol-is/minimax-python/security/advisories/new) for
this repository. Please do not open a public issue for anything that could be
used against a live accounting system before it is fixed.

Include what you can: affected version, what an attacker can achieve, and the
smallest reproduction you have. You will get an acknowledgement; this is a small
project, so expect days rather than hours.

## What counts as a vulnerability here

Beyond the obvious, this library has two failure modes worth reporting even if
they look like ordinary bugs, because their consequences land on a third party's
accounting data:

- **Anything that causes a rejected credential to be retried.** Several
  consecutive credential failures lock the customer's Minimax API application,
  and recovery requires deleting and recreating it. A path that defeats the
  latch is a denial of service against the user's own account.
- **Anything that causes a non-idempotent write to be repeated.** A duplicated
  `POST` means a duplicated invoice in a real ledger.

Also in scope: any path that puts a client secret, user password, or access
token into an exception message, log line, `repr`, or traceback.

## Credentials

This library never stores credentials anywhere but in the process that
constructs a `Credentials` object, plus whatever `TokenStore` the caller
supplies. It writes no files and logs nothing.

- `Credentials` and `Token` hide their secret fields from `repr`, so an
  incidental log line or traceback does not spill them.
- `.env` is gitignored; only `.env.example`, which holds empty placeholders, is
  committed. Never commit real values — a leaked API user password is remediated
  by deleting and recreating the API application in *Moj profil*.
- Access tokens live 3600 seconds. A `TokenStore` backed by a database should be
  treated as holding a credential.

## Supported versions

Pre-1.0: only the latest release gets fixes.
