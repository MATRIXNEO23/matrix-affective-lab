from src.affective_engine import AffectiveEngine, EmotionalImpulse


def test_correcting_one_person_never_changes_another_person():
    e=AffectiveEngine();e.apply_impulse(EmotionalImpulse("anger",.8,"a","alice","standard"));e.apply_impulse(EmotionalImpulse("anger",.8,"b","bob","standard"));bob=e.snapshot()["persistent_affect"]["bob"].copy();e.apply_impulse(EmotionalImpulse("anger",0,"a","alice","standard"));assert e.snapshot()["persistent_affect"]["bob"]==bob
