from src.affective_engine import AffectiveEngine,EmotionalImpulse


def test_affection_and_aversion_can_coexist():
    e=AffectiveEngine();e.apply_impulse(EmotionalImpulse("love",.8,"past","u","attitude"));e.apply_impulse(EmotionalImpulse("hate",.6,"present","u","attitude"));a=e.persistent_affect["u"];assert a.affection>0 and a.aversion>0
