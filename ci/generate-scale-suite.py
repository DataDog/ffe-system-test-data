#!/usr/bin/env python3
"""Generates evaluation-suites/scale and evaluation-suites/scale-json: synthetic, deterministic fixtures at large sizes.

Each expected result follows from the rule design (which allocation matches), not from an SDK
run. Flags with shards compute the shard here with the shared UFC hash, so a result that depends on
a hash is still derived, not recorded.

Usage:
  python3 ci/generate-scale-suite.py --write   # regenerate the suite files
  python3 ci/generate-scale-suite.py --check   # fail if the files differ from the generator

See evaluation-suites/scale/AGENTS.md for how to add a dimension.
"""
import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SUITES_ROOT = REPOSITORY_ROOT / "evaluation-suites"
SUITES = ("scale", "scale-json")
STRING_DEFAULT = "default"
JSON_DEFAULT = {"default": True}
TARGETING_KEY = "scale-subject"
CREATED_AT = "2026-11-16T00:00:00.000Z"
EXPIRED_AT = "2020-01-01T00:00:00.000Z"
FUTURE_AT = "2099-01-01T00:00:00.000Z"
TOTAL_SHARDS = 10_000


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def render_config(flags):
    """One flag per line, so a diff names the flags that changed."""
    lines = [f"  {compact(key)}:{compact(flag)}" for key, flag in flags.items()]
    header = f'{{"createdAt":{compact(CREATED_AT)},"format":"SERVER","environment":{{"name":"Test"}},"flags":{{\n'
    return header + ",\n".join(lines) + "\n}}\n"


def render_cases(items):
    """One case per line."""
    return "[\n" + ",\n".join(f"  {compact(item)}" for item in items) + "\n]\n"


