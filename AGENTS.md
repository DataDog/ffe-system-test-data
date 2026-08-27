# AGENTS.md — Writing FFE Test Fixtures

This guide is for AI agents and contributors writing test fixtures for the
Datadog Feature Flag Evaluation (FFE) system test data repository.

## Repository layout

```
ufc-config.json                        # Flag definitions (UFC server format)
evaluation-cases/test-*.json           # Server-side evaluation test cases
precomputed-assignments/cases/*.json   # Client-side precomputed assignment fixtures
precomputed-assignments/README.md      # Precomputed fixture format reference
```

## Choosing the right fixture type

- **evaluation-cases**: For server SDKs (dd-trace-java, dd-trace-py,
  dd-trace-dotnet, dd-trace-go, etc.) that evaluate flags locally using
  `ufc-config.json`. Each file is a JSON array of test case objects.
- **precomputed-assignments**: For client SDKs (Android, iOS, browser, Flutter,
  etc.) that consume pre-evaluated assignments from a server. Each file is a
  single JSON object containing a mocked server response and evaluations to run.

## Evaluation cases schema

Each file in `evaluation-cases/` is a JSON array. Every element has:

```json
{
  "flag": "flag-key",
  "variationType": "BOOLEAN|STRING|INTEGER|NUMERIC|JSON",
  "defaultValue": "<typed default>",
  "targetingKey": "entity-id or null",
  "attributes": {"key": "value"},
  "result": {
    "value": "<expected value>",
    "reason": "TARGETING_MATCH|SPLIT|STATIC|DEFAULT|ERROR|DISABLED",
    "errorCode": "PARSE_ERROR|FLAG_NOT_FOUND|TYPE_MISMATCH"
  }
}
```

### Field reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `flag` | string | yes | Flag key; must exist in `ufc-config.json` or expect `FLAG_NOT_FOUND` |
| `variationType` | string | yes | `BOOLEAN`, `STRING`, `INTEGER`, `NUMERIC`, or `JSON` |
| `defaultValue` | any | yes | Default value passed to the evaluator |
| `targetingKey` | string or null | yes | Subject identifier; use `null` only for missing-key tests |
| `attributes` | object | yes | Targeting context attributes (may be `{}`) |
| `result.value` | any | yes | Expected evaluation result |
| `result.reason` | string | no | OpenFeature reason code |
| `result.errorCode` | string | no | OpenFeature error code |
| `description` | string | no | Human-readable description of the test case |

### Adding a new flag

If your test case requires a flag not in `ufc-config.json`, add it there first.
Every `flag` value in a test case must correspond to a key in `ufc-config.json`.

### Reason codes

- `TARGETING_MATCH` — entity matched an explicit rule condition
- `SPLIT` — entity assigned via consistent hashing into a shard range
- `STATIC` — single allocation at 100%, no rules or shards
- `DEFAULT` — no allocation matched; default value returned
- `ERROR` — evaluation error (always paired with an `errorCode`)
- `DISABLED` — flag is disabled

### Error codes

- `FLAG_NOT_FOUND` — flag key does not exist in the configuration
- `PARSE_ERROR` — flag was rejected at parse time (malformed config)
- `TYPE_MISMATCH` — requested type does not match `variationType`
- `TARGETING_KEY_MISSING` — evaluation requires targeting key but none provided
- `PROVIDER_NOT_READY` — provider not initialized
- `INVALID_CONTEXT` — evaluation context is invalid

## Precomputed assignment fixtures schema

Each file in `precomputed-assignments/cases/` is a single JSON object:

```json
{
  "name": "fixture-name",
  "description": "What this fixture tests.",
  "context": {
    "targetingKey": "user-id",
    "attributes": {}
  },
  "response": {
    "data": {
      "attributes": {
        "flags": {
          "flag-key": {
            "allocationKey": "allocation-a",
            "variationKey": "variation-a",
            "variationType": "boolean",
            "variationValue": true,
            "reason": "TARGETING_MATCH",
            "doLog": true
          }
        }
      }
    }
  },
  "evaluations": [
    {
      "flag": "flag-key",
      "variationType": "boolean",
      "defaultValue": false,
      "expectedResult": {
        "value": true,
        "reason": "TARGETING_MATCH",
        "errorCode": null,
        "variantKey": "variation-a"
      }
    }
  ],
  "expectations": {
    "exposureEventCount": 1,
    "evaluationEventCount": 1
  }
}
```

