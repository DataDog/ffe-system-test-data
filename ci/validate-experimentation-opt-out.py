#!/usr/bin/env python3
"""Validate the versioned experimentation opt-out contract, not an evaluator."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

REPOSITORY = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPOSITORY / "schemas/experimentation-opt-out.schema.json"
SUITE = REPOSITORY / "experimentation-opt-out/v1"
CAPABILITY = "experimentation-opt-out-v1"


class ContractError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ContractError(message)


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def load(path):
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=unique_object,
            parse_constant=lambda value: (_ for _ in ()).throw(ContractError(f"invalid JSON constant {value}")),
        )
    except (ValueError, OSError) as error:
        raise ContractError(f"{path}: {error}") from error


def validator():
    schema = load(SCHEMA_PATH)
    precomputed = load(REPOSITORY / "schemas/precomputed-assignment.schema.json")
    Draft202012Validator.check_schema(schema)
    registry = Registry().with_resources([
        (schema["$id"], Resource.from_contents(schema)),
        ("https://github.com/DataDog/ffe-system-test-data/schemas/precomputed-assignment.schema.json", Resource.from_contents(precomputed)),
    ])
    return Draft202012Validator(schema, registry=registry)


def check_schema(checker, value, location):
    errors = sorted(checker.iter_errors(value), key=lambda error: str(error.absolute_path))
    if errors:
        error = errors[0]
        raise ContractError(f"{location}: schema {list(error.absolute_path)}: {error.message}")


def enabled(options, attributes, option, attribute):
    return options.get(option) is True and attributes.get(attribute) is True


def same_json(left, right):
    """Keep booleans distinct from numeric 0/1, including nested JSON values."""
    if type(left) is bool or type(right) is bool:
        return type(left) is type(right) and left == right
    if isinstance(left, dict) or isinstance(right, dict):
        return isinstance(left, dict) and isinstance(right, dict) and left.keys() == right.keys() and all(
            same_json(left[key], right[key]) for key in left
        )
    if isinstance(left, list) or isinstance(right, list):
        return isinstance(left, list) and isinstance(right, list) and len(left) == len(right) and all(
            same_json(a, b) for a, b in zip(left, right)
        )
    return left == right


def validate_configuration(config, location):
    require(isinstance(config, dict), f"{location}: configuration must be an object")
    require(config.get("format") == "SERVER", f"{location}: expected SERVER UFC")
    require(isinstance(config.get("createdAt"), str), f"{location}: createdAt required")
    require(isinstance(config.get("environment"), dict), f"{location}: environment required")
    flags = config.get("flags")
    require(isinstance(flags, dict) and flags, f"{location}: non-empty flags required")
    if "evaluationCapabilities" in config:
        capabilities = config["evaluationCapabilities"]
        require(isinstance(capabilities, list) and all(isinstance(item, str) for item in capabilities),
                f"{location}: capabilities must be an array of strings")
        require(len(capabilities) == len(set(capabilities)), f"{location}: duplicate capability")
    for key, flag in flags.items():
        require(isinstance(flag, dict), f"{location}: flag must be an object")
        require(flag.get("key") == key, f"{location}: mismatched flag key {key}")
        variants = flag.get("variations")
        require(isinstance(variants, dict), f"{location}: variations required for {key}")
        for variant_key, variant in variants.items():
            require(isinstance(variant, dict), f"{location}: variant must be an object")
            require(variant.get("key") == variant_key, f"{location}: mismatched variant key")
        allocations = flag.get("allocations")
        require(isinstance(allocations, list), f"{location}: allocations required")
        require(all(isinstance(item, dict) for item in allocations), f"{location}: allocation must be an object")
        keys = [allocation.get("key") for allocation in allocations]
        require(len(set(keys)) == len(keys), f"{location}: duplicate allocation key in {key}")
        for allocation in allocations:
            if "doLog" in allocation:
                require(type(allocation["doLog"]) is bool, f"{location}: doLog must be a boolean when present")
            require(isinstance(allocation.get("rules"), list), f"{location}: rules must be an array")
            require(isinstance(allocation.get("splits"), list), f"{location}: splits must be an array")
            for split in allocation["splits"]:
                require(isinstance(split, dict), f"{location}: split must be an object")
                require(split.get("variationKey") in variants, f"{location}: unknown split variant")
                require(type(split.get("serialId")) is int, f"{location}: serialId must be an integer")
                require(isinstance(split.get("shards"), list), f"{location}: shards must be an array")
                require(split.get("reason") in {"STATIC", "SPLIT", "DEFAULT", "TARGETING_MATCH"},
                        f"{location}: invalid split reason")
                for shard in split["shards"]:
                    total = shard.get("totalShards")
                    require(type(total) is int and total > 0, f"{location}: positive totalShards required")
                    require(isinstance(shard.get("salt"), str), f"{location}: shard salt required")
                    for interval in shard["ranges"]:
                        start, end = interval["start"], interval["end"]
                        require(type(start) is int and type(end) is int and 0 <= start < end <= total,
                                f"{location}: invalid shard range")


def validate_evaluation(case, configs):
    location = case["id"]
    require(case["configuration"] in configs, f"{location}: unknown configuration")
    config = configs[case["configuration"]]
    flag = config["flags"].get(case["evaluation"]["flag"])
    require(flag is not None, f"{location}: unknown flag")
    require(flag["variationType"] == case["evaluation"]["variationType"], f"{location}: variation type mismatch")
    kind = case["evaluation"]["variationType"]
    def correct_type(value):
        return {"BOOLEAN": type(value) is bool, "STRING": type(value) is str,
                "INTEGER": type(value) is int, "NUMERIC": type(value) in (int, float),
                "JSON": isinstance(value, dict)}[kind]
    require(correct_type(case["evaluation"]["defaultValue"]), f"{location}: default value type mismatch")
    expected = case["expected"]
    require(correct_type(expected["value"]), f"{location}: expected result type mismatch")
    attributes, options = case["context"]["attributes"], case["providerOptions"]
    opt_out = enabled(options, attributes, "enableExperimentationOptOutParameter", "dd_experimentation_opt_out")
    telemetry = not enabled(options, attributes, "enableEvaluationTelemetryOptOutParameter", "dd_evaluation_telemetry_opt_out")
    require(expected["effectiveExperimentationOptOut"] is opt_out, f"{location}: incorrect strict activation expectation")
    require(expected["evaluationTelemetryEnabled"] is telemetry, f"{location}: incorrect telemetry expectation")
    require(expected["requestEvaluationOptions"] == ({"experimentation_opt_out": True} if opt_out else None),
            f"{location}: incorrect request option expectation")
    compatible = CAPABILITY in config.get("evaluationCapabilities", [])
    missing_log = any("doLog" not in allocation for allocation in flag["allocations"])
    if opt_out and not compatible:
        require(expected["outcome"] == "incompatible-configuration", f"{location}: missing capability must reject exclusion")
    elif opt_out and missing_log:
        require(expected["outcome"] == "invalid-configuration", f"{location}: missing doLog must reject exclusion")
    else:
        require(expected["outcome"] in {"assignment", "no-assignment"}, f"{location}: unexpected configuration rejection")
    assignment = expected["assignment"]
    if expected["outcome"] == "assignment":
        require(assignment is not None, f"{location}: assignment required")
        matching = [allocation for allocation in flag["allocations"] if allocation["key"] == assignment["allocationKey"]]
        require(len(matching) == 1, f"{location}: unknown expected allocation")
        allocation = matching[0]
        matching_splits = [split for split in allocation["splits"]
                           if split["variationKey"] == assignment["variationKey"] and split["serialId"] == assignment["serialId"]]
        require(len(matching_splits) == 1, f"{location}: unknown expected split identity")
        split = matching_splits[0]
        require(assignment["wireReason"] == split["reason"], f"{location}: wire reason differs from configuration")
        require(correct_type(assignment["value"]), f"{location}: assignment value type mismatch")
        require(same_json(assignment["value"], flag["variations"][assignment["variationKey"]]["value"]),
                f"{location}: expected variant value differs from configuration")
        require("doLog" in allocation, f"{location}: universal assignment cases require explicit doLog; use a per-adapter baseline test for missing doLog")
        require(assignment["doLog"] is allocation["doLog"], f"{location}: expected doLog differs from configuration")
        require(assignment.get("features", []) == split.get("features", []), f"{location}: expected features differ from configuration")
        require(not (opt_out and assignment["doLog"]), f"{location}: excluded subject cannot receive experimental assignment")
        require(same_json(expected["value"], assignment["value"]), f"{location}: result value mismatch")
    else:
        require(assignment is None, f"{location}: rejected/no-assignment case cannot have an assignment")
        require(same_json(expected["value"], case["evaluation"]["defaultValue"]), f"{location}: must use application default")
    events = case["expectations"]
    require(events.get("noUnmatchedEvents") is True, f"{location}: exact event coverage required")
    exposure_count = sum(matcher["_count"] for matcher in events.get("exposures", []))
    evaluation_count = sum(matcher["_count"] for matcher in events.get("evaluationEvents", []))
    require(exposure_count == int(assignment is not None and assignment["doLog"]), f"{location}: exposure count mismatch")
    require(evaluation_count == int(telemetry), f"{location}: evaluation event count mismatch")


def validate_protocol(case):
    location = case["id"]
    attributes = case["message"].get("data", {}).get("attributes")
    require(isinstance(attributes, dict), f"{location}: envelope attributes required")
    present = "evaluation_options" in attributes
    options = attributes.get("evaluation_options")
    valid_shape = not present or isinstance(options, dict)
    value_present = isinstance(options, dict) and "experimentation_opt_out" in options
    value = options.get("experimentation_opt_out") if isinstance(options, dict) else None
    valid_type = not value_present or type(value) is bool
    actual = value if value_present and valid_type else False
    accepted = valid_shape and valid_type
    is_response = case["operation"] == "response-validation"
    if is_response:
        accepted = accepted and actual is case["requestedOptOut"]
    expected = case["expected"]
    require(expected["accepted"] is accepted, f"{location}: invalid protocol acceptance expectation")
    require(expected["effectiveExperimentationOptOut"] is (actual if accepted else None),
            f"{location}: invalid effective option expectation")
    require(expected["publishAssignments"] is (accepted and is_response), f"{location}: invalid publication expectation")


def validate_sequence(sequence, cases):
    location = sequence["id"]
    requests, completed, caches = set(), set(), set()
    for index, step in enumerate(sequence["steps"]):
        at = f"{location} step {index}"
        action = step["action"]
        for field in ("caseId", "expectedPublishedCase"):
            if step.get(field) is not None:
                require(step[field] in cases, f"{at}: unknown case {step[field]}")
                case = cases[step[field]]
                require(case["evaluation"]["flag"] == sequence["flag"], f"{at}: case flag mismatch")
                require(case["expected"]["outcome"] == "assignment", f"{at}: sequence case must supply an assignment")
        if action == "start-request":
            require(step["requestId"] not in requests, f"{at}: duplicate request ID")
            requests.add(step["requestId"])
        if action in {"deliver-response", "fail-request"}:
            request = step["requestId"]
            require(request in requests and request not in completed, f"{at}: unknown/already completed request")
            completed.add(request)
        if action == "persist-cache":
            require(step["cacheId"] not in caches, f"{at}: duplicate cache ID")
            caches.add(step["cacheId"])
        if action == "restart":
            require(step["cacheId"] in caches, f"{at}: unknown cache")
        if action == "evaluate":
            case = cases.get(step["caseId"])
            value = case["expected"]["value"] if case else sequence["defaultValue"]
            require(same_json(step["expectedValue"], value), f"{at}: evaluation value does not match referenced case")
    require(requests == completed, f"{location}: every started request must complete or fail")


def validate(root=SUITE):
    root = Path(root)
    checker = validator()
    manifest = load(root / "manifest.json")
    check_schema(checker, manifest, "manifest")
    require(manifest["kind"] == "manifest", "manifest: wrong artifact kind")
    configs = {}
    listed_files = {"manifest.json"}
    for entry in manifest["configurations"]:
        require(entry["id"] not in configs, "manifest: duplicate configuration ID")
        require(entry["path"] not in listed_files, "manifest: duplicate path")
        listed_files.add(entry["path"])
        config = load(root / entry["path"])
        validate_configuration(config, entry["id"])
        configs[entry["id"]] = config
    all_cases = {}
    artifacts = {}
    for section, kind in [("evaluationCases", "evaluation"), ("protocolCases", "protocol"), ("sequences", "sequence")]:
        collected = []
        for entry in manifest[section]:
            require(entry["path"] not in listed_files, "manifest: duplicate path")
            listed_files.add(entry["path"])
            value = load(root / entry["path"])
            values = [value] if kind == "sequence" else value
            require(isinstance(values, list) and values, f"{entry['path']}: non-empty artifact list required")
            ids = []
            for artifact in values:
                check_schema(checker, artifact, entry["path"])
                require(artifact["kind"] == kind, f"{entry['path']}: wrong artifact kind")
                identifier = artifact["id"]
                require(identifier not in all_cases, f"duplicate artifact ID {identifier}")
                ids.append(identifier)
                all_cases[identifier] = artifact
                collected.append(artifact)
            require(ids == entry["ids"], f"{entry['path']}: manifest IDs/order do not match")
        artifacts[kind] = collected
    actual_files = {str(path.relative_to(root)) for path in root.rglob("*.json")}
    require(actual_files == listed_files, f"manifest file coverage mismatch: missing={listed_files - actual_files}, unlisted={actual_files - listed_files}")
    counts = {"configurations": len(configs), "evaluations": len(artifacts["evaluation"]),
              "protocols": len(artifacts["protocol"]), "sequences": len(artifacts["sequence"])}
    require(counts == manifest["expectedCounts"], f"manifest counts differ: actual={counts}")
    for case in artifacts["evaluation"]:
        validate_evaluation(case, configs)
    for case in artifacts["protocol"]:
        validate_protocol(case)
    evaluations = {case["id"]: case for case in artifacts["evaluation"]}
    for sequence in artifacts["sequence"]:
        validate_sequence(sequence, evaluations)
    invariants = manifest["invariants"]
    parity_ids = {case["id"] for case in evaluations.values() if "eligible-parity" in case["tags"]}
    require(set(invariants["eligibleParityCaseIds"]) == parity_ids, "eligible parity manifest must cover every parity case")
    for identifier in invariants["eligibleParityCaseIds"] + invariants["concurrentServerCaseIds"]:
        require(identifier in evaluations, f"invariants: unknown evaluation {identifier}")
    concurrent = [evaluations[identifier]["expected"]["effectiveExperimentationOptOut"] for identifier in invariants["concurrentServerCaseIds"]]
    require(set(concurrent) == {False, True}, "concurrent cases must exercise both participation states")
    bucketing = manifest["bucketing"]
    subjects = set()
    for vector in bucketing["vectors"]:
        subject = vector["targetingKey"]
        require(subject not in subjects, "bucketing: duplicate subject")
        subjects.add(subject)
        digest = hashlib.md5(f"{bucketing['salt']}-{subject}".encode(), usedforsecurity=False).digest()
        require(digest.hex() == vector["md5"], f"bucketing: digest mismatch for {subject}")
        require(int.from_bytes(digest[:4], "big") % bucketing["totalShards"] == vector["shard"],
                f"bucketing: shard mismatch for {subject}")
    require({evaluations[identifier]["context"]["targetingKey"] for identifier in parity_ids} == subjects,
            "bucketing vectors must cover exactly the parity subjects")
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=SUITE)
    args = parser.parse_args()
    try:
        counts = validate(args.root)
    except ContractError as error:
        raise SystemExit(f"experimentation opt-out validation failed: {error}") from error
    print("Validated experimentation-opt-out/v1: " + ", ".join(f"{value} {key}" for key, value in counts.items()))
    print("This validates contract data. It does not prove compiler, evaluator, or SDK conformance.")


if __name__ == "__main__":
    main()
