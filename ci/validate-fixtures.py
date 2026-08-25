#!/usr/bin/env python3
"""Validate the static shape of the shared FFE fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import NoReturn


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPOSITORY_ROOT / "ufc-config.json"
EVALUATION_CASES_DIRECTORY = REPOSITORY_ROOT / "evaluation-cases"
VALID_VARIATION_TYPES = frozenset({"BOOLEAN", "INTEGER", "JSON", "NUMERIC", "STRING"})
REQUIRED_CASE_FIELDS = frozenset(
    {
        "attributes",
        "defaultValue",
        "flag",
        "result",
        "targetingKey",
        "variationType",
    }
)


class FixtureValidationError(ValueError):
    """A fixture is syntactically valid JSON but violates the repository shape."""


def _relative(path: Path) -> Path:
    return path.relative_to(REPOSITORY_ROOT)


def _fail(path: Path, message: str) -> NoReturn:
    raise FixtureValidationError(f"{_relative(path)}: {message}")


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise FixtureValidationError(f"duplicate object key {key!r}")
        result[key] = value
    return result


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_keys)
    except json.JSONDecodeError as error:
        _fail(path, f"invalid JSON at line {error.lineno}, column {error.colno}: {error.msg}")
    except FixtureValidationError as error:
        _fail(path, str(error))


def _validate_config(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        _fail(CONFIG_PATH, "top-level value must be an object")

    if not isinstance(value.get("createdAt"), str) or not value["createdAt"]:
        _fail(CONFIG_PATH, "top-level createdAt must be a non-empty string")
    if not isinstance(value.get("format"), str) or not value["format"]:
        _fail(CONFIG_PATH, "top-level format must be a non-empty string")
    environment = value.get("environment")
    if not isinstance(environment, dict):
        _fail(CONFIG_PATH, "top-level environment must be an object")
    if not isinstance(environment.get("name"), str) or not environment["name"]:
        _fail(CONFIG_PATH, "environment.name must be a non-empty string")

    flags = value.get("flags")
    if not isinstance(flags, dict):
        _fail(CONFIG_PATH, "top-level flags must be an object")
    if not flags:
        _fail(CONFIG_PATH, "top-level flags must not be empty")

    for flag_name, flag_value in flags.items():
        if not isinstance(flag_name, str) or not flag_name:
            _fail(CONFIG_PATH, "every flag map key must be a non-empty string")
        if not isinstance(flag_value, dict):
            _fail(CONFIG_PATH, f"flag {flag_name!r} must be an object")
        if flag_value.get("key") != flag_name:
            _fail(CONFIG_PATH, f"flag {flag_name!r} must repeat its map key in the key field")

        variations = flag_value.get("variations")
        if not isinstance(variations, dict):
            _fail(CONFIG_PATH, f"flag {flag_name!r} variations must be an object")
        for variation_name, variation_value in variations.items():
            if not isinstance(variation_value, dict):
                _fail(CONFIG_PATH, f"flag {flag_name!r} variation {variation_name!r} must be an object")
            if variation_value.get("key") != variation_name:
                _fail(
                    CONFIG_PATH,
                    f"flag {flag_name!r} variation {variation_name!r} must repeat its map key in the key field",
                )

        if "allocations" not in flag_value:
            _fail(CONFIG_PATH, f"flag {flag_name!r} must declare allocations")

    return flags


def _validate_evaluation_case(
    path: Path,
    index: int,
    value: object,
    configured_flags: dict[str, object],
) -> None:
    location = f"case {index}"
    if not isinstance(value, dict):
        _fail(path, f"{location} must be an object")

    missing_fields = sorted(REQUIRED_CASE_FIELDS.difference(value))
    if missing_fields:
        _fail(path, f"{location} is missing required fields: {', '.join(missing_fields)}")

    flag = value["flag"]
    if not isinstance(flag, str) or not flag:
        _fail(path, f"{location} flag must be a non-empty string")

    variation_type = value["variationType"]
    if not isinstance(variation_type, str) or variation_type not in VALID_VARIATION_TYPES:
        _fail(
            path,
            f"{location} variationType must be one of {', '.join(sorted(VALID_VARIATION_TYPES))}",
        )

    targeting_key = value["targetingKey"]
    if targeting_key is not None and not isinstance(targeting_key, str):
        _fail(path, f"{location} targetingKey must be a string or null")

    if not isinstance(value["attributes"], dict):
        _fail(path, f"{location} attributes must be an object")

    result = value["result"]
    if not isinstance(result, dict):
        _fail(path, f"{location} result must be an object")
    if "value" not in result:
        _fail(path, f"{location} result must include value")
    if not isinstance(result.get("reason"), str) or not result["reason"]:
        _fail(path, f"{location} result.reason must be a non-empty string")

    error_code = result.get("errorCode")
    if result["reason"] == "ERROR":
        if not isinstance(error_code, str) or not error_code:
            _fail(path, f"{location} result.errorCode is required when result.reason is ERROR")
    elif "errorCode" in result:
        _fail(path, f"{location} result.errorCode is only valid when result.reason is ERROR")

    if flag not in configured_flags and result.get("errorCode") != "FLAG_NOT_FOUND":
        _fail(
            path,
            f"{location} references unknown flag {flag!r} without a FLAG_NOT_FOUND expectation",
        )


def main() -> None:
    configured_flags = _validate_config(_load_json(CONFIG_PATH))

    evaluation_paths = sorted(EVALUATION_CASES_DIRECTORY.glob("*.json"))
    if not evaluation_paths:
        _fail(EVALUATION_CASES_DIRECTORY, "must contain at least one JSON file")

    case_count = 0
    for path in evaluation_paths:
        cases = _load_json(path)
        if not isinstance(cases, list):
            _fail(path, "top-level value must be an array")
        if not cases:
            _fail(path, "evaluation-case array must not be empty")

        for index, case in enumerate(cases):
            _validate_evaluation_case(path, index, case, configured_flags)
            case_count += 1

    print(
        f"Validated {_relative(CONFIG_PATH)} and {case_count} evaluation cases "
        f"across {len(evaluation_paths)} files."
    )


if __name__ == "__main__":
    try:
        main()
    except FixtureValidationError as error:
        raise SystemExit(f"fixture validation failed: {error}") from error
