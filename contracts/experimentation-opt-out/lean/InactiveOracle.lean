import Lean
import InactivePath

open Lean PR423

namespace InactiveOracle

def dispatch (input : Json) : Except String Json := do
  let id ← input.getObjVal? "id"
  let args ← input.getObjVal? "args"
  let mode ← match ← args.getObjValAs? String "mode" with
    | "disabled" => pure Mode.disabled
    | "immediate" => pure Mode.immediate
    | "future_experiments_only" => pure Mode.future
    | other => throw s!"Unknown mode: {other}"
  let attr ← match ← args.getObjValAs? String "attribute" with
    | "absent" => pure Attribute.absent
    | "valid" => pure Attribute.valid
    | "invalid" => pure Attribute.invalid
    | other => throw s!"Unknown attribute: {other}"
  let checks ← args.getObjValAs? (List Bool) "checkResults"
  let result := InactivePath.evaluate mode attr checks
  let error := match result.error with
    | .none => "NONE"
    | .invalidContext => "INVALID_CONTEXT"
    | .parseError => "PARSE_ERROR"
    | .providerNotReady => "PROVIDER_NOT_READY"
  return Json.mkObj [("id", id), ("observed", Json.mkObj [
    ("error", toJson error), ("excluded", toJson result.trace.excluded),
    ("exclusionChecks", toJson result.trace.checkCalls)])]

end InactiveOracle

def main : IO Unit := do
  let stdin ← IO.getStdin
  let stdout ← IO.getStdout
  repeat
    let line ← stdin.getLine
    if line.isEmpty then break
    let input ← match Json.parse line with
      | .ok input => pure input
      | .error message => throw (IO.userError message)
    let output ← match InactiveOracle.dispatch input with
      | .ok output => pure output
      | .error message => throw (IO.userError message)
    stdout.putStrLn output.compress
