from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Optional

# Source-derived implementation.
# FAtiMA Toolkit (Apache-2.0), commit 56b7cbd992f953cfe21a7b12cb1a0e6cdf6ccf9f:
# ActiveEmotion.cs, Mood.cs, ConcreteEmotionalState.cs,
# EmotionalAppraisalConfiguration.cs. Internal [0,10] normalized to [0,1].
# Cognitiv (MIT), commit f3aad875a77a3c7c522781e03acbb1944c3ab25c:
# saturation across independent impulses.
# Alma.Net (MIT), commit 55b0475abdd077f145ed90575b435111c288454e:
# OCEAN->PAD and emotion->PAD mappings.


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
class OceanProfile:
    openness: float = 0.0
    conscientiousness: float = 0.0
    extroversion: float = 0.0
    agreeableness: float = 0.0
    neuroticism: float = 0.0


@dataclass(frozen=True)
class AffectiveProfile:
    reactivity: float = 1.0
    positive_reactivity: float = 1.0
    negative_reactivity: float = 1.0
    recovery_scale: float = 1.0
    persistent_step: float = 0.05
    mood_bias_strength: float = 0.15
    mood_half_life: Optional[float] = None
    ocean: Optional[OceanProfile] = None


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
    dominance: float = 0.0
    virtual_emotion_intensity: float = 0.0
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
    # Matrix-owned accounting value. Persistent affect is evidence-derived and
    # must not decay with the transient emotion. Corrections reverse this exact
    # amount even if the emotion has decayed in the meantime.
    persistent_intensity: float

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

    ALMA_PAD = {
        "admiration": (0.5, 0.3, -0.2), "anger": (-0.51, 0.59, 0.25),
        "disliking": (-0.4, 0.2, 0.1), "disappointment": (-0.3, 0.1, -0.4),
        "distress": (-0.4, -0.2, -0.5), "fear": (-0.64, 0.60, -0.43),
        "fears-confirmed": (-0.5, -0.3, -0.7), "gloating": (0.3, -0.3, -0.1),
        "gratification": (0.6, 0.5, 0.4), "gratitude": (0.4, 0.2, -0.3),
        "happy-for": (0.4, 0.2, 0.2), "hate": (-0.6, 0.6, 0.3),
        "hope": (0.2, 0.2, -0.1), "joy": (0.4, 0.2, 0.1),
        "liking": (0.4, 0.16, -0.24), "love": (0.3, 0.1, 0.2),
        "pity": (-0.4, -0.2, -0.5), "pride": (0.4, 0.3, 0.3),
        "relief": (0.2, -0.3, 0.4), "remorse": (-0.3, 0.1, -0.6),
        "reproach": (-0.3, -0.1, 0.4), "resentment": (-0.2, -0.3, -0.2),
        "satisfaction": (0.3, -0.2, 0.4), "shame": (-0.3, 0.1, -0.6),
    }

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

    @staticmethod
    def ocean_to_pad(ocean: OceanProfile) -> tuple[float, float, float]:
        p = 0.21 * ocean.extroversion + 0.59 * ocean.agreeableness + 0.19 * ocean.neuroticism
        a = 0.15 * ocean.openness + 0.30 * ocean.agreeableness - 0.57 * ocean.neuroticism
        d = 0.25 * ocean.openness + 0.17 * ocean.conscientiousness + 0.60 * ocean.extroversion - 0.32 * ocean.agreeableness
        return tuple(max(-1.0, min(1.0, x)) for x in (p, a, d))

    def contribution_for(self, cause_id: str, appraisal_channel: str, target_id: Optional[str]) -> Optional[tuple[str, float]]:
        c = self._contributions.get((cause_id, appraisal_channel, target_id))
        return None if c is None else (c.emotion_type, self._decayed_contribution(c, self._time))

    def apply_impulse(self, impulse: EmotionalImpulse) -> bool:
        slot = (impulse.cause_id, impulse.appraisal_channel, impulse.target_id)
        previous = self._contributions.get(slot)
        raw_potential = self._profiled_intensity(impulse.emotion_type, impulse.intensity)

        if previous is not None and previous.emotion_type == impulse.emotion_type and math.isclose(previous.source_potential, raw_potential, abs_tol=1e-12):
            return False

        if previous is not None:
            del self._contributions[slot]
            self._recompute_emotion(previous.emotion_type)
            if impulse.target_id:
                self._update_persistent_affect(impulse.target_id, previous.emotion_type, -previous.persistent_intensity)

        disp = self.disposition(impulse.emotion_type)
        threshold = self._clamp(disp.threshold)
        if raw_potential <= threshold:
            self._update_dimensions()
            return previous is not None

        potential = self._determine_potential(impulse.emotion_type, raw_potential)
        if potential <= threshold:
            self._update_dimensions()
            return previous is not None

        intensity = self._clamp(potential - threshold)
        new = _Contribution(
            impulse.emotion_type,
            intensity,
            self._time,
            threshold,
            self._fatima_decay_multiplier(disp),
            raw_potential,
            intensity,
        )
        self._contributions[slot] = new
        self._recompute_emotion(new.emotion_type)

        if previous is None and self._influences_mood(new.emotion_type):
            self._update_mood_from_new_emotion(new.emotion_type, intensity)
        if impulse.target_id:
            self._update_persistent_affect(impulse.target_id, new.emotion_type, new.persistent_intensity)

        self._update_dimensions()
        return True

    def decay(self, delta_time: float) -> None:
        if delta_time <= 0:
            return
        self._time += delta_time
        self._decay_mood_to(self._time)
        dead: list[tuple[str, str, Optional[str]]] = []
        touched: set[str] = set()
        for slot, c in self._contributions.items():
            touched.add(c.emotion_type)
            if self._decayed_contribution(c, self._time) <= self.config.extinction_threshold:
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
        a, b = current_potential * 10.0, p * 10.0
        pivot = max(a, b)
        reinforced = min(1.0, (pivot + math.log(math.exp(a - pivot) + math.exp(b - pivot))) / 10.0)
        new_intensity = self._clamp(reinforced - c.threshold)
        persistent_delta = new_intensity - c.persistent_intensity
        self._contributions[slot] = _Contribution(
            c.emotion_type,
            new_intensity,
            self._time,
            c.threshold,
            c.decay_multiplier,
            max(c.source_potential, p),
            new_intensity,
        )
        if target_id and not math.isclose(persistent_delta, 0.0, abs_tol=1e-12):
            self._update_persistent_affect(target_id, c.emotion_type, persistent_delta)
        self._recompute_emotion(c.emotion_type)
        self._update_dimensions()
        return True

    def _fatima_decay_multiplier(self, disp: EmotionDisposition) -> float:
        effective_half_life = max(0.01, disp.half_life * max(0.01, self.profile.recovery_scale))
        return self.config.emotional_half_life_decay_time / effective_half_life

    def _decayed_contribution(self, c: _Contribution, tick: float) -> float:
        delta = max(0.0, tick - c.tick_t0)
        lam = math.log(self.config.half_life_decay_constant) / max(0.01, self.config.emotional_half_life_decay_time)
        return c.intensity_at_t0 * math.exp(lam * c.decay_multiplier * delta)

    def _determine_potential(self, emotion_type: str, potential: float) -> float:
        return max(0.0, potential + self._emotion_valence(emotion_type) * self.state.mood_valence * self.config.mood_influence_on_emotion_factor)

    def _set_mood(self, value: float) -> None:
        value = max(-1.0, min(1.0, value))
        if abs(value) < self.config.minimum_mood_for_influence:
            value = 0.0
        self.state.mood_valence = value
        self._mood_at_t0 = value
        self._mood_tick_t0 = self._time

    def _update_mood_from_new_emotion(self, emotion_type: str, intensity: float) -> None:
        self._set_mood(self.state.mood_valence + self._emotion_valence(emotion_type) * intensity * self.config.emotion_influence_on_mood_factor)

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
        vals = [self._decayed_contribution(c, self._time) for c in self._contributions.values() if c.emotion_type == emotion_type]
        if not vals:
            self.state.emotions.pop(emotion_type, None)
            return
        remaining = 1.0
        for value in vals:
            remaining *= 1.0 - self._clamp(value)
        self.state.emotions[emotion_type] = self._clamp(1.0 - remaining)

    def _update_dimensions(self) -> None:
        if not self.state.emotions:
            self.state.valence = self.state.arousal = self.state.dominance = self.state.virtual_emotion_intensity = 0.0
            return
        p = a = d = total_intensity = 0.0
        mapped = 0
        for emotion_type, intensity in self.state.emotions.items():
            pad = self.ALMA_PAD.get(emotion_type)
            if pad is None:
                continue
            p += pad[0]
            a += pad[1]
            d += pad[2]
            total_intensity += intensity
            mapped += 1
        if mapped == 0:
            self.state.valence = self.state.arousal = self.state.dominance = self.state.virtual_emotion_intensity = 0.0
            return
        self.state.valence = max(-1.0, min(1.0, p))
        self.state.arousal = max(-1.0, min(1.0, a))
        self.state.dominance = max(-1.0, min(1.0, d))
        self.state.virtual_emotion_intensity = self._clamp(total_intensity / mapped)

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

    def _update_persistent_affect(self, entity_id: str, emotion_type: str, intensity_delta: float) -> None:
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
        default_pad = self.ocean_to_pad(self.profile.ocean) if self.profile.ocean else None
        return {
            "emotions": dict(self.state.emotions),
            "valence": self.state.valence,
            "arousal": self.state.arousal,
            "dominance": self.state.dominance,
            "virtual_emotion_intensity": self.state.virtual_emotion_intensity,
            "default_personality_pad": default_pad,
            "mood_valence": self.state.mood_valence,
            "mood_arousal": self.state.mood_arousal,
            "persistent_affect": {entity: vars(affect).copy() for entity, affect in self.persistent_affect.items()},
        }
