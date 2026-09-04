from src.affective_engine import AffectiveEngine,EmotionalImpulse


def test_hope_and_fear_do_not_directly_push_mood():
    h=AffectiveEngine();f=AffectiveEngine();h.apply_impulse(EmotionalImpulse("hope",.8,"h"));f.apply_impulse(EmotionalImpulse("fear",.8,"f"));assert h.state.mood_valence==0;assert f.state.mood_valence==0
