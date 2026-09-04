from src.affective_engine import AffectiveEngine,EmotionalImpulse


def test_identical_replay_after_decay_is_idempotent_for_source_evidence():
    e=AffectiveEngine();i=EmotionalImpulse("anger",.8,"x","u","standard");e.apply_impulse(i);a=e.snapshot()["persistent_affect"]["u"].copy();e.decay(5);assert e.apply_impulse(i) is False;assert e.snapshot()["persistent_affect"]["u"]==a
