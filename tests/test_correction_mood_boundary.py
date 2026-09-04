from src.affective_engine import AffectiveEngine,EmotionalImpulse


def test_correction_does_not_retroactively_erase_mood_history():
    e=AffectiveEngine();e.apply_impulse(EmotionalImpulse("anger",.8,"x","u","standard"));m=e.state.mood_valence;assert m<0;e.apply_impulse(EmotionalImpulse("anger",0,"x","u","standard"));assert e.state.mood_valence==m
