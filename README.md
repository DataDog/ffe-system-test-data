# ffe-system-test-data

Canonical test fixtures for Datadog's Feature Flag Evaluation (FFE) system, shared across all SDK repositories via git submodule.

## Contents

- `ufc-config.json` -- UFC (Unified Feature Configuration) server payload used by all evaluation test cases
- `evaluation-cases/` -- 24 JSON fixture files, each containing an array of evaluation test cases

## Fixture Schema

Each evaluation case uses a universal schema with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `flag` | string | The flag key to evaluate |
| `variationType` | string | Expected type: `BOOLEAN`, `STRING`, `INTEGER`, `DOUBLE`, `JSON` |
| `defaultValue` | any | The default value passed to the evaluation call |
| `targetingKey` | string | The subject/user identifier for evaluation |
| `attributes` | object | Additional context attributes for targeting rules |
| `result.value` | any | The expected evaluation result value |
| `result.reason` | string | The expected OpenFeature reason: `STATIC`, `SPLIT`, `TARGETING_MATCH`, `DEFAULT`, `ERROR`, `DISABLED` |

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
2. For each file in `evaluation-cases/`, parse the JSON array
3. For each test case, call your evaluator with `flag`, `defaultValue`, `targetingKey`, and `attributes`
4. Assert the result matches `result.value` and `result.reason`

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
| `test-case-numeric-flag.json` | Numeric (double) flag evaluation |
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