def shard(salt, targeting_key, total=TOTAL_SHARDS):
    """The UFC shard: the first 8 hex digits of md5("<salt>-<targetingKey>") modulo the shard count."""
    digest = hashlib.md5(f"{salt}-{targeting_key}".encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % total


def in_ranges(value, ranges):
    return any(start <= value < end for start, end in ranges)


def first_key(predicate, prefix="subject"):
    """The first targeting key subject-<n> for which predicate(key) holds."""
    n = 0
    while not predicate(f"{prefix}-{n}"):
        n += 1
    return f"{prefix}-{n}"


class Suite:
    def __init__(self):
        self.flags = {}
        self.cases = {}

    def flag(self, key, variation_type, variations, allocations, enabled=True):
        assert key not in self.flags, key
        self.flags[key] = {
            "key": key,
            "enabled": enabled,
            "variationType": variation_type,
            "variations": {name: {"key": name, "value": value} for name, value in variations.items()},
            "allocations": allocations,
        }

    def case(self, file, flag, attributes, value, reason, variation_type="STRING", default=STRING_DEFAULT,
             targeting_key=TARGETING_KEY):
        assert flag in self.flags, flag
        self.cases.setdefault(file, []).append(
            {
                "flag": flag,
                "variationType": variation_type,
                "defaultValue": default,
                "targetingKey": targeting_key,
                "attributes": attributes,
                "result": {"value": value, "reason": reason},
            }
        )

    def files(self):
        out = {"ufc-config.json": render_config(self.flags)}
        for name, items in self.cases.items():
            out[f"cases/{name}"] = render_cases(items)
        return out


def allocation(key, variation, conditions=None, shards=None, **extra):
    """An allocation with one split. conditions is one rule (a list) or several rules (a list of lists)."""
    if conditions is None:
        rules = []
    elif conditions and isinstance(conditions[0], list):
        rules = [{"conditions": rule} for rule in conditions]
    else:
        rules = [{"conditions": conditions}]
    return {
        "key": key,
        "rules": rules,
        "splits": [{"variationKey": variation, "shards": shards or []}],
        "doLog": False,
        **extra,
    }


def shard_spec(salt, ranges, total=TOTAL_SHARDS):
    return {"salt": salt, "totalShards": total, "ranges": [{"start": s, "end": e} for s, e in ranges]}


def cond(attribute, operator, value):
    return {"attribute": attribute, "operator": operator, "value": value}


def names(prefix, count):
    return {f"{prefix}-{i:04d}": f"{prefix}-{i:04d}" for i in range(count)}


# ---------------------------------------------------------------------------------------------
# scale: structure at large N and N x M. Small values, so the cost is in targeting.
# ---------------------------------------------------------------------------------------------


def lists(s):
    # ONE_OF and NOT_ONE_OF with 10,000 entries. The server sorts lists in byte order;
    # zero-padded keys and same-width numbers are already sorted.
    accounts = [f"acct-{i:05d}" for i in range(10_000)]
    numbers = [str(1_000_000 + 7 * i) for i in range(10_000)]
    f = "one-of.json"

    s.flag("scale-one-of-strings", "STRING", {"listed": "listed", "unlisted": "unlisted"},
           [allocation("listed-accounts", "listed", [cond("account", "ONE_OF", accounts)]),
            allocation("fallback", "unlisted")])
    s.case(f, "scale-one-of-strings", {"account": "acct-00000"}, "listed", "TARGETING_MATCH")
    s.case(f, "scale-one-of-strings", {"account": "acct-05000"}, "listed", "TARGETING_MATCH")
    s.case(f, "scale-one-of-strings", {"account": "acct-09999"}, "listed", "TARGETING_MATCH")
    s.case(f, "scale-one-of-strings", {"account": "acct-10000"}, "unlisted", "STATIC")
    s.case(f, "scale-one-of-strings", {"account": "ACCT-00001"}, "unlisted", "STATIC")
    s.case(f, "scale-one-of-strings", {"account": "acct-0001"}, "unlisted", "STATIC")
    s.case(f, "scale-one-of-strings", {}, "unlisted", "STATIC")

    s.flag("scale-not-one-of-strings", "STRING", {"outside": "outside", "inside": "inside"},
           [allocation("outside-accounts", "outside", [cond("account", "NOT_ONE_OF", accounts)]),
            allocation("fallback", "inside")])
    s.case(f, "scale-not-one-of-strings", {"account": "acct-04242"}, "inside", "STATIC")
    s.case(f, "scale-not-one-of-strings", {"account": "acct-99999"}, "outside", "TARGETING_MATCH")

    s.flag("scale-one-of-numbers", "STRING", {"listed": "listed", "unlisted": "unlisted"},
           [allocation("listed-numbers", "listed", [cond("account_num", "ONE_OF", numbers)]),
            allocation("fallback", "unlisted")])
    s.case(f, "scale-one-of-numbers", {"account_num": 1_000_042}, "listed", "TARGETING_MATCH")
    s.case(f, "scale-one-of-numbers", {"account_num": 1_069_993}, "listed", "TARGETING_MATCH")
    s.case(f, "scale-one-of-numbers", {"account_num": 1_000_043}, "unlisted", "STATIC")
    s.case(f, "scale-one-of-numbers", {"account_num": "1000042"}, "listed", "TARGETING_MATCH")

    # Allocations x list size: per-tenant targeting. 500 allocations of 100 UUID-shaped accounts.
    rng = random.Random(20261117)
    tenants = []
    for t in range(500):
        members = sorted(f"{rng.getrandbits(128):032x}" for _ in range(100))
        tenants.append([f"{m[:8]}-{m[8:12]}-{m[12:16]}-{m[16:20]}-{m[20:]}" for m in members])
    s.flag("scale-one-of-per-tenant", "STRING", {**names("tenant", 500), "none": "none"},
           [allocation(f"tenant-{t:04d}", f"tenant-{t:04d}", [cond("account_id", "ONE_OF", members)])
            for t, members in enumerate(tenants)] + [allocation("fallback", "none")])
    f = "one-of-many.json"
    s.case(f, "scale-one-of-per-tenant", {"account_id": tenants[0][0]}, "tenant-0000", "TARGETING_MATCH")
    s.case(f, "scale-one-of-per-tenant", {"account_id": tenants[250][50]}, "tenant-0250", "TARGETING_MATCH")
    s.case(f, "scale-one-of-per-tenant", {"account_id": tenants[499][99]}, "tenant-0499", "TARGETING_MATCH")
    s.case(f, "scale-one-of-per-tenant", {"account_id": "00000000-0000-0000-0000-000000000000"}, "none", "STATIC")

    # Long entries: 1,000 strings of 256 characters, so hashing and equality cost is per byte.
    long_values = sorted(f"{i:04d}-" + "x" * 251 for i in range(1_000))
    s.flag("scale-one-of-long-values", "STRING", {"listed": "listed", "unlisted": "unlisted"},
           [allocation("long", "listed", [cond("token", "ONE_OF", long_values)]), allocation("fallback", "unlisted")])
    s.case(f, "scale-one-of-long-values", {"token": long_values[-1]}, "listed", "TARGETING_MATCH")
    s.case(f, "scale-one-of-long-values", {"token": long_values[-1][:-1] + "y"}, "unlisted", "STATIC")

    # Many lists on many attributes: 50 conditions in one rule, each a 200-entry list on its own attribute.
    attribute_lists = {f"dim{d:02d}": [f"d{d:02d}-{i:04d}" for i in range(200)] for d in range(50)}
    s.flag("scale-one-of-many-attributes", "STRING", {"all": "all", "fallback": "fallback"},
           [allocation("all-dimensions", "all", [cond(a, "ONE_OF", v) for a, v in attribute_lists.items()]),
            allocation("fallback", "fallback")])
    member = {a: v[-1] for a, v in attribute_lists.items()}
    s.case(f, "scale-one-of-many-attributes", member, "all", "TARGETING_MATCH")
    s.case(f, "scale-one-of-many-attributes", {**member, "dim49": "d49-9999"}, "fallback", "STATIC")


def regex(s):
    f = "regex.json"
    s.flag("scale-regex-wildcard", "STRING", {"match": "match", "no-match": "no-match"},
           [allocation("wildcard", "match", [cond("email", "MATCHES", ".*@(alpha|bravo)\\.(example|test)$")]),
            allocation("fallback", "no-match")])
    s.case(f, "scale-regex-wildcard", {"email": "x" * 2048}, "no-match", "STATIC")
    s.case(f, "scale-regex-wildcard", {"email": "a" * 2000 + "@bravo.test"}, "match", "TARGETING_MATCH")
    s.case(f, "scale-regex-wildcard", {"email": "a" * 2000 + "@alpha.test.invalid"}, "no-match", "STATIC")

    s.flag("scale-regex-charclass", "STRING", {"match": "match", "no-match": "no-match"},
           [allocation("charclass", "match", [cond("email", "MATCHES", "^[a-zA-Z0-9._%+-]+@scale\\.test$")]),
            allocation("fallback", "no-match")])
    s.case(f, "scale-regex-charclass", {"email": "a.b" * 700 + "@other.test"}, "no-match", "STATIC")
    s.case(f, "scale-regex-charclass", {"email": "a" * 2048 + "@scale.test"}, "match", "TARGETING_MATCH")
    s.case(f, "scale-regex-charclass", {"email": "a" * 1024 + "!" + "a" * 1024 + "@scale.test"}, "no-match", "STATIC")

    # Each duplicate allocation has its own variation, so a result shows which allocation won.
    duplicates = [allocation(f"duplicate-{i:03d}", f"dup-{i:03d}", [cond("tenant", "MATCHES", f"^tenant-{i % 10}-[0-9]+$")])
                  for i in range(300)]
    s.flag("scale-regex-duplicates", "STRING",
           {**{f"dup-{i:03d}": f"dup-{i:03d}" for i in range(300)}, "final": "final", "none": "none"},
           duplicates + [allocation("final", "final", [cond("tenant", "MATCHES", "^final-[0-9]+$")]),
                         allocation("fallback", "none")])
    s.case(f, "scale-regex-duplicates", {"tenant": "final-123"}, "final", "TARGETING_MATCH")
    s.case(f, "scale-regex-duplicates", {"tenant": "tenant-3-77"}, "dup-003", "TARGETING_MATCH")
    s.case(f, "scale-regex-duplicates", {"tenant": "tenant-0-1"}, "dup-000", "TARGETING_MATCH")
    s.case(f, "scale-regex-duplicates", {"tenant": "tenant-9-0"}, "dup-009", "TARGETING_MATCH")
    s.case(f, "scale-regex-duplicates", {"tenant": "nobody"}, "none", "STATIC")

    # 1,000 distinct patterns: compile time and memory at load, one pattern per allocation.
    f = "regex-many.json"
    s.flag("scale-regex-distinct", "STRING", {**names("pattern", 1_000), "none": "none"},
           [allocation(f"pattern-{i:04d}", f"pattern-{i:04d}", [cond("tenant", "MATCHES", f"^org-{i:04d}-[a-z]+-[0-9]{{2,6}}$")])
            for i in range(1_000)] + [allocation("fallback", "none")])
    s.case(f, "scale-regex-distinct", {"tenant": "org-0000-east-12"}, "pattern-0000", "TARGETING_MATCH")
    s.case(f, "scale-regex-distinct", {"tenant": "org-0999-west-123456"}, "pattern-0999", "TARGETING_MATCH")
    s.case(f, "scale-regex-distinct", {"tenant": "org-0999-west-1"}, "none", "STATIC")

    # One pattern with 500 alternatives, which some users write in place of ONE_OF.
    alternatives = [f"t{i:04d}" for i in range(500)]
    s.flag("scale-regex-alternation", "STRING", {"match": "match", "no-match": "no-match"},
           [allocation("alternation", "match", [cond("tenant", "MATCHES", "^(" + "|".join(alternatives) + ")$")]),
            allocation("fallback", "no-match")])
    s.case(f, "scale-regex-alternation", {"tenant": "t0000"}, "match", "TARGETING_MATCH")
    s.case(f, "scale-regex-alternation", {"tenant": "t0499"}, "match", "TARGETING_MATCH")
    s.case(f, "scale-regex-alternation", {"tenant": "t0500"}, "no-match", "STATIC")
    s.case(f, "scale-regex-alternation", {"tenant": "t0499x"}, "no-match", "STATIC")

    # Counted repetition, which a linear-time engine expands into its automaton.
    s.flag("scale-regex-counted", "STRING", {"match": "match", "no-match": "no-match"},
           [allocation("counted", "match", [cond("handle", "MATCHES", "^[a-z]{1,64}(\\.[a-z0-9]{1,32}){0,8}@counted\\.test$")]),
            allocation("fallback", "no-match")])
    s.case(f, "scale-regex-counted", {"handle": "a" * 64 + ".b1" * 8 + "@counted.test"}, "match", "TARGETING_MATCH")
    s.case(f, "scale-regex-counted", {"handle": "a" * 65 + "@counted.test"}, "no-match", "STATIC")
    s.case(f, "scale-regex-counted", {"handle": "a" * 64 + ".b1" * 9 + "@counted.test"}, "no-match", "STATIC")


def rules(s):
    # 20 allocations of 5 conditions. The condition that tells the allocations apart comes last,
    # so an evaluator that stops at the first failed condition still runs all 5 in each rule.
    deep = [allocation(f"rule-{i:02d}", f"rule-{i:02d}", [
        cond("age", "GTE", 18), cond("age", "LT", 65), cond("plan", "ONE_OF", ["pro", "team"]),
        cond("email", "MATCHES", "@deep\\.test$"), cond("country", "ONE_OF", [f"c{i:02d}"]),
    ]) for i in range(20)]
    s.flag("scale-deep-rules", "STRING", {**{f"rule-{i:02d}": f"rule-{i:02d}" for i in range(20)}, "fallback": "fallback"},
           deep + [allocation("fallback", "fallback")])
    f = "rules.json"
    member = {"country": "c19", "age": 30, "plan": "pro", "email": "user@deep.test"}
    s.case(f, "scale-deep-rules", member, "rule-19", "TARGETING_MATCH")
    s.case(f, "scale-deep-rules", {**member, "country": "c07"}, "rule-07", "TARGETING_MATCH")
    s.case(f, "scale-deep-rules", {**member, "age": 70}, "fallback", "STATIC")
    s.case(f, "scale-deep-rules", {**member, "email": "user@deep.test.example"}, "fallback", "STATIC")

    # Allocations x rules x conditions. In each shape the subject matches only the last rule of the
    # last allocation, and each rule fails on its last condition, so every condition runs.
    def shape(allocations, rules_per_allocation, conditions_per_rule):
        key = f"scale-rules-{allocations}x{rules_per_allocation}x{conditions_per_rule}"
        built = []
        for a in range(allocations):
            alloc_rules = []
            for r in range(rules_per_allocation):
                common = [cond(f"attr{c:02d}", "GTE", c) for c in range(conditions_per_rule - 1)]
                alloc_rules.append(common + [cond("slot", "ONE_OF", [f"a{a:03d}-r{r:03d}"])])
            built.append(allocation(f"alloc-{a:03d}", f"alloc-{a:03d}", alloc_rules))
        s.flag(key, "STRING", {**{f"alloc-{a:03d}": f"alloc-{a:03d}" for a in range(allocations)}, "fallback": "fallback"},
               built + [allocation("fallback", "fallback")])
        attributes = {f"attr{c:02d}": 100 for c in range(conditions_per_rule - 1)}
        last = f"alloc-{allocations - 1:03d}"
        s.case(f, key, {**attributes, "slot": f"a{allocations - 1:03d}-r{rules_per_allocation - 1:03d}"}, last, "TARGETING_MATCH")
        s.case(f, key, {**attributes, "slot": "none"}, "fallback", "STATIC")

    f = "rules-sweep.json"
    for dims in ((1, 1, 50), (1, 50, 1), (50, 1, 1), (10, 10, 10), (50, 10, 5)):
        shape(*dims)

    # Semver ladder: 50 allocations, each a version range on the same attribute.
    f = "semver.json"
    ladder = [allocation(f"v1-{i:02d}", f"v1-{i:02d}", [cond("app_version", "SEMVER_GTE", f"1.{i}.0"),
                                                         cond("app_version", "SEMVER_LT", f"1.{i + 1}.0")])
              for i in range(50)]
    s.flag("scale-semver-ladder", "STRING", {**{f"v1-{i:02d}": f"v1-{i:02d}" for i in range(50)}, "fallback": "fallback"},
           ladder + [allocation("fallback", "fallback")])
    s.case(f, "scale-semver-ladder", {"app_version": "1.0.0"}, "v1-00", "TARGETING_MATCH")
    s.case(f, "scale-semver-ladder", {"app_version": "1.49.3"}, "v1-49", "TARGETING_MATCH")
    s.case(f, "scale-semver-ladder", {"app_version": "1.49.3-beta.11.rc-7+build.20261117.sha.0123456789abcdef"}, "v1-49", "TARGETING_MATCH")
    s.case(f, "scale-semver-ladder", {"app_version": "1.50.0-alpha"}, "v1-49", "TARGETING_MATCH")
    s.case(f, "scale-semver-ladder", {"app_version": "2.0.0"}, "fallback", "STATIC")
    s.case(f, "scale-semver-ladder", {"app_version": "not-a-version"}, "fallback", "STATIC")

    # Numeric ladder: 50 allocations, each a GTE/LT range on the same attribute.
    f = "numeric.json"
    s.flag("scale-numeric-ladder", "STRING", {**{f"n-{i:02d}": f"n-{i:02d}" for i in range(50)}, "fallback": "fallback"},
           [allocation(f"n-{i:02d}", f"n-{i:02d}", [cond("score", "GTE", i * 10), cond("score", "LT", (i + 1) * 10)])
            for i in range(50)] + [allocation("fallback", "fallback")])
    s.case(f, "scale-numeric-ladder", {"score": 0}, "n-00", "TARGETING_MATCH")
    s.case(f, "scale-numeric-ladder", {"score": 495.5}, "n-49", "TARGETING_MATCH")
    s.case(f, "scale-numeric-ladder", {"score": 500}, "fallback", "STATIC")

    # Time windows: 100 expired and 100 future allocations before the active one.
    f = "time-windows.json"
    windows = ([allocation(f"expired-{i:03d}", "expired", endAt=EXPIRED_AT) for i in range(100)]
               + [allocation(f"future-{i:03d}", "future", startAt=FUTURE_AT) for i in range(100)]
               + [allocation("active", "active", [cond("plan", "ONE_OF", ["pro"])]), allocation("fallback", "fallback")])
    s.flag("scale-time-windows", "STRING",
           {"expired": "expired", "future": "future", "active": "active", "fallback": "fallback"}, windows)
    s.case(f, "scale-time-windows", {"plan": "pro"}, "active", "TARGETING_MATCH")
    s.case(f, "scale-time-windows", {"plan": "free"}, "fallback", "STATIC")

    # Wide evaluation context.
    f = "wide-context.json"
    s.flag("scale-wide-context", "STRING", {"matched": "matched", "fallback": "fallback"},
           [allocation("last-attribute", "matched", [cond("a0199", "ONE_OF", ["v0199"])]), allocation("fallback", "fallback")])
    wide = {f"a{i:04d}": f"v{i:04d}" for i in range(200)}
    s.case(f, "scale-wide-context", wide, "matched", "TARGETING_MATCH")
    s.case(f, "scale-wide-context", {**wide, "a0199": "other"}, "fallback", "STATIC")

    # The id attribute falls back to the targeting key. 20 rules on id, with a wide context.
    s.flag("scale-id-wide-context", "STRING", {"matched": "matched", "fallback": "fallback"},
           [allocation("id-rules", "matched", [[cond("id", "ONE_OF", [f"user-{r:02d}"])] for r in range(20)]),
            allocation("fallback", "fallback")])
    s.case(f, "scale-id-wide-context", wide, "matched", "TARGETING_MATCH", targeting_key="user-19")
    s.case(f, "scale-id-wide-context", wide, "fallback", "STATIC", targeting_key="user-20")


def splits(s):
    f = "splits.json"

    # Allocations x shards: 50 rollout allocations of 2% each with their own salt, then 100%.
    rollout = [(f"rollout-{i:02d}", [(0, 200)]) for i in range(49)] + [("rollout-49", [(0, TOTAL_SHARDS)])]
    s.flag("scale-rollout-allocations", "STRING", names("rollout", 50),
           [allocation(salt, f"rollout-{i:04d}", shards=[shard_spec(salt, ranges)]) for i, (salt, ranges) in enumerate(rollout)])
    last = first_key(lambda k: not any(in_ranges(shard(salt, k), r) for salt, r in rollout[:-1]))
    s.case(f, "scale-rollout-allocations", {}, "rollout-0049", "SPLIT", targeting_key=last)
    for target in (0, 25):
        salt, ranges = rollout[target]
        key = first_key(lambda k: in_ranges(shard(salt, k), ranges)
                        and not any(in_ranges(shard(sl, k), r) for sl, r in rollout[:target]))
        s.case(f, "scale-rollout-allocations", {}, f"rollout-{target:04d}", "SPLIT", targeting_key=key)

    # Splits x shards: one allocation, 100 splits of 2 shards. The traffic shard has the same salt in
    # every split, so an evaluator can hash it once.
    traffic = [(0, 5_000)]
    variant_ranges = [[(j * 100, (j + 1) * 100)] for j in range(100)]
    split_list = [{"variationKey": f"arm-{j:04d}",
                   "shards": [shard_spec("experiment-traffic", traffic), shard_spec("experiment-arm", variant_ranges[j])]}
                  for j in range(100)]
    s.flag("scale-many-splits", "STRING", {**names("arm", 100), "holdout": "holdout"},
           [{"key": "experiment", "rules": [], "splits": split_list, "doLog": True}, allocation("holdout", "holdout")])
    for arm in (0, 99):
        key = first_key(lambda k: in_ranges(shard("experiment-traffic", k), traffic)
                        and in_ranges(shard("experiment-arm", k), variant_ranges[arm]))
        s.case(f, "scale-many-splits", {}, f"arm-{arm:04d}", "SPLIT", targeting_key=key)
    outside = first_key(lambda k: not in_ranges(shard("experiment-traffic", k), traffic))
    s.case(f, "scale-many-splits", {}, "holdout", "STATIC", targeting_key=outside)

    # Shard ranges: one shard with 1,000 ranges that cover every other block of 5 shards.
    fragmented = [(i * 10, i * 10 + 5) for i in range(1_000)]
    s.flag("scale-shard-ranges", "STRING", {"in": "in", "out": "out"},
           [allocation("fragmented", "in", shards=[shard_spec("fragmented", fragmented)]), allocation("fallback", "out")])
    hit = first_key(lambda k: shard("fragmented", k) >= 9_990 and in_ranges(shard("fragmented", k), fragmented))
    miss = first_key(lambda k: not in_ranges(shard("fragmented", k), fragmented))
    s.case(f, "scale-shard-ranges", {}, "in", "SPLIT", targeting_key=hit)
    s.case(f, "scale-shard-ranges", {}, "out", "STATIC", targeting_key=miss)

    # Rules x shards: 20 targeted rollouts. Each allocation's rule matches, but its shard does not.
    targeted = [(f"targeted-{i:02d}", [(0, 100)]) for i in range(20)]
    s.flag("scale-targeted-rollouts", "STRING", {**names("targeted", 20), "fallback": "fallback"},
           [allocation(salt, f"targeted-{i:04d}", [cond("plan", "ONE_OF", ["pro"])], shards=[shard_spec(salt, ranges)])
            for i, (salt, ranges) in enumerate(targeted)] + [allocation("fallback", "fallback")])
    none = first_key(lambda k: not any(in_ranges(shard(salt, k), r) for salt, r in targeted))
    s.case(f, "scale-targeted-rollouts", {"plan": "pro"}, "fallback", "STATIC", targeting_key=none)

    # Many variations x many allocations, with split features and doLog on every allocation.
    f = "variations.json"
    features = [{"key": f"feature.{i:03d}", "value": f"value-{i:03d}", "destinations": ["HOOK", "EXPOSURE", "EVALUATION"]}
                for i in range(200)]
    allocations = []
    for i in range(1_000):
        alloc = allocation(f"slot-{i:04d}", f"slot-{i:04d}", [cond("slot", "ONE_OF", [f"s{i:04d}"])], doLog=True)
        alloc["splits"][0]["serialId"] = i
        if i == 999:
            alloc["splits"][0]["features"] = features
        allocations.append(alloc)
    s.flag("scale-many-variations", "STRING", {**names("slot", 1_000), "fallback": "fallback"},
           allocations + [allocation("fallback", "fallback")])
    s.case(f, "scale-many-variations", {"slot": "s0000"}, "slot-0000", "TARGETING_MATCH")
    s.case(f, "scale-many-variations", {"slot": "s0999"}, "slot-0999", "TARGETING_MATCH")
    s.case(f, "scale-many-variations", {"slot": "s1000"}, "fallback", "STATIC")


def bulk(s):
    # 10,000 flags: lookup, load time, and heap. Every 10th flag is disabled.
    f = "flags.json"
    for i in range(10_000):
        s.flag(f"scale-bulk-{i:05d}", "BOOLEAN", {"on": True, "off": False},
               [allocation("beta", "on", [cond("cohort", "ONE_OF", [f"cohort-{i % 100:02d}"])]), allocation("fallback", "off")],
               enabled=i % 10 != 9)
    for i, cohort, value, reason in ((0, "cohort-00", True, "TARGETING_MATCH"), (5_000, "cohort-01", False, "STATIC"),
                                     (9_998, "cohort-98", True, "TARGETING_MATCH"), (9_999, "cohort-99", False, "DISABLED")):
        s.case(f, f"scale-bulk-{i:05d}", {"cohort": cohort}, value, reason, variation_type="BOOLEAN", default=False)


# ---------------------------------------------------------------------------------------------
# scale-json: JSON variant values from hundreds of nodes to 10 MB.
# ---------------------------------------------------------------------------------------------


def json_values(s):
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

    f = "json-values.json"
    for key, value in (("scale-json-large", large), ("scale-json-wide", wide_json), ("scale-json-deep", deep_json)):
        s.flag(key, "JSON", {"value": value}, [allocation("static", "value")])
        s.case(f, key, {}, value, "STATIC", variation_type="JSON", default=JSON_DEFAULT)

    # Size sweep of a realistic dynamic config: a list of records with mixed scalar types.
    def records(target_bytes, seed):
        r = random.Random(seed)
        out = {"version": seed, "records": []}
        size = 0
        n = 0
        while size < target_bytes:
            record = {
                "id": n,
                "name": f"line-item-{n:07d}",
                "enabled": r.random() < 0.8,
                "weight": r.randrange(0, 1 << 16) / 64,
                "tags": [f"tag-{r.randrange(1000):03d}" for _ in range(r.randrange(1, 5))],
                "limits": {"daily": r.randrange(10_000_000), "hourly": r.randrange(100_000), "cap": None},
                "label": "Ünïcødé ✓ 広告",
            }
            out["records"].append(record)
            size += len(compact(record).encode("utf-8")) + 1
            n += 1
        return out

    f = "json-sizes.json"
    for key, size in (("scale-json-100kb", 100_000), ("scale-json-1mb", 1_000_000), ("scale-json-10mb", 10_000_000)):
        value = records(size, size)
        s.flag(key, "JSON", {"value": value, "small": {"small": True}},
               [allocation("targeted", "value", [cond("plan", "ONE_OF", ["pro"])]), allocation("fallback", "small")])
        s.case(f, key, {"plan": "pro"}, value, "TARGETING_MATCH", variation_type="JSON", default=JSON_DEFAULT)
        s.case(f, key, {"plan": "free"}, {"small": True}, "STATIC", variation_type="JSON", default=JSON_DEFAULT)

    # Shapes that stress the parser and the conversion: a 100,000-number array, a 1 MB string,
    # and strings full of escapes.
    f = "json-shapes.json"
    r = random.Random(7)
    shapes = {
        "scale-json-number-array": {"values": [r.randrange(-(1 << 31), 1 << 31) for _ in range(100_000)]},
        "scale-json-long-string": {"blob": "".join(r.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(1_000_000))},
        "scale-json-escapes": {f"k{i:04d}": f"quote\" backslash\\ newline\n tab\t control\u0001 separator  emoji😀 {i}"
                               for i in range(5_000)},
        "scale-json-nested-arrays": {"rows": [[[i, j, f"{i}-{j}"] for j in range(50)] for i in range(500)]},
    }
    for key, value in shapes.items():
        s.flag(key, "JSON", {"value": value}, [allocation("static", "value")])
        s.case(f, key, {}, value, "STATIC", variation_type="JSON", default=JSON_DEFAULT)


def build():
    """Returns {path relative to evaluation-suites/: file text} for every scale suite."""
    scale = Suite()
    for part in (lists, regex, rules, splits, bulk):
        part(scale)
    scale_json = Suite()
    json_values(scale_json)
    out = {}
    for name, suite in (("scale", scale), ("scale-json", scale_json)):
        for relative, text in suite.files().items():
            out[f"{name}/{relative}"] = text
    return out


def generated_paths():
    for name in SUITES:
        root = SUITES_ROOT / name
        for path in [root / "ufc-config.json", *sorted((root / "cases").glob("*.json"))]:
            if path.exists():
                yield path


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="regenerate the suite files")
    mode.add_argument("--check", action="store_true", help="fail if the files differ from the generator")
    args = parser.parse_args()

    expected = build()
    if args.write:
        for path in generated_paths():
            if str(path.relative_to(SUITES_ROOT)) not in expected:
                path.unlink()
        for relative, text in expected.items():
            path = SUITES_ROOT / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        print(f"Wrote {len(expected)} files to {SUITES_ROOT.relative_to(REPOSITORY_ROOT)}/{{{','.join(SUITES)}}}")
        return 0

    actual = {str(path.relative_to(SUITES_ROOT)): path.read_text(encoding="utf-8") for path in generated_paths()}
    stale = sorted(name for name in expected.keys() | actual.keys() if expected.get(name) != actual.get(name))
    if stale:
        print("The scale suites differ from ci/generate-scale-suite.py: " + ", ".join(stale), file=sys.stderr)
        print("Run: python3 ci/generate-scale-suite.py --write", file=sys.stderr)
        return 1
    print(f"The scale suites match the generator ({len(expected)} files).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
