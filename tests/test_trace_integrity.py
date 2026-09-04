from src.prototype import AffectiveStimulus,MatrixAffectivePrototype


def test_trace_before_after_and_cause_are_consistent():
    p=MatrixAffectivePrototype();t=p.process(AffectiveStimulus(id="evt",category="event",actor_id="alice",goal_relevance=1,goal_congruence=.8));assert t.before["emotions"]=={};assert t.after["emotions"];assert all(i.cause_id=="evt" for i in t.appraisal.impulses)
