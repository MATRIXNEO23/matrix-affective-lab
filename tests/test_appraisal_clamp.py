from src.prototype import AffectiveStimulus,MatrixAffectivePrototype


def test_all_scalar_appraisal_outputs_are_bounded():
    p=MatrixAffectivePrototype();t=p.process(AffectiveStimulus(id="x",category="event",goal_relevance=-99,goal_congruence=99,novelty=-99,ambiguity=99));assert 0<=t.appraisal.relevance<=1;assert -1<=t.appraisal.congruence<=1;assert 0<=t.appraisal.novelty<=1
