from src.affective_engine import AffectiveEngine


def test_reinforcing_missing_cause_is_safe_noop():
    e=AffectiveEngine();s=e.snapshot();assert e.reinforce("missing","goal","u",1) is False;assert e.snapshot()==s
