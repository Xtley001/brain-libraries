"""
Extreme Sentiment Reversal Strategy Sub-System.
Academic Reference: Baker & Wurgler (2006, 2007), Tetlock (2007).
"""
from __future__ import annotations

from brain_sentiment.templates import SentimentCandidate
from brain_sentiment.strategies.base import BaseSentimentStrategy, SentimentStrategyMetadata


class ExtremeSentimentReversalStrategy(BaseSentimentStrategy):
    @property
    def metadata(self) -> SentimentStrategyMetadata:
        return SentimentStrategyMetadata(
            strategy_id="extreme_sentiment_reversal",
            display_name="Extreme Lexical Mood Reversal",
            theory_summary="Extreme optimism or pessimism reflects emotional overreaction that mean-reverts.",
            academic_references=[
                "Baker & Wurgler (2006) - Investor Sentiment in the Cross-Section of Stock Returns",
                "Tetlock (2007) - Giving Content to Investor Sentiment",
            ],
            preferred_decays=[8, 10, 12],
        )

    def get_fields(self) -> list[str]:
        return ["daily_equity_mood_indicator"]

    def generate_candidates(self) -> list[SentimentCandidate]:
        candidates = []
        for u in self.metadata.preferred_universes:
            for g in self.metadata.preferred_neutralizations:
                for d in self.metadata.preferred_decays:
                    candidates.append(SentimentCandidate(
                        expression=f"trade_when(abs(daily_equity_mood_indicator - 50) > 25, group_neutralize(rank(-ts_decay_linear(ts_decay_linear(daily_equity_mood_indicator, {d}), 3)), {g.lower()}), -1)",
                        archetype=self.strategy_id,
                        family="Mood_Contrarian_Reversion",
                        hypothesis=f"Extreme mood overreaction (|mood - 50| > 25) mean-reverts with double decay ({d}d, 3d) to eliminate turnover spikes.",
                        universe=u,
                        neutralization=g,
                        decay=d,
                    ))
        return candidates
