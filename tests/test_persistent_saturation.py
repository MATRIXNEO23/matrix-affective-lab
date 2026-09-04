from src.affective_engine import AffectiveEngine,EmotionalImpulse


def test_persistent_affect_saturates_safely():
    e=AffectiveEngine()
    for n in range(1000):e.apply_impulse(EmotionalImpulse("anger",1,f"x{n}","u","standard"))
    a=e.persistent_affect["u"];assert a.resentment==1;assert a.trust==0
