"""
brain-sentiment — Institutional Sentiment & Analyst Expectations Alpha Pipeline.
"""
from brain_sentiment.catalog import SentimentCatalog, SentimentField
from brain_sentiment.archetypes import SENTIMENT_ARCHETYPES, SentimentArchetype
from brain_sentiment.dedup import SentimentDeduplicator
from brain_sentiment.kb import SentimentKnowledgeBase, SentimentKnowledgeCard, SENTIMENT_CARDS
from brain_sentiment.templates import SentimentCandidate, compile_sentiment_invariant, generate_template_candidates
from brain_sentiment.generator import SentimentGenerator
from brain_sentiment.engine import SentimentAlphaEngine
from brain_sentiment.strategies import (
    SENTIMENT_STRATEGY_REGISTRY,
    BaseSentimentStrategy,
    generate_modular_candidates,
)

__all__ = [
    "SentimentCatalog",
    "SentimentField",
    "SENTIMENT_ARCHETYPES",
    "SentimentArchetype",
    "SentimentDeduplicator",
    "SentimentKnowledgeBase",
    "SentimentKnowledgeCard",
    "SENTIMENT_CARDS",
    "SentimentCandidate",
    "compile_sentiment_invariant",
    "generate_template_candidates",
    "SentimentGenerator",
    "SentimentAlphaEngine",
    "SENTIMENT_STRATEGY_REGISTRY",
    "BaseSentimentStrategy",
    "generate_modular_candidates",
]
