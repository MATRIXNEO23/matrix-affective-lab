from src.prototype import AffectiveStimulus,MatrixAffectivePrototype


def test_self_good_action_yields_gratification():
    p=MatrixAffectivePrototype();t=p.process(AffectiveStimulus(id="success",category="action",actor_id="self",goal_relevance=1,goal_congruence=.8,standard_compliance=.8));assert "gratification" in [i.emotion_type for i in t.appraisal.impulses]
