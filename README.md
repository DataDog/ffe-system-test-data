# ffe-system-test-data

Canonical test data for Datadog's Feature Flags & Experimentation (FFE) SDK implementations.

## Overview

This repository contains the canonical set of flag configurations and evaluation test cases used to validate FFE SDK implementations across multiple languages. It serves as a single source of truth consumed via git submodules by:

- [system-tests](https://github.com/DataDog/system-tests) - Parametric tests
- [dd-trace-py](https://github.com/DataDog/dd-trace-py) - Python tracer
- [dd-trace-java](https://github.com/DataDog/dd-trace-java) - Java tracer
- [dd-trace-dotnet](https://github.com/DataDog/dd-trace-dotnet) - .NET tracer
- [dd-trace-go](https://github.com/DataDog/dd-trace-go) - Go tracer
- [dd-trace-js](https://github.com/DataDog/dd-trace-js) - JavaScript tracer
- [dd-trace-rb](https://github.com/DataDog/dd-trace-rb) - Ruby tracer
- [libdatadog](https://github.com/DataDog/libdatadog) - Shared Rust FFE evaluator
- [openfeature-js-client](https://github.com/DataDog/openfeature-js-client) - Datadog OpenFeature JavaScript clients

`dd-trace-php` is intentionally excluded until its OpenFeature client has landed.

## Directory Structure

```
ffe-system-test-data/
├── ufc-config.json          # Master flag configuration (UFC format)
└── evaluation-cases/
    └── test-*.json          # Evaluation test case files
```

## Usage

### As a Git Submodule

Add this repository as a submodule to your project:

```bash
git submodule add https://github.com/DataDog/ffe-system-test-data path/to/ffe-data
```

Initialize and update submodules when cloning:

```bash
git clone --recurse-submodules <your-repo>
# or after cloning:
git submodule update --init --recursive
```

### In Tests

1. Load `ufc-config.json` to initialize your UFC evaluator
2. For each file in `evaluation-cases/`, parse the JSON array
3. For each test case, call your evaluator with `flag`, `defaultValue`, `targetingKey`, and `attributes`
4. Assert the result matches `result.value` and `result.reason`

## File Formats

### UFC Config (`ufc-config.json`)

The UFC (Unified Flag Configuration) file contains flag definitions in the format used by Datadog's Remote Configuration:

```json
{
  "flag-key": {
    "key": "flag-key",
    "enabled": true,
    "variationType": "STRING|BOOLEAN|INTEGER|NUMERIC|JSON",
    "variations": { ... },
    "allocations": [ ... ]
  }
}
```

### Evaluation Test Cases (`evaluation-cases/test-*.json`)

Each evaluation case uses a universal schema with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `flag` | string | The flag key to evaluate |
| `variationType` | string | Expected type: `BOOLEAN`, `STRING`, `INTEGER`, `NUMERIC`, `JSON` |
| `defaultValue` | any | The default value passed to the evaluation call |
| `targetingKey` | string or null | The subject/user identifier for evaluation. Use `null` only for explicit missing-targeting-key coverage |
| `attributes` | object | Additional context attributes for targeting rules |
| `result.value` | any | The expected evaluation result value |
| `result.reason` | string | The expected OpenFeature reason: `STATIC`, `SPLIT`, `TARGETING_MATCH`, `DEFAULT`, `ERROR`, `DISABLED` |

Example:

```json
[
  {
    "flag": "flag-key",
    "variationType": "STRING",
    "defaultValue": "default",
    "targetingKey": "user-123",
    "attributes": { "country": "US" },
    "result": { "value": "expected-value", "reason": "TARGETING_MATCH" }
  }
]
```

### SDK-Specific Fields

The shared fixtures intentionally exclude SDK-specific fields such as `variant` and `flagMetadata`. SDKs that need these fields should compute them at test load time from the universal fields. For example:

- **variant**: Derive from the flag configuration in `ufc-config.json` by matching the result value
- **flagMetadata**: Extract from the flag's metadata field in `ufc-config.json`

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
| `test-case-malformed-flag-isolation.json` | Structurally malformed flag is ignored without poisoning valid flags |
| `test-case-microsecond-date-flag.json` | Flag with microsecond-precision date targeting |
| `test-case-new-user-onboarding-flag.json` | Multi-allocation onboarding flag with sharding |
| `test-case-no-allocations-flag.json` | Flag with no allocations (returns default) |
| `test-case-null-operator-flag.json` | Flag using IS_NULL operator |
| `test-case-null-targeting-key.json` | Evaluations with an explicit null targeting key |
| `test-case-numeric-flag.json` | Numeric flag evaluation |
| `test-case-numeric-one-of.json` | Numeric ONE_OF operator matching |
| `test-case-of-7-empty-targeting-key.json` | Evaluation with empty targeting key |
| `test-case-numeric-one-of-default.json` | Numeric ONE_OF flag returning the default value when no rule matches |
| `test-case-regex-flag.json` | Flag using regex matching operator |
| `test-case-start-and-end-date-flag.json` | Flag with start/end date time bounds |
| `test-case-unknown-fields-tolerance.json` | Unknown UFC object fields are ignored |
| `test-case-unknown-operator-isolation.json` | Flag with unknown operator is ignored without poisoning valid flags |
| `test-flag-that-does-not-exist.json` | Non-existent flag returning the default value with `FLAG_NOT_FOUND` |
| `test-json-config-flag.json` | JSON-typed flag returning object value |
| `test-no-allocations-flag.json` | Another no-allocations variant |
| `test-special-characters.json` | Flag keys/values with special characters |
| `test-string-with-special-characters.json` | String values with special characters |

## Origin

These fixtures are derived from the Go SDK (`dd-trace-go`) reference implementation, which was the first to implement and validate the OpenFeature `reason` field. The Go fixtures serve as the canonical source of truth for expected evaluation behavior across all Datadog SDKs.

## Downstream Updates

Downstream repositories should consume this repository as a git submodule and run their fixture coverage by loading every JSON file in `evaluation-cases/`. Shared evaluator behavior should be added here first, then downstream repositories should update their submodule SHA. Do not add copied JSON fixture directories or language-only programmatic cases for behavior that belongs in this shared fixture set.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding or modifying test cases.

## License

Unless explicitly stated otherwise, all files in this repository are licensed under the Apache 2.0 License.

This product includes software developed at Datadog (https://www.datadoghq.com/). Copyright 2026 Datadog, Inc.

See [LICENSE](LICENSE) for the full license text.
