"""
PEAD Earnings Drift Strategy Sub-System.
Academic Reference: Bernard & Thomas (1989, 1990), Chan, Jegadeesh, & Lakonishok (1996).
"""
from __future__ import annotations

from typing import List
from brain_sentiment.templates import SentimentCandidate
from brain_sentiment.strategies.base import BaseSentimentStrategy, SentimentStrategyMetadata


class PEADEarningsDriftStrategy(BaseSentimentStrategy):
    @property
    def metadata(self) -> SentimentStrategyMetadata:
        return SentimentStrategyMetadata(
            strategy_id="pead_earnings_drift",
            display_name="Post-Earnings Announcement Drift (PEAD)",
            theory_summary="Sluggish analyst earnings estimate revisions create multi-month persistent price drift.",
            academic_references=[
                "Bernard & Thomas (1989) - Post-Earnings-Announcement Drift",
                "Chan, Jegadeesh & Lakonishok (1996) - Momentum Strategies & PEAD",
            ],
            preferred_decays=[10, 12, 15, 20],
        )

    def get_fields(self) -> list[str]:
        return ["snt1_d1_netearningsrevision", "snt1_d1_earningssurprise"]

    def generate_candidates(self) -> list[SentimentCandidate]:
        candidates = []
        for u in self.metadata.preferred_universes:
            for g in self.metadata.preferred_neutralizations:
                for d in self.metadata.preferred_decays:
                    # Pure double-decay revision drift
                    candidates.append(SentimentCandidate(
                        expression=f"group_neutralize(rank(ts_decay_linear(ts_decay_linear(snt1_d1_netearningsrevision, {d}), 3)), {g.lower()})",
                        archetype=self.strategy_id,
                        family="PEAD_Revision_Drift",
                        hypothesis=f"Double-decay ({d}d, 3d) net earnings revisions eliminate turnover spikes while isolating PEAD drift.",
                        universe=u,
                        neutralization=g,
                        decay=d,
                    ))
                    # High conviction shock with double decay
                    candidates.append(SentimentCandidate(
                        expression=f"trade_when(abs(snt1_d1_earningssurprise) > 0.05, group_neutralize(rank(ts_decay_linear(ts_decay_linear(snt1_d1_earningssurprise, {d}), 3)), {g.lower()}), -1)",
                        archetype=self.strategy_id,
                        family="PEAD_SUE_Shock",
                        hypothesis=f"Material SUE surprise shocks (>5%) held with double decay ({d}d, 3d) isolate fundamental drift.",
                        universe=u,
                        neutralization=g,
                        decay=d,
                    ))
        return candidates
