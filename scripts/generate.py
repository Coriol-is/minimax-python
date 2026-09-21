#!/usr/bin/env python3
"""Generate `minimax_api._generated` from the committed Swagger document.

The output is committed. That is deliberate: a regenerated diff is a readable
report on what Minimax changed, consumers do not need this script installed,
and IDE navigation works. Never hand-edit the output — change this script and
regenerate.

Naming rule (`class_name`):
  - `SAOP.API.Common.mMApiFkField` is renamed `FkField` (`SPECIAL_CLASS_NAMES`);
    every other definition keeps its vendor leaf name (the segment after the
    last `.`, generic parameter stripped).
  - If a leaf name is unique among all non-`SearchResult[...]` definitions, it
    is used as-is.
  - If it collides with another definition's leaf name, it is disambiguated:
      * Generic definitions (`Namespace.Base[Namespace.Param]`) are
        disambiguated by their type PARAMETER's leaf name, e.g. three
        `Dashboard.Chart[...]` widgets become `AgregateInvoiceChart`,
        `DashboardCustomerChart`, `DashboardMonthChart`. The parent namespace
        segment is *not* used here because colliding generic instantiations
        of the same base are typically declared in the same namespace, so the
        segment would be identical for all of them and would not break the
        tie (this happened once: three `Chart[...]` widgets and two
        `ListResult[...]` instantiations collapsed onto one class name each,
        silently dropping two definitions — see git history on this file).
      * Non-generic definitions are disambiguated by prefixing the preceding
        namespace segment, e.g. `Dashboard.Chart` / `Report.Chart` ->
        `DashboardChart` / `ReportChart`.
  - Known limitation: two generic families in *different* namespaces that
    share both their base leaf name and their type parameter's leaf name
    would still collide (e.g. `Foo.Widget[Foo.Bar]` and `Baz.Widget[Foo.Bar]`
    both resolve to `BarWidget`). No such case exists in the spec this
    generator has been run against. Rather than silently merging two
    definitions into one class again, `build_models` fails loudly
    (`SystemExit`) if the naming rule ever produces a duplicate class name —
    see `tests/test_generator_models.py` for the tests that pin this.

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

_PRIMITIVES: dict[tuple[str | None, str | None], str] = {
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
    if name not in collisions:
        return name

    base, _, generic = definition.partition("[")
    if generic:
        # A handful of definitions are themselves generic (e.g. three
        # `Dashboard.Chart[...]` widgets sharing one namespace) — the type
        # parameter is what actually distinguishes them, so the namespace
        # segment alone would still collide.
        return f"{leaf(generic.rstrip(']'))}{name}"

    segments = base.split(".")
    parent = segments[-2] if len(segments) > 1 else ""
    return f"{parent}{name}"


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

    kind: str | None = schema.get("type")
    if kind == "array":
        return f"list[{python_type(schema.get('items', {}), collisions)}]"

    fmt: str | None = schema.get("format")
    mapped = _PRIMITIVES.get((kind, fmt)) or _PRIMITIVES.get((kind, None))
    # Anything unmapped stays `Any`: guessing a narrower type would reject
    # payloads the live API actually sends.
    return mapped or "Any"


#: The project's ruff line-length (see `[tool.ruff]` in pyproject.toml). The
#: generated file is linted like any other source file, so a field whose
#: single-line form would exceed it is wrapped instead.
_MAX_LINE_LENGTH = 100


def _fits(candidate: str) -> bool:
    return all(len(line) <= _MAX_LINE_LENGTH for line in candidate.splitlines())


def field_line(prop: str, schema: dict[str, Any], collisions: set[str]) -> str:
    annotation = python_type(schema, collisions)
    attribute = snake_case(prop)
    if attribute in {"id", "type", "format"} and prop != "ID":
        attribute = f"{attribute}_"

    # Long vendor names (deeply nested definitions, in particular) can push a
    # single-line field past the project's line-length limit. Try increasingly
    # aggressive wrappings — matching how a formatter would break the same
    # code — and use the first one that fits.
    candidates = [
        f'    {attribute}: {annotation} | None = Field(default=None, alias="{prop}")',
        (
            f"    {attribute}: {annotation} | None = Field(\n"
            f'        default=None, alias="{prop}"\n'
            "    )"
        ),
        (
            f"    {attribute}: (\n"
            f"        {annotation} | None\n"
            f'    ) = Field(default=None, alias="{prop}")'
        ),
        (
            f"    {attribute}: (\n"
            f"        {annotation} | None\n"
            "    ) = Field(\n"
            f'        default=None, alias="{prop}"\n'
            "    )"
        ),
    ]
    for candidate in candidates:
        if _fits(candidate):
            return candidate
    return candidates[-1]


def build_models(document: dict[str, Any]) -> str:
    definitions = document["definitions"]
    collisions = find_collisions(definitions)

    body: list[str] = []
    class_names: list[str] = []
    #: Every definition that produced a given class name, so a collision the
    #: naming rule failed to break can be reported precisely instead of one
    #: definition silently overwriting another's class.
    sources_by_name: dict[str, list[str]] = {}
    for definition in sorted(definitions):
        if definition.startswith("SAOP.API.Models.SearchResult["):
            continue
        schema = definitions[definition]
        name = class_name(definition, collisions=collisions)
        class_names.append(name)
        sources_by_name.setdefault(name, []).append(definition)
        properties: dict[str, Any] = schema.get("properties", {})

        body.append("")
        body.append(f"class {name}(MinimaxModel):")
        body.append(f'    """`{definition}`"""')
        body.append("")
        if not properties:
            body.append("    pass")
            continue
        for prop, prop_schema in properties.items():
            body.append(field_line(prop, prop_schema, collisions))

    # A naming-rule gap must never fall back to Python's "last definition
    # wins" class redefinition: that is exactly how a 3-way and a 2-way
    # collision were once silently collapsed into one class each (see the
    # module docstring). Anything not fully disambiguated by `class_name`
    # is a bug in the naming rule, and generation must fail loudly on it.
    duplicates = {n: s for n, s in sources_by_name.items() if len(s) > 1}
    if duplicates:
        report = "; ".join(
            f"{name!r} <- {', '.join(sources)}" for name, sources in sorted(duplicates.items())
        )
        raise SystemExit(
            "generate.py: naming rule produced duplicate class name(s), "
            f"which would silently merge distinct definitions: {report}"
        )

    # `from __future__ import annotations` makes every annotation a lazily
    # evaluated string, so a class referencing another one declared later
    # (alphabetically, by definition name) would otherwise be left
    # "not fully defined". Rebuilding after every class exists resolves all
    # forward references regardless of declaration order or import context.
    if class_names:
        body.append("")
        for name in class_names:
            body.append(f"{name}.model_rebuild()")
    body.append("")

    # `Any` is only needed when a field's type could not be mapped; importing
    # it unconditionally would leave an unused import on specs where every
    # property happens to be mapped.
    uses_any = re.search(r"\bAny\b", "\n".join(body)) is not None

    header = [
        '"""Models generated from the Minimax Swagger document. Do not edit.',
        "",
        "Regenerate with `uv run python scripts/generate.py`.",
        "",
        "Generic collection-envelope definitions are skipped: `minimax_api.envelope`",
        "already covers every one of them. `mMApiFkField` is renamed `FkField`.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
    ]
    if uses_any:
        header += ["from typing import Any", ""]
    header += [
        "from pydantic import Field",
        "",
        "from minimax_api.envelope import MinimaxModel",
        "",
    ]

    return "\n".join(header + body)


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
