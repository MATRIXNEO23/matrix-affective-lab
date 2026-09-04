from src.affective_engine import AffectiveEngine, EmotionalImpulse


def test_general_positive_affect_does_not_invent_attraction():
    e=AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("love", .9, "care", "user", "attitude"))
    assert e.persistent_affect["user"].affection > 0
    assert e.persistent_affect["user"].attraction == 0
