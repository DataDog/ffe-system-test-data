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
- [dd-trace-php](https://github.com/DataDog/dd-trace-php) - PHP tracer
- [libdatadog](https://github.com/DataDog/libdatadog) - Shared Rust FFE evaluator
- [openfeature-js-client](https://github.com/DataDog/openfeature-js-client) - Datadog OpenFeature JavaScript clients

## Directory Structure

```
ffe-system-test-data/
├── ufc-config.json          # Master flag configuration (UFC format)
├── evaluation-cases/
│   └── test-*.json          # Evaluation test case files
└── regex-conformance/
    ├── targeting-regex-conformance.json   # FFE authoring and matching contract
    ├── targeting-regex-conformance.sha256 # SHA-256 of the JSON bytes
    ├── validate-targeting-regex-conformance.jq # Canonical schema validator
    └── test-validate-targeting-regex-conformance.sh # Validator regression tests
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
| `result.errorCode` | string | Optional OpenFeature error code, such as `PARSE_ERROR` or `FLAG_NOT_FOUND` |

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

### Targeting Regex Conformance

`regex-conformance/targeting-regex-conformance.json` is a standalone, versioned
contract for authoring targeting regular expressions in FFE. It is intentionally
outside `evaluation-cases/`; consumers of that directory parse every JSON file
as a complete UFC evaluation case.

The fixture records native observations for four implementations: Go `regexp`,
RE2JS, the Rust rules-based evaluator, and the Rust rkyv evaluator. The accepted
authoring subset is narrower: accepted cases must also evaluate consistently in
the shipped Java, JavaScript, and .NET SDK evaluators. Several SDKs share the
Rust evaluator, so agreement across those SDKs is not evidence from independent
regex engines.

Each regex case has a stable ID, an FFE authoring `contract`, raw and normalized
patterns, native compile observations, an input, and an unanchored match
observation when the modeled engines agree. Go and RE2JS consumers compile
`normalizedPattern`; Rust consumers compile `rawPattern`. Cases with differences
between modeled engines include per-engine expectations. Downstream SDK checks
must require consistent behavior for accepted cases. A native engine accepting
rejected syntax does not change the authoring contract. Inline Unicode flags and
repeated inline flags are rejected for authoring even when an engine can compile
them or normalization can remove a redundant standalone flag. The adjacent
SHA-256 file lets downstream tests detect fixture drift.

## Automated Validation

Pull requests run a blocking static validation check over `ufc-config.json`
and every file in `evaluation-cases/`. It rejects invalid JSON, duplicate
object keys, malformed evaluation-case envelopes, mismatched flag or variation
map keys, and references to unknown flags without a `FLAG_NOT_FOUND`
expectation.

The validator deliberately does not fully schema-check allocation internals.
Some fixtures contain malformed flag fields on purpose to verify that consumers
reject only the affected flag. Run the same check locally with:

Consumers exclude malformed flags from the active evaluation map while retaining
their rejected keys for the current configuration. Evaluating a rejected key
returns the caller default with `ERROR` / `PARSE_ERROR`; a key absent from both
maps returns `ERROR` / `FLAG_NOT_FOUND`. Each configuration refresh replaces both
maps atomically so fixed or deleted flags do not leave stale rejection entries.

```bash
python3 ci/validate-fixtures.py
```

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
| `test-case-invalid-condition-operands.json` | Flags with invalid configured operands for GT, ONE_OF, and IS_NULL are removed without poisoning valid flags |
| `test-case-invalid-shard-bounds-isolation.json` | Flags with shard bounds outside Rust/schema integer ranges are removed without poisoning valid flags |
| `test-case-invalid-regex-isolation.json` | A flag with an invalid regular expression is removed without poisoning the configuration |
| `test-case-malformed-flag-isolation.json` | A structurally malformed flag is removed without poisoning valid flags |
| `test-case-variant-type-mismatch.json` | A flag whose variant violates its declared type is removed without poisoning valid neighboring flags |
| `test-case-microsecond-date-flag.json` | Flag with microsecond-precision date targeting |
| `test-case-missing-split-shards-isolation.json` | A flag with a split missing required `shards` is removed without poisoning valid flags |
| `test-case-new-user-onboarding-flag.json` | Multi-allocation onboarding flag with sharding |
| `test-case-no-allocations-flag.json` | Flag with no allocations (returns default) |
| `test-case-null-operator-flag.json` | Flag using IS_NULL operator |
| `test-case-null-shard-range-isolation.json` | A flag with a null shard range is removed without poisoning valid flags |
| `test-case-null-targeting-key.json` | Evaluations with an explicit null targeting key |
| `test-case-numeric-flag.json` | Numeric flag evaluation |
| `test-case-numeric-one-of.json` | Numeric ONE_OF operator matching |
| `test-case-of-7-empty-targeting-key.json` | Evaluation with empty targeting key |
| `test-case-numeric-one-of-default.json` | Numeric ONE_OF flag returning the default value when no rule matches |
| `test-case-regex-flag.json` | Flag using regex matching operator |
| `test-case-semver-comparison-flag.json` | Flag using semver comparison operators (SEMVER_EQ, SEMVER_NEQ, SEMVER_LT, SEMVER_LTE, SEMVER_GT, SEMVER_GTE), including prerelease ordering and invalid/missing attribute handling |
| `test-case-semver-precedence-flag.json` | SemVer precedence edge cases that are easy to get wrong: multi-digit numeric prerelease ordering (beta.2 < beta.11), build-metadata-ignored across every operator (EQ/NEQ/LT/LTE/GT/GTE), and alphanumeric prerelease ordering (alpha < alpha.1 < alpha.beta < beta < release) |
| `test-case-semver-version-parts.json` | Extended version-part support: one- and two-part versions normalize to three parts, and four- and five-part versions are accepted, covering both attributes and configured comparands |
| `test-case-semver-validation-flag.json` | SemVer 2 syntax boundaries retained by the extended parser, invalid syntax, non-string attributes, and invalid configured comparands |
| `test-case-semver-invalid-comparand-waterfall.json` | An invalid configured SemVer comparand in a non-last allocation of a waterfall must reject the whole flag at parse time rather than skipping it and falling through to a later valid default |
| `test-case-semver-invalid-comparand-categories.json` | Configured SemVer comparand boundaries: a valid hyphen-heavy prerelease matches, while invalid syntax (including consecutive dots and a Ruby-style `.DEV` suffix), v-prefixed, leading-zero, and non-string comparands reject their flag at parse time with PARSE_ERROR without poisoning the rest of the configuration |
| `test-case-start-and-end-date-flag.json` | Flag with start/end date time bounds |
| `test-case-unknown-fields-tolerance.json` | Unknown UFC object fields are ignored |
| `test-case-unknown-operator-isolation.json` | A flag with an unknown operator is removed without poisoning valid flags |
| `test-flag-that-does-not-exist.json` | Non-existent flag returning the default value with `FLAG_NOT_FOUND` |
| `test-json-config-flag.json` | JSON-typed flag returning object value |
| `test-no-allocations-flag.json` | Another no-allocations variant |
| `test-special-characters.json` | Flag keys/values with special characters |
| `test-string-with-special-characters.json` | String values with special characters |

## Origin

These fixtures are derived from the Go SDK (`dd-trace-go`) reference implementation, which was the first to implement and validate the OpenFeature `reason` field. The Go fixtures serve as the canonical source of truth for expected evaluation behavior across all Datadog SDKs.

## Downstream Updates

Downstream repositories should consume this repository as a git submodule and run their fixture coverage by loading every JSON file in `evaluation-cases/`. Shared evaluator behavior should be added here first, then downstream repositories should update their submodule SHA. Do not add copied JSON fixture directories or language-only programmatic cases for behavior that belongs in this shared fixture set.

### Informational Compatibility Preview

Fixture pull requests also run the canonical evaluation suite from Go, Java,
JavaScript, Python, Ruby, .NET, PHP, and `libdatadog` against both the
pull-request merge base and proposed head. Each job classifies the result as
compatible, a new regression, an improvement, or existing downstream drift and
uploads the two logs.

These compatibility jobs are intentionally advisory and are allowed to fail.
They must not be configured as required merge checks. Their purpose is to show
contributors where to start investigating; a mismatch can indicate either a
downstream implementation gap or an incorrect expectation in this repository.
The preview does not automatically update submodule pins, open issues, or
decide which side is wrong.

The executable entrypoints currently live on purpose-built consumer branches
based on each repository's default branch. This repository only orchestrates
those consumer-owned tests.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding or modifying test cases.

## License

Unless explicitly stated otherwise, all files in this repository are licensed under the Apache 2.0 License.

This product includes software developed at Datadog (https://www.datadoghq.com/). Copyright 2026 Datadog, Inc.

See [LICENSE](LICENSE) for the full license text.
