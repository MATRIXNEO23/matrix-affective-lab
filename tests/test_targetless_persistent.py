from src.affective_engine import AffectiveEngine, EmotionalImpulse


def test_targetless_emotion_never_creates_persistent_person():
    e=AffectiveEngine();e.apply_impulse(EmotionalImpulse("joy",.9,"world",None,"goal"));assert e.persistent_affect=={}
