from src.prototype import AffectiveStimulus,MatrixAffectivePrototype


def test_unique_ids_same_kind_do_habituate():
    p=MatrixAffectivePrototype();a=p.process(AffectiveStimulus(id="a",category="event",goal_relevance=1,goal_congruence=.5,habituation_key="kind"));b=p.process(AffectiveStimulus(id="b",category="event",goal_relevance=1,goal_congruence=.5,habituation_key="kind"));assert b.appraisal.habituation_factor<a.appraisal.habituation_factor
