from src.affective_engine import AffectiveEngine, EmotionalImpulse
from src.prototype import AffectiveStimulus, MatrixAffectivePrototype


def test_mood_biases_ambiguous_not_unambiguous_appraisal():
    positive=MatrixAffectivePrototype(AffectiveEngine())
    positive.affect.apply_impulse(EmotionalImpulse("joy",.9,"seed",None,"seed"))
    amb=positive.process(AffectiveStimulus(id="amb",category="event",goal_relevance=1,goal_congruence=0,ambiguity=1))
    assert amb.appraisal.congruence > 0

    certain=positive.process(AffectiveStimulus(id="certain",category="event",goal_relevance=1,goal_congruence=-1,ambiguity=0))
    assert certain.appraisal.congruence == -1
