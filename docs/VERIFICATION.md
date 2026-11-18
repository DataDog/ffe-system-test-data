# Verification

The [verification contract](../factory/contracts/verification.yaml) maps
changed paths to the CI fixture validators. Each procedure runs the same
commands as `.github/workflows/validate-*.yml` through
[the fixture check adapter](../scripts/factorykit_fixture_check.py).

Plan a committed change, then run the plan. Keep evidence outside the
repository:

```bash
"$factorykit_executable" --root . --format json verification plan \
  --request /tmp/ffe-request.json --base <BASE_SHA> --head <HEAD_SHA> \
  --judgment /tmp/ffe-judgment.json --output /tmp/ffe-plan.json
"$factorykit_executable" --root . --format json verification run \
  --request /tmp/ffe-request.json --head <HEAD_SHA> \
  --plan /tmp/ffe-plan.json --output /tmp/ffe-results.json
```

The `response-signing` procedure needs the `python-cryptography`
prerequisite. Pass `--prerequisite python-cryptography` when the
`cryptography` package is installed.

These procedures validate the fixtures in this repository only. They do not
prove that a downstream SDK conforms to the contract.
