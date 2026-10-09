"""
Beta Horizon Divergence Strategy Sub-System.
Academic Reference: Black (1972), Baker, Bradley, & Wurgler (2011).
"""
from __future__ import annotations

from brain_risk_model.templates import RiskModelCandidate
from brain_risk_model.strategies.base import BaseRiskStrategy, RiskStrategyMetadata


class BetaDivergenceStrategy(BaseRiskStrategy):
    @property
    def metadata(self) -> RiskStrategyMetadata:
        return RiskStrategyMetadata(
            strategy_id="beta_divergence",
            display_name="Multi-Horizon Beta Divergence",
            theory_summary="Spreads between short-horizon (30d) and long-horizon (360d) betas capture transient leverage shocks.",
            academic_references=[
                "Black (1972) - Capital Market Equilibrium with Restricted Borrowing",
                "Baker, Bradley & Wurgler (2011) - Benchmarks as Limits to Arbitrage",
            ],
            preferred_decays=[10, 12, 15],
        )

    def get_fields(self) -> list[str]:
        return ["beta_last_30_days_spy", "beta_last_360_days_spy"]

    def generate_candidates(self) -> list[RiskModelCandidate]:
        candidates = []
        for u in self.metadata.preferred_universes:
            for g in self.metadata.preferred_neutralizations:
                for d in self.metadata.preferred_decays:
                    candidates.append(RiskModelCandidate(
                        expression=f"group_neutralize(rank(-ts_decay_linear(ts_decay_linear(beta_last_30_days_spy - beta_last_360_days_spy, {d}), 3)), {g.lower()})",
                        archetype=self.strategy_id,
                        family="Beta_Horizon_Spread",
                        hypothesis=f"Transient beta spikes over 360d equilibrium revert systematically with double decay ({d}d, 3d).",
                        universe=u,
                        neutralization=g,
                        decay=d,
                    ))
        return candidates
