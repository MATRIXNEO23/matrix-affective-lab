from __future__ import annotations

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
    novelty: float = 0.0


@dataclass(frozen=True)
class AppraisalResult:
    stimulus_id: str
    relevance: float
    congruence: float
    agency: Optional[str]
    novelty: float
    impulses: tuple[EmotionalImpulse, ...] = ()


@dataclass(frozen=True)
class AffectiveTrace:
    stimulus: AffectiveStimulus
    appraisal: AppraisalResult
    before: dict
    after: dict


class MatrixAffectivePrototype:
    """Compact end-to-end affective prototype.

    Uses the reduced OCC split already present in FAtiMA/Cognitiv:
    event->goal, action->standard, entity->attitude. Matrix keeps one public
    operation while the affect state remains isolated and testable.
    """

    def __init__(self, affect: AffectiveEngine | None = None):
        self.affect = affect or AffectiveEngine()

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
        impulses: list[EmotionalImpulse] = []

        # OCC event -> goal consequence.
        if relevance > 0.0 and congruence != 0.0:
            intensity = min(1.0, relevance * abs(congruence))
            emotion = (
                "joy" if s.confirmed else "hope"
                if congruence > 0 else
                "distress" if s.confirmed else "fear"
            )
            impulses.append(EmotionalImpulse(emotion, intensity, s.id, s.actor_id or s.target_id))

        # OCC action -> standard appraisal.
        if s.category == "action" and s.actor_id and s.standard_compliance is not None:
            compliance = max(-1.0, min(1.0, s.standard_compliance))
            if compliance != 0.0:
                is_self = s.actor_id == self_id
                emotion = (
                    ("pride" if is_self else "admiration")
                    if compliance > 0 else
                    ("shame" if is_self else "reproach")
                )
                impulses.append(EmotionalImpulse(
                    emotion, abs(compliance), s.id, None if is_self else s.actor_id
                ))

        # OCC entity -> attitude appraisal. Kept structured: Understanding/App
        # supplies attitude evidence; this engine never infers it from text.
        target = s.target_id or s.actor_id
        if target and s.attitude_valence is not None:
            valence = max(-1.0, min(1.0, s.attitude_valence))
            strength = self._clamp(s.attitude_intensity)
            intensity = abs(valence) * strength
            if intensity > 0.0:
                impulses.append(EmotionalImpulse(
                    "liking" if valence > 0 else "disliking",
                    intensity,
                    s.id,
                    target,
                ))

        return AppraisalResult(
            s.id, relevance, congruence, s.actor_id, self._clamp(s.novelty), tuple(impulses)
        )

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))
