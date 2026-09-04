import math, random
from src.affective_engine import AffectiveEngine, EmotionalImpulse


def test_no_nan_or_inf_under_extreme_stress():
    r=random.Random(99);e=AffectiveEngine();types=list(e.POSITIVE|e.NEGATIVE)
    for n in range(5000):
        e.apply_impulse(EmotionalImpulse(r.choice(types),r.uniform(-100,100),f"x{n}",f"p{n%7}","stress"))
        if n%19==0:e.decay(r.uniform(0,100))
    s=e.snapshot();nums=[s["valence"],s["arousal"],s["dominance"],s["mood_valence"]]+list(s["emotions"].values())
    assert all(math.isfinite(x) for x in nums)
