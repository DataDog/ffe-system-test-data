import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('validator', ROOT / 'ci/validate-precomputed-fixtures.py')
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class PrecomputedValidationTest(unittest.TestCase):
    def setUp(self):
        self.schema = json.loads((ROOT / 'schemas/precomputed-assignment.schema.json').read_text())
        self.case = json.loads((ROOT / 'precomputed-assignments/cases/evaluator/numeric-number.json').read_text())
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)

    def validate(self, value):
        path = Path(self.directory.name) / 'numeric-number.json'
        path.write_text(json.dumps(value))
        return validator.validate_fixture(path, self.schema)

    def test_valid_numeric_matrix(self):
        self.assertEqual([], self.validate(self.case))

    def test_unknown_platform_fails(self):
        self.case['_skip'] = [{'platform': 'andriod'}]
        self.assertTrue(self.validate(self.case))

    def test_rejected_response_cannot_also_evaluate(self):
        self.case['expectedResponseError'] = 'INVALID_RESPONSE'
        self.assertTrue(self.validate(self.case))

    def test_empty_evaluations_require_rejection(self):
        self.case['evaluations'] = []
        self.assertTrue(self.validate(self.case))
        self.case['expectedResponseError'] = 'INVALID_RESPONSE'
        self.case['expectations'] = {'noUnmatchedEvents': True, 'exposures': [], 'evaluationEvents': []}
        self.assertEqual([], self.validate(self.case))

    def test_rejected_response_cannot_allow_or_expect_events(self):
        self.case['evaluations'] = []
        self.case['expectedResponseError'] = 'INVALID_RESPONSE'
        for expectations in [{}, {'noUnmatchedEvents': False},
                             {'noUnmatchedEvents': True, 'exposures': [{'_count': 1}]},
                             {'noUnmatchedEvents': True, 'evaluationEvents': [{'_count': 1}]}]:
            with self.subTest(expectations=expectations):
                self.case['expectations'] = expectations
                self.assertTrue(self.validate(self.case))

    def test_non_object_is_reported_not_crashed(self):
        self.assertTrue(self.validate([]))

    def test_malformed_expectations_are_reported_not_crashed(self):
        for value in [None, [], {"exposures": None}, {"exposures": [None]}]:
            self.case['expectations'] = value
            self.assertTrue(self.validate(self.case))

    def test_payload_keys_are_not_platform_filters(self):
        self.case['response']['custom'] = {'_skip': 'payload', '_include': 'payload'}
        self.assertEqual([], self.validate(self.case))

    def test_assignment_and_error_maps_are_mutually_exclusive(self):
        attributes = self.case['response']['data']['attributes']
        assigned_key = next(iter(attributes['flags']))
        attributes['flagEvaluationErrors'] = {
            assigned_key: {
                'reason': 'ERROR',
                'errorCode': 'GENERAL',
                'errorMessage': 'A prerequisite flag could not be evaluated',
                'dependencyEvaluations': [],
            }
        }
        self.assertTrue(self.validate(self.case))

    def test_error_entries_require_reason_code_and_dependencies(self):
        attributes = self.case['response']['data']['attributes']
        for entry in [
            {},
            {'reason': 'ERROR'},
            {'reason': 'ERROR', 'errorCode': 'GENERAL'},
            {
                'reason': 'ERROR',
                'errorCode': 'FLAG_NOT_FOUND',
                'errorMessage': 'A prerequisite flag could not be evaluated',
                'dependencyEvaluations': [],
            },
        ]:
            with self.subTest(entry=entry):
                candidate = copy.deepcopy(self.case)
                candidate['response']['data']['attributes']['flagEvaluationErrors'] = {
                    'failed': entry
                }
                self.assertTrue(self.validate(candidate))

    def test_new_nested_fixture_is_discovered(self):
        path = Path(self.directory.name) / 'new' / 'nested' / 'numeric-number.json'
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(self.case))
        self.assertEqual([path], validator.find_fixtures(Path(self.directory.name)))

    def test_empty_directory_fails(self):
        result = subprocess.run([sys.executable, str(ROOT / 'ci/validate-precomputed-fixtures.py'),
                                 '--schema', str(ROOT / 'schemas/precomputed-assignment.schema.json'), self.directory.name],
                                capture_output=True)
        self.assertEqual(1, result.returncode)


if __name__ == '__main__':
    unittest.main()
