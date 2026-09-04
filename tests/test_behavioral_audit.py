from src.affective_engine import AffectiveEngine, EmotionalImpulse
from src.prototype import AffectiveStimulus, MatrixAffectivePrototype


def test_late_semantic_correction_fully_reverses_persistent_affect():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("anger", 0.8, "claim-1", "user", "standard"))
    assert e.persistent_affect["user"].resentment > 0.0
    e.decay(30.0)
    e.apply_impulse(EmotionalImpulse("anger", 0.0, "claim-1", "user", "standard"))
    affect = e.persistent_affect["user"]
    assert abs(affect.resentment) < 1e-12
    assert abs(affect.trust - 0.5) < 1e-12


def test_late_reappraisal_negative_to_positive_has_no_negative_residue():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("reproach", 0.9, "claim-2", "user", "standard"))
    e.decay(30.0)
    e.apply_impulse(EmotionalImpulse("admiration", 0.8, "claim-2", "user", "standard"))
    affect = e.persistent_affect["user"]
    assert abs(affect.resentment) < 1e-12
    assert abs(affect.trust - 0.5) < 1e-12
    assert affect.admiration > 0.0
    assert affect.respect > 0.5


def test_reinforcement_updates_persistent_affect_by_delta_only():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("reproach", 0.4, "claim-3", "user", "standard"))
    before = e.persistent_affect["user"].resentment
    assert e.reinforce("claim-3", "standard", "user", 0.8) is True
    after = e.persistent_affect["user"].resentment
    assert after > before


def test_replaying_same_event_remains_persistent_idempotent():
    e = AffectiveEngine()
    impulse = EmotionalImpulse("gratitude", 0.8, "event-4", "user", "compound")
    e.apply_impulse(impulse)
    first = e.snapshot()["persistent_affect"]["user"].copy()
    assert e.apply_impulse(impulse) is False
    second = e.snapshot()["persistent_affect"]["user"].copy()
    assert second == first


def test_duplicate_delivery_does_not_consume_future_habituation():
    p = MatrixAffectivePrototype()
    first = AffectiveStimulus(
        id="compliment-1", category="event", actor_id="user",
        goal_relevance=1.0, goal_congruence=0.8,
        habituation_key="compliment",
    )
    p.process(first)
    p.process(first)  # duplicate bus delivery: must not count as new exposure
    second = p.process(AffectiveStimulus(
        id="compliment-2", category="event", actor_id="user",
        goal_relevance=1.0, goal_congruence=0.8,
        habituation_key="compliment",
    ))
    expected = max(0.2, __import__("math").exp(-0.35))
    assert abs(second.appraisal.habituation_factor - expected) < 1e-12


def test_habituation_still_counts_distinct_evidence():
    p = MatrixAffectivePrototype()
    factors = []
    for i in range(3):
        trace = p.process(AffectiveStimulus(
            id=f"event-{i}", category="event", actor_id="user",
            goal_relevance=1.0, goal_congruence=0.7,
            habituation_key="same-pattern",
        ))
        factors.append(trace.appraisal.habituation_factor)
    assert factors[0] > factors[1] > factors[2]
