from src.affective_engine import AffectiveEngine,EmotionalImpulse


def test_reproach_changes_trust_not_respect_in_matrix_extension():
    e=AffectiveEngine();e.apply_impulse(EmotionalImpulse("reproach",.8,"x","u","standard"));a=e.persistent_affect["u"];assert a.trust<.5 and a.respect==.5
