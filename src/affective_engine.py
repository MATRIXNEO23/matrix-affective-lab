from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Optional


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
    half_life: float = 10.0


@dataclass(frozen=True)
class AffectiveProfile:
    """ALMA/Cognitiv-style character-level affect parameters."""
    reactivity: float = 1.0
    positive_reactivity: float = 1.0
    negative_reactivity: float = 1.0
    recovery_scale: float = 1.0
    mood_bias_strength: float = 0.15
    mood_half_life: float = 120.0
    persistent_step: float = 0.05


@dataclass
class EmotionState:
    emotions: Dict[str, float] = field(default_factory=dict)
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


@dataclass(frozen=True)
class _Contribution:
    emotion_type: str
    intensity: float


class AffectiveEngine:
    POSITIVE = {"joy", "hope", "relief", "admiration", "pride", "affection", "liking", "gratitude"}
    NEGATIVE = {"distress", "fear", "anger", "reproach", "shame", "resentment", "aversion", "disliking", "disappointment"}
    HIGH_AROUSAL = {"anger", "fear", "joy", "distress", "surprise", "gratitude"}

    def __init__(
        self,
        dispositions: Optional[Dict[str, EmotionDisposition]] = None,
        profile: Optional[AffectiveProfile] = None,
    ):
        self.state = EmotionState()
        self.dispositions = dispositions or {}
        self.profile = profile or AffectiveProfile()
        self.persistent_affect: Dict[str, PersistentAffect] = {}
        self._contributions: Dict[tuple[str, str, Optional[str]], _Contribution] = {}

    def disposition(self, emotion_type: str) -> EmotionDisposition:
        return self.dispositions.get(emotion_type, EmotionDisposition())

    def apply_impulse(self, impulse: EmotionalImpulse) -> bool:
        intensity = self._profiled_intensity(impulse.emotion_type, impulse.intensity)
        slot = (impulse.cause_id, impulse.appraisal_channel, impulse.target_id)
        previous = self._contributions.get(slot)
        threshold = self.disposition(impulse.emotion_type).threshold

        if intensity <= threshold:
            if previous is None:
                return False
            del self._contributions[slot]
            self._recompute_emotion(previous.emotion_type)
            self._update_mood_from_emotions()
            if impulse.target_id:
                self._update_persistent_affect(
                    impulse.target_id, previous.emotion_type, -previous.intensity
                )
            return True

        new = _Contribution(impulse.emotion_type, intensity)
        if previous == new:
            return False

        self._contributions[slot] = new
        if previous is not None:
            self._recompute_emotion(previous.emotion_type)
        self._recompute_emotion(new.emotion_type)
        self._update_mood_from_emotions()

        if impulse.target_id:
            if previous is not None:
                self._update_persistent_affect(
                    impulse.target_id, previous.emotion_type, -previous.intensity
                )
            self._update_persistent_affect(
                impulse.target_id, new.emotion_type, new.intensity
            )
        return True

    def decay(self, delta_time: float) -> None:
        if delta_time <= 0:
            return
        touched: set[str] = set()
        dead = []
        recovery_scale = max(0.01, self.profile.recovery_scale)
        for slot, contribution in list(self._contributions.items()):
            half_life = max(
                0.01,
                self.disposition(contribution.emotion_type).half_life * recovery_scale,
            )
            value = contribution.intensity * math.exp(
                -(math.log(2.0) / half_life) * delta_time
            )
            touched.add(contribution.emotion_type)
            if value < 0.01:
                dead.append(slot)
            else:
                self._contributions[slot] = _Contribution(
                    contribution.emotion_type, value
                )
        for slot in dead:
            del self._contributions[slot]
        for emotion_type in touched:
            self._recompute_emotion(emotion_type)

        self._relax_mood(delta_time)
        if self.state.emotions:
            self._update_mood_from_emotions()

    def compound_emotions(self) -> Dict[str, float]:
        """Derived compounds; no extra mutable emotion state is introduced."""
        e = self.state.emotions
        compounds: Dict[str, float] = {}
        pairs = {
            "anger": ("distress", "reproach"),
            "gratitude": ("joy", "admiration"),
            "remorse": ("distress", "shame"),
        }
        for name, (a, b) in pairs.items():
            value = min(e.get(a, 0.0), e.get(b, 0.0))
            if value > 0.0:
                compounds[name] = value
        return compounds

    def _profiled_intensity(self, emotion_type: str, value: float) -> float:
        scale = self.profile.reactivity
        if emotion_type in self.POSITIVE:
            scale *= self.profile.positive_reactivity
        elif emotion_type in self.NEGATIVE:
            scale *= self.profile.negative_reactivity
        return self._clamp(value * max(0.0, scale))

    def _recompute_emotion(self, emotion_type: str) -> None:
        vals = [
            c.intensity
            for c in self._contributions.values()
            if c.emotion_type == emotion_type
        ]
        if not vals:
            self.state.emotions.pop(emotion_type, None)
            return
        remaining = 1.0
        for value in vals:
            remaining *= 1.0 - self._clamp(value)
        self.state.emotions[emotion_type] = 1.0 - remaining

    def _update_mood_from_emotions(self) -> None:
        pos = sum(self.state.emotions.get(e, 0.0) for e in self.POSITIVE)
        neg = sum(self.state.emotions.get(e, 0.0) for e in self.NEGATIVE)
        total = pos + neg
        valence = 0.0 if total == 0 else (pos - neg) / total
        total_intensity = sum(self.state.emotions.values())
        arousal = 0.0 if total_intensity == 0 else min(
            1.0,
            sum(self.state.emotions.get(e, 0.0) for e in self.HIGH_AROUSAL)
            / total_intensity,
        )
        self.state.mood_valence += (valence - self.state.mood_valence) * 0.10
        self.state.mood_arousal += (arousal - self.state.mood_arousal) * 0.05

    def _relax_mood(self, delta_time: float) -> None:
        half_life = max(0.01, self.profile.mood_half_life)
        factor = math.exp(-(math.log(2.0) / half_life) * delta_time)
        self.state.mood_valence *= factor
        self.state.mood_arousal *= factor
        if abs(self.state.mood_valence) < 1e-9:
            self.state.mood_valence = 0.0
        if abs(self.state.mood_arousal) < 1e-9:
            self.state.mood_arousal = 0.0

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

        if emotion_type in {"joy", "relief", "affection", "liking", "gratitude"}:
            affect.affection = self._clamp(affect.affection + step)
            affect.attachment = self._clamp(affect.attachment + step * 0.5)
        if emotion_type in {"admiration", "pride", "gratitude"}:
            affect.admiration = self._clamp(affect.admiration + step)
            affect.respect = self._clamp(affect.respect + step * 0.5)
        if emotion_type in {"anger", "reproach", "resentment", "disappointment"}:
            affect.resentment = self._clamp(affect.resentment + step)
            affect.trust = self._clamp(affect.trust - step)
        if emotion_type in {"aversion", "disliking"}:
            affect.aversion = self._clamp(affect.aversion + step)

    def snapshot(self) -> dict:
        return {
            "emotions": dict(self.state.emotions),
            "compound_emotions": self.compound_emotions(),
            "mood_valence": self.state.mood_valence,
            "mood_arousal": self.state.mood_arousal,
            "persistent_affect": {
                entity: vars(affect).copy()
                for entity, affect in self.persistent_affect.items()
            },
        }
