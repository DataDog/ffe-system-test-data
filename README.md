# ffe-system-test-data

Canonical test fixtures for Datadog's Feature Flag Evaluation (FFE) system, shared across all SDK repositories via git submodule.

## Contents

- `ufc-config.json` -- UFC (Unified Feature Configuration) server payload used by all evaluation test cases
- `evaluation-cases/` -- 25 JSON fixture files, each a wrapper object containing evaluation test cases

## Fixture Schema

### File format

Each `evaluation-cases/test-*.json` file is a wrapper object:

```json
{
  "skip":  <SkipValue>,   // optional
  "xfail": <XfailValue>,  // optional
  "cases": [ ...test case objects... ]
}
```

When neither `skip` nor `xfail` is present the file uses the minimal form:

```json
{ "cases": [ ...test case objects... ] }
```

### Test case fields

Each test case object uses a universal schema:

| Field | Type | Description |
|-------|------|-------------|
| `flag` | string | The flag key to evaluate |
| `variationType` | string | Expected type: `BOOLEAN`, `STRING`, `INTEGER`, `NUMERIC`, `JSON` |
| `defaultValue` | any | The default value passed to the evaluation call |
| `targetingKey` | string | The subject/user identifier for evaluation |
| `attributes` | object | Additional context attributes for targeting rules |
| `result.value` | any | The expected evaluation result value |
| `result.reason` | string | The expected OpenFeature reason: `STATIC`, `SPLIT`, `TARGETING_MATCH`, `DEFAULT`, `ERROR`, `DISABLED` |
| `skip` | SkipValue | Optional. Override file-level skip for this case. |
| `xfail` | XfailValue | Optional. Override file-level xfail for this case. |

### `skip` and `xfail` annotation fields

These fields appear at both the file level (on the wrapper object) and the case level (on individual test case objects). They let SDK test runners adjust behavior without modifying canonical test data.

**SkipValue** — controls whether the SDK executes a test:

| Value | Meaning |
|-------|---------|
| `true` | Skip on all SDKs |
| `["go", "java"]` | Skip on the listed SDKs only |
| `null` | Run normally (use at case-level to opt out of a file-level skip) |

**XfailValue** — marks a test as expected to fail:

| Value | Meaning |
|-------|---------|
| `true` | Expect failure on all SDKs |
| `"<reason>"` | Expect failure on all SDKs, reason attached |
| `{"go": "reason", "dotnet": true}` | Expect failure on listed SDKs only, per-SDK reason |
| `null` | Run normally (use at case-level to opt out of a file-level xfail) |

**Canonical SDK identifiers:** `"go"`, `"java"`, `"python"`, `"dotnet"`

**Precedence rules:**
1. Case-level overrides file-level.
2. `null` at case-level opts that case back in to normal execution.
3. `skip` takes precedence over `xfail` when both apply to the same SDK.

**SDK behavior:**
- `skip`: do not execute the assertion; report as skipped/pending; does not count as pass or fail.
- `xfail`: execute the assertion; failure → report as expected failure (run passes); pass → report as unexpected pass (SDKs may treat this as a test failure).

See `evaluation-cases/test-case-regex-flag.json` for a worked example showing file-level `xfail` with a case-level `null` override.

### SDK-Specific Fields

The shared fixtures intentionally exclude SDK-specific fields such as `variant` and `flagMetadata`. SDKs that need these fields should compute them at test load time from the universal fields. For example:

- **variant**: Derive from the flag configuration in `ufc-config.json` by matching the result value
- **flagMetadata**: Extract from the flag's metadata field in `ufc-config.json`

## Usage

### Adding as a Git Submodule

```bash
git submodule add https://github.com/DataDog/ffe-system-test-data.git path/to/testdata
git submodule update --init
```

### In Tests

1. Load `ufc-config.json` to initialize your UFC evaluator
2. For each file in `evaluation-cases/`, parse the wrapper object and read the `cases` array
3. Apply `skip`/`xfail` annotations (file-level and case-level) for your SDK identifier
4. For each non-skipped case, call your evaluator with `flag`, `defaultValue`, `targetingKey`, and `attributes`
5. Assert the result matches `result.value` and `result.reason`
6. For xfail cases: treat assertion failures as expected failures; treat assertion passes as unexpected passes

## Evaluation Cases

| File | Description |
|------|-------------|
| `test-case-boolean-false-assignment.json` | Boolean flag with false assignment via targeting |
| `test-case-boolean-one-of-matches.json` | Boolean flag with ONE_OF operator matching |
| `test-case-comparator-operator-flag.json` | Flag using comparator operators (GT, LT, etc.) |
| `test-case-disabled-flag.json` | Disabled flag returning DISABLED reason |
| `test-case-empty-flag.json` | Flag with empty configuration |
| `test-case-empty-string-variation.json` | Flag returning empty string as value |
| `test-case-falsy-value-assignments.json` | Flags returning falsy values (0, false, empty) |
| `test-case-flag-with-empty-string.json` | Flag with empty string in configuration |
| `test-case-integer-flag.json` | Integer-typed flag evaluation |
| `test-case-kill-switch-flag.json` | Kill switch (emergency off) flag |
| `test-case-microsecond-date-flag.json` | Flag with microsecond-precision date targeting |
| `test-case-new-user-onboarding-flag.json` | Multi-allocation onboarding flag with sharding |
| `test-case-no-allocations-flag.json` | Flag with no allocations (returns default) |
| `test-case-null-operator-flag.json` | Flag using IS_NULL operator |
| `test-case-null-targeting-key.json` | Evaluation with null targeting key |
| `test-case-numeric-flag.json` | Numeric flag evaluation |
| `test-case-numeric-one-of.json` | Numeric ONE_OF operator matching |
| `test-case-of-7-empty-targeting-key.json` | Evaluation with empty targeting key |
| `test-case-regex-flag.json` | Flag using regex matching operator |
| `test-case-start-and-end-date-flag.json` | Flag with start/end date time bounds |
| `test-flag-that-does-not-exist.json` | Non-existent flag (error/default case) |
| `test-json-config-flag.json` | JSON-typed flag returning object value |
| `test-no-allocations-flag.json` | Another no-allocations variant |
| `test-special-characters.json` | Flag keys/values with special characters |
| `test-string-with-special-characters.json` | String values with special characters |

## Origin

These fixtures are derived from the Go SDK (`dd-trace-go`) reference implementation, which was the first to implement and validate the OpenFeature `reason` field. The Go fixtures serve as the canonical source of truth for expected evaluation behavior across all Datadog SDKs.
