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


@dataclass
class EmotionDisposition:
    threshold: float = 0.05
    half_life: float = 10.0


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


class AffectiveEngine:
    POSITIVE = {"joy", "hope", "relief", "admiration", "pride", "affection", "liking"}
    NEGATIVE = {"distress", "fear", "anger", "reproach", "shame", "resentment", "aversion", "disliking"}
    HIGH_AROUSAL = {"anger", "fear", "joy", "distress", "surprise"}

    def __init__(self, dispositions: Optional[Dict[str, EmotionDisposition]] = None):
        self.state = EmotionState()
        self.dispositions = dispositions or {}
        self.persistent_affect: Dict[str, PersistentAffect] = {}
        self._contributions: Dict[tuple[str, str, Optional[str]], float] = {}

    def disposition(self, emotion_type: str) -> EmotionDisposition:
        return self.dispositions.get(emotion_type, EmotionDisposition())

    def apply_impulse(self, impulse: EmotionalImpulse) -> bool:
        """Insert or replace one cause-specific appraisal contribution.

        Reappraisal is replacement, not accumulation. If a previously active
        cause is reappraised below threshold, that cause is removed. An exact
        no-op reappraisal does not update mood or persistent affect.
        """
        intensity = self._clamp(impulse.intensity)
        disp = self.disposition(impulse.emotion_type)
        key = (impulse.cause_id, impulse.emotion_type, impulse.target_id)
        previous = self._contributions.get(key)

        # New sub-threshold evidence has no effect; a sub-threshold reappraisal
        # explicitly extinguishes the prior contribution from the same cause.
        if intensity <= disp.threshold:
            if previous is None:
                return False
            del self._contributions[key]
            self._recompute_emotion(impulse.emotion_type)
            self._update_mood()
            if impulse.target_id:
                self._update_persistent_affect(
                    impulse.target_id, impulse.emotion_type, -previous
                )
            return True

        # Exact same evidence is a true no-op. This prevents repeated reads of
        # the same event from drifting mood or long-lived affect.
        if previous is not None and math.isclose(previous, intensity, rel_tol=0.0, abs_tol=1e-12):
            return False

        prior = previous or 0.0
        self._contributions[key] = intensity
        self._recompute_emotion(impulse.emotion_type)
        self._update_mood()
        if impulse.target_id:
            self._update_persistent_affect(
                impulse.target_id, impulse.emotion_type, intensity - prior
            )
        return True

    def decay(self, delta_time: float) -> None:
        if delta_time <= 0:
            return
        touched = set()
        dead = []
        for key, intensity in list(self._contributions.items()):
            _, emotion_type, _ = key
            half_life = max(0.01, self.disposition(emotion_type).half_life)
            value = intensity * math.exp(-(math.log(2.0) / half_life) * delta_time)
            touched.add(emotion_type)
            if value < 0.01:
                dead.append(key)
            else:
                self._contributions[key] = value
        for key in dead:
            del self._contributions[key]
        for emotion_type in touched:
            self._recompute_emotion(emotion_type)
        if touched:
            self._update_mood()

    def _recompute_emotion(self, emotion_type: str) -> None:
        vals = [v for (_, et, _), v in self._contributions.items() if et == emotion_type]
        if not vals:
            self.state.emotions.pop(emotion_type, None)
            return
        # Cognitiv-style saturation of independent causes:
        # combined = 1 - product(1 - contribution_i)
        remaining = 1.0
        for value in vals:
            remaining *= 1.0 - self._clamp(value)
        self.state.emotions[emotion_type] = 1.0 - remaining

    def _update_mood(self) -> None:
        pos = sum(self.state.emotions.get(e, 0.0) for e in self.POSITIVE)
        neg = sum(self.state.emotions.get(e, 0.0) for e in self.NEGATIVE)
        total = pos + neg
        valence = 0.0 if total == 0 else (pos - neg) / total
        total_intensity = sum(self.state.emotions.values())
        arousal = 0.0 if total_intensity == 0 else min(
            1.0,
            sum(self.state.emotions.get(e, 0.0) for e in self.HIGH_AROUSAL) / total_intensity,
        )
        self.state.mood_valence += (valence - self.state.mood_valence) * 0.10
        self.state.mood_arousal += (arousal - self.state.mood_arousal) * 0.05

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))

    def _update_persistent_affect(self, entity_id: str, emotion_type: str, intensity_delta: float) -> None:
        if math.isclose(intensity_delta, 0.0, rel_tol=0.0, abs_tol=1e-12):
            return
        affect = self.persistent_affect.setdefault(entity_id, PersistentAffect())
        step = intensity_delta * 0.05
        if emotion_type in {"joy", "relief", "affection", "liking"}:
            affect.affection = self._clamp(affect.affection + step)
            affect.attachment = self._clamp(affect.attachment + step * 0.5)
        if emotion_type in {"admiration", "pride"}:
            affect.admiration = self._clamp(affect.admiration + step)
            affect.respect = self._clamp(affect.respect + step * 0.5)
        if emotion_type in {"anger", "reproach", "resentment"}:
            affect.resentment = self._clamp(affect.resentment + step)
            affect.trust = self._clamp(affect.trust - step)
        if emotion_type in {"aversion", "disliking"}:
            affect.aversion = self._clamp(affect.aversion + step)

    def snapshot(self) -> dict:
        return {
            "emotions": dict(self.state.emotions),
            "mood_valence": self.state.mood_valence,
            "mood_arousal": self.state.mood_arousal,
            "persistent_affect": {
                entity: vars(affect).copy()
                for entity, affect in self.persistent_affect.items()
            },
        }
