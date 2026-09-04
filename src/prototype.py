from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .affective_engine import AffectiveEngine
from .appraisal import AffectiveStimulus, AppraisalEngine, AppraisalResult


@dataclass(frozen=True)
class AffectiveTrace:
    stimulus: AffectiveStimulus
    appraisal: AppraisalResult
    before: dict
    after: dict


class MatrixAffectivePrototype:
    """End-to-end lab prototype: structured stimulus -> appraisal -> affect.

    This intentionally starts after Understanding/Matrix-NLU. It never parses
    free text, never changes canonical relationship state, and never writes
    memory. Those boundaries are deliberate.
    """

    def __init__(self, appraisal: AppraisalEngine | None = None, affect: AffectiveEngine | None = None):
        self.appraisal = appraisal or AppraisalEngine()
        self.affect = affect or AffectiveEngine()

    def process(self, stimulus: AffectiveStimulus, self_id: str = "self") -> AffectiveTrace:
        before = self.affect.snapshot()
        appraisal = self.appraisal.appraise(stimulus, self_id=self_id)
        for impulse in appraisal.impulses:
            self.affect.apply_impulse(impulse)
        after = self.affect.snapshot()
        return AffectiveTrace(stimulus, appraisal, before, after)

    def process_many(self, stimuli: Iterable[AffectiveStimulus], self_id: str = "self") -> list[AffectiveTrace]:
        return [self.process(s, self_id=self_id) for s in stimuli]

    def decay(self, delta_time: float) -> dict:
        self.affect.decay(delta_time)
        return self.affect.snapshot()
