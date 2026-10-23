"""Regression checks for rules-based evaluation fixture validation."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location("validate_fixtures", Path(__file__).with_name("validate-fixtures.py"))
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class MetadataExpectationValidationTest(unittest.TestCase):
    def validate(self, metadata: dict[str, object]) -> None:
        validator._validate_result(
            validator.EVALUATION_CASES_DIRECTORY / "test-case-metadata.json",
            "case 0 result",
            {"value": True, "reason": "STATIC", **metadata},
            "flag",
            {"flag": {}},
        )

    def test_absent_null_and_zero_serial_id_are_valid(self) -> None:
        for metadata in ({}, {"serialId": None}, {"serialId": 0}, {"serialId": 42}):
            with self.subTest(metadata=metadata):
                self.validate(metadata)

    def test_serial_id_rejects_booleans_and_other_non_integer_values(self) -> None:
        for value in (False, True, 0.0, "0", [], {}):
            with self.subTest(value=value):
                with self.assertRaisesRegex(validator.FixtureValidationError, "serialId must be an integer or null"):
                    self.validate({"serialId": value})

    def test_both_logging_decisions_are_valid(self) -> None:
        self.validate({"doLog": False})
        self.validate({"doLog": True})

    def test_logging_decision_rejects_null_and_boolean_coercion(self) -> None:
        for value in (None, 0, 1, "false", "true", [], {}):
            with self.subTest(value=value):
                with self.assertRaisesRegex(validator.FixtureValidationError, "doLog must be a boolean"):
                    self.validate({"doLog": value})

    def test_features_preserve_empty_maps_and_falsy_scalars(self) -> None:
        self.validate({"features": {"HOOK": {}, "EXPOSURE": {}, "EVALUATION": {}}})
        self.validate({"features": {
            "HOOK": {"empty": "", "false": False},
            "EXPOSURE": {"zero": 0},
            "EVALUATION": {"fraction": 1.25},
        }})

    def test_features_require_all_known_destinations(self) -> None:
        for value in (None, [], {}, {"HOOK": {}},
                      {"HOOK": {}, "EXPOSURE": {}, "EVALUATION": {}, "FUTURE": {}},
                      {"hook": {}, "EXPOSURE": {}, "EVALUATION": {}}):
            with self.subTest(value=value):
                with self.assertRaisesRegex(validator.FixtureValidationError, "must contain exactly"):
                    self.validate({"features": value})

    def test_feature_destinations_require_maps(self) -> None:
        for destination in validator.FEATURE_DESTINATIONS:
            for value in (None, [], "", False, 0):
                with self.subTest(destination=destination, value=value):
                    features = {name: {} for name in validator.FEATURE_DESTINATIONS}
                    features[destination] = value
                    with self.assertRaisesRegex(validator.FixtureValidationError, "must be an object"):
                        self.validate({"features": features})

    def test_feature_values_reject_null_containers_and_nonfinite_numbers(self) -> None:
        for value in (None, {}, [], float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                with self.assertRaisesRegex(validator.FixtureValidationError, "finite number"):
                    self.validate({"features": {"HOOK": {"key": value}, "EXPOSURE": {}, "EVALUATION": {}}})

    def test_feature_keys_must_not_be_empty(self) -> None:
        with self.assertRaisesRegex(validator.FixtureValidationError, "keys must be non-empty"):
            self.validate({"features": {"HOOK": {"": True}, "EXPOSURE": {}, "EVALUATION": {}}})

    def test_capability_feature_expectations_are_also_validated(self) -> None:
        case = {
            "flag": "flag", "variationType": "BOOLEAN", "defaultValue": False,
            "targetingKey": "subject", "attributes": {},
            "result": {"value": True, "reason": "STATIC"},
            "capabilities": {"example": {"value": True, "reason": "STATIC", "features": {}}},
        }
        with self.assertRaisesRegex(validator.FixtureValidationError, "capabilities.example.features"):
            validator._validate_evaluation_case(
                validator.EVALUATION_CASES_DIRECTORY / "test-case-metadata.json", 0, case, {"flag": {}},
            )


class EvaluationSuiteValidationTest(unittest.TestCase):
    platforms = frozenset({"php", "python"})

    @staticmethod
    def config(flag: str) -> dict[str, object]:
        return {
            "createdAt": "2026-01-01T00:00:00Z",
            "format": "SERVER",
            "environment": {"name": "test"},
            "flags": {
                flag: {
                    "key": flag,
                    "variations": {"on": {"key": "on", "value": True}},
                    "allocations": [],
                }
            },
        }

    @staticmethod
    def case(flag: str) -> dict[str, object]:
        return {
            "flag": flag,
            "variationType": "BOOLEAN",
            "defaultValue": False,
            "targetingKey": "subject",
            "attributes": {},
            "result": {"value": True, "reason": "STATIC"},
        }

    def test_legacy_and_directory_core_cannot_both_exist(self) -> None:
        suite_path = validator.EVALUATION_SUITES_DIRECTORY / "core"
        with self.assertRaisesRegex(validator.FixtureValidationError, "cannot exist in both"):
            validator._validate_suite_id(suite_path, legacy_core_exists=True)

    def test_self_contained_suite_uses_its_adjacent_config(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            suite = Path(temporary_directory) / "example"
            cases = suite / "cases"
            cases.mkdir(parents=True)
            config_path = suite / "ufc-config.json"
            config_path.write_text(json.dumps(self.config("suite-flag")), encoding="utf-8")
            (cases / "test-suite.json").write_text(
                json.dumps([self.case("suite-flag")]), encoding="utf-8",
            )

            self.assertEqual(
                (1, 1),
                validator._validate_suite(config_path, cases, self.platforms, self_contained=True),
            )

            (cases / "test-suite.json").write_text(
                json.dumps([self.case("root-only-flag")]), encoding="utf-8",
            )
            with self.assertRaisesRegex(validator.FixtureValidationError, "unknown flag 'root-only-flag'"):
                validator._validate_suite(config_path, cases, self.platforms, self_contained=True)

    def test_self_contained_suite_rejects_missing_or_extra_entries(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            suite = Path(temporary_directory) / "example"
            suite.mkdir()
            config_path = suite / "ufc-config.json"
            config_path.write_text(json.dumps(self.config("suite-flag")), encoding="utf-8")
            cases = suite / "cases"

            with self.assertRaisesRegex(validator.FixtureValidationError, "must be a directory"):
                validator._validate_suite(config_path, cases, self.platforms, self_contained=True)

            cases.mkdir()
            (cases / "test-suite.json").write_text(
                json.dumps([self.case("suite-flag")]), encoding="utf-8",
            )
            (suite / "unexpected.json").write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(validator.FixtureValidationError, "unexpected suite entry"):
                validator._validate_suite(config_path, cases, self.platforms, self_contained=True)


class EvaluationPlatformValidationTest(unittest.TestCase):
    platforms = frozenset({"php", "python"})
    path = validator.EVALUATION_CASES_DIRECTORY / "test-case-filter.json"

    def validate(self, value: dict[str, object]) -> None:
        validator._validate_platform_filter(self.path, "case 0", value, self.platforms)

    def test_canonical_platforms_cover_annotated_sdks(self) -> None:
        self.assertIn("php", validator.CANONICAL_PLATFORMS)
        self.assertIn("python", validator.CANONICAL_PLATFORMS)

    def test_skip_and_include_accept_canonical_platforms(self) -> None:
        self.validate({"_skip": [{"platform": "php", "reason": "Known gap."}]})
        self.validate({"_include": [{"platform": "python"}]})

    def test_skip_and_include_are_mutually_exclusive(self) -> None:
        with self.assertRaisesRegex(validator.FixtureValidationError, "mutually exclusive"):
            self.validate({"_skip": [{"platform": "php"}], "_include": [{"platform": "python"}]})

    def test_filters_reject_invalid_shapes_and_platforms(self) -> None:
        invalid = (
            ({"_skip": []}, "non-empty array"),
            ({"_skip": [{"platform": "unknown"}]}, "canonical platform"),
            ({"_skip": [{"platform": "php"}, {"platform": "php"}]}, "repeats platform"),
            ({"_skip": [{"platform": "php", "reason": ""}]}, "non-empty string"),
            ({"_skip": [{"platform": "php", "ticket": "ABC-1"}]}, "unexpected fields"),
        )
        for value, message in invalid:
            with self.subTest(value=value):
                with self.assertRaisesRegex(validator.FixtureValidationError, message):
                    self.validate(value)


if __name__ == "__main__":
    unittest.main()
