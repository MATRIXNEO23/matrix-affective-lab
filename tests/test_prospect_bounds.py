from src.prototype import AffectiveStimulus,MatrixAffectivePrototype


def test_extreme_probabilities_are_clamped_before_prospect_appraisal():
    p=MatrixAffectivePrototype();t=p.process(AffectiveStimulus(id="x",category="event",goal_probability=99,previous_goal_probability=-99));assert all(0<=i.intensity<=1 for i in t.appraisal.impulses)
