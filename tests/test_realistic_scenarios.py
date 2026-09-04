from src.affective_engine import AffectiveEngine, EmotionalImpulse
from src.prototype import AffectiveStimulus, MatrixAffectivePrototype


def test_broken_promise_then_correction_clears_false_resentment():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("reproach", .9, "promise", "user", "standard"))
    e.decay(120)
    assert e.persistent_affect["user"].resentment > 0
    e.apply_impulse(EmotionalImpulse("admiration", .8, "promise", "user", "standard"))
    a = e.persistent_affect["user"]
    assert abs(a.resentment) < 1e-12
    assert abs(a.trust - .5) < 1e-12
    assert a.respect > .5


def test_independent_bad_events_accumulate_and_one_correction_only_removes_its_cause():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("reproach", .8, "lie-1", "user", "standard"))
    e.apply_impulse(EmotionalImpulse("reproach", .7, "lie-2", "user", "standard"))
    both = e.persistent_affect["user"].resentment
    e.apply_impulse(EmotionalImpulse("reproach", 0, "lie-1", "user", "standard"))
    one = e.persistent_affect["user"].resentment
    assert 0 < one < both


def test_mixed_feelings_toward_same_person_coexist():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("love", .8, "history", "user", "attitude"))
    e.apply_impulse(EmotionalImpulse("anger", .7, "today", "user", "standard"))
    a = e.persistent_affect["user"]
    assert a.affection > 0
    assert a.resentment > 0
    assert e.state.emotions["love"] > 0
    assert e.state.emotions["anger"] > 0


def test_people_are_affectively_isolated():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("gratitude", .8, "alice-help", "alice", "compound"))
    e.apply_impulse(EmotionalImpulse("anger", .8, "bob-lie", "bob", "compound"))
    assert e.persistent_affect["alice"].affection > 0
    assert e.persistent_affect["alice"].resentment == 0
    assert e.persistent_affect["bob"].resentment > 0
    assert e.persistent_affect["bob"].affection == 0


def test_prospect_resolution_path_hope_to_disappointment():
    p = MatrixAffectivePrototype()
    hopeful = p.process(AffectiveStimulus(
        id="trip", category="event", actor_id="user", goal_relevance=1,
        goal_congruence=.8, goal_probability=.7, previous_goal_probability=.3,
    ))
    assert any(i.emotion_type == "hope" for i in hopeful.appraisal.impulses)
    failed = p.process(AffectiveStimulus(
        id="trip-resolution", category="event", actor_id="user", goal_relevance=1,
        goal_congruence=-.8, goal_probability=0, previous_goal_probability=.7,
    ))
    assert any(i.emotion_type == "disappointment" for i in failed.appraisal.impulses)


def test_prospect_resolution_path_fear_to_relief():
    p = MatrixAffectivePrototype()
    feared = p.process(AffectiveStimulus(
        id="risk", category="event", actor_id="user", goal_relevance=1,
        goal_congruence=-.8, goal_probability=.3, previous_goal_probability=.7,
    ))
    assert any(i.emotion_type == "fear" for i in feared.appraisal.impulses)
    resolved = p.process(AffectiveStimulus(
        id="risk-resolution", category="event", actor_id="user", goal_relevance=1,
        goal_congruence=.8, goal_probability=1, previous_goal_probability=.3,
    ))
    assert any(i.emotion_type == "relief" for i in resolved.appraisal.impulses)


def test_long_sequence_stays_bounded_and_keeps_entity_isolation():
    e = AffectiveEngine()
    emotions = ("joy", "gratitude", "anger", "reproach", "love", "disliking")
    people = ("alice", "bob", "carol")
    for n in range(3000):
        person = people[n % len(people)]
        emotion = emotions[n % len(emotions)]
        e.apply_impulse(EmotionalImpulse(emotion, .2 + (n % 8) * .1, f"evt-{n}", person, "scenario"))
        if n % 13 == 0:
            e.decay(.5)
    s = e.snapshot()
    assert all(0 <= v <= 1 for v in s["emotions"].values())
    for a in s["persistent_affect"].values():
        assert all(0 <= v <= 1 for v in a.values())
    assert set(s["persistent_affect"]) == set(people)
