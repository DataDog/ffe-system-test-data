#!/usr/bin/env python3
"""Validate immediate opt-out fixture shape without implementing an evaluator."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "experimentation-opt-out" / "immediate-v1"


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load(path):
    return json.loads(path.read_text(), object_pairs_hook=unique_object)


def check(condition, message):
    if not condition:
        raise ValueError(message)


def valid_value(kind, value):
    return {
        "BOOLEAN": type(value) is bool,
        "STRING": isinstance(value, str),
        "INTEGER": type(value) in (int, float) and int(value) == value,
        "NUMERIC": type(value) in (int, float),
        "JSON": isinstance(value, dict),
    }.get(kind, False)


def validate(config, cases):
    check(config["format"] == "SERVER", "expected SERVER UFC")
    flags = config["flags"]
    check(isinstance(flags, dict) and flags, "flags must not be empty")
    for key, flag in flags.items():
        check(flag["key"] == key, f"flag key mismatch: {key}")
        check(type(flag["enabled"]) is bool, f"{key}: enabled must be boolean")
        allocations = set()
        for variant_key, variant in flag["variations"].items():
            check(variant["key"] == variant_key, f"{key}: variant key mismatch")
            check(valid_value(flag["variationType"], variant["value"]), f"{key}: variant type mismatch")
        for allocation in flag["allocations"]:
            check(allocation["key"] not in allocations, f"{key}: duplicate allocation key")
            allocations.add(allocation["key"])
            check("doLog" not in allocation or type(allocation["doLog"]) is bool, f"{key}: invalid doLog")
            for split in allocation["splits"]:
                check(split["variationKey"] in flag["variations"], f"{key}: unknown split variant")

    check(isinstance(cases, list) and cases, "cases must not be empty")
    ids = set()
    evaluations = 0
    for case in cases:
        case_id = case["id"]
        check(isinstance(case_id, str) and case_id and case_id not in ids, "case IDs must be unique")
        ids.add(case_id)
        options = case["providerOptions"]
        check(set(options) <= {"experimentationOptOutMode", "enableEvaluationTelemetryOptOutParameter"}, f"{case_id}: unknown provider option")
        check(options.get("experimentationOptOutMode", "DISABLED") in ("DISABLED", "IMMEDIATE"), f"{case_id}: invalid mode")
        check(type(options.get("enableEvaluationTelemetryOptOutParameter", False)) is bool, f"{case_id}: invalid telemetry option")
        check(isinstance(case["evaluations"], list) and case["evaluations"], f"{case_id}: missing evaluations")
        previous = {"exposureCount": 0, "evaluationCount": 0}
        for step in case["evaluations"]:
            flag = flags[step["flag"]]
            kind = step["variationType"]
            check(kind == flag["variationType"], f"{case_id}: getter type mismatch")
            check(valid_value(kind, step["defaultValue"]) and valid_value(kind, step["result"]["value"]), f"{case_id}: result/default type mismatch")
            check(isinstance(step["targetingKey"], str), f"{case_id}: targetingKey must be a string")
            check(isinstance(step["attributes"], dict), f"{case_id}: attributes must be an object")
            result = step["result"]
            check(result["reason"] in ("STATIC", "SPLIT", "TARGETING_MATCH", "DEFAULT", "DISABLED", "ERROR"), f"{case_id}: invalid reason")
            check((result["reason"] == "ERROR") == (result.get("errorCode") == "INVALID_CONTEXT"), f"{case_id}: error code mismatch")
            check(result["allocationKey"] is None or result["allocationKey"] in {a["key"] for a in flag["allocations"]}, f"{case_id}: unknown allocation")
            for counter in previous:
                value = step[counter]
                check(type(value) is int and previous[counter] <= value <= previous[counter] + 1, f"{case_id}: invalid cumulative {counter}")
                previous[counter] = value
            evaluations += 1
    return len(cases), evaluations


if __name__ == "__main__":
    try:
        scenarios, evaluations = validate(load(SUITE / "ufc-config.json"), load(SUITE / "cases.json"))
        print(f"Validated {scenarios} immediate opt-out scenarios and {evaluations} evaluations.")
    except (ValueError, KeyError, TypeError) as error:
        raise SystemExit(f"immediate opt-out validation failed: {error}") from error
