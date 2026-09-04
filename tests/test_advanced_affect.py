from src.affective_engine import AffectiveEngine, AffectiveProfile, EmotionalImpulse, EmotionDisposition
from src.prototype import AffectiveStimulus, MatrixAffectivePrototype


def test_profile_reactivity_changes_same_event_response():
    calm = MatrixAffectivePrototype(AffectiveEngine(profile=AffectiveProfile(reactivity=0.5)))
    intense = MatrixAffectivePrototype(AffectiveEngine(profile=AffectiveProfile(reactivity=1.5)))
    s = AffectiveStimulus("e", "event", actor_id="user", goal_relevance=1.0, goal_congruence=-0.6)
    assert calm.process(s).after["emotions"]["distress"] < intense.process(s).after["emotions"]["distress"]


def test_positive_and_negative_profile_biases_are_separate():
    e = AffectiveEngine(profile=AffectiveProfile(positive_reactivity=0.5, negative_reactivity=1.5))
    e.apply_impulse(EmotionalImpulse("joy", 0.4, "p", appraisal_channel="goal"))
    e.apply_impulse(EmotionalImpulse("distress", 0.4, "n", appraisal_channel="goal"))
    assert e.state.emotions["joy"] < e.state.emotions["distress"]


def test_fatima_compound_anger_is_direct_occ_emotion():
    p = MatrixAffectivePrototype()
    trace = p.process(AffectiveStimulus(
        id="lie", category="action", actor_id="user",
        goal_relevance=1.0, goal_congruence=-0.8,
        standard_compliance=-0.7,
    ))
    assert [i.emotion_type for i in trace.appraisal.impulses] == ["anger"]
    assert abs(trace.appraisal.impulses[0].intensity - 0.75) < 1e-12
    assert "anger" in trace.after["emotions"]


def test_fatima_compound_gratitude_is_direct_occ_emotion():
    p = MatrixAffectivePrototype()
    trace = p.process(AffectiveStimulus(
        id="help", category="action", actor_id="user",
        goal_relevance=1.0, goal_congruence=0.8,
        standard_compliance=0.7,
    ))
    assert [i.emotion_type for i in trace.appraisal.impulses] == ["gratitude"]
    assert abs(trace.appraisal.impulses[0].intensity - 0.75) < 1e-12


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


def test_habituation_extension_is_isolated_and_reduces_repeats():
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


def test_mixed_feelings_joy_and_fatima_anger_can_coexist():
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
    assert trace.after["emotions"]["anger"] > 0
    assert trace.after["persistent_affect"]["user"]["affection"] > 0
    assert trace.after["persistent_affect"]["user"]["resentment"] > 0


def test_fatima_mood_relaxes_after_emotions_are_gone():
    e = AffectiveEngine(
        {"joy": EmotionDisposition(threshold=0.0, half_life=1.0)},
        profile=AffectiveProfile(mood_half_life=10.0),
    )
    e.apply_impulse(EmotionalImpulse("joy", 1.0, "e", appraisal_channel="goal"))
    e.decay(20.0)
    m1 = abs(e.state.mood_valence)
    assert "joy" not in e.state.emotions
    e.decay(10.0)
    assert abs(e.state.mood_valence) < m1


def test_fatima_goal_probability_drop_to_zero_is_disappointment():
    p = MatrixAffectivePrototype()
    trace = p.process(AffectiveStimulus(
        id="outcome", category="event", actor_id="u",
        goal_relevance=1.0, goal_congruence=0.0,
        previous_goal_probability=0.8, goal_probability=0.0,
        goal_significance=0.9,
    ))
    assert [i.emotion_type for i in trace.appraisal.impulses] == ["disappointment"]
    assert abs(trace.appraisal.impulses[0].intensity - 0.9) < 1e-12


def test_fatima_goal_probability_rise_to_one_from_low_is_relief():
    p = MatrixAffectivePrototype()
    trace = p.process(AffectiveStimulus(
        id="threat", category="event", actor_id="u",
        goal_relevance=1.0, goal_congruence=0.0,
        previous_goal_probability=0.2, goal_probability=1.0,
        goal_significance=0.8,
    ))
    assert [i.emotion_type for i in trace.appraisal.impulses] == ["relief"]
    assert abs(trace.appraisal.impulses[0].intensity - 0.8) < 1e-12


def test_fatima_goal_probability_rise_to_one_from_high_is_satisfaction():
    p = MatrixAffectivePrototype()
    trace = p.process(AffectiveStimulus(
        id="goal", category="event",
        previous_goal_probability=0.8, goal_probability=1.0,
        goal_significance=0.6,
    ))
    assert trace.appraisal.impulses[0].emotion_type == "satisfaction"


def test_fatima_goal_probability_drop_to_zero_from_low_is_fears_confirmed():
    p = MatrixAffectivePrototype()
    trace = p.process(AffectiveStimulus(
        id="goal", category="event",
        previous_goal_probability=0.2, goal_probability=0.0,
        goal_significance=0.6,
    ))
    assert trace.appraisal.impulses[0].emotion_type == "fears-confirmed"


def test_fatima_fortune_of_others_quadrants():
    cases = [
        (0.6, 0.7, "happy-for"),
        (0.6, -0.7, "gloating"),
        (-0.6, 0.7, "resentment"),
        (-0.6, -0.7, "pity"),
    ]
    for idx, (des, other_des, expected) in enumerate(cases):
        p = MatrixAffectivePrototype()
        trace = p.process(AffectiveStimulus(
            id=f"other-{idx}", category="event", actor_id="actor",
            goal_congruence=des, desirability_for_other=other_des, other_id="bob",
        ))
        assert trace.appraisal.impulses[0].emotion_type == expected


def test_fatima_reinforce_uses_log_sum_exp_and_increases_active_emotion():
    e = AffectiveEngine()
    e.apply_impulse(EmotionalImpulse("joy", 0.4, "e", appraisal_channel="goal"))
    before = e.state.emotions["joy"]
    assert e.reinforce("e", "goal", None, 0.4) is True
    assert before < e.state.emotions["joy"] <= 1.0


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
    assert 0.0 <= snap["arousal"] <= 1.0
    assert 0.0 <= snap["dominance"] <= 1.0
    for affect in snap["persistent_affect"].values():
        for value in affect.values():
            assert 0.0 <= value <= 1.0
