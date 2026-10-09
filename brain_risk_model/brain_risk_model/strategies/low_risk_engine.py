"""
Composite Low-Risk Engine Strategy Sub-System.
Academic Reference: Baker, Bradley, & Wurgler (2011), Blitz & van Vliet (2007).
"""
from __future__ import annotations

from brain_risk_model.templates import RiskModelCandidate
from brain_risk_model.strategies.base import BaseRiskStrategy, RiskStrategyMetadata


class LowRiskEngineStrategy(BaseRiskStrategy):
    @property
    def metadata(self) -> RiskStrategyMetadata:
        return RiskStrategyMetadata(
            strategy_id="low_risk_engine",
            display_name="Composite Low-Risk Multi-Factor",
            theory_summary="Fuses rolling market beta with SPY correlation into an institutional low-risk alpha engine.",
            academic_references=[
                "Baker, Bradley & Wurgler (2011) - Benchmarks as Limits to Arbitrage: The Low-Volatility Anomaly",
                "Blitz & van Vliet (2007) - The Volatility Effect",
            ],
            preferred_decays=[10, 15, 20],
        )

    def get_fields(self) -> list[str]:
        return ["beta_last_60_days_spy", "correlation_last_60_days_spy"]

    def generate_candidates(self) -> list[RiskModelCandidate]:
        candidates = []
        for u in self.metadata.preferred_universes:
            for g in self.metadata.preferred_neutralizations:
                for d in self.metadata.preferred_decays:
                    candidates.append(RiskModelCandidate(
                        expression=f"group_neutralize(rank(-0.60 * rank(ts_decay_linear(ts_decay_linear(beta_last_60_days_spy, {d}), 3)) - 0.40 * rank(ts_decay_linear(ts_decay_linear(correlation_last_60_days_spy, {d}), 3))), {g.lower()})",
                        archetype=self.strategy_id,
                        family="Low_Risk_Multi_Factor",
                        hypothesis=f"60% low-beta and 40% low-correlation with double decay ({d}d, 3d) eliminates single-factor fragility.",
                        universe=u,
                        neutralization=g,
                        decay=d,
                    ))
        return candidates
