from src.affective_engine import AffectiveEngine, AffectiveProfile, EmotionalImpulse


def test_negative_reactivity_changes_same_event_strength():
    calm=AffectiveEngine(profile=AffectiveProfile(negative_reactivity=.5))
    reactive=AffectiveEngine(profile=AffectiveProfile(negative_reactivity=1.5))
    i=EmotionalImpulse("anger",.6,"same","user","standard")
    calm.apply_impulse(i); reactive.apply_impulse(i)
    assert reactive.state.emotions["anger"] > calm.state.emotions["anger"]


def test_recovery_scale_changes_decay_rate():
    fast=AffectiveEngine(profile=AffectiveProfile(recovery_scale=.5))
    slow=AffectiveEngine(profile=AffectiveProfile(recovery_scale=2.0))
    i=EmotionalImpulse("anger",.8,"same","user","standard")
    fast.apply_impulse(i);slow.apply_impulse(i);fast.decay(15);slow.decay(15)
    assert slow.state.emotions["anger"] > fast.state.emotions.get("anger",0)
