from src.affective_engine import AffectiveEngine, EmotionalImpulse


def test_nonpositive_decay_is_noop():
    e=AffectiveEngine();e.apply_impulse(EmotionalImpulse("joy",.8,"x"));s=e.snapshot();e.decay(0);e.decay(-100);assert e.snapshot()==s
