"""FactoryKit command-v1 adapter that runs the repository's CI fixture validators (POC)."""

from __future__ import annotations

import json
import os
import subprocess
import sys

# Same commands as .github/workflows/validate-*.yml.
SUITES = {
    "ufc-fixtures": [
        ["python3", "ci/validate-fixtures.py"],
        ["python3", "ci/generate-scale-suite.py", "--check"],
    ],
    "precomputed": [
        ["python3", "ci/validate-precomputed-fixtures.py"],
        ["python3", "ci/precomputed_obfuscation.py", "--check"],
        ["python3", "-m", "unittest", "discover", "-s", "ci", "-p", "test_precomputed*.py"],
    ],
    "response-signing": [
        ["python3", "response-signing/generate-boundary-supplements.py", "--check"],
        ["python3", "ci/validate-response-signing.py"],
    ],
    "flag-selection": [
        ["python3", "ci/validate-flag-selection.py"],
    ],
    "ci-unittests": [
        ["python3", "-m", "unittest", "discover", "-s", "ci", "-p", "test_*.py"],
    ],
}


def main() -> int:
    request = json.load(sys.stdin)
    fields = request["result_fields"]
    context = request["context"]
    suite = request["input"]["suite"]
    evidence = []
    passed = True
    for command in SUITES[suite]:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=900,
                                   env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        output = (completed.stdout + completed.stderr)[-4000:]
        evidence.append({"kind": "command", "ref": " ".join(command),
                         "summary": f"exit={completed.returncode}; output={output}"})
        passed = passed and completed.returncode == 0
    status = "pass" if passed else "fail"
    result = {
        "schema_version": 1, "kind": "work-result", "id": fields["id"],
        "context_mode": fields["context_mode"], "request_ref": fields["request_ref"],
        "execution_profile": fields.get("execution_profile", "direct"),
        "stage": "verify", "result_scope": "procedure", "procedure_id": fields["procedure_id"],
        "configuration_identity": fields["configuration_identity"],
        "implementation_identity": fields["implementation_identity"],
        "evaluated_revision": fields["evaluated_revision"],
        "outcome": status,
        "evidence": evidence,
        "criterion_results": [
            {"criterion_id": criterion, "status": status, "evidence": evidence, "findings": []}
            for criterion in context.get("criteria", [])
        ],
        "blockers": [], "unrun": [],
    }
    if "plan_ref" in fields:
        result["plan_ref"] = fields["plan_ref"]
        result["selection_basis"] = fields["selection_basis"]
    if "task_ref" in fields:
        result["task_ref"] = fields["task_ref"]
    print(json.dumps(result, sort_keys=True))
    return 0


raise SystemExit(main())
