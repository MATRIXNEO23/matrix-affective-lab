from src.affective_engine import AffectiveEngine, EmotionalImpulse


def test_mood_recovers_toward_neutral_over_long_time():
    e=AffectiveEngine();e.apply_impulse(EmotionalImpulse("joy",.9,"good",None,"goal"));before=e.state.mood_valence
    assert before>0
    e.decay(600)
    assert abs(e.state.mood_valence) < abs(before)
