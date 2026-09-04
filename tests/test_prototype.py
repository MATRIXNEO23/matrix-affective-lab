from src.prototype import AffectiveStimulus, MatrixAffectivePrototype


def test_positive_event_end_to_end():
    p = MatrixAffectivePrototype()
    trace = p.process(AffectiveStimulus(
        id="promise-kept", category="event", actor_id="user",
        goal_relevance=1.0, goal_congruence=0.8, confirmed=True,
    ))
    assert trace.appraisal.impulses[0].emotion_type == "joy"
    assert trace.after["emotions"]["joy"] > 0
    assert trace.after["persistent_affect"]["user"]["affection"] > 0


def test_negative_action_generates_goal_and_standard_emotions():
    p = MatrixAffectivePrototype()
    trace = p.process(AffectiveStimulus(
        id="lie", category="action", actor_id="user",
        goal_relevance=1.0, goal_congruence=-0.9,
        standard_compliance=-0.8, confirmed=True,
    ))
    types = {i.emotion_type for i in trace.appraisal.impulses}
    assert {"distress", "reproach"} <= types
    assert trace.after["persistent_affect"]["user"]["trust"] < 0.5


def test_unconfirmed_threat_produces_fear():
    p = MatrixAffectivePrototype()
    trace = p.process(AffectiveStimulus(
        id="possible-loss", category="event", actor_id="user",
        goal_relevance=0.8, goal_congruence=-0.7, confirmed=False,
    ))
    assert trace.appraisal.impulses[0].emotion_type == "fear"


def test_other_good_action_is_admiration():
    p = MatrixAffectivePrototype()
    trace = p.process(AffectiveStimulus(
        id="help", category="action", actor_id="alice", standard_compliance=0.7
    ))
    assert trace.appraisal.impulses[0].emotion_type == "admiration"
    assert trace.appraisal.impulses[0].target_id == "alice"


def test_self_good_action_is_pride_without_external_target():
    p = MatrixAffectivePrototype()
    trace = p.process(AffectiveStimulus(
        id="self-good", category="action", actor_id="self", standard_compliance=0.6
    ))
    assert trace.appraisal.impulses[0].emotion_type == "pride"
    assert trace.appraisal.impulses[0].target_id is None


def test_trace_preserves_before_after():
    p = MatrixAffectivePrototype()
    trace = p.process(AffectiveStimulus(
        id="good", category="event", actor_id="alice",
        goal_relevance=1.0, goal_congruence=1.0,
    ))
    assert "joy" not in trace.before["emotions"]
    assert trace.after["emotions"]["joy"] == 1.0


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
