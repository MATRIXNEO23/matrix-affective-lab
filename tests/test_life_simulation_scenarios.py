from src.affective_engine import AffectiveEngine, EmotionalImpulse
from src.prototype import AffectiveStimulus, MatrixAffectivePrototype


def _affect(engine: AffectiveEngine, entity: str):
    return engine.snapshot()["persistent_affect"][entity]


def test_betrayal_apology_and_repair_requires_consistent_actions():
    e = AffectiveEngine()

    e.apply_impulse(EmotionalImpulse("anger", 0.95, "betrayal", "user", "standard"))
    after_betrayal = _affect(e, "user")
    assert after_betrayal["trust"] < 0.5
    assert after_betrayal["resentment"] > 0.0

    # An apology must help, but it must not magically reset trust after a breach.
    e.decay(12.0)
    e.apply_impulse(EmotionalImpulse("gratitude", 0.45, "apology", "user", "compound"))
    after_apology = _affect(e, "user")
    assert after_apology["trust"] > after_betrayal["trust"]
    assert after_apology["trust"] < 0.5
    assert after_apology["resentment"] < after_betrayal["resentment"]

    # Trust repair should require repeated new evidence, not repeated replay.
    for i in range(12):
        e.apply_impulse(EmotionalImpulse("gratitude", 0.65, f"kept-promise-{i}", "user", "compound"))
        e.decay(6.0)

    after_repair = _affect(e, "user")
    assert after_repair["trust"] > after_apology["trust"]
    assert 0.5 <= after_repair["trust"] < 0.9
    assert after_repair["resentment"] < after_apology["resentment"]
    assert after_repair["affection"] > after_apology["affection"]


def test_replaying_repair_events_does_not_accelerate_forgiveness():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("anger", 0.9, "betrayal", "user", "standard"))
    repair = EmotionalImpulse("gratitude", 0.7, "single-repair", "user", "compound")
    e.apply_impulse(repair)
    first = _affect(e, "user").copy()

    for _ in range(25):
        e.apply_impulse(repair)
    replayed = _affect(e, "user").copy()

    assert replayed == first


def test_love_and_anger_can_coexist_without_erasing_attachment():
    e = AffectiveEngine()
    for i in range(8):
        e.apply_impulse(EmotionalImpulse("love", 0.6, f"bond-{i}", "user", "attitude"))
    bonded = _affect(e, "user")
    assert bonded["affection"] > 0.0
    assert bonded["attachment"] > 0.0

    e.apply_impulse(EmotionalImpulse("anger", 0.85, "jealousy-conflict", "user", "standard"))
    conflicted = _affect(e, "user")
    assert conflicted["affection"] == bonded["affection"]
    assert conflicted["attachment"] == bonded["attachment"]
    assert conflicted["resentment"] > 0.0
    assert conflicted["trust"] < bonded["trust"]


def test_unconfirmed_negative_report_is_weaker_than_confirmed_harm():
    p = MatrixAffectivePrototype()

    report = p.process(AffectiveStimulus(
        id="rumor", category="event", actor_id="user",
        goal_relevance=1.0, goal_congruence=-0.8, confirmed=False,
    ))
    assert [i.emotion_type for i in report.appraisal.impulses] == ["fear"]
    assert "user" not in report.after["persistent_affect"]

    confirmed = p.process(AffectiveStimulus(
        id="confirmed-harm", category="action", actor_id="user",
        goal_relevance=1.0, goal_congruence=-0.8,
        standard_compliance=-0.8, confirmed=True,
    ))
    assert confirmed.after["persistent_affect"]["user"]["trust"] < 0.5
    assert confirmed.after["persistent_affect"]["user"]["resentment"] > 0.0


def test_habituation_reduces_repeated_small_positive_events_without_blocking_bonding():
    p = MatrixAffectivePrototype()
    intensities = []
    for i in range(18):
        trace = p.process(AffectiveStimulus(
            id=f"compliment-{i}", category="action", actor_id="user",
            goal_relevance=0.7, goal_congruence=0.5,
            standard_compliance=0.4,
            habituation_key="small-compliment",
        ))
        intensities.append(trace.appraisal.impulses[0].intensity)

    assert intensities[0] > intensities[1] > intensities[2]
    assert intensities[-1] >= intensities[0] * 0.19
    affect = p.affect.snapshot()["persistent_affect"]["user"]
    assert 0.0 < affect["affection"] < 0.5
    assert 0.0 < affect["admiration"] < 0.5


