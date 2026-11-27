# Rules resource audit — coordinator verification

CONTROL-053, November 27, 2026. BitsCode completed a documentation-only audit locally and delivered Markdown/patch attachments in [its Slack handoff](https://dd.slack.com/archives/C0CKGQ8T483/p1795817755308099). Its branch is not present on remote at the coordinator's check. Automatic approval review in that session rejected a required PR-metadata step because PRs were forbidden. Do not retry the rejected action or create a PR. Coordinator requests a text handoff if publication remains unavailable, then can preserve the audit through the already-authorised Control workflow. The text handoff was subsequently completed and independently reconstructed: all eight chunk hashes and the final16,796-byte/239-line document hash matched. The unchanged [full audit](../docs/audits/BITS-02-rules-resource-provenance.md) is preserved on this Control Branch; document SHA256 `e587c293acdeeb4b6b9dfaf96fc01a9b2d012c8e24616dbcf46a22a4ab500447`. The BitsCode branch itself remains unpublished; no rejected metadata action was retried.

## Independently verified current public main

Pinned main: `fe24ed2c4872bf109b0c71ffb2229152d76b8963`.

- Catalogue contains one resource, canonical-evaluator, from ufc-config.json.
- Source has68flags:50converted and18omitted. Those omissions affect20of398core evaluation cases. Keep producer/conversion limitations distinct from SDK defects; do not count these cases as SDK conformance.
- Five optional suites contain269cases in total: dependent-flags16, flag-selection62, regex69, scale-json13, scale109. None has a catalogue resource pair. Main therefore has667authored cases, while only the core resource is generated.
- The exact protobuf artifact is20,436bytes, SHA256 `8d01db1863661d0086f7139461d7110715e5e979af23e445f6b557d07094a0d6`.
- The exact ConfigurationWire artifact is27,285UTF-8bytes, SHA256 `e9f3dd55172d2c39dd2ca5e583caf1ed8f071d9769f845673d1f077628a62465`. Send those existing serialized contents for offline initialization; no replacement serializer is required.
- All declared generator-input hashes match. The WS-12 verified resource loader accepts this exact main snapshot.

## Independently verified open PR86

[PR86](https://github.com/DataDog/ffe-system-test-data/pull/86), head `67873b470ce5cec9e2e1a45650dcc2fff12e9ac1`, adds source flags/cases without refreshing the generated resource pair/manifest. Its source has72flags and410core cases. The manifest still declares the previous source digest `e7b29c91472d9b9064ee01f08b50acd5e81f55b1465d5ffc622f7d8a60e18d66`; actual source digest is `ac82b833a99749cea36fbd1ebd7e03c556af440c0de91bbaca999205faef7bfc`.

The WS-12 loader rejects this exact snapshot as stale and requests resource regeneration. Regenerate through the existing producer before adopting this PR for binary/wire testing. Do not weaken provenance checks or silently pair the old payload with the new cases. No PR feedback, fixture change, regeneration or ticket was published by this verification.

## Remaining audit handoff and scope

BitsCode reports nine tooling tests and six diagnostic missing-PARSE_ERROR discrepancies. The full unchanged audit has now been read and preserved. Its nine tooling tests and diagnostic execution remain implementor-reported rather than independently re-executed, and the six discrepancies are not SDK defect classifications. The canonical counts/hashes and PR86 stale rejection were independently verified above. No FIT SDK rules-mode runtime was executed; no later platform cell was activated and no activation PR opened.
