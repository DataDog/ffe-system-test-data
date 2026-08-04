# Contributing to ffe-system-test-data

Thank you for your interest in contributing to the FFE system test data repository!

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
    "result": { "value": "<expected value>", "reason": "STATIC|SPLIT|TARGETING_MATCH|DEFAULT|ERROR|DISABLED" }
  }
]
```

3. If your test case requires a new flag, add the flag definition to `ufc-config.json`
4. Keep the fixture SDK-neutral. Do not include SDK-specific fields such as `variant` or `flagMetadata`; downstream SDKs should derive those from `ufc-config.json` when they need them.

### Updating Targeting Regex Conformance

The standalone targeting regex contract lives in
`regex-conformance/targeting-regex-conformance.json`. Do not put it in
`evaluation-cases/`; consumers parse every JSON file there as a full UFC
evaluation case.

When changing the contract:

1. Bump `schemaVersion` only for an incompatible schema change and bump
   `contractVersion` when portable behavior changes.
2. Keep case IDs stable. Add a new ID instead of changing the meaning of an
   existing case.
3. Include every required case field: `id`, `description`, `category`,
   `contract`, `rawPattern`, `normalizedPattern`, `expectedCompile`, `input`,
   and `expectedMatch`.
4. Use `contract` for the portable authoring decision. Use `expectedCompile`
   and `expectedMatch` only for common native-engine observations. Set a common
   field to `null` and add `engineExpectations` when native engines differ.
5. Verify accepted cases in every supported engine. A compiler accepting a
   pattern in one engine does not make it part of the portable contract.
6. Recompute `targeting-regex-conformance.sha256` from the exact JSON bytes.

Validate JSON syntax, unique case IDs, required field types, and the hash:

```bash
jq empty ufc-config.json evaluation-cases/*.json regex-conformance/targeting-regex-conformance.json
jq -e -f regex-conformance/validate-targeting-regex-conformance.jq regex-conformance/targeting-regex-conformance.json
regex-conformance/test-validate-targeting-regex-conformance.sh
(cd regex-conformance && shasum -a 256 -c targeting-regex-conformance.sha256)
```

### Modifying Flag Configuration

When adding or modifying flags in `ufc-config.json`:

1. Ensure the flag key is unique and descriptive
2. Include all required fields: `key`, `enabled`, `variationType`, `variations`, `allocations`
3. Add corresponding test cases to validate the flag behavior

## Code Review

All changes require review from the @DataDog/feature-flagging-and-experimentation-sdk team.

## Testing

After making changes, ensure that:

1. All JSON files are valid (no syntax errors)
2. Test cases reference flags that exist in the config
3. Expected results match the flag configuration logic

## Updating Downstream Repositories

After your changes are merged to this repository, update the submodule references in downstream repos. Each downstream repository should:

1. Keep `ffe-system-test-data` as a git submodule adjacent to the OpenFeature/FFE tests
2. Configure Dependabot with `package-ecosystem: "gitsubmodule"` so fixture updates are proposed automatically
3. Load `ufc-config.json` and loop over every `evaluation-cases/*.json` file in unit tests
4. Avoid copied fixture directories and programmatic-only shared evaluator cases

Current downstream consumers are `system-tests`, `dd-trace-go`, `dd-trace-java`, `dd-trace-js`, `dd-trace-py`, `dd-trace-rb`, `dd-trace-dotnet`, `libdatadog`, and `openfeature-js-client`. `dd-trace-php` is excluded until its OpenFeature client lands.

## Questions?

If you have questions about contributing, please open an issue or reach out to the FFE SDK team.
