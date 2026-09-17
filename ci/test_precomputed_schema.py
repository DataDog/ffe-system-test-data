"""Regression tests for typed precomputed evaluation values."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas/precomputed-assignment.schema.json"
VALID_VALUES = {
    "boolean": [False, True],
    "string": ["", "value"],
    "integer": [0, -2, 1.0],
    "float": [0, -2, 1.0, 1.5],
    "object": [{}, {"nested": [None, True, {"value": 1}]}],
}
INVALID_VALUES = {
    "boolean": ["true", 0, 1, 1.5, {}, [], None],
    "string": [False, True, 0, 1.5, {}, [], None],
    "integer": [1.5, "1", False, True, {}, [], None],
    "float": ["1.5", False, True, {}, [], None],
    "object": [[], "value", False, True, 0, 1.5, None],
}


def fixture(variation_type):
    value = VALID_VALUES[variation_type][0]
    return {
        "name": "typed-evaluation",
        "description": "Typed evaluation schema regression test.",
        "context": {"targetingKey": "user", "attributes": {}},
        "response": {},
        "evaluations": [{
            "flag": "flag",
            "variationType": variation_type,
            "defaultValue": copy.deepcopy(value),
            "expectedResult": {
                "value": copy.deepcopy(value),
                "reason": "DEFAULT",
                "errorCode": None,
                "variantKey": None,
            },
        }],
        "expectations": {},
    }


def set_value(data, field, value):
    evaluation = data["evaluations"][0]
    if field == "defaultValue":
        evaluation[field] = value
    else:
        evaluation["expectedResult"]["value"] = value


class TypedEvaluationSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        cls.validator = Draft202012Validator(schema)

    def test_matching_types_are_accepted_independently(self):
        for variation_type, values in VALID_VALUES.items():
            for field in ("defaultValue", "expectedResult.value"):
                for value in values:
                    with self.subTest(type=variation_type, field=field, value=value):
                        data = fixture(variation_type)
                        set_value(data, field, value)
                        self.assertEqual(list(self.validator.iter_errors(data)), [])

    def test_mismatched_types_are_rejected_independently(self):
        for variation_type, values in INVALID_VALUES.items():
            for field in ("defaultValue", "expectedResult.value"):
                for value in values:
                    with self.subTest(type=variation_type, field=field, value=value):
                        data = fixture(variation_type)
                        set_value(data, field, value)
                        errors = list(self.validator.iter_errors(data))
                        self.assertEqual(len(errors), 1)
                        self.assertEqual(errors[0].validator, "type")
                        self.assertEqual(
                            list(errors[0].absolute_path),
                            ["evaluations", 0, *field.split(".")],
                        )

    def test_expected_result_retains_existing_constraints(self):
        for variation_type in VALID_VALUES:
            for mutation in ("missing_value", "extra_property", "invalid_reason"):
                with self.subTest(type=variation_type, mutation=mutation):
                    data = fixture(variation_type)
                    expected = data["evaluations"][0]["expectedResult"]
                    if mutation == "missing_value":
                        del expected["value"]
                    elif mutation == "extra_property":
                        expected["extra"] = True
                    else:
                        expected["reason"] = 42
                    self.assertFalse(self.validator.is_valid(data))

    def test_cli_rejects_numeric_string_float_default(self):
        data = fixture("float")
        set_value(data, "defaultValue", "1.5")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "typed-evaluation.json"
            path.write_text(json.dumps(data))
            result = subprocess.run(
                [sys.executable, str(ROOT / "ci/validate-precomputed-fixtures.py"),
                 "--schema", str(SCHEMA), directory],
                capture_output=True, text=True, check=False,
            )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("evaluations.0.defaultValue", result.stdout)
        self.assertIn("is not of type 'number'", result.stdout)


if __name__ == "__main__":
    unittest.main()
