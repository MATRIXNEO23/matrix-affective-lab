from src.affective_engine import AffectiveEngine, EmotionalImpulse


def test_many_same_emotion_causes_saturate_without_exceeding_one():
    e=AffectiveEngine()
    values=[]
    for n in range(100):
        e.apply_impulse(EmotionalImpulse("joy",.4,f"good-{n}",None,"goal"));values.append(e.state.emotions["joy"])
    assert all(a<=b for a,b in zip(values,values[1:]));assert values[-1]<=1;assert values[-1]>.99
