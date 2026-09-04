from src.affective_engine import AffectiveEngine,EmotionalImpulse


def test_snapshot_mutation_does_not_mutate_engine():
    e=AffectiveEngine();e.apply_impulse(EmotionalImpulse("joy",.8,"x","u"));s=e.snapshot();s["emotions"]["joy"]=0;s["persistent_affect"]["u"]["affection"]=0;assert e.state.emotions["joy"]>0;assert e.persistent_affect["u"].affection>0
