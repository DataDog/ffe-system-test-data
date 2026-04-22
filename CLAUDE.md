# CLAUDE.md — ffe-system-test-data

## Repository purpose

This repository holds canonical fixture data for Datadog's Feature Flag Evaluation (FFE) engine. It is consumed as a git submodule by downstream tracer repos (dd-trace-java, dd-trace-py, dd-trace-dotnet, system-tests). Changes here propagate to all consumers; treat every merge to `main` as a release.

## Repository structure

```
config/
  ufc-config.json          # All flag definitions (UFC server format)
evaluation-cases/
  test-*.json              # Evaluation scenarios, one wrapper object per file
```

The `config/` and `evaluation-cases/` directories are populated through feature branches. A fresh clone of `main` may not contain data files yet.

## File formats

### config/ufc-config.json

UFC (Unified Flag Configuration) server format. Top-level keys:

- `createdAt` — ISO 8601 timestamp
- `format` — always `"SERVER"`
- `environment.name` — environment label
- `flags` — map of flag key → flag definition

Each flag definition has `key`, `enabled`, `variationType` (`BOOLEAN`, `STRING`, `INTEGER`, `NUMERIC`, `JSON`), `variations` (map of variation key → `{key, value}`), and `allocations` (ordered list of allocation rules).

Each allocation rule has `key`, optional `rules` (targeting conditions), `splits` (variation assignments with optional shard ranges), optional `startAt`/`endAt` (ISO 8601), and `doLog` (boolean).

### evaluation-cases/test-*.json

Each file is a wrapper object:

```json
{
  "skip":  <SkipValue>,   // optional
  "xfail": <XfailValue>,  // optional
  "cases": [ ...test case objects... ]
}
```

Files with no annotations use the minimal form: `{"cases": [...]}`.

#### Test case object

```json
{
  "flag": "flag-key",
  "variationType": "BOOLEAN|STRING|INTEGER|NUMERIC|JSON",
  "defaultValue": <matches variationType>,
  "targetingKey": "entity-id or null",
  "attributes": { "key": "value" },
  "result": {
    "value": <expected evaluated value>,
    "reason": "TARGETING_MATCH|SPLIT|STATIC|DEFAULT|ERROR"  // optional
  },
  "skip":  <SkipValue>,   // optional
  "xfail": <XfailValue>   // optional
}
```

`result.reason` is optional. When omitted, consumers assert only on `result.value`. Reason code support varies by SDK implementation — verify that a downstream tracer implements a given reason code before adding reason assertions for it.

Reason code semantics:
- `TARGETING_MATCH` — entity matched an explicit rule condition within an allocation
- `SPLIT` — entity was assigned via consistent hashing into a shard range
- `STATIC` — entity was assigned deterministically without hashing (e.g. a single split at 100%)
- `DEFAULT` — no allocation matched; default value was returned
- `DISABLED` — flag was disabled (`flag.enabled = false`)
- `ERROR` — evaluation error (flag not found, type mismatch, etc.)

#### SkipValue

| Value | Meaning |
|-------|---------|
| `true` | Skip on all SDKs |
| `["go", "java"]` | Skip on listed SDKs only |
| `null` | Run normally (case-level: opt out of file-level skip) |

#### XfailValue

| Value | Meaning |
|-------|---------|
| `true` | Expect failure on all SDKs |
| `"<reason>"` | Expect failure on all SDKs, reason attached |
| `{"go": "reason", "dotnet": true}` | Expect failure on listed SDKs, per-SDK reason |
| `null` | Run normally (case-level: opt out of file-level xfail) |

#### Canonical SDK identifiers

`"go"`, `"java"`, `"python"`, `"dotnet"`

#### Precedence rules

1. Case-level overrides file-level.
2. `null` at case-level opts that case back in to normal execution.
3. `skip` takes precedence over `xfail` when both apply.

## Adding or modifying test data

1. To add a new test scenario, create `evaluation-cases/test-<descriptive-name>.json` as a wrapper object with a `cases` array.
2. If the scenario requires a new flag, add the flag definition to `config/ufc-config.json`.
3. Every `flag` value in an evaluation case must correspond to a key in `config/ufc-config.json`.
4. Validate all JSON files before opening a PR. Use `jq . path/to/file.json` or `python -m json.tool path/to/file.json` to catch syntax errors. No automated schema validator is currently enforced in CI.
5. After your PR merges to `main`, open follow-up PRs in each downstream repo to advance the submodule pointer.

## Downstream submodule update workflow

Run from the downstream repo root:

```bash
git submodule update --remote path/to/ffe-data
git add path/to/ffe-data
git commit -m "Update ffe-system-test-data submodule"
```

Repeat for each consumer: system-tests, dd-trace-py, dd-trace-java, dd-trace-dotnet.

## Code ownership

All changes require review from `@DataDog/feature-flagging-and-experimentation-sdk`.
