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

After your changes are merged to this repository, update the submodule references in downstream repos. Each downstream repository should:

1. Keep `ffe-system-test-data` as a git submodule adjacent to the OpenFeature/FFE tests
2. Configure Dependabot with `package-ecosystem: "gitsubmodule"` so fixture updates are proposed automatically
3. Load `ufc-config.json` and loop over every `evaluation-cases/*.json` file in unit tests
4. Avoid copied fixture directories and programmatic-only shared evaluator cases

Current downstream consumers are `system-tests`, `dd-trace-go`, `dd-trace-java`, `dd-trace-js`, `dd-trace-py`, `dd-trace-rb`, `dd-trace-dotnet`, `dd-trace-php`, `libdatadog`, and `openfeature-js-client`.

## Questions?

If you have questions about contributing, please open an issue or reach out to the FFE SDK team.
