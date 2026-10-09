"""
Betting Against Beta (BAB) Strategy Sub-System.
Academic Reference: Frazzini & Pedersen (2014) - Betting Against Beta, Journal of Financial Economics.
"""
from __future__ import annotations

from brain_risk_model.templates import RiskModelCandidate
from brain_risk_model.strategies.base import BaseRiskStrategy, RiskStrategyMetadata


class BettingAgainstBetaStrategy(BaseRiskStrategy):
    @property
    def metadata(self) -> RiskStrategyMetadata:
        return RiskStrategyMetadata(
            strategy_id="betting_against_beta",
            display_name="Betting Against Beta (BAB)",
            theory_summary="Borrowing-constrained investors bid up high beta, leaving low-beta securities systematically underpriced.",
            academic_references=[
                "Frazzini & Pedersen (2014) - Betting Against Beta",
                "Black (1972) - Capital Market Equilibrium with Restricted Borrowing",
            ],
            preferred_decays=[10, 12, 15, 20],
        )

    def get_fields(self) -> list[str]:
        return ["beta_last_60_days_spy", "beta_last_90_days_spy"]

    def generate_candidates(self) -> list[RiskModelCandidate]:
        candidates = []
        for u in self.metadata.preferred_universes:
            for g in self.metadata.preferred_neutralizations:
                for d in self.metadata.preferred_decays:
                    candidates.append(RiskModelCandidate(
                        expression=f"group_neutralize(rank(-ts_decay_linear(ts_decay_linear(beta_last_60_days_spy, {d}), 3)), {g.lower()})",
                        archetype=self.strategy_id,
                        family="BAB_60D_Spy",
                        hypothesis=f"Shorting 60d SPY beta with double decay ({d}d, 3d) captures the leverage constraint risk premium with turnover < 12%.",
                        universe=u,
                        neutralization=g,
                        decay=d,
                    ))
                    candidates.append(RiskModelCandidate(
                        expression=f"group_neutralize(rank(-ts_decay_linear(ts_decay_linear(beta_last_90_days_spy, {d}), 3)), {g.lower()})",
                        archetype=self.strategy_id,
                        family="BAB_90D_Spy",
                        hypothesis=f"Shorting 90d SPY beta with double decay ({d}d, 3d) isolates structural medium-term mispricing.",
                        universe=u,
                        neutralization=g,
                        decay=d,
                    ))
        return candidates
