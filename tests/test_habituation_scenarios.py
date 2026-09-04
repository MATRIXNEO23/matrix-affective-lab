from src.prototype import AffectiveStimulus, MatrixAffectivePrototype


def test_repeated_unique_equivalent_events_habituate_but_do_not_vanish():
    p=MatrixAffectivePrototype(); factors=[]
    for n in range(20):
        t=p.process(AffectiveStimulus(id=f"hello-{n}",category="event",goal_relevance=1,goal_congruence=.8,habituation_key="same-kind"))
        factors.append(t.appraisal.habituation_factor)
    assert factors[0] == 1
    assert factors[-1] == .2
    assert all(a>=b for a,b in zip(factors,factors[1:]))
