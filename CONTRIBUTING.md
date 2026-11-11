# Contributing to ffe-system-test-data

Thank you for your interest in contributing to the FFE system test data repository!

## Changing the contract

Read [contract ownership](README.md#contract-ownership) before changing an
expectation. These fixtures define behavior for downstream implementations;
they are not snapshots of whichever SDK or backend happens to be deployed.

Describe the rule being added or corrected, include a concrete input and expected
result, and explain the effect on consumers. Validate against actual native
implementations where available and record the tested revisions and capability
coverage. A consumer mismatch calls for investigation; it does not by itself
justify changing the expected result. Follow [handling a mismatch](README.md#handling-a-mismatch).

Keep deployment prerequisites, release versions, and temporary consumer workarounds
in downstream changes. Contract documentation should remain valid as those
projects ship support.

## Getting Started

1. Fork the repository
2. Create a feature branch from `main`
3. Make your changes
4. Submit a pull request

## Adding Test Cases

### Adding a New Evaluation Test Case

1. Create a new file in `evaluation-cases/` named `test-<descriptive-name>.json`
2. Follow the test case format:

```json
[
  {
    "flag": "flag-key",
    "variationType": "STRING|BOOLEAN|INTEGER|NUMERIC|JSON",
    "defaultValue": "<default value>",
    "targetingKey": "<user identifier>",
    "attributes": { "<key>": "<value>" },
    "result": {
      "value": "<expected value>",
      "reason": "STATIC|SPLIT|TARGETING_MATCH|DEFAULT|ERROR|DISABLED",
      "errorCode": "<optional OpenFeature error code>"
    }
  }
]
```

3. If your test case requires a new flag, add the flag definition to `ufc-config.json`
4. Keep the fixture SDK-neutral. Do not include SDK-specific fields such as `variant` or `flagMetadata`; downstream SDKs should derive those from `ufc-config.json` when they need them.

Use `_skip` or `_include` only for a known cross-platform applicability gap.
Never specify both. Entries must use a canonical identifier from
`ci/validate-fixtures.py` and should include a concise reason. These controls
apply only to rules-based evaluation cases. Do not edit precomputed-assignment
fixtures, schemas, documentation, or validators when changing this contract.

When a new feature's UFC syntax itself is not supported by every SDK, create a
self-contained `evaluation-suites/<suite>/` directory containing its own
`ufc-config.json` and `cases/`. Do not add that syntax to the legacy root config:
a suite the consumer has not enabled must not have its configuration parsed.

For selected split/allocation metadata, add optional `result.serialId` (integer or
`null`) and `result.doLog` (boolean) expectations. A serial ID of `0` is valid;
`null` asserts absence, while omitting the field leaves it unspecified. Keep
SDK-specific metadata key names in the downstream adapter. See
[selected metadata fixtures](README.md#selected-split-and-allocation-metadata)
for the extraction from system-tests and the integration-test boundary.

Use optional `result.features` for exact `HOOK`, `EXPOSURE`, and `EVALUATION`
maps, without internal metadata prefixes. Empty maps assert absence; omission
leaves features unspecified. See [split features and destinations](README.md#split-features-and-destinations)
for the native assertion requirements and the separate limit-policy question.

Malformed flags must be isolated during configuration ingestion. Exclude them
from the active evaluation map, retain only their rejected keys for the current
configuration, and return the caller default with `ERROR` / `PARSE_ERROR` when
those keys are evaluated. Reserve `ERROR` / `FLAG_NOT_FOUND` for keys absent from
both the active and rejected maps. Replace both maps atomically on refresh.

### Modifying Flag Configuration

When adding or modifying flags in `ufc-config.json`:

1. Ensure the flag key is unique and descriptive
2. Include all required fields: `key`, `enabled`, `variationType`, `variations`, `allocations`
3. Add corresponding test cases to validate the flag behavior

## Code Review

All changes require review from the @DataDog/feature-flagging-and-experimentation-sdk team.

## Testing

After making changes, ensure that:

1. `python3 ci/validate-fixtures.py` passes
2. Expected results match the flag configuration logic
3. Informational downstream results are reviewed for new regressions

Static fixture validation is a merge gate. Downstream compatibility results are
advisory: they provide evidence for review, but a mismatch may be caused by
either a consumer implementation or the proposed fixture and does not block
merge by itself.

## Updating Downstream Repositories

After your changes are merged to this repository, update the pinned fixture
revision in downstream repos. Each rules-based consumer should:

1. Pin an exact fixture revision, normally with a git submodule adjacent to the
   OpenFeature/FFE tests. Generated snapshots must retain the source repository
   and commit SHA and be refreshed from that source.
2. Automate fixture updates. For submodules, configure Dependabot with
   `package-ecosystem: "gitsubmodule"`; for snapshots, automate regeneration from
   the source revision.
3. Treat `ufc-config.json` and `evaluation-cases/` as the legacy `core` suite.
4. Implement `_skip`/`_include` filtering before parametrization and side effects,
   using the canonical platform identifiers from `ci/validate-fixtures.py`.
5. Run applicable cases for every implemented capability as well as the baseline;
   follow the [runner requirements](README.md#implement-the-rules-based-runner).
6. Explicitly opt into supported `evaluation-suites/<suite>/` directories; do
   not auto-enable new suites.
7. Preserve shared expectations unchanged. Avoid hand-maintained copies and
   programmatic-only replacements for shared evaluator cases.

Precomputed-assignment consumers use the same pinning and provenance rules with
the [precomputed fixture runner](precomputed-assignments/README.md).

Current downstream consumers are `system-tests`, `dd-trace-go`, `dd-trace-java`, `dd-trace-js`, `dd-trace-py`, `dd-trace-rb`, `dd-trace-dotnet`, `dd-trace-php`, `libdatadog`, and `openfeature-js-client`.

## Questions?

If you have questions about contributing, please open an issue or reach out to the FFE SDK team.
