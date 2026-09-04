from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Optional

# Source-derived implementation.
# FAtiMA Toolkit (Apache-2.0), commit 56b7cbd992f953cfe21a7b12cb1a0e6cdf6ccf9f:
# - Assets/EmotionalAppraisal/ActiveEmotion.cs
# - Assets/EmotionalAppraisal/Mood.cs
# - Assets/EmotionalAppraisal/ConcreteEmotionalState.cs
# - Assets/EmotionalAppraisal/EmotionalAppraisalConfiguration.cs
# Adaptation: FAtiMA's internal [0,10] scale is normalized to [0,1].
# Cognitiv (MIT), commit f3aad875a77a3c7c522781e03acbb1944c3ab25c:
# - cognitiv/emotion.py dimensional V/A/D aggregation and saturation.


@dataclass(frozen=True)
class EmotionalImpulse:
    emotion_type: str
    intensity: float
    cause_id: str
    target_id: Optional[str] = None
    appraisal_channel: str = "generic"


@dataclass
class EmotionDisposition:
    threshold: float = 0.05
    half_life: float = 15.0


@dataclass(frozen=True)
class AffectiveProfile:
    reactivity: float = 1.0
    positive_reactivity: float = 1.0
    negative_reactivity: float = 1.0
    recovery_scale: float = 1.0
    persistent_step: float = 0.05
    # Cognitiv-compatible appraisal knob retained for the prototype adapter.
    mood_bias_strength: float = 0.15
    # Optional override; None keeps the FAtiMA default from AffectiveConfig.
    mood_half_life: Optional[float] = None


@dataclass(frozen=True)
class AffectiveConfig:
    half_life_decay_constant: float = 0.5
    emotion_influence_on_mood_factor: float = 0.3
    mood_influence_on_emotion_factor: float = 0.3
    minimum_mood_for_influence: float = 0.05
    emotional_half_life_decay_time: float = 15.0
    mood_half_life_decay_time: float = 60.0
    extinction_threshold: float = 0.01


@dataclass
class EmotionState:
    emotions: Dict[str, float] = field(default_factory=dict)
    valence: float = 0.0
    arousal: float = 0.0
    dominance: float = 0.5
    mood_valence: float = 0.0
    mood_arousal: float = 0.0


@dataclass
class PersistentAffect:
    trust: float = 0.5
    attachment: float = 0.0
    affection: float = 0.0
    attraction: float = 0.0
    resentment: float = 0.0
    respect: float = 0.5
    admiration: float = 0.0
    aversion: float = 0.0


@dataclass
class _Contribution:
    emotion_type: str
    intensity_at_t0: float
    tick_t0: float
    threshold: float
    decay_multiplier: float
    source_potential: float

    @property
    def potential(self) -> float:
        return self.intensity_at_t0 + self.threshold


