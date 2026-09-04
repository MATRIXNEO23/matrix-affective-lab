from src.affective_engine import AffectiveEngine,EmotionalImpulse


def test_reappraising_one_cause_does_not_replace_another_same_emotion_cause():
    e=AffectiveEngine();e.apply_impulse(EmotionalImpulse("anger",.8,"a","u","standard"));e.apply_impulse(EmotionalImpulse("anger",.8,"b","u","standard"));e.apply_impulse(EmotionalImpulse("admiration",.8,"a","u","standard"));assert e.contribution_for("b","standard","u")[0]=="anger"
