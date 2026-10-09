"""
Net Target Price Revisions Strategy Sub-System.
Academic Reference: Brav & Lehavy (2003), Asquith, Mikhail, & Au (2005).
"""
from __future__ import annotations

from brain_sentiment.templates import SentimentCandidate
from brain_sentiment.strategies.base import BaseSentimentStrategy, SentimentStrategyMetadata


class NetTargetPriceRevisionsStrategy(BaseSentimentStrategy):
    @property
    def metadata(self) -> SentimentStrategyMetadata:
        return SentimentStrategyMetadata(
            strategy_id="net_target_price_revisions",
            display_name="Net Target Price Revision Drift",
            theory_summary="Target price revisions provide valuation information orthogonal to earnings surprises.",
            academic_references=[
                "Brav & Lehavy (2003) - An Empirical Analysis of Target Price Revisions",
                "Asquith, Mikhail & Au (2005) - Information Content of Equity Analyst Reports",
            ],
            preferred_decays=[10, 12, 15],
        )

    def get_fields(self) -> list[str]:
        return ["snt1_d1_uptargetpercent", "snt1_d1_downtargetpercent", "snt1_d1_nettargetpercent"]

    def generate_candidates(self) -> list[SentimentCandidate]:
        candidates = []
        for u in self.metadata.preferred_universes:
            for g in self.metadata.preferred_neutralizations:
                for d in self.metadata.preferred_decays:
                    candidates.append(SentimentCandidate(
                        expression=f"group_neutralize(rank(ts_decay_linear(ts_decay_linear(snt1_d1_uptargetpercent - snt1_d1_downtargetpercent, {d}), 3)), {g.lower()})",
                        archetype=self.strategy_id,
                        family="Target_Spread_Drift",
                        hypothesis=f"Spread between upward and downward target price revisions with double decay ({d}d, 3d) captures valuation multiple re-ratings with turnover < 12%.",
                        universe=u,
                        neutralization=g,
                        decay=d,
                    ))
        return candidates