class AffectiveEngine:
    POSITIVE = {
        "joy", "hope", "relief", "satisfaction", "admiration", "pride",
        "gratitude", "gratification", "love", "liking", "happy-for", "gloating",
        "affection",
    }
    NEGATIVE = {
        "distress", "fear", "fears-confirmed", "disappointment", "anger",
        "reproach", "shame", "remorse", "resentment", "hate", "disliking",
        "pity", "aversion",
    }
    HIGH_AROUSAL = {
        "anger", "fear", "fears-confirmed", "joy", "distress", "gratitude",
        "gratification", "reproach",
    }
    LOW_AROUSAL = {"relief", "satisfaction", "pity", "liking", "disliking"}
    HIGH_DOMINANCE = {"anger", "pride", "admiration", "gloating", "gratification"}
    LOW_DOMINANCE = {"fear", "distress", "shame", "remorse", "pity", "disappointment"}

    def __init__(
        self,
        dispositions: Optional[Dict[str, EmotionDisposition]] = None,
        profile: Optional[AffectiveProfile] = None,
        config: Optional[AffectiveConfig] = None,
    ):
        self.state = EmotionState()
        self.dispositions = dispositions or {}
        self.profile = profile or AffectiveProfile()
        self.config = config or AffectiveConfig()
        self.persistent_affect: Dict[str, PersistentAffect] = {}
        self._contributions: Dict[tuple[str, str, Optional[str]], _Contribution] = {}
        self._time = 0.0
        self._mood_at_t0 = 0.0
        self._mood_tick_t0 = 0.0

    def disposition(self, emotion_type: str) -> EmotionDisposition:
        return self.dispositions.get(emotion_type, EmotionDisposition())

    def contribution_for(
        self, cause_id: str, appraisal_channel: str, target_id: Optional[str]
    ) -> Optional[tuple[str, float]]:
        c = self._contributions.get((cause_id, appraisal_channel, target_id))
        if c is None:
            return None
        return (c.emotion_type, self._decayed_contribution(c, self._time))

    def apply_impulse(self, impulse: EmotionalImpulse) -> bool:
        slot = (impulse.cause_id, impulse.appraisal_channel, impulse.target_id)
        previous = self._contributions.get(slot)
        raw_potential = self._profiled_intensity(impulse.emotion_type, impulse.intensity)

        # Matrix semantic adapter: replaying the identical validated appraisal is
        # idempotent. FAtiMA assumes a new appraisal call carries new evidence;
        # our event bus can legitimately deliver the same event more than once.
        if (
            previous is not None
            and previous.emotion_type == impulse.emotion_type
            and math.isclose(previous.source_potential, raw_potential, abs_tol=1e-12)
        ):
            return False

        old_intensity = 0.0
        if previous is not None:
            old_intensity = self._decayed_contribution(previous, self._time)
            del self._contributions[slot]
            self._recompute_emotion(previous.emotion_type)
            if impulse.target_id:
                self._update_persistent_affect(
                    impulse.target_id, previous.emotion_type, -old_intensity
                )

        disp = self.disposition(impulse.emotion_type)
        threshold = self._clamp(disp.threshold)

        # Matrix semantic adapter: explicit zero/below-threshold source evidence
        # extinguishes a prior appraisal. Mood may modulate a real appraisal but
        # cannot manufacture one from semantically absent evidence.
        if raw_potential <= threshold:
            self._update_dimensions()
            return previous is not None

        potential = self._determine_potential(impulse.emotion_type, raw_potential)
        if potential <= threshold:
            self._update_dimensions()
            return previous is not None

        intensity = self._clamp(potential - threshold)
        new = _Contribution(
            emotion_type=impulse.emotion_type,
            intensity_at_t0=intensity,
            tick_t0=self._time,
            threshold=threshold,
            decay_multiplier=self._fatima_decay_multiplier(disp),
            source_potential=raw_potential,
        )
        self._contributions[slot] = new
        self._recompute_emotion(new.emotion_type)

        # Direct FAtiMA behavior: a reappraisal does not push mood again.
        if previous is None and self._influences_mood(new.emotion_type):
            self._update_mood_from_new_emotion(new.emotion_type, intensity)

        if impulse.target_id:
            self._update_persistent_affect(
                impulse.target_id, new.emotion_type, intensity
            )

        self._update_dimensions()
        return True

    def decay(self, delta_time: float) -> None:
        if delta_time <= 0:
            return
        self._time += delta_time
        self._decay_mood_to(self._time)

        dead: list[tuple[str, str, Optional[str]]] = []
        touched: set[str] = set()
        for slot, contribution in self._contributions.items():
            touched.add(contribution.emotion_type)
            if self._decayed_contribution(contribution, self._time) <= self.config.extinction_threshold:
                dead.append(slot)
        for slot in dead:
            touched.add(self._contributions[slot].emotion_type)
            del self._contributions[slot]
        for emotion_type in touched:
            self._recompute_emotion(emotion_type)
        self._update_dimensions()

    def reinforce(self, cause_id: str, appraisal_channel: str, target_id: Optional[str], potential: float) -> bool:
        slot = (cause_id, appraisal_channel, target_id)
        c = self._contributions.get(slot)
        if c is None:
            return False
        current_intensity = self._decayed_contribution(c, self._time)
        current_potential = current_intensity + c.threshold
        p = self._clamp(potential)
        a = current_potential * 10.0
        b = p * 10.0
        pivot = max(a, b)
        reinforced_internal = pivot + math.log(math.exp(a - pivot) + math.exp(b - pivot))
        reinforced = min(1.0, reinforced_internal / 10.0)
        new_intensity = self._clamp(reinforced - c.threshold)
        self._contributions[slot] = _Contribution(
            c.emotion_type,
            new_intensity,
            self._time,
            c.threshold,
            c.decay_multiplier,
            max(c.source_potential, p),
        )
        self._recompute_emotion(c.emotion_type)
        self._update_dimensions()
        return True

    def _fatima_decay_multiplier(self, disp: EmotionDisposition) -> float:
        effective_half_life = max(0.01, disp.half_life * max(0.01, self.profile.recovery_scale))
        return self.config.emotional_half_life_decay_time / effective_half_life

    def _decayed_contribution(self, c: _Contribution, tick: float) -> float:
        delta = max(0.0, tick - c.tick_t0)
        lam = math.log(self.config.half_life_decay_constant) / max(
            0.01, self.config.emotional_half_life_decay_time
        )
        return c.intensity_at_t0 * math.exp(lam * c.decay_multiplier * delta)

    def _determine_potential(self, emotion_type: str, potential: float) -> float:
        valence = self._emotion_valence(emotion_type)
        return max(
            0.0,
            potential
            + valence
            * (self.state.mood_valence * self.config.mood_influence_on_emotion_factor),
        )

    def _set_mood(self, value: float) -> None:
        value = max(-1.0, min(1.0, value))
        if abs(value) < self.config.minimum_mood_for_influence:
            value = 0.0
        self.state.mood_valence = value
        self._mood_at_t0 = value
        self._mood_tick_t0 = self._time

    def _update_mood_from_new_emotion(self, emotion_type: str, intensity: float) -> None:
        self._set_mood(
            self.state.mood_valence
            + self._emotion_valence(emotion_type)
            * (intensity * self.config.emotion_influence_on_mood_factor)
        )

    def _decay_mood_to(self, tick: float) -> None:
        if self._mood_at_t0 == 0.0:
            self.state.mood_valence = 0.0
            return
        delta = max(0.0, tick - self._mood_tick_t0)
        half_life = self.profile.mood_half_life or self.config.mood_half_life_decay_time
        lam = math.log(self.config.half_life_decay_constant) / max(0.01, half_life)
        value = self._mood_at_t0 * math.exp(lam * delta)
        if abs(value) < self.config.minimum_mood_for_influence:
            self.state.mood_valence = 0.0
            self._mood_at_t0 = 0.0
            self._mood_tick_t0 = 0.0
        else:
            self.state.mood_valence = value

    def _recompute_emotion(self, emotion_type: str) -> None:
        vals = [
            self._decayed_contribution(c, self._time)
            for c in self._contributions.values()
            if c.emotion_type == emotion_type
        ]
        if not vals:
            self.state.emotions.pop(emotion_type, None)
            return
        remaining = 1.0
        for value in vals:
            remaining *= 1.0 - self._clamp(value)
        self.state.emotions[emotion_type] = self._clamp(1.0 - remaining)

    def _update_dimensions(self) -> None:
        emotions = self.state.emotions
        if not emotions:
            self.state.valence = self.state.mood_valence * 0.1
            self.state.arousal = self.state.mood_arousal * 0.1
            self.state.dominance = 0.5
            return

        pos = sum(emotions.get(e, 0.0) for e in self.POSITIVE)
        neg = sum(emotions.get(e, 0.0) for e in self.NEGATIVE)
        total = pos + neg
        self.state.valence = (pos - neg) / total if total > 0 else 0.0

        high = sum(emotions.get(e, 0.0) for e in self.HIGH_AROUSAL)
        low = sum(emotions.get(e, 0.0) for e in self.LOW_AROUSAL)
        all_intensities = sum(emotions.values())
        self.state.arousal = min(1.0, (high + low * 0.3) / all_intensities) if all_intensities > 0 else 0.0

        hi_dom = sum(emotions.get(e, 0.0) for e in self.HIGH_DOMINANCE)
        lo_dom = sum(emotions.get(e, 0.0) for e in self.LOW_DOMINANCE)
        dom_total = hi_dom + lo_dom
        self.state.dominance = 0.5 + 0.5 * (hi_dom - lo_dom) / dom_total if dom_total > 0 else 0.5
        # Cognitiv updates mood via a separate update_mood(delta_time) call.
        # Do not mutate mood here: dimensional recomputation must be idempotent.

    def _profiled_intensity(self, emotion_type: str, value: float) -> float:
        scale = self.profile.reactivity
        if emotion_type in self.POSITIVE:
            scale *= self.profile.positive_reactivity
        elif emotion_type in self.NEGATIVE:
            scale *= self.profile.negative_reactivity
        return self._clamp(value * max(0.0, scale))

    def _emotion_valence(self, emotion_type: str) -> float:
        if emotion_type in self.POSITIVE:
            return 1.0
        if emotion_type in self.NEGATIVE:
            return -1.0
        return 0.0

    def _influences_mood(self, emotion_type: str) -> bool:
        return emotion_type not in {"hope", "fear"}

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))

    def _update_persistent_affect(
        self, entity_id: str, emotion_type: str, intensity_delta: float
    ) -> None:
        if math.isclose(intensity_delta, 0.0, rel_tol=0.0, abs_tol=1e-12):
            return
        affect = self.persistent_affect.setdefault(entity_id, PersistentAffect())
        step = intensity_delta * max(0.0, self.profile.persistent_step)

        if emotion_type in {"joy", "relief", "satisfaction", "love", "liking", "gratitude", "happy-for", "affection"}:
            affect.affection = self._clamp(affect.affection + step)
            affect.attachment = self._clamp(affect.attachment + step * 0.5)
        if emotion_type in {"admiration", "pride", "gratitude", "gratification"}:
            affect.admiration = self._clamp(affect.admiration + step)
            affect.respect = self._clamp(affect.respect + step * 0.5)
        if emotion_type in {"anger", "reproach", "resentment", "disappointment", "fears-confirmed"}:
            affect.resentment = self._clamp(affect.resentment + step)
            affect.trust = self._clamp(affect.trust - step)
        if emotion_type in {"hate", "disliking", "aversion"}:
            affect.aversion = self._clamp(affect.aversion + step)

    def snapshot(self) -> dict:
        return {
            "emotions": dict(self.state.emotions),
            "valence": self.state.valence,
            "arousal": self.state.arousal,
            "dominance": self.state.dominance,
            "mood_valence": self.state.mood_valence,
            "mood_arousal": self.state.mood_arousal,
            "persistent_affect": {
                entity: vars(affect).copy()
                for entity, affect in self.persistent_affect.items()
            },
        }
