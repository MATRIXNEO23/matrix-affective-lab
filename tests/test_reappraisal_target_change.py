from src.affective_engine import AffectiveEngine,EmotionalImpulse


def test_same_cause_retargeted_is_new_causal_slot():
    e=AffectiveEngine();e.apply_impulse(EmotionalImpulse("reproach",.8,"x","alice","standard"));e.apply_impulse(EmotionalImpulse("reproach",.8,"x","bob","standard"));assert e.contribution_for("x","standard","alice") and e.contribution_for("x","standard","bob")
