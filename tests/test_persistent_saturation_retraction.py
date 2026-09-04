from src.affective_engine import AffectiveEngine,EmotionalImpulse


def test_saturated_many_cause_retraction_remains_bounded():
    e=AffectiveEngine()
    for n in range(100):e.apply_impulse(EmotionalImpulse("anger",1,f"x{n}","u","standard"))
    for n in range(100):e.apply_impulse(EmotionalImpulse("anger",0,f"x{n}","u","standard"))
    a=e.persistent_affect["u"]
    assert 0<=a.resentment<=1 and 0<=a.trust<=1
