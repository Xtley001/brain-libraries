"""
Analyst Revision Dispersion Strategy Sub-System.
Academic Reference: Diether, Malloy, & Scherbina (2002) - Differences of Opinion and Cross-Sectional Stock Returns.
"""
from __future__ import annotations

from brain_sentiment.templates import SentimentCandidate
from brain_sentiment.strategies.base import BaseSentimentStrategy, SentimentStrategyMetadata


class AnalystRevisionDispersionStrategy(BaseSentimentStrategy):
    @property
    def metadata(self) -> SentimentStrategyMetadata:
        return SentimentStrategyMetadata(
            strategy_id="analyst_revision_dispersion",
            display_name="Analyst Forecast Dispersion Anomaly",
            theory_summary="High forecast dispersion reflects short-sale-constrained overvaluation; shorting captures reversion.",
            academic_references=[
                "Diether, Malloy & Scherbina (2002) - Differences of Opinion and Cross-Sectional Stock Returns",
            ],
            preferred_decays=[10, 12, 15],
        )

    def get_fields(self) -> list[str]:
        return ["snt1_d1_dtstsespe", "close"]

    def generate_candidates(self) -> list[SentimentCandidate]:
        candidates = []
        for u in self.metadata.preferred_universes:
            for g in self.metadata.preferred_neutralizations:
                for d in self.metadata.preferred_decays:
                    candidates.append(SentimentCandidate(
                        expression=f"trade_when(volume > adv20 * 0.8, group_neutralize(rank(-ts_decay_linear(ts_decay_linear(snt1_d1_dtstsespe / (close + 0.001), {d}), 3)) * rank(ts_decay_linear(ts_decay_linear(snt1_d1_netearningsrevision, {d}), 3)), {g.lower()}), -1)",
                        archetype=self.strategy_id,
                        family="Dispersion_Overvaluation",
                        hypothesis=f"Shorting high dispersion of EPS estimates interacted with upward earnings revision momentum with double decay ({d}d, 3d) yields alpha with turnover < 12%.",
                        universe=u,
                        neutralization=g,
                        decay=d,
                    ))
        return candidates
