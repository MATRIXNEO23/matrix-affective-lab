from src.affective_engine import AffectiveEngine, EmotionDisposition, EmotionalImpulse


def test_below_disposition_threshold_does_not_activate():
    e=AffectiveEngine(dispositions={"anger":EmotionDisposition(threshold=.5)});assert e.apply_impulse(EmotionalImpulse("anger",.4,"x","user")) is False;assert "anger" not in e.state.emotions

def test_above_threshold_activates_minus_threshold():
    e=AffectiveEngine(dispositions={"anger":EmotionDisposition(threshold=.5)});e.apply_impulse(EmotionalImpulse("anger",.8,"x","user"));assert abs(e.state.emotions["anger"]-.3)<1e-12