### Top-level fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Fixture identifier (matches filename stem) |
| `description` | string | yes | What the fixture tests |
| `context` | object | yes | `targetingKey` (string) and `attributes` (object) |
| `response` | object | yes | Mocked precomputed-assignments JSON:API response |
| `evaluations` | array | yes | Typed flag evaluations to run |
| `expectations` | object | yes | Expected emission counts and event matchers |
| `skip` | array | no | Per-platform skip entries for the entire fixture |

### Response flag fields

Each flag in `response.data.attributes.flags` has:

| Field | Type | Description |
|-------|------|-------------|
| `allocationKey` | string | Allocation that resolved this flag |
| `variationKey` | string | Variation key for the assigned value |
| `variationType` | string | `boolean`, `string`, `integer`, `float`, or `object` |
| `variationValue` | any | The pre-evaluated flag value |
| `reason` | string | Server-side reason code |
| `doLog` | boolean | Whether to log exposure events |

Note: `variationType` uses lowercase in precomputed responses (`boolean`,
`string`, `integer`, `float`, `object`) unlike UFC which uses uppercase
(`BOOLEAN`, `STRING`, `INTEGER`, `NUMERIC`, `JSON`).

### Evaluation fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `flag` | string | yes | Flag key to evaluate |
| `variationType` | string | yes | Type to request from the SDK |
| `defaultValue` | any | yes | Default value passed to the getter |
| `expectedResult` | object | yes | Expected outcome |
| `expectedResult.value` | any | yes | Expected flag value |
| `expectedResult.reason` | string | no | Expected reason code (null if error) |
| `expectedResult.errorCode` | string | no | Expected error code (null if success) |
| `expectedResult.variantKey` | string | no | Expected variation key (null if error) |
| `skip` | array | no | Per-platform skip entries for this evaluation |

### Expectations fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `exposureEventCount` | int | yes | Expected exposure events after flush |
| `evaluationEventCount` | int | yes | Expected flagevaluation events after flush |
| `overrides` | array | no | Per-platform count overrides |
| `overrides[].platform` | string | yes | Platform identifier |
| `overrides[].exposureEventCount` | int | yes | Override exposure count |
| `overrides[].evaluationEventCount` | int | yes | Override evaluation count |
| `events` | object | no | Field-level matchers (subset match contract) |

### Skip entries

Skip entries use `{"platform": "<id>", "reason": "<why>"}`. They can appear at
case level, evaluation level, or event matcher level.

Valid platform identifiers: `web`, `ios`, `android`, `react-native`, `flutter`,
`maui`, `kotlin-multiplatform`, `electron`.

```json
"skip": [
  {"platform": "web", "reason": "Browser SDK aggregates differently."}
]
```

## Naming conventions

- All schema field names use **camelCase** (`expectedResult`, `variationType`,
  `evaluationEventCount`).
- Snake_case in fixture data is only for wire-format fields that match emitted
  event schemas (e.g., `evaluation_count`, `serial_id`).
- Fixture filenames use **kebab-case** (`malformed-flag-isolation.json`).
- Evaluation-case filenames use `test-case-` or `test-` prefix.

## Emission count rules

- **Exposures**: Only emitted when `doLog: true` on the flag AND the evaluation
  succeeds (no error). Malformed/dropped flags produce zero exposures.
- **Evaluation events**: Emitted for ALL evaluations (success and error alike)
  per EVALLOG.2 in the FFE SDK Requirements.
- **Web overrides**: Browser SDK typically emits `evaluationEventCount: 0`
  because evaluation events are not yet implemented on web, or aggregates them
  differently.

## Validation

Before opening a PR:

1. Validate all JSON: `jq . path/to/file.json`
2. Every `flag` in evaluation-cases must exist in `ufc-config.json`
3. Run `python3 ci/validate-fixtures.py` if available

## Common patterns

### Testing flag isolation

When testing that malformed flags don't break valid ones, interleave valid and
malformed flags in the response, then assert valid flags return correct values
while malformed flags return `defaultValue` with `FLAG_NOT_FOUND`.

### Testing type mismatch

To test that requesting the wrong type returns an error, put a valid flag in
the response but evaluate it with a different `variationType` than declared.
Expect `defaultValue` with `TYPE_MISMATCH` error code.

### Platform-specific behavior

When behavior differs across platforms, use `skip` entries on individual
evaluations rather than skipping the entire fixture. Use
`expectations.overrides` to adjust emission counts for platforms that skip
evaluations.
