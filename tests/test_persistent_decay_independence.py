from src.affective_engine import AffectiveEngine,EmotionalImpulse


def test_decay_alone_never_changes_persistent_affect():
    e=AffectiveEngine();e.apply_impulse(EmotionalImpulse("gratitude",.8,"x","u","compound"));a=e.snapshot()["persistent_affect"]["u"].copy();e.decay(100);assert e.snapshot()["persistent_affect"]["u"]==a
