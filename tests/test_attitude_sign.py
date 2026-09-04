from src.prototype import AffectiveStimulus,MatrixAffectivePrototype


def test_attitude_sign_maps_to_love_and_hate():
    p=MatrixAffectivePrototype();a=p.process(AffectiveStimulus(id="a",category="entity",target_id="alice",attitude_valence=.8));b=p.process(AffectiveStimulus(id="b",category="entity",target_id="bob",attitude_valence=-.8));assert "love" in [i.emotion_type for i in a.appraisal.impulses];assert "hate" in [i.emotion_type for i in b.appraisal.impulses]