def test_people_remain_isolated_under_opposite_histories():
    e = AffectiveEngine()
    for i in range(10):
        e.apply_impulse(EmotionalImpulse("gratitude", 0.7, f"alice-help-{i}", "alice", "compound"))
        e.apply_impulse(EmotionalImpulse("anger", 0.7, f"bob-harm-{i}", "bob", "standard"))

    alice = _affect(e, "alice")
    bob = _affect(e, "bob")
    assert alice["trust"] > 0.5
    assert alice["affection"] > 0.0
    assert alice["resentment"] == 0.0
    assert bob["trust"] < 0.5
    assert bob["resentment"] > 0.0
    assert bob["affection"] == 0.0


def test_probability_arc_uses_prospect_emotions_before_outcome():
    p = MatrixAffectivePrototype()

    hope = p.process(AffectiveStimulus(
        id="exam", category="event", actor_id="user",
        goal_relevance=1.0, goal_congruence=0.0,
        goal_probability=0.65, previous_goal_probability=0.20,
        goal_significance=0.9,
    ))
    assert any(i.emotion_type == "hope" for i in hope.appraisal.impulses)

    relief = p.process(AffectiveStimulus(
        id="exam", category="event", actor_id="user",
        goal_relevance=1.0, goal_congruence=0.0,
        goal_probability=1.0, previous_goal_probability=0.40,
        goal_significance=0.9,
    ))
    assert any(i.emotion_type == "relief" for i in relief.appraisal.impulses)

    disappointment = p.process(AffectiveStimulus(
        id="contest", category="event", actor_id="user",
        goal_relevance=1.0, goal_congruence=0.0,
        goal_probability=0.0, previous_goal_probability=0.70,
        goal_significance=0.9,
    ))
    assert any(i.emotion_type == "disappointment" for i in disappointment.appraisal.impulses)


def test_long_scripted_relationship_simulation_has_plausible_end_state():
    p = MatrixAffectivePrototype()

    # Phase 1: gradual positive bond.
    for i in range(15):
        p.process(AffectiveStimulus(
            id=f"kind-{i}", category="action", actor_id="user",
            goal_relevance=0.7, goal_congruence=0.5,
            standard_compliance=0.5,
            attitude_valence=0.3, attitude_intensity=0.6,
            habituation_key=f"kindness-{i % 4}",
        ))
        p.decay(4.0)

    positive = p.affect.snapshot()["persistent_affect"]["user"].copy()
    assert positive["trust"] >= 0.5
    assert positive["affection"] > 0.0

    # Phase 2: serious breach.
    p.process(AffectiveStimulus(
        id="serious-lie", category="action", actor_id="user",
        goal_relevance=1.0, goal_congruence=-1.0,
        standard_compliance=-1.0,
    ))
    p.decay(24.0)
    breached = p.affect.snapshot()["persistent_affect"]["user"].copy()
    assert breached["trust"] < positive["trust"]
    assert breached["resentment"] > positive["resentment"]
    assert breached["affection"] >= positive["affection"]

    # Phase 3: repair, but not full amnesia.
    for i in range(20):
        p.process(AffectiveStimulus(
            id=f"repair-{i}", category="action", actor_id="user",
            goal_relevance=0.8, goal_congruence=0.6,
            standard_compliance=0.7,
            habituation_key=f"repair-pattern-{i % 5}",
        ))
        p.decay(12.0)

    repaired = p.affect.snapshot()["persistent_affect"]["user"]
    assert repaired["trust"] > breached["trust"]
    assert repaired["trust"] < 0.95
    assert repaired["resentment"] < breached["resentment"]
    assert repaired["affection"] >= breached["affection"]

    snap = p.affect.snapshot()
    assert all(0.0 <= v <= 1.0 for v in snap["emotions"].values())
    assert -1.0 <= snap["valence"] <= 1.0
    assert -1.0 <= snap["arousal"] <= 1.0
    assert -1.0 <= snap["dominance"] <= 1.0
