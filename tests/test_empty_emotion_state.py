from src.affective_engine import AffectiveEngine


def test_empty_state_is_neutral_and_finite():
    s=AffectiveEngine().snapshot();assert s["emotions"]=={};assert s["valence"]==s["arousal"]==s["dominance"]==0
