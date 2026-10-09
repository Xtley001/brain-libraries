"""
Quality Surface Acceleration Strategy Sub-System.
Academic Reference: Piotroski (2000) - Value Investing (F-Score).
"""
from __future__ import annotations

from brain_risk_model.templates import RiskModelCandidate
from brain_risk_model.strategies.base import BaseRiskStrategy, RiskStrategyMetadata


class SurfaceAccelerationStrategy(BaseRiskStrategy):
    @property
    def metadata(self) -> RiskStrategyMetadata:
        return RiskStrategyMetadata(
            strategy_id="surface_acceleration",
            display_name="Quality Surface Acceleration (F-Score)",
            theory_summary="Tracking the second derivative / acceleration of accounting quality isolates rapid turnarounds.",
            academic_references=[
                "Piotroski (2000) - Value Investing: The Use of Historical Financial Statement Information",
            ],
            preferred_decays=[10, 15, 20],
        )

    def get_fields(self) -> list[str]:
        return ["fscore_surface_accel", "fscore_bfl_quality"]

    def generate_candidates(self) -> list[RiskModelCandidate]:
        candidates = []
        for u in self.metadata.preferred_universes:
            for g in self.metadata.preferred_neutralizations:
                for d in self.metadata.preferred_decays:
                    candidates.append(RiskModelCandidate(
                        expression=f"group_neutralize(rank(0.60 * rank(ts_decay_linear(ts_decay_linear(fscore_surface_accel, {d}), 3)) + 0.40 * rank(ts_decay_linear(ts_decay_linear(fscore_bfl_quality, {d}), 3))), {g.lower()})",
                        archetype=self.strategy_id,
                        family="Piotroski_Surface_Acceleration",
                        hypothesis=f"Quality acceleration combined with quality baseline with double decay ({d}d, 3d) captures turnaround momentum.",
                        universe=u,
                        neutralization=g,
                        decay=d,
                    ))
        return candidates
