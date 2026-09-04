from src.affective_engine import AffectiveEngine,EmotionalImpulse


def test_same_cause_channel_different_targets_are_independent():
    e=AffectiveEngine();e.apply_impulse(EmotionalImpulse("reproach",.8,"shared","alice","standard"));e.apply_impulse(EmotionalImpulse("reproach",.8,"shared","bob","standard"));e.apply_impulse(EmotionalImpulse("reproach",0,"shared","alice","standard"));assert e.contribution_for("shared","standard","alice") is None;assert e.contribution_for("shared","standard","bob") is not None
