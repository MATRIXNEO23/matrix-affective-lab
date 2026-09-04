from src.affective_engine import AffectiveEngine,EmotionalImpulse


def test_slot_identity_is_cause_channel_target_not_emotion_type():
    e=AffectiveEngine();e.apply_impulse(EmotionalImpulse("reproach",.8,"x","u","standard"));e.apply_impulse(EmotionalImpulse("admiration",.8,"x","u","standard"));assert "reproach" not in e.state.emotions;assert "admiration" in e.state.emotions
