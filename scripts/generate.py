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
import textwrap
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
    """The distinguishing tail of a path, e.g. `by_customer_id` or `by_code`.

    Every path in this spec starts `/api/orgs/{organisationId}/<collection>...`,
    so the first four segments (`api`, `orgs`, `{organisationId}`, the collection
    name) never disambiguate a collision — only what follows the collection
    segment does.
    """
    parts = []
    segments = [s for s in path.split("/") if s]
    for segment in segments[4:]:
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


def _operation_id_to_snake_case(operation_id: str) -> str:
    """`Customer_Get` -> `customer_get`.

    `snake_case` inserts its own `_` before every capitalised word, so an
    operationId that already contains a `_` (the vendor's own word separator)
    comes out doubled (`customer__get`). Collapsing repeats afterwards is
    only ever a no-op on `snake_case`'s other callers (property and parameter
    names, which never contain `_`), so this is applied here rather than
    inside the shared helper.
    """
    return re.sub(r"_+", "_", snake_case(operation_id))


def operation_names(document: dict[str, Any]) -> list[str]:
    """Deterministic function names, disambiguated where operationIds collide.

    A colliding operationId (e.g. `Customer_Get`, reused by the collection, the
    by-ID and the by-code routes) is disambiguated by its path tail. That alone
    would leave `Customer_Put` and `Customer_Delete` bare (each operationId is
    individually unique — only `Customer_Get` repeats), even though they sit on
    the exact same `{customerId}` route as the now-suffixed GET. Since callers
    read a resource's operations as a set, silently mixing bare and suffixed
    names across siblings on one URL would be worse than the extra length, so
    a route that hosts any colliding operationId gets its suffix applied to
    every operation on it, not only the colliding one.
    """
    operations = _operations(document)
    candidates = [_operation_id_to_snake_case(op["spec"]["operationId"]) for op in operations]
    counts = Counter(candidates)

    colliding_paths = {
        operation["path"]
        for operation, candidate in zip(operations, candidates, strict=True)
        if counts[candidate] > 1
    }

    names = []
    for operation, candidate in zip(operations, candidates, strict=True):
        if counts[candidate] == 1 and operation["path"] not in colliding_paths:
            names.append(candidate)
            continue
        suffix = _path_suffix(operation["path"])
        names.append(f"{candidate}_{suffix}" if suffix else candidate)

    duplicates = [name for name, count in Counter(names).items() if count > 1]
    if duplicates:
        raise SystemExit(f"operation names are not unique: {duplicates}")
    return names


_BUILTIN_ANNOTATION_WORDS = {"list", "int", "str", "float", "bool", "None", "Any", "SearchResult"}

#: `python_type`'s possible outputs for anything that is not a `$ref` to a
#: generated model. An array body whose item type is one of these cannot be
#: serialised by `_call_lines`'s `item.model_dump(...)` comprehension, so
#: `build_operations` refuses to generate such an operation (see its body-type
#: check) rather than emitting a call that fails at runtime on the first item.
_PRIMITIVE_ANNOTATIONS = {"int", "str", "float", "bool", "Any"}


def _model_names(annotation: str) -> set[str]:
    """Generated model class names referenced by a type annotation.

    Handles compound annotations (`SearchResult[CustomerSearch]`,
    `list[InboxAttachment]`), not just a single bare class name.
    """
    return {
        word
        for word in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", annotation)
        if word not in _BUILTIN_ANNOTATION_WORDS
    }


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


def _docstring_lines(method: str, path: str, operation_id: str) -> list[str]:
    """The one-line docstring for an operation, wrapped across lines if it would
    otherwise exceed the project's line-length limit (a handful of vendor paths
    are long enough that `METHOD /path (operationId X).` alone does not fit)."""
    sentence = f"`{method.upper()} {path}` (operationId `{operation_id}`)."
    one_line = f'    """{sentence}"""'
    if _fits(one_line):
        return [one_line]
    wrapped = textwrap.wrap(
        sentence,
        width=_MAX_LINE_LENGTH,
        initial_indent='    """',
        subsequent_indent="    ",
        break_long_words=False,
        break_on_hyphens=False,
    )
    return [*wrapped, '    """']


