from src.affective_engine import PersistentAffect


def test_persistent_schema_keeps_relationship_dimensions_separate():
    a=PersistentAffect();assert a.trust==.5 and a.respect==.5;assert a.affection==a.attachment==a.attraction==a.resentment==a.admiration==a.aversion==0
