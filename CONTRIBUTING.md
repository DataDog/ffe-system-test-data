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
    "result": { "value": "<expected value>" }
  }
]
```

3. If your test case requires a new flag, add the flag definition to `config/ufc-config.json`

### Modifying Flag Configuration

When adding or modifying flags in `config/ufc-config.json`:

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

After your changes are merged to this repository, you need to update the submodule references in downstream repos:

### system-tests

```bash
cd system-tests
git checkout -b update-ffe-test-data
cd tests/parametric/test_ffe/ffe-data
git fetch origin && git checkout main && git pull
cd ../../../..
git add tests/parametric/test_ffe/ffe-data
git commit -m "Update ffe-system-test-data submodule"
git push origin update-ffe-test-data
# Create PR
```

### dd-trace-py

```bash
cd dd-trace-py
git checkout -b update-ffe-test-data
cd tests/openfeature/ffe-data
git fetch origin && git checkout main && git pull
cd ../../..
git add tests/openfeature/ffe-data
git commit -m "Update ffe-system-test-data submodule"
git push origin update-ffe-test-data
# Create PR
```

### Other Tracers

Follow the same pattern for other tracer repositories (dd-trace-java, dd-trace-dotnet, etc.) that consume this submodule.

## Questions?

If you have questions about contributing, please open an issue or reach out to the FFE SDK team.
