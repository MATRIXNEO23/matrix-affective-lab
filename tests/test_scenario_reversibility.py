import random

from src.affective_engine import AffectiveEngine, EmotionalImpulse


def test_many_independent_false_negative_claims_can_be_fully_retracted():
    rng = random.Random(42)
    e = AffectiveEngine()
    for n in range(300):
        e.apply_impulse(EmotionalImpulse("reproach", rng.uniform(.2, 1), f"false-{n}", "user", "standard"))
        if n % 7 == 0:
            e.decay(1)
    assert e.persistent_affect["user"].resentment > 0

    for n in range(300):
        e.apply_impulse(EmotionalImpulse("reproach", 0, f"false-{n}", "user", "standard"))

    a = e.persistent_affect["user"]
    assert abs(a.resentment) < 1e-10
    assert abs(a.trust - .5) < 1e-10
