from src.prototype import AffectiveStimulus,MatrixAffectivePrototype


def test_self_harmful_action_yields_remorse():
    p=MatrixAffectivePrototype();t=p.process(AffectiveStimulus(id="mistake",category="action",actor_id="self",goal_relevance=1,goal_congruence=-.8,standard_compliance=-.8));assert "remorse" in [i.emotion_type for i in t.appraisal.impulses]
