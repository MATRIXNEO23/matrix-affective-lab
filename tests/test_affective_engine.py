from src.affective_engine import AffectiveEngine, EmotionalImpulse, EmotionDisposition


def test_saturating_repeated_distinct_causes():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("joy", 0.6, "a"))
    e.apply_impulse(EmotionalImpulse("joy", 0.6, "b"))
    assert 0.6 < e.state.emotions["joy"] < 1.0


def test_same_cause_reappraisal_does_not_blindly_stack():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("anger", 0.7, "event-1", "user"))
    first = e.state.emotions["anger"]
    e.apply_impulse(EmotionalImpulse("anger", 0.7, "event-1", "user"))
    assert e.state.emotions["anger"] == first


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


def test_below_threshold_is_ignored():
    e = AffectiveEngine({"fear": EmotionDisposition(threshold=0.3, half_life=10.0)})
    accepted = e.apply_impulse(EmotionalImpulse("fear", 0.2, "event"))
    assert accepted is False
    assert "fear" not in e.state.emotions
