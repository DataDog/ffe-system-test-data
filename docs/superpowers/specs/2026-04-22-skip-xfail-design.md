# skip / xfail annotation fields for ffe-system-test-data

**Date:** 2026-04-22
**Status:** approved
**Scope:** `evaluation-cases/test-*.json` schema

---

## Motivation

The evaluation test cases in this repository are executed by multiple SDK test runners (Go, Java, Python, .NET). Some SDKs have known behavioral divergences or unimplemented features that make specific test cases inapplicable or expected to fail on that SDK only. Today there is no way to express this — the test runner either runs the case (and may fail) or skips the entire file by convention.

This design adds two optional annotation fields — `skip` and `xfail` — at two hierarchical levels: the test file and the individual test case. SDK test runners use these fields to adjust their behavior without modifying the canonical test data.

---

## Schema

### File-level wrapper object

Each `evaluation-cases/test-*.json` file currently contains a bare JSON array. The new format wraps that array in an object with optional annotation fields and a required `cases` key.

**This is a breaking change.** All consuming SDK test runners must be updated to parse the new format.

```json
{
  "skip": <SkipValue>,
  "xfail": <XfailValue>,
  "cases": [ ...test case objects... ]
}
```

Both `skip` and `xfail` are optional at the file level. When both are absent the file contains a plain wrapper:

```json
{
  "cases": [ ...test case objects... ]
}
```

### Case-level fields

Each test case object may carry optional `skip` and/or `xfail` fields alongside the existing `flag`, `variationType`, `defaultValue`, `targetingKey`, `attributes`, and `result` fields.

```json
{
  "flag": "regex-flag",
  "variationType": "STRING",
  "defaultValue": "default",
  "targetingKey": "alice",
  "attributes": { "email": "alice@example.com" },
  "result": { "value": "on", "reason": "TARGETING_MATCH" },
  "skip": <SkipValue>,
  "xfail": <XfailValue>
}
```

### Value types

#### `SkipValue`

| Value | Meaning |
|---|---|
| `true` | Skip this case/file on all SDKs |
| `["go", "java"]` | Skip on the listed SDKs only |
| `null` | Explicitly run normally (used at case-level to override a file-level skip) |

#### `XfailValue`

| Value | Meaning |
|---|---|
| `true` | Expect failure on all SDKs, no reason given |
| `"<reason string>"` | Expect failure on all SDKs, reason attached |
| `{"go": "reason", "dotnet": "reason"}` | Expect failure only on the listed SDKs, per-SDK reason |
| `{"go": true}` | Expect failure on `go` only, no reason |
| `null` | Explicitly run normally (used at case-level to override a file-level xfail) |

### Canonical SDK identifiers

| SDK | Identifier |
|---|---|
| Go tracer | `"go"` |
| Java tracer | `"java"` |
| Python tracer | `"python"` |
| .NET tracer | `"dotnet"` |

SDK test runners must know their own identifier and match it against annotation values.

---

## Precedence rules

1. **Case-level overrides file-level.** When both levels define an annotation, the case-level value wins unconditionally.
2. **`null` means "run normally."** Setting `"skip": null` or `"xfail": null` at the case level explicitly opts that case back in, even if the file-level annotation would otherwise apply.
3. **`skip` takes precedence over `xfail`.** If both are set (at the same effective level after override resolution) and both apply to the current SDK, the SDK treats the case as skipped (does not run it at all).

Effective annotation resolution algorithm per case, per SDK:

```
case_skip  = resolve(case.skip,  sdk_id)   # null if not set
file_skip  = resolve(file.skip,  sdk_id)   # null if not set
case_xfail = resolve(case.xfail, sdk_id)   # null if not set
file_xfail = resolve(file.xfail, sdk_id)   # null if not set

effective_skip  = case.skip  IS PRESENT ? case_skip  : file_skip
effective_xfail = case.xfail IS PRESENT ? case_xfail : file_xfail

if effective_skip  → SKIP (do not run)
if effective_xfail → run, expect failure
otherwise          → run, expect pass
```

`resolve(value, sdk_id)`:
- `true` → `true` (applies to all SDKs)
- `"<string>"` → `"<string>"` (applies to all SDKs, reason attached)
- `[...]` → `true` if `sdk_id` in list, else `null`
- `{...}` → value at `sdk_id` key if present, else `null`
- `null` or absent → `null`

---

## Consumer SDK behavior spec

### `skip`

- The SDK test runner **does not execute** the assertion for this case.
- The case is reported as **skipped / pending** in the test output.
- It does **not** count as a pass or failure.
- The SDK must not error if `skip` is present and applies to it.

### `xfail`

- The SDK test runner **executes** the assertion.
- If the assertion **fails** → report as **expected failure** (the overall test run passes).
- If the assertion **passes** → report as **unexpected pass**. SDKs may treat this as a test failure (recommended) or a warning, depending on the test framework's conventions.
- If a `reason` string is available (from a string or object value), include it in the test output.

---

## Migration notes

### This repository

1. All `evaluation-cases/test-*.json` files must be updated from bare arrays to the wrapper object format.
2. Files with no annotations use the minimal wrapper: `{"cases": [...]}`.
3. README.md and CLAUDE.md must be updated to document the new schema.

### Consuming repos (one PR each)

| Repo | Change |
|---|---|
| `dd-trace-go` | Update parser to unwrap `cases` array; implement skip/xfail handling |
| `dd-trace-java` (`DDEvaluatorFixtureTest.java`) | Same |
| `dd-trace-py` | Same |
| `dd-trace-dotnet` | Same |
| `system-tests` | Same |

Each consuming repo should update the submodule pointer **after** updating its parser, not before, to avoid broken CI.

---

## Before / after example

### Before (current format)

`evaluation-cases/test-case-regex-flag.json`:
```json
[
  {
    "flag": "regex-flag",
    "variationType": "STRING",
    "defaultValue": "unknown",
    "targetingKey": "alice",
    "attributes": { "email": "alice@example.com" },
    "result": { "value": "on", "reason": "TARGETING_MATCH" }
  },
  {
    "flag": "regex-flag",
    "variationType": "STRING",
    "defaultValue": "unknown",
    "targetingKey": "bob",
    "attributes": { "email": "bob@example.com" },
    "result": { "value": "unknown" }
  }
]
```

### After (new format, with annotations)

```json
{
  "xfail": { "dotnet": "regex MATCHES operator not yet implemented" },
  "cases": [
    {
      "flag": "regex-flag",
      "variationType": "STRING",
      "defaultValue": "unknown",
      "targetingKey": "alice",
      "attributes": { "email": "alice@example.com" },
      "result": { "value": "on", "reason": "TARGETING_MATCH" }
    },
    {
      "flag": "regex-flag",
      "variationType": "STRING",
      "defaultValue": "unknown",
      "targetingKey": "bob",
      "attributes": { "email": "bob@example.com" },
      "result": { "value": "unknown" },
      "xfail": null
    }
  ]
}
```

In this example:
- The file-level `xfail` marks all cases as expected to fail on `dotnet`.
- The second case overrides with `"xfail": null`, opting it back in to run normally on all SDKs (including dotnet).

### After (new format, no annotations — minimal wrapper)

```json
{
  "cases": [
    {
      "flag": "regex-flag",
      "variationType": "STRING",
      "defaultValue": "unknown",
      "targetingKey": "alice",
      "attributes": { "email": "alice@example.com" },
      "result": { "value": "on", "reason": "TARGETING_MATCH" }
    }
  ]
}
```
