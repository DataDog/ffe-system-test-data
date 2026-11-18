#!/usr/bin/env python3
"""Regression tests: invalid contract data must fail before consumers use it."""

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
SPEC = importlib.util.spec_from_file_location("opt_out_validator", Path(__file__).with_name("validate-experimentation-opt-out.py"))
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ValidatorTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ffe-opt-out-fixtures-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "v1"
        shutil.copytree(MODULE.SUITE, self.root)

    def modify(self, relative, mutation):
        path = self.root / relative
        value = json.loads(path.read_text())
        mutation(value)
        path.write_text(json.dumps(value), encoding="utf-8")

    def invalid(self, message):
        with self.assertRaisesRegex(MODULE.ContractError, message):
            MODULE.validate(self.root)

    def rehash_generation_file(self, relative, field):
        digest = hashlib.sha256((self.root / relative).read_bytes()).hexdigest()
        self.modify("manifest.json", lambda data: data["compilerGeneration"].update({field: digest}))

    def test_checked_in_contract(self):
        self.assertEqual(MODULE.validate(self.root), {
            "configurations": 10, "evaluations": 136, "protocols": 20, "sequences": 9
        })

    def test_duplicate_json_key(self):
        path = self.root / "manifest.json"
        path.write_text(path.read_text().replace('"schemaVersion": 1', '"schemaVersion": 1, "schemaVersion": 1', 1))
        self.invalid("duplicate JSON key")

    def test_non_json_number(self):
        path = self.root / "manifest.json"
        path.write_text(path.read_text().replace('"schemaVersion": 1', '"schemaVersion": NaN', 1))
        self.invalid("invalid JSON constant")

    def test_missing_manifest_case(self):
        self.modify("manifest.json", lambda data: data["evaluationCases"][0]["ids"].pop())
        self.invalid("manifest IDs/order")

    def test_unlisted_file(self):
        (self.root / "cases/unlisted.json").write_text("[]")
        self.invalid("unlisted")

    def test_incorrect_case_count(self):
        self.modify("manifest.json", lambda data: data["expectedCounts"].update(evaluations=1))
        self.invalid("manifest counts differ")

    def test_unknown_configuration(self):
        self.modify("cases/activation.json", lambda data: data[0].update(configuration="unknown"))
        self.invalid("unknown configuration")

    def test_unknown_field(self):
        self.modify("cases/activation.json", lambda data: data[0].update(ignoredOptOut=True))
        self.invalid("schema")

    def test_string_is_not_boolean_activation(self):
        def mutate(cases):
            case = next(item for item in cases if item["id"] == "activation-enabled-string-true")
            case["expected"]["effectiveExperimentationOptOut"] = True
        self.modify("cases/activation.json", mutate)
        self.invalid("strict activation")

    def test_excluded_assignment_cannot_log(self):
        def mutate(cases):
            excluded = next(item for item in cases if item["id"] == "excluded-control")
            eligible = next(item for item in cases if item["id"] == "eligible-two-arm-subject-2")
            excluded["expected"]["assignment"] = eligible["expected"]["assignment"]
            excluded["expected"]["value"] = eligible["expected"]["value"]
        self.modify("cases/evaluation.json", mutate)
        self.invalid("excluded subject cannot receive")

    def test_false_value_cannot_stand_for_boolean_true(self):
        def mutate(cases):
            case = next(item for item in cases if item["id"] == "boolean-fallback-is-true")
            case["expected"]["value"] = 1
        self.modify("cases/evaluation.json", mutate)
        self.invalid("expected result type mismatch")

    def test_assignment_identity_is_required(self):
        self.modify("cases/evaluation.json", lambda data: data[0]["expected"]["assignment"].update(allocationKey="unknown"))
        self.invalid("unknown expected allocation")

    def test_assignment_value_keeps_boolean_type(self):
        def mutate(cases):
            case = next(item for item in cases if item["id"] == "boolean-fallback-is-true")
            case["expected"]["assignment"]["value"] = 1
        self.modify("cases/evaluation.json", mutate)
        self.invalid("assignment value type mismatch")

    def test_nested_boolean_is_not_number(self):
        self.assertFalse(MODULE.same_json({"value": [True]}, {"value": [1]}))
        self.assertFalse(MODULE.same_json(False, 0))

    def test_wire_reason_matches_selected_split(self):
        self.modify("cases/evaluation.json", lambda data: data[0]["expected"]["assignment"].update(wireReason="STATIC"))
        self.invalid("wire reason differs")

    def test_holdout_metadata_is_not_lost(self):
        def mutate(cases):
            case = next(item for item in cases if item["id"] == "holdout-after-route-status-quo-eligible")
            case["expected"]["assignment"]["features"] = []
        self.modify("cases/holdouts.json", mutate)
        self.invalid("features differ")

    def test_telemetry_opt_out_does_not_remove_exposure(self):
        def mutate(cases):
            case = next(item for item in cases if item["id"] == "independent-experiment-false-telemetry-true")
            case["expectations"]["exposures"] = []
        self.modify("cases/telemetry.json", mutate)
        self.invalid("exposure count mismatch")

    def test_legacy_configuration_cannot_claim_exclusion(self):
        def mutate(cases):
            case = next(item for item in cases if item["id"] == "legacy-excluded")
            case["expected"]["outcome"] = "no-assignment"
        self.modify("cases/compatibility.json", mutate)
        self.invalid("missing capability must reject")

    def test_missing_dolog_is_not_ordinary_when_excluded(self):
        def mutate(cases):
            case = next(item for item in cases if item["id"] == "missing-dolog-excluded")
            case["expected"]["outcome"] = "no-assignment"
        self.modify("cases/compatibility.json", mutate)
        self.invalid("missing doLog must reject")

    def test_string_request_cannot_be_accepted(self):
        def mutate(cases):
            case = next(item for item in cases if item["id"] == "request-string")
            case["expected"]["accepted"] = True
        self.modify("protocol/request-and-response.json", mutate)
        self.invalid("protocol acceptance")

    def test_missing_ack_cannot_publish(self):
        def mutate(cases):
            case = next(item for item in cases if item["id"] == "response-missing-ack")
            case["expected"]["publishAssignments"] = True
        self.modify("protocol/request-and-response.json", mutate)
        self.invalid("publication expectation")

    def test_unknown_sequence_case(self):
        self.modify("sequences/missing-ack-never-publishes.json", lambda data: data["steps"][3].update(caseId="unknown"))
        self.invalid("unknown case")

    def test_response_without_request(self):
        self.modify("sequences/missing-ack-never-publishes.json", lambda data: data["steps"][3].update(requestId="unknown"))
        self.invalid("unknown/already completed request")

    def test_corrupt_hash_vector(self):
        self.modify("manifest.json", lambda data: data["bucketing"]["vectors"][0].update(shard=0))
        self.invalid("shard mismatch")

    def test_concurrency_must_cover_both_participation_states(self):
        self.modify("manifest.json", lambda data: data["invariants"].update(
            concurrentServerCaseIds=["excluded-control", "excluded-treatment"]
        ))
        self.invalid("both participation states")

    def test_generated_protobuf_corruption(self):
        path = self.root / "compiler-generated/compiler-active-50-50.pb"
        path.chmod(0o600)
        path.write_bytes(path.read_bytes() + b"corruption")
        self.invalid("SHA256 mismatch")

    def test_generated_json_is_verbatim(self):
        self.modify("configurations/compiler-active-50-50.json", lambda data: data.update(createdAt="2026-10-17T12:00:00Z"))
        self.invalid("SHA256 mismatch")

    def test_generated_configuration_requires_pair(self):
        self.modify("manifest.json", lambda data: data["compilerGeneration"]["pairs"].pop())
        self.invalid("every generated configuration needs a pair")

    def test_generated_pair_configuration_must_exist(self):
        self.modify("manifest.json", lambda data: data["compilerGeneration"]["pairs"][0].update(configurationId="unknown"))
        self.invalid("unknown/duplicate configuration pair")

    def test_unlisted_protobuf_is_rejected(self):
        (self.root / "compiler-generated/unlisted.pb").write_bytes(b"unlisted")
        self.invalid("generated artifact enumeration")

    def test_generated_parity_case_cannot_be_omitted(self):
        self.modify("manifest.json", lambda data: data["compilerGeneration"]["eligibleParityCaseIds"].pop())
        self.invalid("eligible parity case coverage")

    def test_independent_shard_vector_is_verified_after_rehash(self):
        self.modify("compiler-generated/hash-vectors.json", lambda data: data["vectors"][0].update(shard=0))
        self.rehash_generation_file("compiler-generated/hash-vectors.json", "hashVectorsSha256")
        self.invalid("independent shard mismatch")

    def test_observed_scenario_references_are_checked(self):
        self.modify("compiler-generated/compiler-scenarios.json", lambda data: data[0].update(configuration="unknown.json"))
        self.rehash_generation_file("compiler-generated/compiler-scenarios.json", "observationsSha256")
        self.invalid("observed configuration path mismatch")

    def test_generated_configuration_cannot_lose_provenance(self):
        self.modify("manifest.json", lambda data: data.pop("compilerGeneration"))
        self.invalid("metadata/configuration mismatch")


if __name__ == "__main__":
    unittest.main()
