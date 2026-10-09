"""
Modular Sentiment Strategy Registry.
Aggregates all institutional sentiment strategy sub-systems.
"""
from __future__ import annotations

from typing import Dict, List
from brain_sentiment.templates import SentimentCandidate
from brain_sentiment.strategies.base import BaseSentimentStrategy
from brain_sentiment.strategies.pead_earnings_drift import PEADEarningsDriftStrategy
from brain_sentiment.strategies.analyst_revision_dispersion import AnalystRevisionDispersionStrategy
from brain_sentiment.strategies.media_attention_buzz import MediaAttentionBuzzStrategy
from brain_sentiment.strategies.extreme_sentiment_reversal import ExtremeSentimentReversalStrategy
from brain_sentiment.strategies.net_target_price_revisions import NetTargetPriceRevisionsStrategy
from brain_sentiment.strategies.dual_target_rec_confluence import DualTargetRecConfluenceStrategy

SENTIMENT_STRATEGY_REGISTRY: dict[str, BaseSentimentStrategy] = {
    "pead_earnings_drift": PEADEarningsDriftStrategy(),
    "analyst_revision_dispersion": AnalystRevisionDispersionStrategy(),
    "media_attention_buzz": MediaAttentionBuzzStrategy(),
    "extreme_sentiment_reversal": ExtremeSentimentReversalStrategy(),
    "net_target_price_revisions": NetTargetPriceRevisionsStrategy(),
    "dual_target_rec_confluence": DualTargetRecConfluenceStrategy(),
}


def generate_modular_candidates() -> List[SentimentCandidate]:
    """Generates all candidates across all registered modular sentiment strategies."""
    all_candidates: List[SentimentCandidate] = []
    for strategy in SENTIMENT_STRATEGY_REGISTRY.values():
        all_candidates.extend(strategy.generate_candidates())
    return all_candidates
