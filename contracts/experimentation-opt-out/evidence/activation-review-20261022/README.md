# Public activation feedback evidence

This directory publishes the reusable RFC decision, Lean proofs, source hashes,
native test counts, and review dispositions. Full internal RFC/PR snapshots,
private source patches, SQL traces, and raw logs are retained in the private local
evidence worktree. They are not part of this publication history.

- [RFC reconciliation](decision-reconciliation.json) and [decision summary](rfc-snapshot.json).
- [Feedback ledger](feedback-ledger.json) and [draft replies](review-replies.md).
- [Original native results](native-validation.json), including the two failing
  baseline cases, test-assertion correction, timeout attempts and eventual pass.
- [Native results after main integration](main-merge-native-validation.json).
- [Merged model results](merged-model-validation.json) and [provenance](merge-model-provenance.json).
- [Public export provenance](public-export.json) maps original evidence hashes
  to these reduced summaries. Historical source and patch hashes continue to
  identify the private originals; public summaries are not byte-identical copies.

The new native regression directly exercises the database service. Existing HTTP,
cross-DC and lifecycle suites provide surrounding coverage. No new exact HTTP
sync-start reproduction, combined producer/future evaluator test, CI or deployed
end-to-end result is claimed. The central contract remains a draft.
