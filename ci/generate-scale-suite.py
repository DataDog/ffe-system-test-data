#!/usr/bin/env python3
"""Generates evaluation-suites/scale: synthetic, deterministic fixtures at large sizes.

Each expected result follows from the rule design (which allocation matches), not from an SDK
run. No flag uses shards, so no result depends on a hash.

Usage:
  python3 ci/generate-scale-suite.py --write   # regenerate the suite files
  python3 ci/generate-scale-suite.py --check   # fail if the files differ from the generator
"""
import argparse
import json
import random
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SUITE = REPOSITORY_ROOT / "evaluation-suites" / "scale"
STRING_DEFAULT = "default"
JSON_DEFAULT = {"default": True}


def render(doc):
    return json.dumps(doc, indent=2, ensure_ascii=False, separators=(",", ": ")) + "\n"


def build():
    """Returns {relative path: file text} for the whole suite."""
    flags = {}
    cases = {}

    def add_flag(key, variation_type, variations, allocations):
        flags[key] = {
            "key": key,
            "enabled": True,
            "variationType": variation_type,
            "variations": {name: {"key": name, "value": value} for name, value in variations.items()},
            "allocations": allocations,
        }

    def allocation(key, variation, conditions=None):
        return {
            "key": key,
            "rules": [] if conditions is None else [{"conditions": conditions}],
            "splits": [{"variationKey": variation, "shards": []}],
            "doLog": False,
        }

    def cond(attribute, operator, value):
        return {"attribute": attribute, "operator": operator, "value": value}

    def case(file, flag, attributes, value, reason, variation_type="STRING", default=STRING_DEFAULT):
        cases.setdefault(file, []).append(
            {
                "flag": flag,
                "variationType": variation_type,
                "defaultValue": default,
                "targetingKey": "scale-subject",
                "attributes": attributes,
                "result": {"value": value, "reason": reason},
            }
        )

    # ONE_OF and NOT_ONE_OF with 10,000 entries. The server sorts lists in byte order;
    # zero-padded keys and same-width numbers are already sorted.
    accounts = [f"acct-{i:05d}" for i in range(10_000)]
    numbers = [str(1_000_000 + 7 * i) for i in range(10_000)]

    add_flag(
        "scale-one-of-strings", "STRING", {"listed": "listed", "unlisted": "unlisted"},
        [allocation("listed-accounts", "listed", [cond("account", "ONE_OF", accounts)]),
         allocation("fallback", "unlisted")],
    )
    f = "one-of.json"
    case(f, "scale-one-of-strings", {"account": "acct-00000"}, "listed", "TARGETING_MATCH")
    case(f, "scale-one-of-strings", {"account": "acct-05000"}, "listed", "TARGETING_MATCH")
    case(f, "scale-one-of-strings", {"account": "acct-09999"}, "listed", "TARGETING_MATCH")
    case(f, "scale-one-of-strings", {"account": "acct-10000"}, "unlisted", "STATIC")
    case(f, "scale-one-of-strings", {"account": "ACCT-00001"}, "unlisted", "STATIC")
    case(f, "scale-one-of-strings", {"account": "acct-0001"}, "unlisted", "STATIC")
    case(f, "scale-one-of-strings", {}, "unlisted", "STATIC")

    add_flag(
        "scale-not-one-of-strings", "STRING", {"outside": "outside", "inside": "inside"},
        [allocation("outside-accounts", "outside", [cond("account", "NOT_ONE_OF", accounts)]),
         allocation("fallback", "inside")],
    )
    case(f, "scale-not-one-of-strings", {"account": "acct-04242"}, "inside", "STATIC")
    case(f, "scale-not-one-of-strings", {"account": "acct-99999"}, "outside", "TARGETING_MATCH")

    add_flag(
        "scale-one-of-numbers", "STRING", {"listed": "listed", "unlisted": "unlisted"},
        [allocation("listed-numbers", "listed", [cond("account_num", "ONE_OF", numbers)]),
         allocation("fallback", "unlisted")],
    )
    case(f, "scale-one-of-numbers", {"account_num": 1_000_042}, "listed", "TARGETING_MATCH")
    case(f, "scale-one-of-numbers", {"account_num": 1_069_993}, "listed", "TARGETING_MATCH")
    case(f, "scale-one-of-numbers", {"account_num": 1_000_043}, "unlisted", "STATIC")
    case(f, "scale-one-of-numbers", {"account_num": "1000042"}, "listed", "TARGETING_MATCH")

    # Regex with long inputs and many duplicate patterns.
    add_flag(
        "scale-regex-wildcard", "STRING", {"match": "match", "no-match": "no-match"},
        [allocation("wildcard", "match", [cond("email", "MATCHES", ".*@(alpha|bravo)\\.(example|test)$")]),
         allocation("fallback", "no-match")],
    )
    f = "regex.json"
    case(f, "scale-regex-wildcard", {"email": "x" * 2048}, "no-match", "STATIC")
    case(f, "scale-regex-wildcard", {"email": "a" * 2000 + "@bravo.test"}, "match", "TARGETING_MATCH")
    case(f, "scale-regex-wildcard", {"email": "a" * 2000 + "@alpha.test.invalid"}, "no-match", "STATIC")

    add_flag(
        "scale-regex-charclass", "STRING", {"match": "match", "no-match": "no-match"},
        [allocation("charclass", "match", [cond("email", "MATCHES", "^[a-zA-Z0-9._%+-]+@scale\\.test$")]),
         allocation("fallback", "no-match")],
    )
    case(f, "scale-regex-charclass", {"email": "a.b" * 700 + "@other.test"}, "no-match", "STATIC")
    case(f, "scale-regex-charclass", {"email": "a" * 2048 + "@scale.test"}, "match", "TARGETING_MATCH")
    case(f, "scale-regex-charclass", {"email": "a" * 1024 + "!" + "a" * 1024 + "@scale.test"}, "no-match", "STATIC")

    # Each duplicate allocation has its own variation, so a result shows which allocation won.
    duplicate_allocations = [
        allocation(f"duplicate-{i:03d}", f"dup-{i:03d}", [cond("tenant", "MATCHES", f"^tenant-{i % 10}-[0-9]+$")])
        for i in range(300)
    ]
    add_flag(
        "scale-regex-duplicates", "STRING",
        {**{f"dup-{i:03d}": f"dup-{i:03d}" for i in range(300)}, "final": "final", "none": "none"},
        duplicate_allocations
        + [allocation("final", "final", [cond("tenant", "MATCHES", "^final-[0-9]+$")]), allocation("fallback", "none")],
    )
    case(f, "scale-regex-duplicates", {"tenant": "final-123"}, "final", "TARGETING_MATCH")
    case(f, "scale-regex-duplicates", {"tenant": "tenant-3-77"}, "dup-003", "TARGETING_MATCH")
    case(f, "scale-regex-duplicates", {"tenant": "tenant-0-1"}, "dup-000", "TARGETING_MATCH")
    case(f, "scale-regex-duplicates", {"tenant": "tenant-9-0"}, "dup-009", "TARGETING_MATCH")
    case(f, "scale-regex-duplicates", {"tenant": "nobody"}, "none", "STATIC")

    # 20 allocations of 5 conditions. The condition that tells the allocations apart comes last,
    # so an evaluator that stops at the first failed condition still runs all 5 in each rule.
    deep = [
        allocation(f"rule-{i:02d}", f"rule-{i:02d}", [
            cond("age", "GTE", 18),
            cond("age", "LT", 65),
            cond("plan", "ONE_OF", ["pro", "team"]),
            cond("email", "MATCHES", "@deep\\.test$"),
            cond("country", "ONE_OF", [f"c{i:02d}"]),
        ])
        for i in range(20)
    ]
    add_flag(
        "scale-deep-rules", "STRING",
        {**{f"rule-{i:02d}": f"rule-{i:02d}" for i in range(20)}, "fallback": "fallback"},
        deep + [allocation("fallback", "fallback")],
    )
    f = "rules.json"
    member = {"country": "c19", "age": 30, "plan": "pro", "email": "user@deep.test"}
    case(f, "scale-deep-rules", member, "rule-19", "TARGETING_MATCH")
    case(f, "scale-deep-rules", {**member, "country": "c07"}, "rule-07", "TARGETING_MATCH")
    case(f, "scale-deep-rules", {**member, "age": 70}, "fallback", "STATIC")
    case(f, "scale-deep-rules", {**member, "email": "user@deep.test.example"}, "fallback", "STATIC")

    # Wide evaluation context.
    add_flag(
        "scale-wide-context", "STRING", {"matched": "matched", "fallback": "fallback"},
        [allocation("last-attribute", "matched", [cond("a0199", "ONE_OF", ["v0199"])]), allocation("fallback", "fallback")],
    )
    f = "wide-context.json"
    wide = {f"a{i:04d}": f"v{i:04d}" for i in range(200)}
    case(f, "scale-wide-context", wide, "matched", "TARGETING_MATCH")
    case(f, "scale-wide-context", {**wide, "a0199": "other"}, "fallback", "STATIC")

    # Large JSON values.
    rng = random.Random(20261116)

    def scalar(i):
        kind = i % 5
        if kind == 0:
            return f"text-{rng.randrange(1_000_000):06d}-é-日本"
        if kind == 1:
            return rng.randrange(-1_000_000, 1_000_000)
        if kind == 2:
            return rng.randrange(0, 4096) / 8  # exact in binary floating point
        if kind == 3:
            return rng.random() < 0.5
        return None

    large = {"variant": "large"}
    for i in range(120):
        large[f"field{i:03d}"] = scalar(i)
    large["sections"] = [{f"s{j}": scalar(j) for j in range(8)} for _ in range(60)]
    large["matrix"] = [[rng.randrange(100) for _ in range(10)] for _ in range(5)]
    wide_json = {f"k{i:04d}": scalar(i) for i in range(2000)}
    deep_json = {"level": 16, "leaf": True}
    for level in range(15, 0, -1):
        deep_json = {"level": level, "child": deep_json}

    add_flag("scale-json-large", "JSON", {"large": large}, [allocation("static", "large")])
    add_flag("scale-json-wide", "JSON", {"wide": wide_json}, [allocation("static", "wide")])
    add_flag("scale-json-deep", "JSON", {"deep": deep_json}, [allocation("static", "deep")])
    f = "json-values.json"
    for key, value in (("scale-json-large", large), ("scale-json-wide", wide_json), ("scale-json-deep", deep_json)):
        case(f, key, {}, value, "STATIC", variation_type="JSON", default=JSON_DEFAULT)

    files = {
        "ufc-config.json": render({
            "createdAt": "2026-11-16T00:00:00.000Z",
            "format": "SERVER",
            "environment": {"name": "Test"},
            "flags": flags,
        })
    }
    for name, items in cases.items():
        files[f"cases/{name}"] = render(items)
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="regenerate the suite files")
    mode.add_argument("--check", action="store_true", help="fail if the files differ from the generator")
    args = parser.parse_args()

    expected = build()
    if args.write:
        for relative, text in expected.items():
            path = SUITE / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        for path in sorted((SUITE / "cases").glob("*.json")):
            if f"cases/{path.name}" not in expected:
                path.unlink()
        print(f"Wrote {len(expected)} files to {SUITE.relative_to(REPOSITORY_ROOT)}")
        return 0

    actual = {
        str(path.relative_to(SUITE)): path.read_text(encoding="utf-8")
        for path in [SUITE / "ufc-config.json", *sorted((SUITE / "cases").glob("*.json"))]
        if path.exists()
    }
    stale = sorted(name for name in expected.keys() | actual.keys() if expected.get(name) != actual.get(name))
    if stale:
        print("The scale suite differs from ci/generate-scale-suite.py: " + ", ".join(stale), file=sys.stderr)
        print("Run: python3 ci/generate-scale-suite.py --write", file=sys.stderr)
        return 1
    print(f"The scale suite matches the generator ({len(expected)} files).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
