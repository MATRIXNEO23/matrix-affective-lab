import random

from src.affective_engine import AffectiveEngine, EmotionalImpulse
from src.prototype import AffectiveStimulus, MatrixAffectivePrototype


def test_randomized_state_never_leaves_bounds():
    rng = random.Random(23)
    e = AffectiveEngine()
    emotions = ["joy", "fear", "anger", "reproach", "admiration", "liking", "disliking"]
    targets = ["user", "alice", "bob", None]

    for i in range(5000):
        e.apply_impulse(EmotionalImpulse(
            rng.choice(emotions),
            rng.uniform(-0.5, 1.5),
            f"cause-{rng.randrange(250)}",
            rng.choice(targets),
        ))
        if i % 11 == 0:
            e.decay(rng.random() * 2.0)

    snap = e.snapshot()
    assert all(0.0 <= value <= 1.0 for value in snap["emotions"].values())
    assert -1.0 <= snap["mood_valence"] <= 1.0
    assert 0.0 <= snap["mood_arousal"] <= 1.0
    for affect in snap["persistent_affect"].values():
        assert all(0.0 <= value <= 1.0 for value in affect.values())


def test_same_event_reprocessed_is_idempotent_for_state():
    p = MatrixAffectivePrototype()
    stimulus = AffectiveStimulus(
        id="stable-event",
        category="action",
        actor_id="user",
        goal_relevance=0.9,
        goal_congruence=-0.7,
        standard_compliance=-0.8,
        attitude_valence=-0.4,
        attitude_intensity=0.6,
    )
    first = p.process(stimulus).after
    second = p.process(stimulus).after
    assert second == first


def test_extreme_appraisal_inputs_are_clamped():
    p = MatrixAffectivePrototype()
    trace = p.process(AffectiveStimulus(
        id="extreme",
        category="action",
        actor_id="user",
        goal_relevance=99.0,
        goal_congruence=-99.0,
        standard_compliance=99.0,
        attitude_valence=-99.0,
        attitude_intensity=99.0,
        novelty=99.0,
    ))
    assert trace.appraisal.relevance == 1.0
    assert trace.appraisal.congruence == -1.0
    assert trace.appraisal.novelty == 1.0
    assert all(0.0 <= impulse.intensity <= 1.0 for impulse in trace.appraisal.impulses)


def test_reappraisal_to_zero_restores_persistent_delta_from_same_cause():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("anger", 0.8, "event", "user"))
    assert e.persistent_affect["user"].resentment > 0.0
    e.apply_impulse(EmotionalImpulse("anger", 0.0, "event", "user"))
    assert abs(e.persistent_affect["user"].resentment) < 1e-12
    assert abs(e.persistent_affect["user"].trust - 0.5) < 1e-12
    assert "anger" not in e.state.emotions