def _wrap_path_argument(path: str, *, indent: str) -> list[str]:
    """Split a long `f"..."` path argument at `/` boundaries into adjacent string
    literals, which Python concatenates implicitly. Never splits inside a `{param}`.
    """
    budget = _MAX_LINE_LENGTH - len(indent) - len('f""')
    segments = path.split("/")
    chunks: list[str] = []
    current = ""
    for index, segment in enumerate(segments):
        piece = segment if index == 0 else f"/{segment}"
        if current and len(current) + len(piece) > budget:
            chunks.append(current)
            current = piece
        else:
            current += piece
    chunks.append(current)
    lines = [f'{indent}f"{chunk}"' for chunk in chunks]
    lines[-1] += ","
    return lines


def _call_lines(
    method: str,
    interpolated_path: str,
    *,
    has_params: bool,
    body_type: str | None,
    bind_response: bool,
) -> list[str]:
    """The `transport.request(...)` call, wrapped across lines if it would
    otherwise exceed the project's line-length limit (routes with a body
    parameter regularly do)."""
    if "{" in interpolated_path:
        path_literal = f'f"{interpolated_path}"'
    else:
        path_literal = f'"{interpolated_path}"'
    args = [f'"{method.upper()}"', path_literal]
    if has_params:
        args.append("params=params")
    if body_type and body_type.startswith("list["):
        args.append("json=[item.model_dump(by_alias=True, exclude_none=True) for item in body]")
    elif body_type:
        args.append("json=body.model_dump(by_alias=True, exclude_none=True)")

    target = "    response = " if bind_response else "    "
    one_line = f'{target}transport.request({", ".join(args)})'
    if _fits(one_line):
        return [one_line]

    lines = [f"{target}transport.request("]
    for arg in args:
        arg_line = f"        {arg},"
        if _fits(arg_line):
            lines.append(arg_line)
        else:
            # Only the interpolated path argument is long enough to land here.
            lines.extend(_wrap_path_argument(interpolated_path, indent="        "))
    lines.append("    )")
    return lines


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
                if body_type.startswith("list["):
                    item_type = body_type.removeprefix("list[").removesuffix("]")
                    if item_type in _PRIMITIVE_ANNOTATIONS:
                        raise SystemExit(
                            "generate.py: array body of primitive "
                            f"{item_type!r} is not supported (operationId "
                            f"{spec['operationId']!r}, {method.upper()} {path}). "
                            "The generated call serialises each array item with "
                            "`.model_dump(...)`, which only a generated model "
                            "supports — extend `_call_lines` before regenerating."
                        )
                signature.append(f"body: {body_type}")
                used_models.update(_model_names(body_type))

        has_query = any(parameter["in"] == "query" for parameter in parameters)
        has_params = method == "get" or has_query
        if has_params:
            signature.append("params: Mapping[str, Any] | None = None")

        return_type = _response_type(spec, collisions)
        if return_type:
            used_models.update(_model_names(return_type))
        elif method == "post":
            return_type = "int | None"
        else:
            return_type = "None"

        interpolated = _PATH_PARAM.sub(lambda m: "{" + snake_case(m.group(1)) + "}", path)
        bind_response = return_type != "None"

        lines = [
            "",
            "",
            f"def {name}(",
            "    " + ",\n    ".join(signature) + ",",
            f") -> {return_type}:",
            *_docstring_lines(method, path, spec["operationId"]),
            *_call_lines(
                method,
                interpolated,
                has_params=has_params,
                body_type=body_type,
                bind_response=bind_response,
            ),
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

    import_names = sorted((name for name in used_models if name != "Any"), key=str.casefold)
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
    ]
    if import_names:
        one_line = f"from minimax_api._generated.models import {', '.join(import_names)}"
        if _fits(one_line):
            header.append(one_line)
        else:
            header.append("from minimax_api._generated.models import (")
            header.extend(f"    {name}," for name in import_names)
            header.append(")")
    header.append("from minimax_api.envelope import SearchResult")
    header.append("from minimax_api.transport import Transport")
    return "\n".join(header + bodies) + "\n"


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
    outputs = {
        OUT_DIR / "models.py": build_models(document),
        OUT_DIR / "operations.py": build_operations(document),
    }

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
