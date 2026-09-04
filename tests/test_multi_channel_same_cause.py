from src.affective_engine import AffectiveEngine,EmotionalImpulse


def test_same_cause_different_channels_coexist_and_retract_independently():
    e=AffectiveEngine();e.apply_impulse(EmotionalImpulse("distress",.8,"evt","u","goal"));e.apply_impulse(EmotionalImpulse("reproach",.8,"evt","u","standard"));assert "distress" in e.state.emotions and "reproach" in e.state.emotions;e.apply_impulse(EmotionalImpulse("distress",0,"evt","u","goal"));assert "distress" not in e.state.emotions and "reproach" in e.state.emotions
