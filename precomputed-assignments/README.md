# Precomputed Assignment Fixtures (`precomputed-assignments/`)

These fixtures cover the Datadog precompute assignment API consumed by mobile
and browser SDKs which do not run the evaluator locally.

Each case contains:

- `context`: the evaluation context sent to `/precompute-assignments`.
- `response`: a mocked precomputed response.
- `evaluations`: a set of assignment calls to make against the SDK and expected assignment values.
- `expectedEmissions`: expected emission counts after the evaluations and an explicit flush. Fields:
  - `exposures` — number of exposure events expected at `/api/v2/exposures`
  - `flagevaluationEvents` — total number of flagevaluation event payloads
  - `overrides` *(optional)* — per-platform count overrides: `[{"platform": "web", "exposures": N, "flagevaluationEvents": M}]`
- `expectedEvents` *(optional)*: field-level matchers for emitted events (see below)

The precompute response uses the assignment shape returned to client SDKs:

```json
{
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
}
```


## expectedEvents — subset match contract

`expectedEvents` is an optional field that asserts field-level properties of
specific emitted events. The matching contract is **subset**: each entry in
`expectedEvents.exposures` or `expectedEvents.flagevaluations` must match at
least one received event. Not every received event needs a corresponding entry.

Example: `expectedEmissions.exposures: 2` with
`expectedEvents.exposures: [{"serial_id": 340132}]` means two exposure events
must arrive AND at least one of them must carry `serial_id: 340132`. The second
event is counted by `expectedEmissions` but is not further constrained.

Matchers that carry `skip` entries are omitted for the listed platforms. The
event is still expected to arrive (counts are unchanged); only the property
assertion is relaxed. To change the expected count in conjunction with skipping
an evaluation or expected event, use the `expectedEmissions.overrides` field.

## Skip schema

Skips use a `skip` array of `{sdk, reason}` objects, allowing per-platform
reasons. This field can appear at case level (skip the entire fixture) or on
individual evaluations and event matchers.

```json
"skip": [
  {"sdk": "web", "reason": "Web aggregator deduplicates repeated evaluations."},
  {"sdk": "ios", "reason": "iOS treats null as invalid object."}
]
```

`skip` replaces the earlier `skipForSdks`/`skipReason` fields.

## Field naming

Evaluation results use `expected_result` (not `result`) to clearly distinguish
fixture expectations from runtime return values.
