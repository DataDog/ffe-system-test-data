# Opt-out decisions from browser and Go review

This is a **draft central-contract proposal**, based on FFE data main
[`89a0f33`](https://github.com/DataDog/ffe-system-test-data/commit/89a0f339b83f0cb6fabed77cc1164d97c9d24356).
The existing evaluation fixtures are unchanged. D004 has separate published Go
implementation and native validation evidence below; fleet approval and deployment
remain separate.

The source workflow is the Codex chat **LEAN**, ID
`01a1309a-1ca7-73e0-bc62-8bad9a0a6d07`, and its `ffe-contract-poc` experiment.
The six imported files are byte-preserved with provenance hashes. Browser
[#423](https://github.com/DataDog/openfeature-js-client/pull/423) is now merged
at `58bc213b51eb539d58ee4a5c7719ccf500f09b66`; the reviewed head was `38d611c`.
Its outcomes establish browser behavior, not automatic adoption by other SDKs.

## Initial review snapshot

| PR | Reviewed head | Relationship and review state |
| --- | --- | --- |
| [#5666 immediate](https://github.com/DataDog/dd-trace-go/pull/5666) | `d93b70746785718b6f43bf9ffee13d01e332f50e` | Changes requested; 6 unresolved threads. |
| [#5700 future](https://github.com/DataDog/dd-trace-go/pull/5700) | `febcc185d27d8edbe4acf16ce2dee91d5aff730c` | Approved with a request to address Aaron's comments; 8 unresolved threads. |

The child contains parent `de399851`, not `d93b707`. Integrate parent changes
without rewriting published history when implementation is authorized. The
child still has the older error constructor and lacks the parent's added
whole-evaluation benchmark. Review approval is separate from CI and mergeability.
At snapshot time #5666 has a failed performance-gate status; #5700's latest
reported statuses are successful. The latter does not resolve the outstanding
review feedback or replace the benchmark evidence quoted in that discussion.

The main remaining work is:

1. **Default-path performance:** the mode guard inside `excludes` did not satisfy
   the later request for a guard at the allocation-loop call site. The reviewer
   reports 7 CI regressions at `febcc185`, +2.1% to +6.7%; this task did not rerun
   those benchmarks. Preserve that head-specific evidence and obtain a fresh
   whole-evaluation measurement after a fix. [Follow-up](https://github.com/DataDog/dd-trace-go/pull/5700#discussion_r4342540461).
2. **Malformed activation: browser D004 selected for Go.** Leo explicitly chose
   the browser rule in this review session: preserve invalid separately and return
   PARSE_ERROR only for an opted-out future-mode subject. Go now implements the rule at
   [`c5fec6a009ff`](https://github.com/DataDog/dd-trace-go/commit/c5fec6a009ffa29bf53f5377a21856c7c4aa5f56).
   [Native evidence](evidence/go-d004/native-receipt.json) records 90 applicable
   policy cases plus full-package/race checks and two negative controls.
   The [decision reply is published](https://github.com/DataDog/dd-trace-go/pull/5700#discussion_r4351454041); the [updated body is saved locally](evidence/go-d004/published-implementation-reply.json).
   [Local adoption record](evidence/go-5700-d004-adoption.json); fleet adoption is separate.
   [Request](https://github.com/DataDog/dd-trace-go/pull/5700#discussion_r4342540303).
3. **Disabled-provider precedence:** the current constructor validates mode before
   resolving disablement. D015 proposes returning NoopProvider first when settings
   resolve to disabled, preserving the documented kill-switch behavior. It needs
   native constructor tests and explicit acceptance before fleet reuse.
   [Request](https://github.com/DataDog/dd-trace-go/pull/5666#discussion_r4342541816).
4. **Timestamp policy:** the proposed Go lowercase-rejection rows conflict with the
   later browser decision to accept lowercase and truncate excess fraction digits.
   Whitespace and invalid-calendar controls remain useful. A native-parser parity
   test cannot decide the fleet grammar. [Go request](https://github.com/DataDog/dd-trace-go/pull/5666#discussion_r4342542473),
   [later browser decision](https://github.com/DataDog/openfeature-js-client/pull/423#discussion_r4348403258).
5. **Native safety and integration:** preserve the typed-nil Stringer follow-up,
   same-key Remote Config activation refresh, complete fixture inventory, and
   future-mode benchmark registration as native obligations. The panic predates
   this PR; no native fix is included here. [Panic](https://github.com/DataDog/dd-trace-go/pull/5666#discussion_r4342542617),
   [refresh/inventory](https://github.com/DataDog/dd-trace-go/pull/5700#discussion_r4342541315).

The strict invalid-subject-input tradeoff is already explicit: Leo chose
INVALID_CONTEXT/default in enabled modes, including ordinary flags. Preserve
that decision and document precedence over flag lookup after existing readiness
and targeting-key checks. Do not replace it with inferred opt-out intent.
[Author decision](https://github.com/DataDog/dd-trace-go/pull/5666#discussion_r4329524575).

Immediate fixtures #49 are merged and #5666 pins the landed commit. Future
fixtures #52 remain open and #5700 pins an earlier proposal commit. Producer
activation metadata and `doLog=false` ordinary winner delivery remain deployment
dependencies. These were not verified against a deployed backend in this task.
The remaining optional helper/error/comment changes are in the complete ledger.

## Persisted review surface

- [decisions.json](decisions.json): 14 existing IDs, three additional Go decisions,
  explicit scope/authority, and three distinguishing conflict cases.
- [decision-history.md](decision-history.md): each current decision-setting PR/thread
  and a linked historical table of passing, failing and incomplete checks. Three
  imported rules (D008, D009, D014) have PR context but no identified public
  setting of the complete rule. D004 now links to the published Go decision;
  its prior browser-setting link and historical checks are retained.
- [validation-history.json](validation-history.json): append-only checks with
  tested revisions/profiles, source/patch pins, evidence kinds and limits.
  Regenerate the table with `python3 contracts/experimentation-opt-out/decision_history.py`.
  A later test does not replace a decision-setting source. Earlier POC receipts
  are preserved in [evidence/poc-receipts.json](evidence/poc-receipts.json), including
  backend disagreements; those Go parser rows belong to dd-source, not dd-trace-go.
- [feedback.json](feedback.json): 24 dispositions covering all inline conversations,
  release dependencies, and the split refresh/inventory concern.
- [evidence/go-review-snapshot.json](evidence/go-review-snapshot.json): all paginated
  conversation comments, review submissions, inline replies and thread states;
  quoted executions remain reviewer/author reports.
- [evidence/source-pins.json](evidence/source-pins.json): exact inspected file hashes,
  stack merge-base, and fixture pins.
- [propagation.json](propagation.json): proposed implementation-owner routing.
- [browser-decisions.json](browser-decisions.json), [provenance.json](provenance.json):
  unchanged historical browser proposal and import provenance.

## Runnable model and limits

The imported Lean model covers timestamp parsing, allocation policy, browser
pending errors, request options and acknowledgement admission. Its 30 existing
theorems and 313 oracle rows are retained. Six new theorems in
[lean/Review.lean](lean/Review.lean) cover proposed provider-disablement ordering,
scoped lookup precedence, and the fact that activation alternatives differ.
The model keeps the alternatives distinguishable. Leo selected the browser policy
for Go in the local adoption record; the model itself does not confer approval.

These are model properties. They do not prove full parser correctness, native
SDK refinement, nil safety, latency, lifecycle, transport, concurrency or deployed
behavior. Earlier mobile POC results are historical evidence and are not rerun here.
No tests may be removed based on this proposal alone.

Use Lean **4.19.0**. From the repository root, supply the independently reviewed
SHA-256 of `manifest.json` (recorded in the handoff, not trusted merely because a
mutable neighboring file supplies it):

```sh
python3 contracts/experimentation-opt-out/verify.py \
  --manifest-sha256 REVIEWED_MANIFEST_SHA256 \
  --lean /absolute/path/to/lean-4.19.0/bin/lean
```

The verifier checks frozen file hashes, exact case inventory and controls, decision
references, provenance/history links, rendered-table freshness and complete thread classification; compiles the model/proofs; audits
every theorem's axioms; and replays all oracle inputs in a temporary build directory.
A passing result means this proposal is internally checked, not fleet-approved.
Changing semantics requires a new revision and new downstream receipts. The
manifest is a reproducibility mechanism; it is not a substitute for review.

[Saved local validation](evidence/local-validation.json) records 36 audited
theorems, 313 matching oracle outputs and the axiom report. Eight acceptance
negative controls pass (`python3 -m unittest discover -s
contracts/experimentation-opt-out -p test_verify.py`). Existing repository
checks also pass: 345 evaluation cases, four validator tests and 12 precomputed
fixtures. The independent skill forward-test correctly distinguished all three
activation policies, the browser casing reversal, partial performance fix and
conditional approval; its collector pagination mocks exercised REST, thread and
nested-reply pages. The original proposal ran no native SDK suites. The later D004 Go implementation
now has native suite/race and 90-case policy evidence in [its receipt](evidence/go-d004/native-receipt.json).
No performance benchmarks, system-tests at the new SHA or deployment checks were run for that update.

The reusable workflow lives in [lean-sdk-feedback](../../skills/lean-sdk-feedback/SKILL.md)
and [lean-sdk-decisions](../../skills/lean-sdk-decisions/SKILL.md).
