from src.affective_engine import AffectiveEngine,EmotionalImpulse


def test_positive_and_negative_emotions_push_mood_opposite_directions():
    p=AffectiveEngine();n=AffectiveEngine();p.apply_impulse(EmotionalImpulse("joy",.8,"p"));n.apply_impulse(EmotionalImpulse("anger",.8,"n"));assert p.state.mood_valence>0>n.state.mood_valence
