from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Optional

from .affective_engine import AffectiveEngine, EmotionalImpulse


@dataclass(frozen=True)
class AffectiveStimulus:
    id: str
    category: str
    actor_id: Optional[str] = None
    target_id: Optional[str] = None
    goal_relevance: float = 0.0
    goal_congruence: float = 0.0
    standard_compliance: Optional[float] = None
    attitude_valence: Optional[float] = None
    attitude_intensity: float = 0.0
    confirmed: bool = True
    novelty: float = 1.0
    ambiguity: float = 0.0
    habituation_key: Optional[str] = None


@dataclass(frozen=True)
class AppraisalResult:
    stimulus_id: str
    relevance: float
    congruence: float
    agency: Optional[str]
    novelty: float
    habituation_factor: float
    impulses: tuple[EmotionalImpulse, ...] = ()


@dataclass(frozen=True)
class AffectiveTrace:
    stimulus: AffectiveStimulus
    appraisal: AppraisalResult
    before: dict
    after: dict


class MatrixAffectivePrototype:
    def __init__(self, affect: AffectiveEngine | None = None):
        self.affect = affect or AffectiveEngine()
        self._habituation_counts: dict[str, int] = {}

    def process(self, stimulus: AffectiveStimulus, self_id: str = "self") -> AffectiveTrace:
        before = self.affect.snapshot()
        appraisal = self._appraise(stimulus, self_id)
        for impulse in appraisal.impulses:
            self.affect.apply_impulse(impulse)
        return AffectiveTrace(stimulus, appraisal, before, self.affect.snapshot())

    def process_many(self, stimuli: Iterable[AffectiveStimulus], self_id: str = "self") -> list[AffectiveTrace]:
        return [self.process(s, self_id) for s in stimuli]

    def decay(self, delta_time: float) -> dict:
        self.affect.decay(delta_time)
        return self.affect.snapshot()

    def _appraise(self, s: AffectiveStimulus, self_id: str) -> AppraisalResult:
        relevance = self._clamp(s.goal_relevance)
        congruence = max(-1.0, min(1.0, s.goal_congruence))
        ambiguity = self._clamp(s.ambiguity)
        novelty = self._clamp(s.novelty)
        habituation = self._habituation_factor(s.habituation_key)

        # Cognitiv/Affect-Infusion style mood bias: only ambiguous appraisals are
        # biased. Explicit semantic evidence (ambiguity=0) is never overridden.
        if ambiguity > 0.0 and self.affect.state.mood_valence != 0.0:
            bias = (
                self.affect.state.mood_valence
                * max(0.0, self.affect.profile.mood_bias_strength)
                * ambiguity
            )
            congruence = max(-1.0, min(1.0, congruence + bias))

        impulses: list[EmotionalImpulse] = []
        modulation = novelty * habituation

        if relevance > 0.0 and congruence != 0.0 and modulation > 0.0:
            intensity = min(1.0, relevance * abs(congruence) * modulation)
            if congruence > 0:
                emotion = "joy" if s.confirmed else "hope"
            else:
                emotion = "distress" if s.confirmed else "fear"
            impulses.append(EmotionalImpulse(
                emotion, intensity, s.id, s.actor_id or s.target_id, "goal"
            ))

        if s.category == "action" and s.actor_id and s.standard_compliance is not None:
            compliance = max(-1.0, min(1.0, s.standard_compliance))
            intensity = abs(compliance) * modulation
            if intensity > 0.0:
                is_self = s.actor_id == self_id
                if compliance > 0:
                    emotion = "pride" if is_self else "admiration"
                else:
                    emotion = "shame" if is_self else "reproach"
                impulses.append(EmotionalImpulse(
                    emotion,
                    intensity,
                    s.id,
                    None if is_self else s.actor_id,
                    "standard",
                ))

        target = s.target_id or s.actor_id
        if target and s.attitude_valence is not None:
            valence = max(-1.0, min(1.0, s.attitude_valence))
            intensity = abs(valence) * self._clamp(s.attitude_intensity) * modulation
            if intensity > 0.0:
                impulses.append(EmotionalImpulse(
                    "liking" if valence > 0 else "disliking",
                    intensity,
                    s.id,
                    target,
                    "attitude",
                ))

        return AppraisalResult(
            s.id,
            relevance,
            congruence,
            s.actor_id,
            novelty,
            habituation,
            tuple(impulses),
        )

    def _habituation_factor(self, key: Optional[str]) -> float:
        if not key:
            return 1.0
        count = self._habituation_counts.get(key, 0)
        self._habituation_counts[key] = count + 1
        # Standard exponential habituation curve with a non-zero floor.
        return max(0.2, math.exp(-0.35 * count))

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))
