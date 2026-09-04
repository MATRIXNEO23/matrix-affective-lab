from src.affective_engine import AffectiveEngine, EmotionalImpulse


def test_retraction_after_transient_emotion_extinction_is_safe():
    e=AffectiveEngine();e.apply_impulse(EmotionalImpulse("anger",.8,"old","user","standard"));e.decay(10000);assert e.contribution_for("old","standard","user") is None
    # Once transient contribution has been garbage-collected, persistent history is no longer retractable by the transient engine.
    # This test documents the boundary that memory/lineage must own later.
    before=e.snapshot()["persistent_affect"]["user"].copy();e.apply_impulse(EmotionalImpulse("anger",0,"old","user","standard"));assert e.snapshot()["persistent_affect"]["user"]==before
