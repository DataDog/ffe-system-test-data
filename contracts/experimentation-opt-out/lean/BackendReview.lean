import Contract

namespace BackendReview
open PR423

/-- D018: the backend carries randomization eligibility through the existing
    doLog field, preserving existing experiment/holdout logging requirements.
    Native partition classification is an obligation, not proved by this model. -/
def compiledDoLog (existingExposure randomized : Bool) : Bool :=
  existingExposure || randomized

def compiledPolicy (mode : Mode) (attr : Attribute) (activation : Activation)
    (existingExposure randomized : Bool) : PolicyResult :=
  policy mode attr activation (compiledDoLog existingExposure randomized)

theorem randomized_allocations_set_doLog (existingExposure : Bool) :
    compiledDoLog existingExposure true = true := by
  cases existingExposure <;> rfl

theorem existing_exposure_requirements_are_preserved (randomized : Bool) :
    compiledDoLog true randomized = true := by rfl

theorem deterministic_ordinary_winner_does_not_log :
    compiledDoLog false false = false := by rfl

theorem immediate_excludes_randomized_allocations (existingExposure : Bool) :
    (compiledPolicy .immediate .valid .missing existingExposure true).exclude = true := by
  cases existingExposure <;> rfl

theorem future_excludes_unknown_randomized_allocations (existingExposure : Bool) :
    (compiledPolicy .future .valid .missing existingExposure true).exclude = true := by
  cases existingExposure <;> rfl

theorem future_preserves_earlier_randomized_allocations (existingExposure : Bool) :
    (compiledPolicy .future .valid .before existingExposure true).exclude = false := by
  cases existingExposure <;> rfl

theorem old_nonlogging_split_distinguishes_compiler_contracts :
    (policy .immediate .valid .missing false).exclude = false ∧
    (compiledPolicy .immediate .valid .missing false true).exclude = true := by
  decide

end BackendReview
