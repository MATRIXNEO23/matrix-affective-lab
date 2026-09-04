from src.affective_engine import AffectiveEngine,EmotionalImpulse


def test_tiny_mood_push_below_threshold_is_zeroed():
    e=AffectiveEngine();e.apply_impulse(EmotionalImpulse("joy",.06,"tiny"));assert e.state.mood_valence==0
