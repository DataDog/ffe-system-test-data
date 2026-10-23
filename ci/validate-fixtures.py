#!/usr/bin/env python3
"""Validate the static shape of the shared FFE fixtures."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import NoReturn


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPOSITORY_ROOT / "ufc-config.json"
EVALUATION_CASES_DIRECTORY = REPOSITORY_ROOT / "evaluation-cases"
EVALUATION_SUITES_DIRECTORY = REPOSITORY_ROOT / "evaluation-suites"
SUITE_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CANONICAL_PLATFORMS = frozenset(
    {"cpp", "dotnet", "golang", "java", "nodejs", "php", "python", "ruby", "rust", "web"}
)
VALID_VARIATION_TYPES = frozenset({"BOOLEAN", "INTEGER", "JSON", "NUMERIC", "STRING"})
FEATURE_DESTINATIONS = frozenset({"HOOK", "EXPOSURE", "EVALUATION"})
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
    try:
        return path.relative_to(REPOSITORY_ROOT)
    except ValueError:
        return path


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


def _validate_config(path: Path, value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        _fail(path, "top-level value must be an object")

    if not isinstance(value.get("createdAt"), str) or not value["createdAt"]:
        _fail(path, "top-level createdAt must be a non-empty string")
    if not isinstance(value.get("format"), str) or not value["format"]:
        _fail(path, "top-level format must be a non-empty string")
    environment = value.get("environment")
    if not isinstance(environment, dict):
        _fail(path, "top-level environment must be an object")
    if not isinstance(environment.get("name"), str) or not environment["name"]:
        _fail(path, "environment.name must be a non-empty string")

    flags = value.get("flags")
    if not isinstance(flags, dict):
        _fail(path, "top-level flags must be an object")
    if not flags:
        _fail(path, "top-level flags must not be empty")

    for flag_name, flag_value in flags.items():
        if not isinstance(flag_name, str) or not flag_name:
            _fail(path, "every flag map key must be a non-empty string")
        if not isinstance(flag_value, dict):
            _fail(path, f"flag {flag_name!r} must be an object")
        if flag_value.get("key") != flag_name:
            _fail(path, f"flag {flag_name!r} must repeat its map key in the key field")

        variations = flag_value.get("variations")
        if not isinstance(variations, dict):
            _fail(path, f"flag {flag_name!r} variations must be an object")
        for variation_name, variation_value in variations.items():
            if not isinstance(variation_value, dict):
                _fail(path, f"flag {flag_name!r} variation {variation_name!r} must be an object")
            if variation_value.get("key") != variation_name:
                _fail(
                    path,
                    f"flag {flag_name!r} variation {variation_name!r} must repeat its map key in the key field",
                )

        if "allocations" not in flag_value:
            _fail(path, f"flag {flag_name!r} must declare allocations")

    return flags


def _validate_platform_filter(
    path: Path,
    location: str,
    value: dict[str, object],
    platforms: frozenset[str],
) -> None:
    if "_skip" in value and "_include" in value:
        _fail(path, f"{location} _skip and _include are mutually exclusive")

    for field in ("_skip", "_include"):
        if field not in value:
            continue
        entries = value[field]
        if not isinstance(entries, list) or not entries:
            _fail(path, f"{location} {field} must be a non-empty array")
        seen: set[str] = set()
        for entry_index, entry in enumerate(entries):
            entry_location = f"{location} {field}[{entry_index}]"
            if not isinstance(entry, dict):
                _fail(path, f"{entry_location} must be an object")
            unexpected = sorted(set(entry).difference({"platform", "reason"}))
            if unexpected:
                _fail(path, f"{entry_location} has unexpected fields: {', '.join(unexpected)}")
            platform = entry.get("platform")
            if not isinstance(platform, str) or platform not in platforms:
                _fail(path, f"{entry_location}.platform must be a canonical platform")
            if platform in seen:
                _fail(path, f"{location} {field} repeats platform {platform!r}")
            seen.add(platform)
            if "reason" in entry and (not isinstance(entry["reason"], str) or not entry["reason"]):
                _fail(path, f"{entry_location}.reason must be a non-empty string")


def _validate_evaluation_case(
    path: Path,
    index: int,
    value: object,
    configured_flags: dict[str, object],
    platforms: frozenset[str] | None = None,
) -> None:
    location = f"case {index}"
    if not isinstance(value, dict):
        _fail(path, f"{location} must be an object")

    if platforms is None:
        platforms = CANONICAL_PLATFORMS
    _validate_platform_filter(path, location, value, platforms)

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

    _validate_result(path, f"{location} result", value["result"], flag, configured_flags)
    capabilities = value.get("capabilities", {})
    if not isinstance(capabilities, dict):
        _fail(path, f"{location} capabilities must be an object")
    for capability, result in capabilities.items():
        if not capability:
            _fail(path, f"{location} capability name must not be empty")
        _validate_result(
            path, f"{location} capabilities.{capability}", result, flag, configured_flags,
            allow_invalid_context=True,
        )


def _validate_result(
    path: Path,
    location: str,
    result: object,
    flag: str,
    configured_flags: dict[str, object],
    *,
    allow_invalid_context: bool = False,
) -> None:
    if not isinstance(result, dict):
        _fail(path, f"{location} must be an object")
    if "value" not in result:
        _fail(path, f"{location} must include value")
    if not isinstance(result.get("reason"), str) or not result["reason"]:
        _fail(path, f"{location}.reason must be a non-empty string")
    if "errorCode" in result and not isinstance(result["errorCode"], str):
        _fail(path, f"{location}.errorCode must be a string")
    if "serialId" in result and result["serialId"] is not None and type(result["serialId"]) is not int:
        _fail(path, f"{location}.serialId must be an integer or null")
    if "doLog" in result and not isinstance(result["doLog"], bool):
        _fail(path, f"{location}.doLog must be a boolean")
    if "features" in result:
        _validate_features(path, f"{location}.features", result["features"])

    pre_lookup_error = allow_invalid_context and result.get("errorCode") == "INVALID_CONTEXT"
    if flag not in configured_flags and result.get("errorCode") != "FLAG_NOT_FOUND" and not pre_lookup_error:
        _fail(
            path,
            f"{location} references unknown flag {flag!r} without a FLAG_NOT_FOUND expectation",
        )


def _validate_features(path: Path, location: str, features: object) -> None:
    if not isinstance(features, dict) or set(features) != FEATURE_DESTINATIONS:
        _fail(path, f"{location} must contain exactly HOOK, EXPOSURE, and EVALUATION maps")
    for destination, values in features.items():
        if not isinstance(values, dict):
            _fail(path, f"{location}.{destination} must be an object")
        for key, value in values.items():
            if not isinstance(key, str) or not key:
                _fail(path, f"{location}.{destination} keys must be non-empty strings")
            if not isinstance(value, (str, bool, int, float)) or (
                isinstance(value, float) and not math.isfinite(value)
            ):
                _fail(path, f"{location}.{destination}.{key} must be a string, boolean, or finite number")


def _validate_suite(
    config_path: Path,
    cases_directory: Path,
    platforms: frozenset[str],
    *,
    self_contained: bool = False,
) -> tuple[int, int]:
    if config_path.is_symlink() or not config_path.is_file():
        _fail(config_path, "must be a regular file, not a symlink")
    if cases_directory.is_symlink() or not cases_directory.is_dir():
        _fail(cases_directory, "must be a directory, not a symlink")

    if self_contained:
        suite_directory = config_path.parent
        allowed_entries = {config_path.name, cases_directory.name}
        for entry in suite_directory.iterdir():
            if entry.name not in allowed_entries:
                _fail(entry, "unexpected suite entry; only ufc-config.json and cases/ are allowed")

    configured_flags = _validate_config(config_path, _load_json(config_path))
    evaluation_paths: list[Path] = []
    for entry in sorted(cases_directory.iterdir()):
        if entry.is_symlink() or not entry.is_file():
            _fail(entry, "case entries must be regular files, not directories or symlinks")
        if entry.suffix != ".json":
            _fail(entry, "case filenames must end in .json")
        evaluation_paths.append(entry)
    if not evaluation_paths:
        _fail(cases_directory, "must contain at least one JSON file")

    case_count = 0
    for path in evaluation_paths:
        cases = _load_json(path)
        if not isinstance(cases, list):
            _fail(path, "top-level value must be an array")
        if not cases:
            _fail(path, "evaluation-case array must not be empty")

        for index, case in enumerate(cases):
            _validate_evaluation_case(path, index, case, configured_flags, platforms)
            case_count += 1

    return case_count, len(evaluation_paths)


def _validate_suite_id(suite_directory: Path, *, legacy_core_exists: bool) -> None:
    if not SUITE_NAME_PATTERN.fullmatch(suite_directory.name):
        _fail(suite_directory, "suite directory name must be lowercase kebab-case")
    if legacy_core_exists and suite_directory.name == "core":
        _fail(suite_directory, "core cannot exist in both the legacy and evaluation-suites layouts")


def main() -> None:
    total_cases, total_files = _validate_suite(
        CONFIG_PATH,
        EVALUATION_CASES_DIRECTORY,
        CANONICAL_PLATFORMS,
    )
    suite_count = 1

    if EVALUATION_SUITES_DIRECTORY.exists():
        if EVALUATION_SUITES_DIRECTORY.is_symlink() or not EVALUATION_SUITES_DIRECTORY.is_dir():
            _fail(EVALUATION_SUITES_DIRECTORY, "must be a directory, not a symlink")
        suite_directories: list[Path] = []
        for entry in sorted(EVALUATION_SUITES_DIRECTORY.iterdir()):
            if entry.is_symlink() or not entry.is_dir():
                _fail(entry, "suite entries must be directories, not files or symlinks")
            suite_directories.append(entry)
        if not suite_directories:
            _fail(EVALUATION_SUITES_DIRECTORY, "must contain at least one suite directory")

        for suite_directory in suite_directories:
            _validate_suite_id(suite_directory, legacy_core_exists=True)
            case_count, file_count = _validate_suite(
                suite_directory / "ufc-config.json",
                suite_directory / "cases",
                CANONICAL_PLATFORMS,
                self_contained=True,
            )
            total_cases += case_count
            total_files += file_count
            suite_count += 1

    print(
        f"Validated {suite_count} evaluation suite(s), {total_cases} evaluation cases "
        f"across {total_files} files."
    )


if __name__ == "__main__":
    try:
        main()
    except FixtureValidationError as error:
        raise SystemExit(f"fixture validation failed: {error}") from error
