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
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any

SPEC_URL = "https://moj.minimax.rs/RS/API/swagger/docs/v1"
SPEC_DIR = Path(__file__).resolve().parent.parent / "spec"

# Free-text fields the generator never reads. Minimax re-indents the HTML in
# them now and then; that is not API drift, so whitespace in them is collapsed
# and dropped between tags before comparing. Rewording still shows up.
PROSE_FIELDS = frozenset({"description", "summary", "title"})
_BETWEEN_TAGS = re.compile(r">\s+<")


def newest_spec() -> Path:
    candidates = sorted(SPEC_DIR.glob("swagger-*.json"))
    if not candidates:
        raise SystemExit("no committed spec found in spec/")
    return candidates[-1]


def fetch() -> dict[str, Any]:
    import ssl

    # Some Python builds cannot verify moj.minimax.rs against their default
    # certificate store, while certifi's bundle works reliably. If certifi is
    # available, use its trust store; otherwise use the system default. This
    # remains optional to avoid adding a runtime dependency.
    context = ssl.create_default_context()
    try:
        import certifi

        context = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        pass

    try:
        with urllib.request.urlopen(SPEC_URL, timeout=60, context=context) as response:
            document = json.loads(response.read().decode("utf-8"))
    except ssl.SSLCertVerificationError as e:
        raise SystemExit(
            f"certificate verification failed: {e}\n"
            "The certificate chain for moj.minimax.rs could not be verified "
            "against your system's trust store.\n"
            "Try running with certifi available: "
            "uv run --with certifi python scripts/refresh_spec.py"
        ) from e

    return document  # type: ignore[no-any-return]


def dump(document: Any) -> str:
    return json.dumps(document, ensure_ascii=False, indent=1, sort_keys=True) + "\n"


def _collapse_whitespace(text: str) -> str:
    return _BETWEEN_TAGS.sub("><", " ".join(text.split()))


def _collapse_prose(node: Any) -> Any:
    if isinstance(node, dict):
        return {
            key: _collapse_whitespace(value)
            if key in PROSE_FIELDS and isinstance(value, str)
            else _collapse_prose(value)
            for key, value in node.items()
        }
    if isinstance(node, list):
        return [_collapse_prose(item) for item in node]
    return node


def spec_diff(committed: Any, live: Any, *, fromfile: str) -> list[str]:
    """Unified diff between two Swagger documents, ignoring prose whitespace."""
    return list(
        difflib.unified_diff(
            dump(_collapse_prose(committed)).splitlines(keepends=True),
            dump(_collapse_prose(live)).splitlines(keepends=True),
            fromfile=fromfile,
            tofile="live",
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="only report whether the spec changed")
    args = parser.parse_args()

    current = newest_spec()
    live = fetch()
    diff = spec_diff(json.loads(current.read_text()), live, fromfile=current.name)

    if not diff:
        print(f"No change: {current.name} matches the live API surface.")
        return 0

    sys.stdout.writelines(diff[:400])
    if len(diff) > 400:
        print(f"... {len(diff) - 400} more diff lines")

    if args.check:
        return 1

    target = SPEC_DIR / f"swagger-{dt.date.today().isoformat()}.json"
    target.write_text(dump(live))
    print(f"\nWrote {target.name}. Next: regenerate and commit that on its own.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
