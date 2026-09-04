from src.appraisal import AffectiveStimulus, AppraisalEngine


def test_positive_confirmed_goal_event_is_joy():
    r = AppraisalEngine().appraise(AffectiveStimulus("e1", "event", "user", goal_relevance=1.0, goal_congruence=0.8))
    assert r.impulses[0].emotion_type == "joy"
    assert r.impulses[0].intensity == 0.8


def test_negative_unconfirmed_goal_event_is_fear():
    r = AppraisalEngine().appraise(AffectiveStimulus("e2", "event", "user", goal_relevance=0.5, goal_congruence=-0.8, confirmed=False))
    assert r.impulses[0].emotion_type == "fear"
    assert abs(r.impulses[0].intensity - 0.4) < 1e-9


def test_other_good_action_is_admiration():
    r = AppraisalEngine().appraise(AffectiveStimulus("e3", "action", "alice", standard_compliance=0.7))
    assert r.impulses[0].emotion_type == "admiration"
    assert r.impulses[0].target_id == "alice"


def test_other_bad_action_is_reproach():
    r = AppraisalEngine().appraise(AffectiveStimulus("e4", "action", "alice", standard_compliance=-0.9))
    assert r.impulses[0].emotion_type == "reproach"


def test_self_good_action_is_pride_without_external_target():
    r = AppraisalEngine().appraise(AffectiveStimulus("e5", "action", "self", standard_compliance=0.6))
    assert r.impulses[0].emotion_type == "pride"
    assert r.impulses[0].target_id is None


def test_irrelevant_event_produces_no_goal_emotion():
    r = AppraisalEngine().appraise(AffectiveStimulus("e6", "event", "user", goal_relevance=0.0, goal_congruence=-1.0))
    assert r.impulses == ()
