from src.affective_engine import AffectiveEngine,EmotionalImpulse


def test_positive_affection_event_does_not_invent_trust_change():
    e=AffectiveEngine();e.apply_impulse(EmotionalImpulse("love",.8,"x","u","attitude"));a=e.persistent_affect["u"];assert a.trust==.5 and a.respect==.5
