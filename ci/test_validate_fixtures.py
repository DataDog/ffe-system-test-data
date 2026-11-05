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


class FlagSelectionSuiteValidationTest(unittest.TestCase):
    platforms = frozenset({"php", "python"})
    path = validator.EVALUATION_SUITES_DIRECTORY / "example" / "cases" / "test-case.json"

    @staticmethod
    def case(**fields: object) -> dict[str, object]:
        return {
            **EvaluationSuiteValidationTest.case("suite-flag"),
            "providerOptions": {"flagSelection": {"tags": [" team:checkout "]}},
            "expectations": {
                "configurationRequest": {"selectedFlagTags": ["team:checkout"], "selectedFlagKeyPatterns": []}
            },
            **fields,
        }

    def validate_case(self, case: dict[str, object]) -> None:
        validator._validate_evaluation_case(self.path, 0, case, {"suite-flag": {}}, self.platforms)

    def write_suite(self, directory: str, flag_tags: object, cases: list[dict[str, object]]) -> tuple[Path, Path]:
        suite = Path(directory) / "example"
        (suite / "cases").mkdir(parents=True)
        config_path = suite / "ufc-config.json"
        config_path.write_text(json.dumps(EvaluationSuiteValidationTest.config("suite-flag")), encoding="utf-8")
        (suite / "flag-tags.json").write_text(json.dumps(flag_tags), encoding="utf-8")
        (suite / "cases" / "test-case.json").write_text(json.dumps(cases), encoding="utf-8")
        return config_path, suite / "cases"

    def test_suite_accepts_flag_tags_for_its_own_flags(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            config_path, cases = self.write_suite(
                temporary_directory, {"flags": [{"key": "suite-flag", "tags": ["team:checkout"]}]}, [self.case()]
            )
            self.assertEqual(
                (1, 1), validator._validate_suite(config_path, cases, self.platforms, self_contained=True)
            )

            (config_path.parent / "unexpected.json").write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(validator.FixtureValidationError, "unexpected suite entry"):
                validator._validate_suite(config_path, cases, self.platforms, self_contained=True)

    def test_flag_tags_reject_invalid_shapes_and_unknown_flags(self) -> None:
        invalid = (
            ({"flags": [{"key": "root-only-flag", "tags": []}]}, "must name a flag"),
            ({"flags": [{"key": "suite-flag", "tags": []}, {"key": "suite-flag", "tags": []}]}, "is repeated"),
            ({"flags": [{"key": "suite-flag", "tags": ["", "team:checkout"]}]}, "non-empty strings"),
            ({"flags": [{"key": "suite-flag"}]}, "exactly key and tags"),
            ({"flags": [{"key": "suite-flag", "tags": [], "owner": "team-checkout"}]}, "exactly key and tags"),
            ({"flags": [{"key": "suite-flag", "tags": "team:checkout"}]}, "non-empty strings"),
            ({"flags": []}, "non-empty array"),
            ({"flags": [], "extra": True}, "exactly one field, flags"),
        )
        for flag_tags, message in invalid:
            with self.subTest(flag_tags=flag_tags), tempfile.TemporaryDirectory() as temporary_directory:
                config_path, cases = self.write_suite(temporary_directory, flag_tags, [self.case()])
                with self.assertRaisesRegex(validator.FixtureValidationError, message):
                    validator._validate_suite(config_path, cases, self.platforms, self_contained=True)

    def test_provider_start_fields_accept_valid_shapes(self) -> None:
        self.validate_case(self.case())
        self.validate_case(self.case(configurationResponse={"flagSelectionIgnored": "tag_load_failed"}))
        self.validate_case(
            self.case(
                providerOptions={"flagSelection": {"tags": [], "keyPatterns": []}},
                expectations={"configurationRequest": {"flagSelection": None}},
            )
        )

    def test_provider_start_fields_reject_invalid_shapes(self) -> None:
        no_selection = {"configurationRequest": {"flagSelection": None}}
        invalid = (
            ({"providerOptions": []}, "providerOptions must be an object"),
            ({"providerOptions": {"flagSelections": {}}}, "unknown fields: flagSelections"),
            ({"providerOptions": {"flagSelection": {"tags": [1]}}}, "string arrays"),
            ({"providerOptions": {"flagSelection": {"labels": []}}}, "string arrays"),
            ({"expectations": {}}, "requires expectations.configurationRequest"),
            ({"expectations": {"configurationRequest": {"flagSelection": False}}}, "flagSelection\": null"),
            (
                {
                    "expectations": {
                        "configurationRequest": {"selectedFlagTags": ["b", "a"], "selectedFlagKeyPatterns": []}
                    }
                },
                "sorted by UTF-8 bytes",
            ),
            (
                {
                    "expectations": {
                        "configurationRequest": {"selectedFlagTags": ["a", "a"], "selectedFlagKeyPatterns": []}
                    }
                },
                "without duplicates",
            ),
            (
                {"expectations": {"configurationRequest": {"selectedFlagTags": [], "selectedFlagKeyPatterns": []}}},
                "sends no selection",
            ),
            ({"configurationResponse": {"flagSelectionIgnored": "unknown_reason"}}, "must be one of"),
            ({"configurationResponse": {"flagSelectionIgnored": ["tag_load_failed"]}}, "must be one of"),
            ({"providerOptions": {}}, "without the provider option"),
            ({"configurationResponse": {"reason": "tag_load_failed"}}, "exactly one field, flagSelectionIgnored"),
            (
                {"expectations": no_selection, "configurationResponse": {"flagSelectionIgnored": "tag_load_failed"}},
                "sends a selection",
            ),
        )
        for fields, message in invalid:
            with self.subTest(fields=fields):
                with self.assertRaisesRegex(validator.FixtureValidationError, message):
                    self.validate_case(self.case(**fields))

    def test_provider_start_fields_reject_more_invalid_shapes(self) -> None:
        def request(tags: object, key_patterns: object) -> dict[str, object]:
            selection = {"selectedFlagTags": tags, "selectedFlagKeyPatterns": key_patterns}
            return {"expectations": {"configurationRequest": selection}}

        invalid = (
            ({"providerOptions": {"flagSelection": []}}, "string arrays"),
            ({"providerOptions": {"flagSelection": {"tags": "team:checkout"}}}, "string arrays"),
            ({"expectations": []}, "expectations must be an object"),
            ({"expectations": {"configurationRequest": None}}, "flagSelection\": null"),
            (request(["", "team:checkout"], []), "selectedFlagTags must hold"),
            (request([" team:checkout"], []), "selectedFlagTags must hold trimmed"),
            (request(["team:checkout"], ["b*", "a*"]), "selectedFlagKeyPatterns must hold"),
            (request(["team:checkout"], [""]), "selectedFlagKeyPatterns must hold"),
            (request(["\U0001F600", "\uff61"], []), "sorted by UTF-8 bytes"),
            ({"configurationResponse": None}, "exactly one field, flagSelectionIgnored"),
            (
                {"configurationResponse": {"flagSelectionIgnored": "tag_load_failed", "status": 200}},
                "exactly one field, flagSelectionIgnored",
            ),
        )
        for fields, message in invalid:
            with self.subTest(fields=fields):
                with self.assertRaisesRegex(validator.FixtureValidationError, message):
                    self.validate_case(self.case(**fields))

    def test_provider_start_fields_accept_utf8_order(self) -> None:
        for tags in (["\uff61", "\U0001F600"], ["\ud800"]):
            with self.subTest(tags=tags):
                self.validate_case(
                    self.case(
                        providerOptions={"flagSelection": {"tags": tags}},
                        expectations={
                            "configurationRequest": {"selectedFlagTags": tags, "selectedFlagKeyPatterns": []}
                        },
                    )
                )

    def test_each_provider_start_field_must_match_case_0(self) -> None:
        differing = (
            (self.case(configurationResponse={"flagSelectionIgnored": "tag_load_failed"}), "configurationResponse"),
            (self.case(providerOptions={"flagSelection": {"tags": ["team:checkout"]}}), "providerOptions"),
            (
                self.case(expectations={"configurationRequest": {"flagSelection": None}}),
                "expectations.configurationRequest",
            ),
        )
        for other, field in differing:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temporary_directory:
                config_path, cases_directory = self.write_suite(
                    temporary_directory,
                    {"flags": [{"key": "suite-flag", "tags": ["team:checkout"]}]},
                    [self.case(), other],
                )
                with self.assertRaisesRegex(validator.FixtureValidationError, f"case 1 {field} must equal case 0's"):
                    validator._validate_suite(config_path, cases_directory, self.platforms, self_contained=True)

    def test_flag_tags_must_be_a_regular_file(self) -> None:
        flag_tags = {"flags": [{"key": "suite-flag", "tags": ["team:checkout"]}]}
        for kind in ("symlink", "dangling symlink", "directory"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temporary_directory:
                config_path, cases = self.write_suite(temporary_directory, flag_tags, [self.case()])
                flag_tags_path = config_path.parent / "flag-tags.json"
                flag_tags_path.unlink()
                if kind == "directory":
                    flag_tags_path.mkdir()
                else:
                    target = Path(temporary_directory) / "flag-tags-target.json"
                    if kind == "symlink":
                        target.write_text(json.dumps(flag_tags), encoding="utf-8")
                    flag_tags_path.symlink_to(target)
                with self.assertRaisesRegex(validator.FixtureValidationError, "must be a regular file"):
                    validator._validate_suite(config_path, cases, self.platforms, self_contained=True)

    def test_flag_selection_fields_require_flag_tags(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            config_path, cases = self.write_suite(
                temporary_directory, {"flags": [{"key": "suite-flag", "tags": []}]}, [self.case()]
            )
            (config_path.parent / "flag-tags.json").unlink()
            with self.assertRaisesRegex(validator.FixtureValidationError, "require a suite with flag-tags.json"):
                validator._validate_suite(config_path, cases, self.platforms, self_contained=True)

    def test_suite_with_flag_tags_requires_a_configuration_request(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            config_path, cases = self.write_suite(
                temporary_directory,
                {"flags": [{"key": "suite-flag", "tags": []}]},
                [EvaluationSuiteValidationTest.case("suite-flag")],
            )
            with self.assertRaisesRegex(validator.FixtureValidationError, "needs expectations.configurationRequest"):
                validator._validate_suite(config_path, cases, self.platforms, self_contained=True)

    def test_cases_in_a_file_share_one_provider_start(self) -> None:
        other_start = self.case(
            providerOptions={"flagSelection": {"tags": ["team:search"]}},
            expectations={
                "configurationRequest": {"selectedFlagTags": ["team:search"], "selectedFlagKeyPatterns": []}
            },
        )
        for cases in ([self.case(), other_start], [self.case(), EvaluationSuiteValidationTest.case("suite-flag")]):
            with self.subTest(cases=cases), tempfile.TemporaryDirectory() as temporary_directory:
                config_path, cases_directory = self.write_suite(
                    temporary_directory, {"flags": [{"key": "suite-flag", "tags": []}]}, cases
                )
                with self.assertRaisesRegex(validator.FixtureValidationError, "case 1 .* must equal case 0's"):
                    validator._validate_suite(config_path, cases_directory, self.platforms, self_contained=True)


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
