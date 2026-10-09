"""
Dual Target and Recommendation Confluence Strategy Sub-System.
Academic Reference: Asquith, Mikhail, & Au (2005), Loh & Stulz (2018).
"""
from __future__ import annotations

from brain_sentiment.templates import SentimentCandidate
from brain_sentiment.strategies.base import BaseSentimentStrategy, SentimentStrategyMetadata


class DualTargetRecConfluenceStrategy(BaseSentimentStrategy):
    @property
    def metadata(self) -> SentimentStrategyMetadata:
        return SentimentStrategyMetadata(
            strategy_id="dual_target_rec_confluence",
            display_name="Dual Recommendation & Target Alignment",
            theory_summary="Confluence of both target price upgrades and recommendation changes doubles return predictability.",
            academic_references=[
                "Asquith, Mikhail & Au (2005) - Information Content of Equity Analyst Reports",
                "Loh & Stulz (2018) - Is Sell-Side Research More Valuable in Bad Times?",
            ],
            preferred_decays=[10, 12, 15],
        )

    def get_fields(self) -> list[str]:
        return ["snt1_d1_nettargetpercent", "snt1_d1_netrecpercent"]

    def generate_candidates(self) -> list[SentimentCandidate]:
        candidates = []
        for u in self.metadata.preferred_universes:
            for g in self.metadata.preferred_neutralizations:
                for d in self.metadata.preferred_decays:
                    candidates.append(SentimentCandidate(
                        expression=f"group_neutralize(rank(0.55 * rank(ts_decay_linear(ts_decay_linear(snt1_d1_nettargetpercent, {d}), 3)) + 0.45 * rank(ts_decay_linear(ts_decay_linear(snt1_d1_netrecpercent, {d}), 3))), {g.lower()})",
                        archetype=self.strategy_id,
                        family="Dual_Target_Rec_Alignment",
                        hypothesis=f"Confluence of target revisions and recommendation changes with double decay ({d}d, 3d) confirms persistent consensus upgrade.",
                        universe=u,
                        neutralization=g,
                        decay=d,
                    ))
        return candidates
