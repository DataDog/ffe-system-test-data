# Cross-repository change requests

No requests filed yet. Use this ledger when a contributor cannot access a required repository. Link committed requests in Slack so the coordinator can relay/apply them. Reports alone do not imply the target repository changed.

## Request template

- ID: REQ-number; author/date; status: proposed / accepted / implemented / verified / blocked.
- Target repository and exact base revision; blocking cells; existing owner/ticket/PR.
- Access limitation/error and verification scope.
- Requested file paths and exact diff, or sufficiently precise implementation changes and rationale. Put long patches under requests/REQ-number.patch and link them here.
- Required checks and acceptance evidence; fixture/SDK dependencies; exclusions affected.
- Delivery branch/commit and verification receipt when implemented.

Fetch/rebase before Control Branch writes, preserve others' updates and never force-push over another contributor. If you cannot push the Control Branch, send the request to the coordinator for committed publication.
