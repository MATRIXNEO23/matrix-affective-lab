from src.affective_engine import AffectiveEngine, EmotionalImpulse, EmotionDisposition


def test_saturating_repeated_distinct_causes():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("joy", 0.6, "a"))
    e.apply_impulse(EmotionalImpulse("joy", 0.6, "b"))
    assert 0.6 < e.state.emotions["joy"] < 1.0


def test_same_cause_reappraisal_does_not_blindly_stack():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("anger", 0.7, "event-1", "user"))
    first_emotion = e.state.emotions["anger"]
    first_mood = e.state.mood_valence
    first_affect = e.persistent_affect["user"].resentment
    changed = e.apply_impulse(EmotionalImpulse("anger", 0.7, "event-1", "user"))
    assert changed is False
    assert e.state.emotions["anger"] == first_emotion
    assert e.state.mood_valence == first_mood
    assert e.persistent_affect["user"].resentment == first_affect


def test_reappraisal_replaces_old_intensity():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("anger", 0.8, "event-1", "user"))
    e.apply_impulse(EmotionalImpulse("anger", 0.3, "event-1", "user"))
    assert abs(e.state.emotions["anger"] - 0.3) < 1e-12
    assert abs(e.persistent_affect["user"].resentment - 0.015) < 1e-12


def test_reappraisal_can_replace_negative_emotion_with_positive_emotion():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("reproach", 0.8, "event-1", "user", "standard"))
    assert e.persistent_affect["user"].trust < 0.5
    e.apply_impulse(EmotionalImpulse("admiration", 0.7, "event-1", "user", "standard"))
    assert "reproach" not in e.state.emotions
    assert abs(e.state.emotions["admiration"] - 0.7) < 1e-12
    assert abs(e.persistent_affect["user"].trust - 0.5) < 1e-12
    assert e.persistent_affect["user"].admiration > 0.0


def test_same_cause_different_appraisal_channels_can_coexist():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("distress", 0.9, "event-1", "user", "goal"))
    e.apply_impulse(EmotionalImpulse("reproach", 0.8, "event-1", "user", "standard"))
    assert abs(e.state.emotions["distress"] - 0.9) < 1e-12
    assert abs(e.state.emotions["reproach"] - 0.8) < 1e-12


def test_reappraisal_below_threshold_extinguishes_prior_cause():
    e = AffectiveEngine({"fear": EmotionDisposition(threshold=0.3, half_life=10.0)})
    e.apply_impulse(EmotionalImpulse("fear", 0.8, "event", "user"))
    changed = e.apply_impulse(EmotionalImpulse("fear", 0.2, "event", "user"))
    assert changed is True
    assert "fear" not in e.state.emotions


def test_half_life_decay():
    e = AffectiveEngine({"fear": EmotionDisposition(threshold=0.0, half_life=10.0)})
    e.apply_impulse(EmotionalImpulse("fear", 0.8, "event"))
    e.decay(10.0)
    assert abs(e.state.emotions["fear"] - 0.4) < 1e-6


def test_mood_moves_slower_than_emotion():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("joy", 1.0, "event"))
    assert e.state.emotions["joy"] == 1.0
    assert 0.0 < e.state.mood_valence < 1.0


def test_persistent_affect_is_entity_scoped():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("anger", 0.8, "event", "alice"))
    assert e.persistent_affect["alice"].resentment > 0
    assert "bob" not in e.persistent_affect


def test_persistent_affect_changes_slower_than_emotion():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("affection", 0.8, "event", "user"))
    assert e.persistent_affect["user"].affection < e.state.emotions["affection"]


def test_below_threshold_new_evidence_is_ignored():
    e = AffectiveEngine({"fear": EmotionDisposition(threshold=0.3, half_life=10.0)})
    accepted = e.apply_impulse(EmotionalImpulse("fear", 0.2, "event"))
    assert accepted is False
    assert "fear" not in e.state.emotions


def test_many_distinct_causes_never_exceed_one():
    e = AffectiveEngine()
    for i in range(1000):
        e.apply_impulse(EmotionalImpulse("joy", 0.2, f"event-{i}"))
    assert 0.0 <= e.state.emotions["joy"] <= 1.0
