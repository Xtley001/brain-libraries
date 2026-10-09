"""
Blitz Low-Volatility Strategy Sub-System.
Academic Reference: Blitz & van Vliet (2007) - The Volatility Effect: Lower Risk Without Lower Return.
"""
from __future__ import annotations

from brain_risk_model.templates import RiskModelCandidate
from brain_risk_model.strategies.base import BaseRiskStrategy, RiskStrategyMetadata


class BlitzVolatilityStrategy(BaseRiskStrategy):
    @property
    def metadata(self) -> RiskStrategyMetadata:
        return RiskStrategyMetadata(
            strategy_id="blitz_volatility",
            display_name="Blitz Low-Volatility & Earnings Certainty",
            theory_summary="Low-beta equities with high earnings certainty yield superior risk-adjusted alpha.",
            academic_references=[
                "Blitz & van Vliet (2007) - The Volatility Effect: Lower Risk Without Lower Return",
            ],
            preferred_decays=[10, 15, 20],
        )

    def get_fields(self) -> list[str]:
        return ["beta_last_60_days_spy", "earnings_certainty_rank_derivative"]

    def generate_candidates(self) -> list[RiskModelCandidate]:
        candidates = []
        for u in self.metadata.preferred_universes:
            for g in self.metadata.preferred_neutralizations:
                for d in self.metadata.preferred_decays:
                    candidates.append(RiskModelCandidate(
                        expression=f"group_neutralize(rank(0.55 * rank(ts_decay_linear(ts_decay_linear(earnings_certainty_rank_derivative, {d}), 3)) - 0.45 * rank(ts_decay_linear(ts_decay_linear(beta_last_60_days_spy, {d}), 3))), {g.lower()})",
                        archetype=self.strategy_id,
                        family="Blitz_Volatility_Certainty",
                        hypothesis=f"Long earnings certainty and short SPY beta with double decay ({d}d, 3d) maximizes portfolio Sharpe ratio.",
                        universe=u,
                        neutralization=g,
                        decay=d,
                    ))
        return candidates
