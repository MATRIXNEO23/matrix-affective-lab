from src.affective_engine import AffectiveEngine,EmotionalImpulse


def test_admiration_increases_respect():
    e=AffectiveEngine();e.apply_impulse(EmotionalImpulse("admiration",.8,"x","u","standard"));a=e.persistent_affect["u"];assert a.admiration>0 and a.respect>.5
