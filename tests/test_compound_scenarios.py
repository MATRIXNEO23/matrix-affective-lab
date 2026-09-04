from src.prototype import AffectiveStimulus, MatrixAffectivePrototype


def test_helpful_other_action_yields_gratitude_not_duplicate_joy_admiration():
    p=MatrixAffectivePrototype();t=p.process(AffectiveStimulus(id="help",category="action",actor_id="alice",goal_relevance=1,goal_congruence=.8,standard_compliance=.8));types=[x.emotion_type for x in t.appraisal.impulses];assert "gratitude" in types;assert "joy" not in types;assert "admiration" not in types

def test_harmful_other_action_yields_anger():
    p=MatrixAffectivePrototype();t=p.process(AffectiveStimulus(id="harm",category="action",actor_id="bob",goal_relevance=1,goal_congruence=-.8,standard_compliance=-.8));assert "anger" in [x.emotion_type for x in t.appraisal.impulses]
