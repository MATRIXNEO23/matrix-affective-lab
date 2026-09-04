from src.prototype import AffectiveStimulus, MatrixAffectivePrototype


def test_positive_event_end_to_end():
    p = MatrixAffectivePrototype()
    trace = p.process(AffectiveStimulus(
        id="promise-kept", category="event", actor_id="user",
        goal_relevance=1.0, goal_congruence=0.8, confirmed=True,
    ))
    assert trace.appraisal.impulses[0].emotion_type == "joy"
    assert abs(trace.after["emotions"]["joy"] - 0.75) < 1e-12
    assert trace.after["persistent_affect"]["user"]["affection"] > 0


def test_negative_action_uses_fatima_compound_anger():
    p = MatrixAffectivePrototype()
    trace = p.process(AffectiveStimulus(
        id="lie", category="action", actor_id="user",
        goal_relevance=1.0, goal_congruence=-0.9,
        standard_compliance=-0.8, confirmed=True,
    ))
    assert [i.emotion_type for i in trace.appraisal.impulses] == ["anger"]
    # FAtiMA compound potential abs(-.9 + -.8)/2 = .85; threshold => .80.
    assert abs(trace.after["emotions"]["anger"] - 0.8) < 1e-12
    assert trace.after["persistent_affect"]["user"]["trust"] < 0.5


def test_unconfirmed_threat_uses_matrix_prospect_fallback_only():
    p = MatrixAffectivePrototype()
    trace = p.process(AffectiveStimulus(
        id="possible-loss", category="event", actor_id="user",
        goal_relevance=0.8, goal_congruence=-0.7, confirmed=False,
    ))
    assert [i.emotion_type for i in trace.appraisal.impulses] == ["fear"]
    assert "distress" not in trace.after["emotions"]


def test_other_good_action_is_fatima_admiration():
    p = MatrixAffectivePrototype()
    trace = p.process(AffectiveStimulus(
        id="help", category="action", actor_id="alice", standard_compliance=0.7
    ))
    assert trace.appraisal.impulses[0].emotion_type == "admiration"
    assert trace.appraisal.impulses[0].target_id == "alice"
    assert abs(trace.after["emotions"]["admiration"] - 0.65) < 1e-12


def test_self_good_action_is_fatima_pride():
    p = MatrixAffectivePrototype()
    trace = p.process(AffectiveStimulus(
        id="self-good", category="action", actor_id="self", standard_compliance=0.6
    ))
    assert trace.appraisal.impulses[0].emotion_type == "pride"
    assert trace.appraisal.impulses[0].target_id is None


def test_entity_attitude_ports_fatima_love_magic_factor():
    p = MatrixAffectivePrototype()
    trace = p.process(AffectiveStimulus(
        id="meet-alice", category="entity", target_id="alice",
        attitude_valence=0.8, attitude_intensity=0.75,
    ))
    impulse = trace.appraisal.impulses[0]
    assert impulse.emotion_type == "love"
    assert abs(impulse.intensity - 0.42) < 1e-12
    # active intensity subtracts default threshold .05
    assert abs(trace.after["emotions"]["love"] - 0.37) < 1e-12
    assert trace.after["persistent_affect"]["alice"]["affection"] > 0


def test_negative_entity_attitude_ports_fatima_hate():
    p = MatrixAffectivePrototype()
    trace = p.process(AffectiveStimulus(
        id="meet-bob", category="entity", target_id="bob",
        attitude_valence=-1.0, attitude_intensity=0.7,
    ))
    assert trace.appraisal.impulses[0].emotion_type == "hate"
    assert trace.after["persistent_affect"]["bob"]["aversion"] > 0
    assert "alice" not in trace.after["persistent_affect"]


def test_trace_preserves_before_after_with_fatima_threshold():
    p = MatrixAffectivePrototype()
    trace = p.process(AffectiveStimulus(
        id="good", category="event", actor_id="alice",
        goal_relevance=1.0, goal_congruence=1.0,
    ))
    assert "joy" not in trace.before["emotions"]
    assert abs(trace.after["emotions"]["joy"] - 0.95) < 1e-12


def test_relationship_state_is_not_part_of_affective_state():
    p = MatrixAffectivePrototype()
    p.process(AffectiveStimulus(
        id="good", category="event", actor_id="user",
        goal_relevance=1.0, goal_congruence=1.0,
    ))
    assert "relationship_state" not in p.affect.snapshot()


def test_decay_available_end_to_end():
    p = MatrixAffectivePrototype()
    p.process(AffectiveStimulus(
        id="good", category="event", actor_id="user",
        goal_relevance=1.0, goal_congruence=0.8,
    ))
    before = p.affect.snapshot()["emotions"]["joy"]
    after = p.decay(10.0)["emotions"]["joy"]
    assert after < before
