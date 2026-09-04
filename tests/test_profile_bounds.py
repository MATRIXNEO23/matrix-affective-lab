from src.affective_engine import AffectiveEngine,AffectiveProfile,EmotionalImpulse


def test_extreme_profile_reactivity_remains_bounded():
    e=AffectiveEngine(profile=AffectiveProfile(reactivity=100,positive_reactivity=100,negative_reactivity=100));e.apply_impulse(EmotionalImpulse("anger",1,"x","u"));assert 0<=e.state.emotions["anger"]<=1
