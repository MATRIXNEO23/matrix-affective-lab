from src.affective_engine import AffectiveEngine,EmotionalImpulse


def test_same_slot_reappraisal_does_not_push_mood_twice():
    e=AffectiveEngine();e.apply_impulse(EmotionalImpulse("joy",.6,"x",None,"goal"));m=e.state.mood_valence;e.apply_impulse(EmotionalImpulse("joy",.8,"x",None,"goal"));assert e.state.mood_valence==m
