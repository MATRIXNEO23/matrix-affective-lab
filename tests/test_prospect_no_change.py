from src.prototype import AffectiveStimulus, MatrixAffectivePrototype


def test_unchanged_goal_probability_does_not_activate_prospect_emotion():
    p=MatrixAffectivePrototype();t=p.process(AffectiveStimulus(id="same",category="event",goal_probability=.5,previous_goal_probability=.5));pros=[i for i in t.appraisal.impulses if i.appraisal_channel=="prospect"];assert pros and pros[0].intensity==0;assert p.affect.contribution_for("same","prospect",None) is None
