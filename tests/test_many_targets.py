from src.affective_engine import AffectiveEngine,EmotionalImpulse


def test_many_targets_remain_separate():
    e=AffectiveEngine()
    for n in range(500):e.apply_impulse(EmotionalImpulse("gratitude",.5,f"e{n}",f"p{n}","compound"))
    assert len(e.persistent_affect)==500;assert all(a.affection>0 for a in e.persistent_affect.values())
