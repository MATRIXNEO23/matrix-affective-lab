from src.affective_engine import AffectiveEngine,EmotionalImpulse


def test_repeated_reinforcement_stays_bounded():
    e=AffectiveEngine();e.apply_impulse(EmotionalImpulse("anger",.3,"x","u","standard"))
    for _ in range(100):e.reinforce("x","standard","u",1)
    assert 0<=e.state.emotions["anger"]<=1;assert 0<=e.persistent_affect["u"].resentment<=1
