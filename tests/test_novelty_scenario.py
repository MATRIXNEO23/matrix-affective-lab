from src.prototype import AffectiveStimulus, MatrixAffectivePrototype


def test_zero_novelty_suppresses_new_transient_appraisal():
    p=MatrixAffectivePrototype();t=p.process(AffectiveStimulus(id="known",category="event",goal_relevance=1,goal_congruence=1,novelty=0));assert t.appraisal.impulses==()

def test_full_novelty_allows_appraisal():
    p=MatrixAffectivePrototype();t=p.process(AffectiveStimulus(id="new",category="event",goal_relevance=1,goal_congruence=1,novelty=1));assert t.appraisal.impulses
