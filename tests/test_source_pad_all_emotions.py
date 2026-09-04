from src.affective_engine import AffectiveEngine


def test_core_occ_emotions_have_pad_coordinates():
    core={"admiration","anger","disliking","disappointment","distress","fear","fears-confirmed","gloating","gratification","gratitude","happy-for","hate","hope","joy","liking","love","pity","pride","relief","remorse","reproach","resentment","satisfaction","shame"};assert core<=set(AffectiveEngine.ALMA_PAD)
