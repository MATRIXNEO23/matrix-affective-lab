from src.affective_engine import AffectiveEngine,EmotionalImpulse


def test_persistent_affect_survives_transient_emotion_decay():
    e=AffectiveEngine();e.apply_impulse(EmotionalImpulse("gratitude",.8,"help","u","compound"));before=e.persistent_affect["u"].affection;e.decay(10000);assert "gratitude" not in e.state.emotions;assert e.persistent_affect["u"].affection==before
