import random

from src.affective_engine import AffectiveEngine, EmotionalImpulse


def test_longitudinal_reappraisal_fuzz_preserves_invariants():
    rng = random.Random(8109)
    e = AffectiveEngine()
    people = ["user", "alice", "bob", "carol"]
    channels = ["goal", "standard", "attitude", "compound"]
    emotions = ["joy", "distress", "admiration", "reproach", "gratitude", "anger", "love", "hate"]
    active = {}

    for step in range(10000):
        if active and rng.random() < .28:
            slot = rng.choice(list(active))
            cause, channel, target = slot
            if rng.random() < .45:
                intensity = 0.0
                emotion = active[slot]
                active.pop(slot, None)
            else:
                emotion = rng.choice(emotions)
                intensity = rng.random()
                active[slot] = emotion
            e.apply_impulse(EmotionalImpulse(emotion, intensity, cause, target, channel))
        else:
            target = rng.choice(people)
            channel = rng.choice(channels)
            cause = f"cause-{step}"
            emotion = rng.choice(emotions)
            active[(cause, channel, target)] = emotion
            e.apply_impulse(EmotionalImpulse(emotion, rng.random(), cause, target, channel))

        if step % 17 == 0:
            e.decay(rng.random() * 3)

        if step % 101 == 0:
            snap = e.snapshot()
            assert all(0 <= x <= 1 for x in snap["emotions"].values())
            assert -1 <= snap["valence"] <= 1
            assert -1 <= snap["arousal"] <= 1
            assert -1 <= snap["dominance"] <= 1
            for affect in snap["persistent_affect"].values():
                assert all(0 <= x <= 1 for x in affect.values())
