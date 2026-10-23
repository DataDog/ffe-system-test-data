"""Regression checks for optional selected split/allocation expectations."""

import importlib.util
from pathlib import Path
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


if __name__ == "__main__":
    unittest.main()
