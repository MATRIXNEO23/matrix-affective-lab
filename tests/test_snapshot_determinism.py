from src.affective_engine import AffectiveEngine, EmotionalImpulse


def run():
    e=AffectiveEngine()
    for n in range(100):e.apply_impulse(EmotionalImpulse("joy" if n%2 else "anger",.6,f"e{n}","user","scenario"))
    e.decay(12.5);return e.snapshot()

def test_same_sequence_is_deterministic():assert run()==run()
