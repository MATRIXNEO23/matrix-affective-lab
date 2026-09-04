from src.prototype import AffectiveStimulus,MatrixAffectivePrototype


def test_process_many_matches_sequential_processing():
    xs=[AffectiveStimulus(id=f"x{n}",category="event",actor_id="u",goal_relevance=1,goal_congruence=.5) for n in range(20)];a=MatrixAffectivePrototype();b=MatrixAffectivePrototype();a.process_many(xs);[b.process(x) for x in xs];assert a.affect.snapshot()==b.affect.snapshot()
