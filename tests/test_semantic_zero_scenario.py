from src.affective_engine import AffectiveEngine, EmotionalImpulse


def test_strong_mood_cannot_create_emotion_from_zero_semantic_evidence():
    e=AffectiveEngine();e.apply_impulse(EmotionalImpulse("joy",1,"seed",None,"seed"));assert e.state.mood_valence>0;e.apply_impulse(EmotionalImpulse("joy",0,"zero","user","goal"));assert e.contribution_for("zero","goal","user") is None
