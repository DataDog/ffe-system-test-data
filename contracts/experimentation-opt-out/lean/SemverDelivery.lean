namespace SemverDelivery

/-- A bounded compiler-input profile: two ordered allocations, the first covering
    the full population, and an optional SemVer condition in the second. -/
inductive FirstAllocation where
  | ordinary | completed | active
  deriving DecidableEq

/-- Overrides replace the authored waterfall. Otherwise its SemVer requirement
    survives optimization, even when no SemVer condition survives on the wire. -/
def requiresSemver (authored override : Bool) : Bool := authored && !override

def primaryContains (authored override rollout : Bool) : Bool :=
  rollout || !(requiresSemver authored override)

def compatibilityContains (authored override rollout : Bool) : Bool :=
  primaryContains authored override rollout && !(requiresSemver authored override)

def semverRetained (first : FirstAllocation) (authored override rollout : Bool) : Bool :=
  primaryContains authored override rollout && requiresSemver authored override &&
    (first == .active)

theorem authored_semver_is_not_compatible (rollout : Bool) :
    compatibilityContains true false rollout = false := by
  cases rollout <;> rfl

theorem override_preserves_delivery (authored rollout : Bool) :
    primaryContains authored true rollout = true ∧
    compatibilityContains authored true rollout = true := by
  cases authored <;> cases rollout <;> decide

theorem ordinary_flags_preserve_delivery (override rollout : Bool) :
    compatibilityContains false override rollout = true := by
  cases override <;> cases rollout <;> rfl

theorem rollout_off_omits_authored_semver :
    primaryContains true false false = false := by rfl

theorem pruned_semver_still_requires_capable_delivery :
    semverRetained .completed true false true = false ∧
    primaryContains true false true = true ∧
    compatibilityContains true false true = false := by decide

theorem active_experiment_retains_semver_fallback :
    semverRetained .active true false true = true ∧
    compatibilityContains true false true = false := by decide

end SemverDelivery
