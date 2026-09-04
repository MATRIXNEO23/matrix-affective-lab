from src.affective_engine import AffectiveEngine,EmotionalImpulse


def test_extreme_decay_time_is_safe():
    e=AffectiveEngine();e.apply_impulse(EmotionalImpulse("anger",1,"x"));e.decay(1e12);assert e.state.emotions=={};assert e.state.mood_valence==0
