from src.affective_engine import AffectiveEngine, AffectiveProfile, EmotionalImpulse, EmotionDisposition
from src.prototype import AffectiveStimulus, MatrixAffectivePrototype


def test_profile_reactivity_changes_same_event_response():
    calm = MatrixAffectivePrototype(AffectiveEngine(profile=AffectiveProfile(reactivity=0.5)))
    intense = MatrixAffectivePrototype(AffectiveEngine(profile=AffectiveProfile(reactivity=1.5)))
    s = AffectiveStimulus("e", "event", actor_id="user", goal_relevance=1.0, goal_congruence=-0.6)
    calm_value = calm.process(s).after["emotions"]["distress"]
    intense_value = intense.process(s).after["emotions"]["distress"]
    assert calm_value < intense_value


def test_positive_and_negative_profile_biases_are_separate():
    e = AffectiveEngine(profile=AffectiveProfile(positive_reactivity=0.5, negative_reactivity=1.5))
    e.apply_impulse(EmotionalImpulse("joy", 0.4, "p", appraisal_channel="goal"))
    e.apply_impulse(EmotionalImpulse("distress", 0.4, "n", appraisal_channel="goal"))
    assert e.state.emotions["joy"] < e.state.emotions["distress"]


def test_compound_anger_is_derived_from_distress_and_reproach():
    p = MatrixAffectivePrototype()
    trace = p.process(AffectiveStimulus(
        id="lie", category="action", actor_id="user",
        goal_relevance=1.0, goal_congruence=-0.8,
        standard_compliance=-0.7,
    ))
    assert trace.after["compound_emotions"]["anger"] > 0


def test_compound_gratitude_is_derived_from_joy_and_admiration():
    p = MatrixAffectivePrototype()
    trace = p.process(AffectiveStimulus(
        id="help", category="action", actor_id="user",
        goal_relevance=1.0, goal_congruence=0.8,
        standard_compliance=0.7,
    ))
    assert trace.after["compound_emotions"]["gratitude"] > 0


def test_mood_bias_only_affects_ambiguous_appraisal():
    p = MatrixAffectivePrototype(AffectiveEngine(profile=AffectiveProfile(mood_bias_strength=0.5)))
    p.affect.state.mood_valence = 0.8
    explicit = p.process(AffectiveStimulus(
        id="explicit", category="event", actor_id="u",
        goal_relevance=1.0, goal_congruence=-0.2, ambiguity=0.0,
    ))
    ambiguous = p.process(AffectiveStimulus(
        id="ambiguous", category="event", actor_id="u",
        goal_relevance=1.0, goal_congruence=-0.2, ambiguity=1.0,
    ))
    assert explicit.appraisal.congruence == -0.2
    assert ambiguous.appraisal.congruence > -0.2


def test_mood_cannot_flip_explicit_semantic_fact_when_ambiguity_zero():
    p = MatrixAffectivePrototype(AffectiveEngine(profile=AffectiveProfile(mood_bias_strength=1.0)))
    p.affect.state.mood_valence = 1.0
    trace = p.process(AffectiveStimulus(
        id="explicit-negative", category="event", actor_id="u",
        goal_relevance=1.0, goal_congruence=-1.0, ambiguity=0.0,
    ))
    assert trace.appraisal.impulses[0].emotion_type == "distress"


def test_habituation_reduces_repeated_similar_event_intensity():
    p = MatrixAffectivePrototype()
    values = []
    for i in range(8):
        trace = p.process(AffectiveStimulus(
            id=f"repeat-{i}", category="event", actor_id="u",
            goal_relevance=1.0, goal_congruence=0.8,
            habituation_key="small-compliment",
        ))
        values.append(trace.appraisal.impulses[0].intensity)
    assert values[0] > values[1] > values[2]
    assert values[-1] >= values[0] * 0.19


def test_mixed_feelings_can_coexist_for_same_entity():
    p = MatrixAffectivePrototype()
    p.process(AffectiveStimulus(
        id="good", category="event", actor_id="user",
        goal_relevance=1.0, goal_congruence=0.8,
    ))
    trace = p.process(AffectiveStimulus(
        id="bad", category="action", actor_id="user",
        goal_relevance=1.0, goal_congruence=-0.7,
        standard_compliance=-0.7,
    ))
    assert trace.after["emotions"]["joy"] > 0
    assert trace.after["emotions"]["distress"] > 0
    assert trace.after["persistent_affect"]["user"]["affection"] > 0
    assert trace.after["persistent_affect"]["user"]["resentment"] > 0


def test_mood_relaxes_even_after_all_emotions_are_gone():
    e = AffectiveEngine(
        {"joy": EmotionDisposition(threshold=0.0, half_life=1.0)},
        profile=AffectiveProfile(mood_half_life=10.0),
    )
    e.apply_impulse(EmotionalImpulse("joy", 1.0, "e", appraisal_channel="goal"))
    e.decay(20.0)
    m1 = abs(e.state.mood_valence)
    assert "joy" not in e.state.emotions
    e.decay(10.0)
    m2 = abs(e.state.mood_valence)
    assert m2 < m1


def test_long_stress_sequence_stays_bounded():
    p = MatrixAffectivePrototype()
    for i in range(2000):
        sign = 1.0 if i % 2 == 0 else -1.0
        p.process(AffectiveStimulus(
            id=f"e-{i}", category="action", actor_id=f"person-{i % 5}",
            goal_relevance=0.7, goal_congruence=0.6 * sign,
            standard_compliance=0.5 * sign,
            attitude_valence=0.4 * sign, attitude_intensity=0.6,
            habituation_key=f"pattern-{i % 10}",
        ))
        if i % 20 == 0:
            p.decay(1.0)
    snap = p.affect.snapshot()
    for value in snap["emotions"].values():
        assert 0.0 <= value <= 1.0
    assert -1.0 <= snap["mood_valence"] <= 1.0
    assert 0.0 <= snap["mood_arousal"] <= 1.0
    for affect in snap["persistent_affect"].values():
        for value in affect.values():
            assert 0.0 <= value <= 1.0
