from src.affective_engine import AffectiveEngine,EmotionalImpulse


def test_over_one_intensity_is_clamped():
    e=AffectiveEngine();e.apply_impulse(EmotionalImpulse("joy",99,"x"));assert 0<=e.state.emotions["joy"]<=1
