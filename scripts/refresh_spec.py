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
    import ssl
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(SPEC_URL, timeout=60, context=context) as response:
        document = json.loads(response.read().decode("utf-8"))
    return json.dumps(document, ensure_ascii=False, indent=1, sort_keys=True) + "\n"


def normalise(path: Path) -> str:
    doc = json.loads(path.read_text())
    return json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True) + "\n"


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
