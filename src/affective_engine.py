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
    """Lab prototype combining selected FAtiMA and Cognitiv mechanics.

    FAtiMA-inspired: per-emotion disposition, cause-aware reappraisal.
    Cognitiv-inspired: saturating integration, half-life decay, slow mood.
    Matrix-owned: entity-scoped persistent affect and hard separation from
    canonical relationship state.
    """

    POSITIVE = {"joy", "hope", "relief", "admiration", "pride", "affection", "liking"}
    NEGATIVE = {"distress", "fear", "anger", "reproach", "shame", "resentment", "aversion", "disliking"}
    HIGH_AROUSAL = {"anger", "fear", "joy", "distress", "surprise"}

    def __init__(self, dispositions: Optional[Dict[str, EmotionDisposition]] = None):
        self.state = EmotionState()
        self.dispositions = dispositions or {}
        self.persistent_affect: Dict[str, PersistentAffect] = {}
        self._cause_index: Dict[tuple[str, str, Optional[str]], float] = {}

    def disposition(self, emotion_type: str) -> EmotionDisposition:
        return self.dispositions.get(emotion_type, EmotionDisposition())

    def apply_impulse(self, impulse: EmotionalImpulse) -> bool:
        intensity = max(0.0, min(1.0, impulse.intensity))
        disp = self.disposition(impulse.emotion_type)
        if intensity <= disp.threshold:
            return False

        key = (impulse.cause_id, impulse.emotion_type, impulse.target_id)
        previous_from_cause = self._cause_index.get(key, 0.0)
        current = self.state.emotions.get(impulse.emotion_type, 0.0)

        # Reappraisal replaces the contribution from the same cause instead of
        # blindly stacking it again.
        base = max(0.0, current - previous_from_cause)
        integrated = base + intensity * (1.0 - base)
        self.state.emotions[impulse.emotion_type] = min(1.0, integrated)
        self._cause_index[key] = intensity

        self._update_mood()
        if impulse.target_id:
            self._update_persistent_affect(impulse.target_id, impulse.emotion_type, intensity)
        return True

    def decay(self, delta_time: float) -> None:
        if delta_time <= 0:
            return
        dead = []
        for emotion_type, intensity in self.state.emotions.items():
            half_life = max(0.01, self.disposition(emotion_type).half_life)
            lam = math.log(2.0) / half_life
            value = intensity * math.exp(-lam * delta_time)
            if value < 0.01:
                dead.append(emotion_type)
            else:
                self.state.emotions[emotion_type] = value
        for emotion_type in dead:
            del self.state.emotions[emotion_type]
        self._update_mood()

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
        # Mood deliberately moves slower than immediate emotion.
        self.state.mood_valence += (valence - self.state.mood_valence) * 0.10
        self.state.mood_arousal += (arousal - self.state.mood_arousal) * 0.05

    def _update_persistent_affect(self, entity_id: str, emotion_type: str, intensity: float) -> None:
        affect = self.persistent_affect.setdefault(entity_id, PersistentAffect())
        # Deliberately slow deltas: persistent affect must move much more slowly
        # than immediate emotion. Mapping is provisional and lab-only.
        step = intensity * 0.05
        if emotion_type in {"joy", "relief", "affection", "liking"}:
            affect.affection = min(1.0, affect.affection + step)
            affect.attachment = min(1.0, affect.attachment + step * 0.5)
        if emotion_type in {"admiration", "pride"}:
            affect.admiration = min(1.0, affect.admiration + step)
            affect.respect = min(1.0, affect.respect + step * 0.5)
        if emotion_type in {"anger", "reproach", "resentment"}:
            affect.resentment = min(1.0, affect.resentment + step)
            affect.trust = max(0.0, affect.trust - step)
        if emotion_type in {"aversion", "disliking"}:
            affect.aversion = min(1.0, affect.aversion + step)

    def snapshot(self) -> dict:
        return {
            "emotions": dict(self.state.emotions),
            "mood_valence": self.state.mood_valence,
            "mood_arousal": self.state.mood_arousal,
            "persistent_affect": {
                entity: vars(affect).copy() for entity, affect in self.persistent_affect.items()
            },
        }
