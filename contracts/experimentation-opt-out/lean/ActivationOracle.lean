import Lean
import ActivationReview

open Lean PR423

namespace ActivationOracle

def dispatch (input : Json) : Except String Json := do
  let id ← input.getObjVal? "id"
  let args ← input.getObjVal? "args"
  let observed ← match ← input.getObjValAs? String "kind" with
    | "sync-activation" => do
      let known ← args.getObjValAs? (Option Nat) "known"
      let start ← args.getObjValAs? (Option Nat) "start"
      let standard ← args.getObjValAs? Bool "standard"
      let published ← args.getObjValAs? Bool "published"
      let replicated ← args.getObjValAs? Bool "replicated"
      let previouslyStarted ← args.getObjValAs? Bool "previouslyStarted"
      pure (toJson (ActivationReview.syncActivation known start standard published replicated previouslyStarted))
    | "holdout-policy" => do
      let mode ← match ← args.getObjValAs? String "mode" with
        | "disabled" => pure Mode.disabled
        | "immediate" => pure Mode.immediate
        | "future" => pure Mode.future
        | other => throw s!"Unknown mode: {other}"
      let activation ← match ← args.getObjValAs? String "activation" with
        | "before" => pure Activation.before
        | "equal" => pure Activation.equal
        | "after" => pure Activation.after
        | "missing" => pure Activation.missing
        | other => throw s!"Unknown activation: {other}"
      pure (toJson (ActivationReview.holdoutPolicy mode .valid activation).exclude)
    | other => throw s!"Unknown kind: {other}"
  return Json.mkObj [("id", id), ("observed", observed)]

end ActivationOracle

def main : IO Unit := do
  let stdin ← IO.getStdin
  let stdout ← IO.getStdout
  repeat
    let line ← stdin.getLine
    if line.isEmpty then break
    let input ← match Json.parse line with
      | .ok input => pure input
      | .error message => throw (IO.userError message)
    let output ← match ActivationOracle.dispatch input with
      | .ok output => pure output
      | .error message => throw (IO.userError message)
    stdout.putStrLn output.compress
