#!/usr/bin/env python3
"""Run D017 native observations with an instrumented source overlay.

Inputs remain unchanged; this script writes only its output directory. The
instrumentation adds observations at existing production boundaries and does
not implement the guard or exclusion logic. Never use these binaries for timing.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

BASE = "c5fec6a009ffa29bf53f5377a21856c7c4aa5f56"
PROFILE_MANIFEST_SHA256 = "4d6d2d021b7ca4bb2363f302162272213abdb9cc0aca2e86e3e29ce9067f65e2"
CORPUS_SHA256 = "4cf1ee4ad0a47ad7cba92f80f04a7641e7a3bfc2055787813abfc85b0eb140c2"

def digest(data):
    return hashlib.sha256(data).hexdigest()

def replace_once(source, old, new):
    if source.count(old) != 1:
        raise ValueError(f"expected exactly one instrumentation site: {old}")
    return source.replace(old, new)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path)
    parser.add_argument("corpus", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    repo, corpus, output = args.repo.resolve(), args.corpus.resolve(), args.output.resolve()
    if digest(corpus.read_bytes()) != CORPUS_SHA256:
        raise SystemExit("corpus does not match the reviewed inactive-path-v1 profile")
    output.mkdir(parents=True, exist_ok=True)
    adapter = Path(__file__).with_name("conformance_test.go.txt").resolve()
    provider_file = repo / "openfeature/experimentation_opt_out.go"
    evaluator_file = repo / "openfeature/evaluator.go"
    helper = replace_once(provider_file.read_text(),
        "func (exclusion experimentationExclusion) excludes(a *allocation) bool {",
        "func (exclusion experimentationExclusion) excludes(a *allocation) bool {\n\td017Trace.checks++")
    helper_overlay = output / "experimentation_opt_out.go"
    helper_overlay.write_text(helper)
    receipt = {
        "base_commit": BASE,
        "profile_id": "inactive-path-v1",
        "reviewed_profile_manifest_sha256": PROFILE_MANIFEST_SHA256,
        "corpus_sha256": digest(corpus.read_bytes()),
        "adapter_sha256": digest(adapter.read_bytes()),
        "toolchain": subprocess.check_output(["go", "version"], cwd=repo, text=True).strip(),
        "source_sha256": {str(p.relative_to(repo)): digest(p.read_bytes()) for p in [evaluator_file, provider_file, repo / "openfeature/provider.go"]},
        "runs": {},
        "scope": "36 operational cases through production BooleanEvaluation; excludes entry counts and allocation traversal observations; instrumentation is test-only; no timing claim",
    }
    for name in ["candidate", "baseline"]:
        evaluator = evaluator_file.read_text() if name == "candidate" else subprocess.check_output(["git", "show", f"{BASE}:openfeature/evaluator.go"], cwd=repo, text=True)
        evaluator = replace_once(evaluator, "for _, allocation := range flag.Allocations {", "for _, allocation := range flag.Allocations {\n\t\td017Trace.excluded = append(d017Trace.excluded, true)")
        evaluator = replace_once(evaluator, "func evaluateAllocation(allocation *allocation, context map[string]any, currentTime time.Time) (*split, bool, error) {", "func evaluateAllocation(allocation *allocation, context map[string]any, currentTime time.Time) (*split, bool, error) {\n\td017Trace.excluded[len(d017Trace.excluded)-1] = false")
        overlay_evaluator = output / f"{name}_evaluator.go"
        overlay_evaluator.write_text(evaluator)
        overlay = output / f"{name}_overlay.json"
        overlay.write_text(json.dumps({"Replace": {
            str(evaluator_file): str(overlay_evaluator),
            str(provider_file): str(helper_overlay),
            str(repo / "openfeature/lean_d017_operational_test.go"): str(adapter),
        }}, indent=2) + "\n")
        command = ["go", "test", "-overlay", str(overlay), "-count=1", "-json", "./openfeature", "-run", "^TestLeanD017OperationalConformance$"]
        env = dict(os.environ, LEAN_D017_CASES=str(corpus))
        result = subprocess.run(command, cwd=repo, env=env, capture_output=True, text=True)
        log = output / f"{name}.jsonl"
        log.write_text(result.stdout)
        (output / f"{name}.stderr.txt").write_text(result.stderr)
        events = [json.loads(line) for line in result.stdout.splitlines() if line.startswith("{")]
        cases = [e for e in events if e.get("Action") in ["pass", "fail"] and e.get("Test", "").startswith("TestLeanD017OperationalConformance/")]
        summary = {"command": command, "cwd": str(repo), "env": {"LEAN_D017_CASES": str(corpus)}, "exit_code": result.returncode,
            "cases_executed": len(cases), "passed": sum(e["Action"] == "pass" for e in cases), "failed": sum(e["Action"] == "fail" for e in cases),
            "failed_case_ids": [e["Test"].removeprefix("TestLeanD017OperationalConformance/") for e in cases if e["Action"] == "fail"], "log_sha256": digest(log.read_bytes())}
        receipt["runs"][name] = summary
        print(name, json.dumps({k: summary[k] for k in ["exit_code", "cases_executed", "passed", "failed"]}), flush=True)
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    candidate, baseline = receipt["runs"]["candidate"], receipt["runs"]["baseline"]
    if candidate["exit_code"] != 0 or candidate["passed"] != 36 or baseline["exit_code"] == 0 or baseline["cases_executed"] != 36 or baseline["failed"] != 15:
        raise SystemExit("unexpected native conformance outcome")

if __name__ == "__main__":
    main()
