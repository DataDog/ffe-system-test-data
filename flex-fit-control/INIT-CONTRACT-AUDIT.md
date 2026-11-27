# Initialization contract audit across WIP columns

CONTROL-031, November27. Proposal for review; no implementation or live runner changed.

Current init contracts cannot identify all four modes unambiguously. Main/merged221 selects online precomputed from URL versus offline rules from serialized wire. Portable235 broadens offline wire to precomputed/rules/hybrid, allowing SDK selection by context. Android/current RN additionally select API access. iOS/Flutter retain baseline schema; all current native flag candidates implement online precomputed only. Electron shares Web; KMP/MAUI flag services remain implementation work. Published PR heads were refreshed and latest RN workspace source checked privately. Unity remains Not planned.

| Explicit requested mode | Required source | Forbidden source |
| --- | --- | --- |
| Online precomputed | Nonempty configuration endpoint URL | Any configuration wire |
| Offline precomputed | Pre-produced serialized precomputed ConfigurationWire | Nonempty configuration URL |
| Online rules | Nonempty rules configuration endpoint URL | Any configuration wire |
| Offline rules | Existing generated serialized rules ConfigurationWire | Nonempty configuration URL |

Require an explicit known mode independent of OpenFeature/direct access. Reject missing/conflicting sources, mismatched evaluator payload, unknown values and unsupported combinations before provider replacement. Do not infer mode from URL suffix, payload shape or SDK availability. Hybrid wire cannot silently choose a different evaluator: require an SDK facility guaranteeing the requested mode, otherwise reject for pure-mode init. Preserve independent hybrid/round-trip coverage.

Preserve init fields1–6 and nested client-access field3. Proposed mode uses unused nested field4; legacy source/type allocations1/2 must never be renumbered or reused. Legacy defaulted callers and old generated servers need deliberate migration and exact paired versions: an old server can ignore an unknown selector. This proposal has not been applied or dispatched.

Corpus generation already uses the JavaScript serializer for configuration-wire.json. Python verifies artifact checksums and forwards exact contents. No new Python SDK producer is required; IPC consumes via SDK APIs and never constructs or reserializes wire.

Required verification covers4modes against URL-only/wire-only/both/neither, absent/unknown mode/access, invalid/mismatched/hybrid payload, context presence, waiting semantics, exact artifact forwarding and unchanged provider on rejected requests. Configuration fetch/no-fetch, actual evaluator and intake proof remain per-cell runtime gates. Online-precomputed-first sequencing remains. Full source-backed audit and proposed shape retained privately by coordinator.
