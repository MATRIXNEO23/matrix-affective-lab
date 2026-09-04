from src.affective_engine import AffectiveEngine,EmotionalImpulse


def test_unknown_emotion_is_bounded_and_does_not_corrupt_pad():
    e=AffectiveEngine();e.apply_impulse(EmotionalImpulse("custom",.8,"x"));assert 0<=e.state.emotions["custom"]<=1;assert e.state.valence==e.state.arousal==e.state.dominance==0
