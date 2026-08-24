# Precomputed Assignment Fixtures (`precomputed-assignments/`)

These fixtures cover the Datadog precompute assignment API consumed by mobile
and browser SDKs that do not run the full UFC evaluator locally.

Each case contains:

- `context`: the evaluation context sent to `/precompute-assignments`.
- `response`: a JSON:API-style precompute response.
- `evaluations`: typed client calls to run against the response.
- `expectedEmissions`: expected exposure and flagevaluation HTTP emissions after
  the evaluations and an explicit flush.

The precompute response uses the assignment shape returned to client SDKs:

```json
{
  "data": {
    "attributes": {
      "flags": {
        "flag-key": {
          "allocationKey": "allocation-a",
          "variationKey": "variation-a",
          "variationType": "boolean|string|integer|float|object",
          "variationValue": true,
          "reason": "TARGETING_MATCH",
          "doLog": true
        }
      }
    }
  }
}
```

Downstream SDKs should validate typed values, details metadata, persistence
behavior, exposure emission gates, and flagevaluation aggregation using these
fixtures. Live Datadog credentials are not required.

## expectedEvents — subset match contract

`expectedEvents` is an optional field that asserts field-level properties of
specific emitted events. The matching contract is **subset**: each entry in
`expectedEvents.exposures` or `expectedEvents.flagevaluations` must match at
least one received event. Not every received event needs a corresponding entry.

Example: `expectedEmissions.exposures: 2` with
`expectedEvents.exposures: [{"serial_id": 340132}]` means two exposure events
must arrive AND at least one of them must carry `serial_id: 340132`. The second
event is counted by `expectedEmissions` but is not further constrained.

Matchers that carry `skipForSdks` are omitted for the listed platforms. The
event is still expected to arrive (counts are unchanged); only the property
assertion is relaxed.
