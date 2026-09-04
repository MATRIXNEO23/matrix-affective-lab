from src.affective_engine import AffectiveEngine, EmotionalImpulse


def test_retraction_after_transient_emotion_extinction_reverses_persistent_history():
    e=AffectiveEngine();e.apply_impulse(EmotionalImpulse("anger",.8,"old","user","standard"));e.decay(10000);assert e.contribution_for("old","standard","user") is None
    e.apply_impulse(EmotionalImpulse("anger",0,"old","user","standard"));a=e.persistent_affect["user"];assert abs(a.resentment)<1e-12;assert abs(a.trust-.5)<1e-12
