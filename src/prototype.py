from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Optional

from .affective_engine import AffectiveEngine, EmotionalImpulse

# Source-derived appraisal port.
# FAtiMA Toolkit Apache-2.0, commit 56b7cbd992f953cfe21a7b12cb1a0e6cdf6ccf9f
# Assets/EmotionalAppraisal/OCCModel/OCCAffectDerivationComponent.cs
# Adaptations: normalized [-1,1]/[0,1] inputs and Matrix string IDs.


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
    attitude_intensity: float = 1.0
    confirmed: bool = True
    novelty: float = 1.0
    ambiguity: float = 0.0
    habituation_key: Optional[str] = None
    goal_probability: Optional[float] = None
    previous_goal_probability: Optional[float] = None
    goal_significance: float = 1.0
    desirability_for_other: Optional[float] = None
    other_id: Optional[str] = None


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
        desirability = max(-1.0, min(1.0, s.goal_congruence))
        ambiguity = self._clamp(s.ambiguity)
        novelty = self._clamp(s.novelty)
        habituation = self._habituation_factor(s.habituation_key)

        # Cognitiv source behavior: mood supplies appraisal bias. Matrix applies
        # it only where Understanding explicitly marks semantic ambiguity.
        if ambiguity > 0.0 and self.affect.state.mood_valence != 0.0:
            desirability = max(
                -1.0,
                min(
                    1.0,
                    desirability
                    + self.affect.state.mood_valence
                    * max(0.0, self.affect.profile.mood_bias_strength)
                    * ambiguity,
                ),
            )

        modulation = novelty * habituation
        impulses: list[EmotionalImpulse] = []
        returned_compound = False
        actor = s.actor_id
        target = s.target_id or actor

        # FAtiMA fortune-of-others branch.
        if s.desirability_for_other is not None and s.other_id and modulation > 0.0:
            other_des = max(-1.0, min(1.0, s.desirability_for_other))
            if other_des != 0.0:
                potential = (abs(other_des) + abs(desirability)) * 0.5 * modulation
                if s.other_id in {self_id, actor}:
                    etype = "joy"
                elif desirability >= 0:
                    etype = "happy-for" if other_des >= 0 else "gloating"
                else:
                    etype = "resentment" if other_des >= 0 else "pity"
                impulses.append(EmotionalImpulse(
                    etype, potential, s.id, s.other_id, "fortune-other"
                ))
                returned_compound = True

        # FAtiMA compound desirability+praiseworthiness branch.
        if s.standard_compliance is not None and desirability != 0.0 and modulation > 0.0:
            praise = max(-1.0, min(1.0, s.standard_compliance))
            if praise != 0.0:
                potential = abs(desirability + praise) * 0.5 * modulation
                if potential > 0.0:
                    is_self = not actor or actor == self_id
                    if is_self:
                        etype = "gratification" if desirability > 0 else "remorse"
                        direction = None
                    else:
                        etype = "gratitude" if desirability > 0 else "anger"
                        direction = actor
                    impulses.append(EmotionalImpulse(
                        etype, potential, s.id, direction, "compound"
                    ))
                    returned_compound = True

        # FAtiMA standalone praiseworthiness branch.
        if not returned_compound and s.standard_compliance is not None and actor:
            praise = max(-1.0, min(1.0, s.standard_compliance))
            intensity = abs(praise) * modulation
            if intensity > 0.0:
                is_self = actor == self_id
                if is_self:
                    etype = "pride" if praise >= 0 else "shame"
                    direction = None
                else:
                    etype = "admiration" if praise >= 0 else "reproach"
                    direction = actor
                impulses.append(EmotionalImpulse(
                    etype, intensity, s.id, direction, "standard"
                ))

        # FAtiMA attraction branch: OCC Love/Hate with magicFactor=0.7.
        if target and s.attitude_valence is not None:
            like = max(-1.0, min(1.0, s.attitude_valence))
            if like != 0.0:
                potential = abs(like) * 0.7 * self._clamp(s.attitude_intensity) * modulation
                impulses.append(EmotionalImpulse(
                    "love" if like >= 0 else "hate",
                    potential,
                    s.id,
                    target,
                    "attitude",
                ))

        # FAtiMA standalone well-being branch.
        if not returned_compound and relevance > 0.0 and desirability != 0.0 and modulation > 0.0:
            impulses.append(EmotionalImpulse(
                "joy" if desirability >= 0 else "distress",
                relevance * abs(desirability) * modulation,
                s.id,
                target,
                "goal",
            ))

        # FAtiMA prospect branch.
        if s.goal_probability is not None and s.previous_goal_probability is not None:
            prospect = self._appraise_goal_probability(
                self._clamp(s.goal_probability),
                self._clamp(s.previous_goal_probability),
                self._clamp(s.goal_significance),
            )
            if prospect is not None:
                etype, potential = prospect
                impulses.append(EmotionalImpulse(
                    etype, potential * modulation, s.id, target, "prospect"
                ))
        elif relevance > 0.0 and not s.confirmed and desirability != 0.0:
            # Temporary compatibility until Matrix-NLU emits likelihood deltas.
            impulses.append(EmotionalImpulse(
                "hope" if desirability > 0 else "fear",
                relevance * abs(desirability) * modulation,
                s.id,
                target,
                "prospect",
            ))

        return AppraisalResult(
            s.id,
            relevance,
            desirability,
            s.actor_id,
            novelty,
            habituation,
            tuple(impulses),
        )

    @staticmethod
    def _appraise_goal_probability(
        probability: float, previous: float, significance: float
    ) -> Optional[tuple[str, float]]:
        if previous == probability:
            return ("hope", 0.0)
        if probability > previous:
            if probability == 1.0:
                if previous <= 0.5:
                    return ("relief", probability * significance)
                return ("satisfaction", probability * significance)
            return ("hope", probability * significance)
        if probability == 0.0:
            if previous >= 0.5:
                return ("disappointment", significance)
            return ("fears-confirmed", significance)
        return ("fear", (1.0 - probability) * significance)

    def _habituation_factor(self, key: Optional[str]) -> float:
        # Matrix extension, isolated from source-derived OCC logic.
        if not key:
            return 1.0
        count = self._habituation_counts.get(key, 0)
        self._habituation_counts[key] = count + 1
        return max(0.2, math.exp(-0.35 * count))

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))
