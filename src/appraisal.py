from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .affective_engine import EmotionalImpulse


@dataclass(frozen=True)
class AffectiveStimulus:
    id: str
    category: str
    actor_id: Optional[str] = None
    target_id: Optional[str] = None
    goal_relevance: float = 0.0
    goal_congruence: float = 0.0
    standard_compliance: Optional[float] = None
    confirmed: bool = True
    novelty: float = 0.0


@dataclass(frozen=True)
class AppraisalResult:
    stimulus_id: str
    relevance: float
    congruence: float
    agency: Optional[str]
    novelty: float
    impulses: tuple[EmotionalImpulse, ...] = field(default_factory=tuple)


class AppraisalEngine:
    """Deterministic reduced-OCC appraisal prototype.

    It consumes structured signals only; it does not parse free text and does
    not call an LLM. Understanding remains the responsibility of Matrix-NLU.
    """

    def appraise(self, stimulus: AffectiveStimulus, self_id: str = "self") -> AppraisalResult:
        r = self._clamp(stimulus.goal_relevance)
        c = max(-1.0, min(1.0, stimulus.goal_congruence))
        impulses = []

        if r > 0.0 and abs(c) > 0.0:
            intensity = min(1.0, r * abs(c))
            if c > 0:
                emotion = "joy" if stimulus.confirmed else "hope"
            else:
                emotion = "distress" if stimulus.confirmed else "fear"
            impulses.append(EmotionalImpulse(emotion, intensity, stimulus.id, stimulus.actor_id or stimulus.target_id))

        if stimulus.category == "action" and stimulus.actor_id and stimulus.standard_compliance is not None:
            compliance = max(-1.0, min(1.0, stimulus.standard_compliance))
            if abs(compliance) > 0.0:
                is_self = stimulus.actor_id == self_id
                if compliance > 0:
                    emotion = "pride" if is_self else "admiration"
                else:
                    emotion = "shame" if is_self else "reproach"
                impulses.append(EmotionalImpulse(emotion, abs(compliance), stimulus.id, None if is_self else stimulus.actor_id))

        return AppraisalResult(stimulus.id, r, c, stimulus.actor_id, self._clamp(stimulus.novelty), tuple(impulses))

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))
