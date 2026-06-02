# Precomputed Assignment Fixtures

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
