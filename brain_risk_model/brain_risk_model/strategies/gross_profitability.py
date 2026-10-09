"""
Gross Profitability Strategy Sub-System.
Academic Reference: Novy-Marx (2013) - The Other Side of Value: The Gross Profitability Premium.
"""
from __future__ import annotations

from brain_risk_model.templates import RiskModelCandidate
from brain_risk_model.strategies.base import BaseRiskStrategy, RiskStrategyMetadata


class GrossProfitabilityStrategy(BaseRiskStrategy):
    @property
    def metadata(self) -> RiskStrategyMetadata:
        return RiskStrategyMetadata(
            strategy_id="gross_profitability",
            display_name="Gross Profitability & Certainty Tilt",
            theory_summary="Operating profitability generates substantial alpha orthogonal to valuation and momentum.",
            academic_references=[
                "Novy-Marx (2013) - The Other Side of Value: The Gross Profitability Premium",
            ],
            preferred_decays=[10, 15, 20],
        )

    def get_fields(self) -> list[str]:
        return ["fscore_bfl_profitability", "earnings_certainty_rank_derivative"]

    def generate_candidates(self) -> list[RiskModelCandidate]:
        candidates = []
        for u in self.metadata.preferred_universes:
            for g in self.metadata.preferred_neutralizations:
                for d in self.metadata.preferred_decays:
                    candidates.append(RiskModelCandidate(
                        expression=f"group_neutralize(rank(0.50 * rank(ts_decay_linear(ts_decay_linear(fscore_bfl_profitability, {d}), 3)) + 0.50 * rank(ts_decay_linear(ts_decay_linear(earnings_certainty_rank_derivative, {d}), 3))), {g.lower()})",
                        archetype=self.strategy_id,
                        family="Novy_Marx_Profitability",
                        hypothesis=f"Operating profitability blended with earnings certainty derivative with double decay ({d}d, 3d) captures robust cash earnings.",
                        universe=u,
                        neutralization=g,
                        decay=d,
                    ))
        return candidates
