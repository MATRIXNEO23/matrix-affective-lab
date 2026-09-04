from src.prototype import AffectiveStimulus,MatrixAffectivePrototype


def test_different_habituation_keys_do_not_affect_each_other():
    p=MatrixAffectivePrototype();a=p.process(AffectiveStimulus(id="a",category="event",goal_relevance=1,goal_congruence=.5,habituation_key="A"));b=p.process(AffectiveStimulus(id="b",category="event",goal_relevance=1,goal_congruence=.5,habituation_key="B"));assert a.appraisal.habituation_factor==b.appraisal.habituation_factor==1
