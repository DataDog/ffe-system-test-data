#!/usr/bin/env python3
"""Validate precomputed assignment fixtures against the FLEX schema.

Usage:
    python3 ci/validate-precomputed-fixtures.py [--schema PATH] [FIXTURE_DIR]

Defaults:
    FIXTURE_DIR = precomputed-assignments/cases
    SCHEMA      = schemas/precomputed-assignment.schema.json

Checks:
    1. Every *.json file under FIXTURE_DIR validates against the JSON Schema.
    2. _skip and _include are never both present on the same object.
    3. Every EventMatcher has _count >= 1.
    4. Fixture name matches filename stem.

Exit codes:
    0 = all valid
    1 = validation errors found
    2 = missing dependencies or bad arguments
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print(
        "ERROR: jsonschema package not installed. Install with: pip install jsonschema",
        file=sys.stderr,
    )
    sys.exit(2)


def find_fixtures(root: Path):
    """Recursively find all .json files under root."""
    return sorted(root.rglob("*.json"))


def check_skip_include_mutual_exclusivity(obj, path="$"):
    """Recursively check that _skip and _include never coexist."""
    errors = []
    if isinstance(obj, dict):
        if "_skip" in obj and "_include" in obj:
            errors.append(f"{path}: _skip and _include are mutually exclusive")
        for key, value in obj.items():
            errors.extend(check_skip_include_mutual_exclusivity(value, f"{path}.{key}"))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            errors.extend(check_skip_include_mutual_exclusivity(item, f"{path}[{i}]"))
    return errors


def check_matcher_counts(data, path="$"):
    """Check that all EventMatchers have _count >= 1."""
    errors = []
    expectations = data.get("expectations", {})
    for list_name in ("exposures", "evaluations"):
        matchers = expectations.get(list_name, [])
        for i, matcher in enumerate(matchers):
            mpath = f"{path}.expectations.{list_name}[{i}]"
            count = matcher.get("_count")
            if count is None:
                errors.append(f"{mpath}: missing required _count field")
            elif not isinstance(count, int) or count < 1:
                errors.append(f"{mpath}: _count must be an integer >= 1, got {count}")
    return errors


def check_name_matches_filename(data, filepath):
    """Check that fixture name matches filename stem."""
    errors = []
    name = data.get("name")
    stem = filepath.stem
    if name and name != stem:
        errors.append(
            f"$.name: fixture name '{name}' does not match filename '{stem}'"
        )
    return errors


def check_skip_entry_format(obj, path="$"):
    """Check that _skip and _include entries are arrays of {platform, reason?} objects."""
    errors = []
    if isinstance(obj, dict):
        for field in ("_skip", "_include"):
            if field in obj:
                entries = obj[field]
                if not isinstance(entries, list):
                    errors.append(f"{path}.{field}: must be an array")
                    continue
                for i, entry in enumerate(entries):
                    epath = f"{path}.{field}[{i}]"
                    if not isinstance(entry, dict):
                        errors.append(f"{epath}: must be an object")
                        continue
                    if "platform" not in entry:
                        errors.append(f"{epath}: missing required 'platform' field")
                    allowed = {"platform", "reason"}
                    extra = set(entry.keys()) - allowed
                    if extra:
                        errors.append(
                            f"{epath}: unexpected fields: {', '.join(sorted(extra))}"
                        )
        for key, value in obj.items():
            errors.extend(check_skip_entry_format(value, f"{path}.{key}"))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            errors.extend(check_skip_entry_format(item, f"{path}[{i}]"))
    return errors


def validate_fixture(filepath, schema):
    """Validate a single fixture file. Returns list of error strings."""
    errors = []
    rel = filepath.relative_to(Path.cwd()) if filepath.is_relative_to(Path.cwd()) else filepath

    try:
        with open(filepath) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"{rel}: invalid JSON: {e}"]

    # JSON Schema validation
    validator = jsonschema.Draft202012Validator(schema)
    for error in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        json_path = ".".join(str(p) for p in error.absolute_path) or "$"
        errors.append(f"{rel}: schema: {json_path}: {error.message}")

    # Custom checks
    errors.extend(f"{rel}: {e}" for e in check_skip_include_mutual_exclusivity(data))
    errors.extend(f"{rel}: {e}" for e in check_matcher_counts(data))
    errors.extend(f"{rel}: {e}" for e in check_name_matches_filename(data, filepath))
    errors.extend(f"{rel}: {e}" for e in check_skip_entry_format(data))

    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "fixture_dir",
        nargs="?",
        default="precomputed-assignments/cases",
        help="Directory containing fixture JSON files (default: precomputed-assignments/cases)",
    )
    parser.add_argument(
        "--schema",
        default="schemas/precomputed-assignment.schema.json",
        help="Path to the JSON Schema file",
    )
    args = parser.parse_args()

    fixture_dir = Path(args.fixture_dir)
    schema_path = Path(args.schema)

    if not fixture_dir.is_dir():
        print(f"ERROR: fixture directory not found: {fixture_dir}", file=sys.stderr)
        sys.exit(2)

    if not schema_path.is_file():
        print(f"ERROR: schema file not found: {schema_path}", file=sys.stderr)
        sys.exit(2)

    with open(schema_path) as f:
        schema = json.load(f)

    fixtures = find_fixtures(fixture_dir)
    if not fixtures:
        print(f"WARNING: no .json files found in {fixture_dir}", file=sys.stderr)
        sys.exit(0)

    all_errors = []
    valid_count = 0

    for filepath in fixtures:
        errors = validate_fixture(filepath, schema)
        if errors:
            for e in errors:
                print(f"  FAIL: {e}")
            all_errors.extend(errors)
        else:
            valid_count += 1
            print(f"  OK: {filepath.relative_to(Path.cwd()) if filepath.is_relative_to(Path.cwd()) else filepath}")

    print()
    print(f"{valid_count} valid, {len(all_errors)} errors across {len(fixtures)} fixtures")

    sys.exit(1 if all_errors else 0)


if __name__ == "__main__":
    main()
