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


if __name__ == "__main__":
    unittest.main()
