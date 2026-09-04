from src.affective_engine import AffectiveEngine,EmotionalImpulse


def test_single_emotion_decay_is_monotonic():
    e=AffectiveEngine();e.apply_impulse(EmotionalImpulse("anger",.9,"x"));vals=[]
    for _ in range(30):vals.append(e.state.emotions.get("anger",0));e.decay(1)
    assert all(a>=b for a,b in zip(vals,vals[1:]))
