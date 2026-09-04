from src.prototype import AffectiveStimulus,MatrixAffectivePrototype


def test_neutral_event_produces_no_affect():
    p=MatrixAffectivePrototype();t=p.process(AffectiveStimulus(id="neutral",category="event"));assert t.appraisal.impulses==();assert t.after["emotions"]=={}
