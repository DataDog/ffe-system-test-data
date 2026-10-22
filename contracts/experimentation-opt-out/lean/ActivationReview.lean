import Contract

namespace ActivationReview
open PR423

/-- Stable first activation for a standard experiment's allocation-sync start.
    The native transaction and classification are separate proof obligations. -/
def syncActivation (known start : Option Nat) (standard published replicated previouslyStarted : Bool) : Option Nat :=
  if replicated || !standard || !published || previouslyStarted then known
  else known.or start

theorem first_start_records_activation (t : Nat) :
    syncActivation none (some t) true true false false = some t := by rfl

theorem known_activation_is_preserved (t : Nat) (start : Option Nat)
    (standard published replicated previouslyStarted : Bool) :
    syncActivation (some t) start standard published replicated previouslyStarted = some t := by
  simp [syncActivation]

theorem replication_does_not_invent_activation (known start : Option Nat)
    (standard published previouslyStarted : Bool) :
    syncActivation known start standard published true previouslyStarted = known := by
  simp [syncActivation]

theorem draft_does_not_activate (known start : Option Nat)
    (standard replicated previouslyStarted : Bool) :
    syncActivation known start standard false replicated previouslyStarted = known := by
  simp [syncActivation, Bool.or_assoc]

theorem ordinary_rollout_does_not_activate (known start : Option Nat)
    (published replicated previouslyStarted : Bool) :
    syncActivation known start false published replicated previouslyStarted = known := by
  simp [syncActivation]

theorem running_legacy_allocation_stays_unknown (start : Option Nat)
    (standard published replicated : Bool) :
    syncActivation none start standard published replicated true = none := by
  simp [syncActivation]

theorem no_start_does_not_activate (standard published replicated previouslyStarted : Bool) :
    syncActivation none none standard published replicated previouslyStarted = none := by
  simp [syncActivation]

/-- Generated holdouts preserve their run's activation state and doLog=true.
    No theorem here proves how the producer derives the run timestamp. -/
def holdoutPolicy (mode : Mode) (attr : Attribute) (run : Activation) : PolicyResult :=
  policy mode attr run true

theorem future_retains_existing_holdout :
    (holdoutPolicy .future .valid .before).exclude = false := by rfl

theorem immediate_excludes_existing_holdout :
    (holdoutPolicy .immediate .valid .before).exclude = true := by rfl

theorem future_excludes_equal_holdout :
    (holdoutPolicy .future .valid .equal).exclude = true := by rfl

theorem future_excludes_unknown_holdout :
    (holdoutPolicy .future .valid .missing).exclude = true := by rfl

theorem dropping_holdout_activation_changes_future_policy :
    holdoutPolicy .future .valid .before ≠ holdoutPolicy .future .valid .missing := by decide

end ActivationReview
