# AGENTS.md — Scale suites

This guide is for agents and contributors who add or change the `scale` and
`scale-json` evaluation suites. Both suites are generated. Do not edit their
JSON files by hand.

## What the suites are for

The suites measure evaluator cost at sizes a customer can reach: N of one
thing, or N × M of two. An SDK benchmark loads a suite's `ufc-config.json`,
evaluates its cases, and checks each result before it measures. The expected
results are behavior only. The suites set no time or memory limits.

| Suite | Holds | Why it is separate |
|-------|-------|--------------------|
| `scale` | Targeting structure at large N and N × M: lists, regex, rules, splits, shards, time windows, variations, flag count | The cost is in targeting. The values are small |
| `scale-json` | JSON variant values from hundreds of nodes to 10 MB | A benchmark of targeting must not parse 14 MB of JSON values |

## Files

```
ci/generate-scale-suite.py             # The only source. Edit this file
evaluation-suites/scale/
├── AGENTS.md                          # This guide
├── ufc-config.json                    # Generated. One flag per line
└── cases/<dimension>.json             # Generated. One case per line
evaluation-suites/scale-json/
├── AGENTS.md                          # Points to this guide
├── ufc-config.json
└── cases/<dimension>.json
```

## Commands

```bash
python3 ci/generate-scale-suite.py --write   # regenerate both suites
python3 ci/generate-scale-suite.py --check   # CI: fail if a file differs from the generator
python3 ci/validate-fixtures.py              # CI: validate every suite
```

`--write` also deletes a case file that the generator no longer makes.

## Dimensions

Each case file is one dimension, so a benchmark can select it by name.

| Suite | Case file | Flags | N × M |
|-------|-----------|-------|-------|
| `scale` | `one-of.json` | `scale-one-of-strings`, `scale-not-one-of-strings`, `scale-one-of-numbers` | 1 list × 10,000 entries; string and number attributes |
| `scale` | `one-of-many.json` | `scale-one-of-per-tenant`, `scale-one-of-long-values`, `scale-one-of-many-attributes` | 500 allocations × 100 UUIDs; 1,000 entries × 256 characters; 50 attributes × 200 entries |
| `scale` | `regex.json` | `scale-regex-wildcard`, `scale-regex-charclass`, `scale-regex-duplicates` | 2 KB inputs; 300 conditions × 10 distinct patterns |
| `scale` | `regex-many.json` | `scale-regex-distinct`, `scale-regex-alternation`, `scale-regex-counted` | 1,000 distinct patterns; 500 alternatives; counted repetition |
| `scale` | `rules.json` | `scale-deep-rules` | 20 allocations × 5 conditions |
| `scale` | `rules-sweep.json` | `scale-rules-<A>x<R>x<C>` | allocations × rules × conditions: 1×1×50, 1×50×1, 50×1×1, 10×10×10, 50×10×5 |
| `scale` | `semver.json` | `scale-semver-ladder` | 50 allocations × 2 SemVer conditions on one attribute |
| `scale` | `numeric.json` | `scale-numeric-ladder` | 50 allocations × 2 numeric conditions on one attribute |
| `scale` | `time-windows.json` | `scale-time-windows` | 100 expired + 100 future allocations before the active one |
| `scale` | `wide-context.json` | `scale-wide-context`, `scale-id-wide-context` | 200 context attributes; 20 rules on `id` with that context |
| `scale` | `splits.json` | `scale-rollout-allocations`, `scale-many-splits`, `scale-shard-ranges`, `scale-targeted-rollouts` | 50 allocations × 1 shard; 100 splits × 2 shards; 1 shard × 1,000 ranges; 20 rules × 1 shard |
| `scale` | `variations.json` | `scale-many-variations` | 1,000 variations × 1,000 allocations, `doLog`, serial IDs, 200 split features |
| `scale` | `flags.json` | `scale-bulk-00000` … `scale-bulk-09999` | 10,000 flags, every 10th disabled |
| `scale-json` | `json-values.json` | `scale-json-large`, `scale-json-wide`, `scale-json-deep` | 719 nodes; 2,000 keys; 16 levels |
| `scale-json` | `json-sizes.json` | `scale-json-100kb`, `scale-json-1mb`, `scale-json-10mb` | A list of records at 100 KB, 1 MB, and 10 MB, behind a targeting rule |
| `scale-json` | `json-shapes.json` | `scale-json-number-array`, `scale-json-long-string`, `scale-json-escapes`, `scale-json-nested-arrays` | 100,000 numbers; a 1 MB string; 5,000 escaped strings; 500 × 50 nested arrays |

