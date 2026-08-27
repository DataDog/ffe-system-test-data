# Precomputed Assignment Fixtures (`precomputed-assignments/`)

These fixtures cover the Datadog precompute assignment API consumed by mobile
and browser SDKs which do not run the evaluator locally.

Each case contains:

- `context`: the evaluation context sent to `/precompute-assignments`.
- `response`: a mocked precomputed response.
- `evaluations`: a set of assignment calls to make against the SDK and expected assignment values.
- `expectations`: expected outcomes after the evaluations and an explicit flush. Fields:
  - `exposureEventCount` — number of exposure events expected at `/api/v2/exposures`
  - `evaluationEventCount` — total number of flagevaluation event payloads
  - `overrides` *(optional)* — per-platform count overrides: `[{"platform": "web", "exposureEventCount": N, "evaluationEventCount": M}]`
  - `events` *(optional)* — field-level matchers for emitted events (see below)

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


## expectations.events — subset match contract

`expectations.events` is an optional field that asserts field-level properties
of specific emitted events. The matching contract is **subset**: each entry in
`expectations.events.exposures` or `expectations.events.flagevaluations` must
match at least one received event. Not every received event needs a
corresponding entry.

Example: `expectations.exposureEventCount: 2` with
`expectations.events.exposures: [{"serial_id": 340132}]` means two exposure
events must arrive AND at least one of them must carry `serial_id: 340132`. The
second event is counted by `exposureEventCount` but is not further constrained.

Matchers that carry `skip` entries are omitted for the listed platforms. The
event is still expected to arrive (counts are unchanged); only the property
assertion is relaxed. To change the expected count in conjunction with skipping
an evaluation or expected event, use the `expectations.overrides` field.

## Skip schema

Skips use a `skip` array of `{sdk, reason}` objects, allowing per-platform
reasons. This field can appear at three levels:

- **Case level** — skip the entire fixture for a platform.
- **Evaluation level** — skip a single evaluation within the fixture. The
  evaluation is not run, but the expected emission counts remain unchanged
  unless `expectations.overrides` adjusts them.
- **Event matcher level** — skip a property assertion on an emitted event.
  The event is still expected to arrive (counts unchanged); only the field
  assertion is relaxed.

```json
"skip": [
  {"platform": "web", "reason": "Web aggregator deduplicates repeated evaluations."},
  {"platform": "ios", "reason": "iOS treats null as invalid object."}
]
```

`skip` replaces the earlier `skipForSdks`/`skipReason` fields.

## Field naming

Evaluation results use `expectedResult` to clearly distinguish fixture
expectations from runtime return values.
