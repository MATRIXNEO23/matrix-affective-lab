from src.affective_engine import AffectiveEngine,EmotionalImpulse


def test_transient_contribution_is_garbage_collected_after_long_decay():
    e=AffectiveEngine();e.apply_impulse(EmotionalImpulse("joy",.8,"x",None,"goal"));e.decay(10000);assert e.contribution_for("x","goal",None) is None;assert "joy" not in e.state.emotions
