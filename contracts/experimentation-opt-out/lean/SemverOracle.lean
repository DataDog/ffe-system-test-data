import Lean
import SemverDelivery

open Lean SemverDelivery

def dispatch (input : Json) : Except String Json := do
  let id ← input.getObjVal? "id"
  let args ← input.getObjVal? "args"
  let first ← match ← args.getObjValAs? String "firstAllocation" with
    | "ordinary" => pure FirstAllocation.ordinary
    | "completed" => pure FirstAllocation.completed
    | "active" => pure FirstAllocation.active
    | other => throw s!"Unknown first allocation: {other}"
  let authored ← args.getObjValAs? Bool "authoredSemver"
  let override ← args.getObjValAs? Bool "override"
  let rollout ← args.getObjValAs? Bool "rolloutEnabled"
  return Json.mkObj [("id", id), ("observed", Json.mkObj [
    ("primaryContains", toJson (primaryContains authored override rollout)),
    ("compatibilityContains", toJson (compatibilityContains authored override rollout)),
    ("semverRetained", toJson (semverRetained first authored override rollout))])]

def main : IO Unit := do
  let stdin ← IO.getStdin
  let stdout ← IO.getStdout
  repeat
    let line ← stdin.getLine
    if line.isEmpty then break
    let input ← match Json.parse line with
      | .ok input => pure input
      | .error message => throw (IO.userError message)
    let output ← match dispatch input with
      | .ok output => pure output
      | .error message => throw (IO.userError message)
    stdout.putStrLn output.compress
