import Contract

namespace InactivePath
open PR423

/-- An explicit operational model of the allocation-loop guard. `check` invokes
    the exclusion helper; `skip` does not. The Bool is the helper's result for an
    already visited allocation, not a model of targeting or traversal order. -/
inductive Operation where
  | skip
  | check (excluded : Bool)
  deriving BEq, DecidableEq, Repr

structure Trace where
  excluded : List Bool
  checkCalls : Nat
  deriving BEq, DecidableEq, Repr

def run : List Operation → Trace
  | [] => ⟨[], 0⟩
  | .skip :: rest =>
      let tail := run rest
      ⟨false :: tail.excluded, tail.checkCalls⟩
  | .check excluded :: rest =>
      let tail := run rest
      ⟨excluded :: tail.excluded, tail.checkCalls + 1⟩

def guarded (active : Bool) (checks : List Bool) : List Operation :=
  checks.map fun excluded => if active then .check excluded else .skip

/-- The previous shape calls a helper that returns false internally when inactive. -/
def unconditional (active : Bool) (checks : List Bool) : List Operation :=
  checks.map fun excluded => .check (active && excluded)

theorem guarded_values (active : Bool) (checks : List Bool) :
    (run (guarded active checks)).excluded = checks.map (active && ·) := by
  induction checks with
  | nil => rfl
  | cons head tail ih => cases active <;> simp_all [guarded, run]

theorem unconditional_values (active : Bool) (checks : List Bool) :
    (run (unconditional active checks)).excluded = checks.map (active && ·) := by
  induction checks with
  | nil => rfl
  | cons head tail ih => simp_all [unconditional, run]

theorem guard_preserves_results (active : Bool) (checks : List Bool) :
    (run (guarded active checks)).excluded =
      (run (unconditional active checks)).excluded := by
  rw [guarded_values, unconditional_values]

theorem inactive_skips_every_check (checks : List Bool) :
    (run (guarded false checks)).checkCalls = 0 := by
  induction checks with
  | nil => rfl
  | cons head tail ih => simpa [guarded, run] using ih

theorem active_checks_each_visited_allocation (checks : List Bool) :
    (run (guarded true checks)).checkCalls = checks.length := by
  induction checks with
  | nil => rfl
  | cons head tail ih => simpa [guarded, run] using ih

theorem unconditional_calls_even_when_inactive (active : Bool) (checks : List Bool) :
    (run (unconditional active checks)).checkCalls = checks.length := by
  induction checks with
  | nil => rfl
  | cons head tail ih => simpa [unconditional, run] using ih

/-- Context validation precedes allocation traversal. Invalid enabled input is
    an error, never silently converted to an inactive policy. -/
def resolve (mode : Mode) (attr : Attribute) : Except PR423.Error Bool :=
  match mode, attr with
  | .disabled, _ => .ok false
  | _, .absent => .ok false
  | _, .invalid => .error .invalidContext
  | _, .valid => .ok true

structure Result where
  error : PR423.Error
  trace : Trace
  deriving BEq, DecidableEq, Repr

def evaluate (mode : Mode) (attr : Attribute) (checks : List Bool) : Result :=
  match resolve mode attr with
  | .error error => ⟨error, ⟨[], 0⟩⟩
  | .ok active => ⟨.none, run (guarded active checks)⟩

theorem disabled_has_zero_checks (attr : Attribute) (checks : List Bool) :
    (evaluate .disabled attr checks).trace.checkCalls = 0 := by
  cases attr <;> simp [evaluate, resolve, inactive_skips_every_check]

theorem absent_has_zero_checks (mode : Mode) (checks : List Bool) :
    (evaluate mode .absent checks).trace.checkCalls = 0 := by
  cases mode <;> simp [evaluate, resolve, inactive_skips_every_check]

theorem invalid_enabled_input_remains_error (mode : Mode) (checks : List Bool)
    (enabled : mode ≠ .disabled) :
    evaluate mode .invalid checks = ⟨.invalidContext, ⟨[], 0⟩⟩ := by
  cases mode
  case disabled => exact (enabled rfl).elim
  case immediate => rfl
  case future => rfl

/-- A return-value-only oracle accepts both versions; the operation trace rejects
    the unconditional call. These counts are model events, not CPU instructions. -/
theorem value_only_oracle_misses_regression :
    (run (guarded false [true, false])).excluded =
      (run (unconditional false [true, false])).excluded ∧
    (run (guarded false [true, false])).checkCalls = 0 ∧
    (run (unconditional false [true, false])).checkCalls = 2 := by decide

end InactivePath
