from src.prototype import MatrixAffectivePrototype


def test_empty_batch_is_noop():
    p=MatrixAffectivePrototype();s=p.affect.snapshot();assert p.process_many([])==[];assert p.affect.snapshot()==s
