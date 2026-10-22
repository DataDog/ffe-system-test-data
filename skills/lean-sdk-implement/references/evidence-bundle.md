# Implementation evidence bundle

A bundle identifies the repository and immutable base/head, working-tree state, owned paths, requirement IDs, contract SHA256, corpus SHA256, reviewed applicability profile ID and independently pinned profile-manifest SHA256. Include the patch file and its SHA256, the source files exercised by the adapter, allowed exclusions with expected counts, and which semantics the adapter preserves or excludes. A worker cannot invent a new profile to make a failing trace pass.

For each native check record the exact argv/cwd, toolchain, exit code, log path, discovered adapter name and executed trace/event counts. A failed build or zero matching tests is not a passing semantic check. An extracted-source probe is not a full repository test. CI links apply only to their tested head. Preserve minimized counterexamples and explain any accepted contract decision.

Record status as diff-prepared, locally-validated, draft-published, CI-passed, reviewed, merged, released, or downstream-adopted. These are separate observations. Do not mark later states from earlier evidence. A draft PR is not a landed implementation; a merged shared library is not adoption by its wrappers.

Draft PR prose follows the user's current policy: sections Motivation and Changes and Decisions. Lead with the customer problem and explain behavior, tradeoffs and rollout. Keep local test logs in the bundle rather than the PR body. Link deployment evidence only if actually observed, with version and limits. Never expose internal study contents to an external destination without authorization for that destination.
