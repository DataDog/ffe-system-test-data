#!/usr/bin/env python3
"""Validate the static shape of the flag selection vectors."""

from __future__ import annotations

import json
from pathlib import Path
from typing import NoReturn


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VECTORS_PATH = REPOSITORY_ROOT / "flag-selection" / "selection-vectors.json"
QUERY_PARAMETERS = frozenset({"selected_flag_tags", "selected_flag_key_patterns"})
IGNORED_REASONS = frozenset({"malformed_selection", "too_many_values", "invalid_key_pattern", "invalid_tag"})


class VectorValidationError(ValueError):
    """The vectors file is valid JSON but violates the documented format."""


def _fail(message: str) -> NoReturn:
    raise VectorValidationError(f"{VECTORS_PATH.relative_to(REPOSITORY_ROOT)}: {message}")


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise VectorValidationError(f"duplicate object key {key!r}")
        result[key] = value
    return result


def _load() -> object:
    try:
        return json.loads(VECTORS_PATH.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_keys)
    except json.JSONDecodeError as error:
        _fail(f"invalid JSON at line {error.lineno}, column {error.colno}: {error.msg}")
    except VectorValidationError as error:
        _fail(str(error))


def _is_string_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _check_keys(location: str, value: dict[str, object], required: set[str], optional: set[str]) -> None:
    missing = sorted(required.difference(value))
    if missing:
        _fail(f"{location} is missing {', '.join(missing)}")
    unknown = sorted(set(value).difference(required, optional))
    if unknown:
        _fail(f"{location} has unknown fields {', '.join(unknown)}")


def _validate_flags(value: object) -> set[str]:
    if not isinstance(value, list) or not value:
        _fail("flags must be a non-empty array")
    keys: set[str] = set()
    for index, flag in enumerate(value):
        location = f"flags[{index}]"
        if not isinstance(flag, dict):
            _fail(f"{location} must be an object")
        _check_keys(location, flag, {"key", "tags"}, set())
        if not isinstance(flag["key"], str):
            _fail(f"{location}.key must be a string")
        if flag["key"] in keys:
            _fail(f"{location}.key {flag['key']!r} is repeated")
        if not _is_string_list(flag["tags"]):
            _fail(f"{location}.tags must be an array of strings")
        keys.add(flag["key"])
    return keys


def _validate_case(index: int, case: object, flag_keys: set[str]) -> str:
    location = f"cases[{index}]"
    if not isinstance(case, dict):
        _fail(f"{location} must be an object")
    _check_keys(location, case, {"name", "expected"}, {"query", "rawQuery", "sdk"})
    if not isinstance(case["name"], str) or not case["name"]:
        _fail(f"{location}.name must be a non-empty string")
    location = f"case {case['name']!r}"

    if ("query" in case) == ("rawQuery" in case):
        _fail(f"{location} must have exactly one of query or rawQuery")
    if "query" in case:
        query = case["query"]
        if not isinstance(query, dict):
            _fail(f"{location} query must be an object")
        for name, values in query.items():
            if name not in QUERY_PARAMETERS:
                _fail(f"{location} query has unknown parameter {name!r}")
            if not _is_string_list(values):
                _fail(f"{location} query.{name} must be an array of strings")
    elif not isinstance(case["rawQuery"], str):
        _fail(f"{location} rawQuery must be a string")

    expected = case["expected"]
    if not isinstance(expected, dict):
        _fail(f"{location} expected must be an object")
    outcome = expected.get("outcome")
    if outcome == "ignored":
        _check_keys(f"{location} expected", expected, {"outcome", "reason"}, set())
        if expected["reason"] not in IGNORED_REASONS:
            _fail(f"{location} expected.reason must be one of {', '.join(sorted(IGNORED_REASONS))}")
    elif outcome == "applied":
        _check_keys(f"{location} expected", expected, {"outcome", "selectedKeys"}, set())
        selected = expected["selectedKeys"]
        if not _is_string_list(selected):
            _fail(f"{location} expected.selectedKeys must be an array of strings")
        if selected != sorted(set(selected)):
            _fail(f"{location} expected.selectedKeys must be sorted and distinct")
        unknown = sorted(set(selected).difference(flag_keys))
        if unknown:
            _fail(f"{location} expected.selectedKeys names unknown flags {', '.join(unknown)}")
    else:
        _fail(f"{location} expected.outcome must be applied or ignored")

    if "query" in case:
        if "sdk" not in case:
            _fail(f"{location} must have sdk, because every query case also runs as an SDK selection")
        _validate_sdk(location, case["sdk"], expected)
    elif "sdk" in case:
        _fail(f"{location} sdk is not allowed on a rawQuery case")
    return case["name"]


def _validate_sdk(location: str, sdk: object, expected: dict[str, object]) -> None:
    if not isinstance(sdk, dict) or len(sdk) != 1 or not set(sdk) <= {"selection", "dropped"}:
        _fail(f"{location} sdk must be an object with exactly one of selection or dropped")
    if "dropped" in sdk:
        if expected["outcome"] != "ignored" or sdk["dropped"] != expected["reason"]:
            _fail(f"{location} sdk.dropped must equal expected.reason of an ignored case")
        return

    if expected["outcome"] != "applied":
        _fail(f"{location} sdk.selection requires an applied case")
    selection = sdk["selection"]
    if not isinstance(selection, dict):
        _fail(f"{location} sdk.selection must be an object")
    _check_keys(f"{location} sdk.selection", selection, {"tags", "keyPatterns"}, set())
    for name in ("tags", "keyPatterns"):
        values = selection[name]
        if not _is_string_list(values) or not all(values):
            _fail(f"{location} sdk.selection.{name} must be an array of non-empty strings")
        if values != sorted(set(values), key=lambda value: value.encode("utf-8", "surrogatepass")):
            _fail(f"{location} sdk.selection.{name} must be sorted by UTF-8 bytes and distinct")


def main() -> None:
    vectors = _load()
    if not isinstance(vectors, dict):
        _fail("top-level value must be an object")
    _check_keys("top-level object", vectors, {"flags", "cases"}, set())
    flag_keys = _validate_flags(vectors["flags"])

    cases = vectors["cases"]
    if not isinstance(cases, list) or not cases:
        _fail("cases must be a non-empty array")
    names: set[str] = set()
    for index, case in enumerate(cases):
        name = _validate_case(index, case, flag_keys)
        if name in names:
            _fail(f"case name {name!r} is repeated")
        names.add(name)

    print(f"Validated {len(cases)} flag selection vectors against {len(flag_keys)} flags.")


if __name__ == "__main__":
    try:
        main()
    except VectorValidationError as error:
        raise SystemExit(f"flag selection validation failed: {error}") from error
