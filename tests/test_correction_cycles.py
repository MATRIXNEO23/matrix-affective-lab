from src.affective_engine import AffectiveEngine, EmotionalImpulse


def test_repeated_negative_positive_corrections_do_not_drift():
    e=AffectiveEngine()
    for _ in range(100):
        e.apply_impulse(EmotionalImpulse("reproach",.8,"claim","user","standard"));e.apply_impulse(EmotionalImpulse("admiration",.8,"claim","user","standard"));e.apply_impulse(EmotionalImpulse("admiration",0,"claim","user","standard"))
    a=e.persistent_affect["user"];assert abs(a.resentment)<1e-10;assert abs(a.trust-.5)<1e-10;assert abs(a.admiration)<1e-10;assert abs(a.respect-.5)<1e-10