## Design rules

These rules keep each expected result derived, not recorded from an SDK run.

1. **Worst case first.** Put the matching element last: the last allocation,
   the last rule, the last condition, the last split, the last range. Add a
   case that matches the first element and a case that matches nothing, so a
   benchmark sees the best case, the worst case, and a miss.
2. **One variation per allocation** when a flag has many allocations, so the
   result names the allocation that won.
3. **Derive shard results.** Use `shard()` and `first_key()`. `shard()` is the
   UFC hash: the first 8 hex digits of `md5("<salt>-<targetingKey>")`, modulo
   `totalShards`. `first_key()` finds the first `subject-<n>` with the property
   you need, for example "outside every earlier rollout". Never write a
   targeting key by hand for a sharded flag.
4. **Know the reason rules.** A matched allocation with rules is
   `TARGETING_MATCH`. Without rules, a split with shards is `SPLIT`, and a split
   without shards is `STATIC`. A time-windowed allocation without rules and with
   one unsharded split is `DEFAULT`; avoid that shape, or give the allocation a
   rule. A disabled flag is `DISABLED` with the caller default.
5. **Sort lists in UTF-8 byte order**, as the server does. Zero-padded keys and
   same-width numbers are already sorted. Sort random values (see the UUIDs).
6. **Seed every random source** with a fixed `random.Random(<seed>)`. Never use
   the module-level `random`, the time, or the environment.
7. **Use only root-configuration syntax.** A new operator or field belongs in
   the core suite first. Use regex syntax that the JDK, RE2, and the Rust
   `regex` crate all accept with the same meaning. The `regex` suite covers
   dialect differences.
8. **Keep JSON numbers portable.** Integers within ±2^53, and floats that are
   exact in binary (for example `n / 8`). The core case
   `test-json-number-precision.json` covers integers above 2^53.
9. **Keep values synthetic.** No customer data, no real domains (use `.test`).

## Adding a dimension

1. Pick the suite: targeting structure goes in `scale`, large values go in
   `scale-json`.
2. Write the flags and cases in a function in `ci/generate-scale-suite.py`, or
   add them to the function for that area (`lists`, `regex`, `rules`, `splits`,
   `bulk`, `json_values`). Use a new case file name for a new dimension.
3. Run `--write`, then `--check` and `ci/validate-fixtures.py`.
4. Add a row to the dimensions table above.
5. Run at least one SDK against the new cases before you open the pull
   request. In dd-trace-java, `ScaleSuiteBenchmark` checks every case in its
   setup and fails on the first wrong result:

   ```bash
   ./gradlew :dd-openfeature:jmh -Pjmh.includes=ScaleSuiteBenchmark -Pjmh.params=cases=<file>
   ```

   A failure there is a bug in the generator or in the SDK. Find which one
   before you change an expected result.

## Size

The files are large on purpose: about 8 MB for `scale` and 27 MB for
`scale-json`. Every consumer that checks out this repository downloads them,
so do not raise the largest size past 10 MB without a reason, and prefer a new
shape over a bigger copy of an existing one. `.gitattributes` marks the
generated files, so GitHub collapses them in a pull request diff. Review the
generator, not the output.
