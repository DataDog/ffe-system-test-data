# Publication in Leo's Datadog workspace

Read the current workspace instructions; they override this reference. No push unless Leo explicitly authorizes it. Use regular git push. Never git commit --amend. Every commit, including merge/repair commits, must be signed; signing failure stops before commit or push.

Before committing, verify that the intended GitHub account, account associated with the committer email, and owner of the registered signing key match. Inspect configured/available keys; do not replace a working key merely to match a different active gh login. Select authentication for the intended signing identity. Restore/forward SSH_AUTH_SOCK if needed; do not disable signing.

Before publishing, cryptographically verify every outgoing commit and confirm each signing key is registered to the committer's GitHub account. For an existing PR, audit its entire paginated commit list, including old and merge commits. Unknown/missing signatures or identity mismatch are hard stops. After push, GitHub must report verification.verified=true and reason=valid for every newly published commit and every PR commit before signing success can be claimed.

Remote history rewriting requires a current one-time exception for an exact ref. Verify the live tip, create a local backup ref, and use SHA-pinned --force-with-lease=<ref>:<expected-old-sha>; never bare --force. The exception expires after one attempt. A signed merge does not repair an unsigned ancestor.

If an authorized HTTPS push fails with Invalid username or token, inspect the remote without exposing secrets. Remove embedded credentials in favor of a credential-free canonical remote, use the protocol configured by gh, restore the agent if necessary, and retry the same regular push once. For HTTPS use an ephemeral credential helper; never print, persist or embed the token. If the retry fails, stop and report the concrete authentication blocker.

Create draft PRs only. Never change a draft to ready. Use Motivation and Changes and Decisions sections, customer behavior first, concise rollout decisions, and optional small Mermaid diagrams. Omit unit-test/CI summaries from PR prose; keep evidence in the bundle. Before any readiness assessment, refresh live head/diff/checks/unresolved threads and separate review approval from mergeability. Honor the draft-only constraint even when CI is green.
