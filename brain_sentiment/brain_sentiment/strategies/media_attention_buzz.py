"""
Media Attention Buzz Strategy Sub-System.
Academic Reference: Da, Engelberg, & Gao (2011), Barber & Odean (2008), Tetlock (2007).
"""
from __future__ import annotations

from brain_sentiment.templates import SentimentCandidate
from brain_sentiment.strategies.base import BaseSentimentStrategy, SentimentStrategyMetadata


class MediaAttentionBuzzStrategy(BaseSentimentStrategy):
    @property
    def metadata(self) -> SentimentStrategyMetadata:
        return SentimentStrategyMetadata(
            strategy_id="media_attention_buzz",
            display_name="Media Attention & Focus Drift",
            theory_summary="Volume-confirmed analyst focus reflects informed attention, while unconfirmed noise fades.",
            academic_references=[
                "Da, Engelberg & Gao (2011) - In Search of Attention",
                "Barber & Odean (2008) - All That Glitters: Attention and Investor Buying Behavior",
            ],
            preferred_decays=[10, 15],
        )

    def get_fields(self) -> list[str]:
        return ["snt1_d1_dynamicfocusrank", "volume", "adv20"]

    def generate_candidates(self) -> list[SentimentCandidate]:
        candidates = []
        for u in self.metadata.preferred_universes:
            for g in self.metadata.preferred_neutralizations:
                for d in self.metadata.preferred_decays:
                    candidates.append(SentimentCandidate(
                        expression=f"trade_when(volume > adv20 * 0.85, group_neutralize(rank(ts_decay_linear(ts_decay_linear(snt1_d1_dynamicfocusrank, {d}), 3)), {g.lower()}), -1)",
                        archetype=self.strategy_id,
                        family="Dynamic_Analyst_Focus",
                        hypothesis=f"Volume-gated dynamic analyst focus with double decay ({d}d, 3d) captures persistent informed attention.",
                        universe=u,
                        neutralization=g,
                        decay=d,
                    ))
        return candidates
