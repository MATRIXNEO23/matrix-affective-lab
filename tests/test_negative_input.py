from src.affective_engine import AffectiveEngine,EmotionalImpulse


def test_negative_intensity_does_not_activate_emotion():
    e=AffectiveEngine();assert e.apply_impulse(EmotionalImpulse("anger",-1,"x")) is False;assert e.state.emotions=={}
