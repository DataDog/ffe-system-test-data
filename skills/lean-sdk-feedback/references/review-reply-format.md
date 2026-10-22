# Leo’s shared-contract review reply format

Use this layout for a substantive Lean-backed decision reply in Leo’s PR review workflow. The user-selected example is [the Go D004 reply](https://github.com/DataDog/dd-trace-go/pull/5700#discussion_r4351454041). Treat it as a presentation example, not authority for another decision’s semantics, test counts, or scope.

Keep the visible opening short and put the behavior matrix, validation detail, and proof-workflow explanation in collapsible sections. Preserve the applicable decision revision, original authority, exact tested source, and evidence limits.

## Visible opening

1. Start with `🤖 **Comment from Codex working with Leo:**`.
2. Give a bold **Decision [ID, revision N](exact-published-decision-permalink): concise rule.**
3. Briefly acknowledge the reviewer’s concrete concern, explain the chosen behavior, and link the decision-setting source. Distinguish a reviewer proposal from the author’s choice. Do not invent prior agreement.
4. Give a bold **Implemented in [short SHA](published-commit-url).** Explain the implementation in one short paragraph. When validation occurred at a later merge, link that tested commit separately.
5. Give **Shared proofs:** with both the central draft PR and the exact published decision permalink.

## Collapsible detail

Use these three labels for substantive shared-contract decisions:

```html
<details>
<summary><b>Behavior</b> — the distinction we are preserving</summary>

<!-- Situation/result table, followed by the deliberate tradeoff and any mode-specific boundary. -->

</details>

<details>
<summary><b>Native validation</b> — local checks at <a href="published-commit-url">short SHA</a></summary>

<!-- Native results, distinguishing cases, negative controls, and limits. -->

</details>

<details>
<summary><b>Sneak preview</b> — turning review decisions into reusable, checked contracts</summary>

<!-- Linked artifacts, an actual checked theorem, plain-English meaning, and proof limits. -->

</details>
```

Leave blank lines inside each `details` block so GitHub renders Markdown tables, lists, and code fences. In `summary`, use an HTML anchor for a commit link as shown; keep the visible SHA short.

- **Behavior:** use a small situation/result table. Explain the selected tradeoff and meaningful alternatives, without reopening an already-authorized choice.
- **Native validation:** report the actual checked boundary, tested commit, applicable cases, negative controls, and regression checks. Preserve earlier failures and source pins. Label local tests, CI, deployment, and unperformed checks separately. Later merge results should not silently overwrite earlier mutation receipts.
- **Sneak preview:** link the versioned English decision, executable model/proof, applicable shared corpus, and linked validation history. Include one short theorem copied from the verified published model, followed by its precise plain-English meaning. Report current model/oracle counts only from verified evidence. If a corpus does not cover this new producer rule, say so; do not imply native conformance from model-only cases. Close with the model/native boundary and the draft’s adoption status.

For a mechanical query, formatting, or harness fix without a shared semantic decision, keep the attribution, linked implementation, concise result, and applicable native evidence. Do not fabricate a decision or proof preview to fill the layout.

Before posting, verify all publication links and the copied theorem against their exact revisions. Read back the edited comment, preserve its stable URL in the knowledge base, and retain earlier receipts as history. This format does not authorize publication or expand a request’s scope; use the session’s existing authorization.
