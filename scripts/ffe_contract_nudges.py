"""FFE contract advisories for the FactoryKit Foundation gate (POC)."""

from __future__ import annotations

from factorykit.document_checks import Advisory, NudgeContext

_CONTRACT_PREFIXES = (
    "ufc-config.json",
    "evaluation-cases/",
    "evaluation-suites/",
    "precomputed-assignments/",
    "response-signing/",
    "flag-selection/",
    "rules-resources/",
    "schemas/",
)

_KB_URL = "https://docs.google.com/spreadsheets/d/1vduq0DwkVf16o0vmlcuj5smrOt6ick6m6-WxbAYxWF8/edit"


def contract_decision_nudges(context: NudgeContext) -> tuple[Advisory, ...]:
    """Ask for a decision record when a change alters the shared contract."""
    changed = [path for path in context.change_paths if path.startswith(_CONTRACT_PREFIXES)]
    if not changed:
        return ()
    named = ", ".join(changed[:10])
    if len(changed) > 10:
        named += f", and {len(changed) - 10} more"
    message = (
        f"Contract paths changed: {named}. Search the FFE LEAN KB ({_KB_URL}) "
        "Decisions and Source_Requirements for the affected behavior. Cite the "
        "decision key and revision in the PR. If the change makes a new decision, "
        "record it with the lean-kb-sheets skill. Downstream SDKs must conform to "
        "this contract, so name the consumers that need follow-up."
    )
    return (Advisory(message, code="ffe_contract_decision_nudge"),)
