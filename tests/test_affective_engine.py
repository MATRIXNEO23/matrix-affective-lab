from src.affective_engine import AffectiveEngine, EmotionalImpulse, EmotionDisposition


def test_saturating_repeated_distinct_causes():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("joy", 0.6, "a"))
    e.apply_impulse(EmotionalImpulse("joy", 0.6, "b"))
    assert 0.6 < e.state.emotions["joy"] < 1.0


def test_same_cause_exact_replay_is_matrix_idempotent_adapter():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("anger", 0.7, "event-1", "user"))
    first = e.snapshot()
    changed = e.apply_impulse(EmotionalImpulse("anger", 0.7, "event-1", "user"))
    assert changed is False
    assert e.snapshot() == first


def test_fatima_threshold_is_subtracted_from_potential():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("joy", 1.0, "event"))
    # FAtiMA ActiveEmotion.SetIntensity: intensity = potential - threshold.
    assert abs(e.state.emotions["joy"] - 0.95) < 1e-12


def test_fatima_mood_influences_reappraisal_potential():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("anger", 0.8, "event-1", "user"))
    # Initial active intensity = .8 - .05 = .75; mood = -.75*.3 = -.225.
    assert abs(e.state.emotions["anger"] - 0.75) < 1e-12
    assert abs(e.state.mood_valence + 0.225) < 1e-12

    e.apply_impulse(EmotionalImpulse("anger", 0.3, "event-1", "user"))
    # DeterminePotential = .3 + (-1 * -.225 * .3) = .3675;
    # active intensity = .3675 - .05 = .3175.
    assert abs(e.state.emotions["anger"] - 0.3175) < 1e-12
    assert abs(e.persistent_affect["user"].resentment - 0.015875) < 1e-12


def test_cross_emotion_reappraisal_replaces_old_slot_without_mood_repush():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("reproach", 0.8, "event-1", "user", "standard"))
    assert abs(e.state.mood_valence + 0.225) < 1e-12
    e.apply_impulse(EmotionalImpulse("admiration", 0.7, "event-1", "user", "standard"))
    assert "reproach" not in e.state.emotions
    # Positive reappraisal is damped by existing negative mood: .7-.0675-.05.
    assert abs(e.state.emotions["admiration"] - 0.5825) < 1e-12
    # FAtiMA does not push mood again on reappraisal.
    assert abs(e.state.mood_valence + 0.225) < 1e-12
    assert abs(e.persistent_affect["user"].trust - 0.5) < 1e-12


def test_same_cause_different_appraisal_channels_can_coexist():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("distress", 0.9, "event-1", "user", "goal"))
    e.apply_impulse(EmotionalImpulse("reproach", 0.8, "event-1", "user", "standard"))
    assert abs(e.state.emotions["distress"] - 0.85) < 1e-12
    # Mood from distress (-.255) amplifies subsequent negative potential.
    assert abs(e.state.emotions["reproach"] - 0.8265) < 1e-12


def test_reappraisal_below_threshold_extinguishes_prior_cause():
    e = AffectiveEngine({"fear": EmotionDisposition(threshold=0.3, half_life=10.0)})
    e.apply_impulse(EmotionalImpulse("fear", 0.8, "event", "user"))
    changed = e.apply_impulse(EmotionalImpulse("fear", 0.2, "event", "user"))
    assert changed is True
    assert "fear" not in e.state.emotions


def test_fatima_half_life_decay_mapping():
    e = AffectiveEngine({"fear": EmotionDisposition(threshold=0.0, half_life=10.0)})
    e.apply_impulse(EmotionalImpulse("fear", 0.8, "event"))
    e.decay(10.0)
    assert abs(e.state.emotions["fear"] - 0.4) < 1e-6


def test_fatima_hope_and_fear_do_not_influence_mood():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("hope", 0.8, "hope-event"))
    e.apply_impulse(EmotionalImpulse("fear", 0.8, "fear-event"))
    assert e.state.mood_valence == 0.0


def test_fatima_mood_update_factor_is_point_three():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("joy", 1.0, "event"))
    assert abs(e.state.emotions["joy"] - 0.95) < 1e-12
    assert abs(e.state.mood_valence - 0.285) < 1e-12


def test_persistent_affect_is_entity_scoped():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("anger", 0.8, "event", "alice"))
    assert e.persistent_affect["alice"].resentment > 0
    assert "bob" not in e.persistent_affect


def test_explicit_zero_cancels_old_semantic_contribution():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("anger", 0.8, "event", "user"))
    e.apply_impulse(EmotionalImpulse("anger", 0.0, "event", "user"))
    assert "anger" not in e.state.emotions
    assert abs(e.persistent_affect["user"].resentment) < 1e-12
    assert abs(e.persistent_affect["user"].trust - 0.5) < 1e-12


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
