"""
Sentiment Alpha Generation & Evaluation Engine.
Coordinates candidate generation across 12 institutional sentiment archetypes,
applies orthogonal decorrelation via brain_decorrelator, and records into brain_store.
"""
from __future__ import annotations

import logging
from typing import List, Optional

from brain_core.config import Config
from brain_core.logger import get_logger
from brain_core.types import AlphaCandidate, SimMetrics
from brain_decorrelator import DecorrelationEngine, DecorrelationResult
from brain_sentiment.catalog import SentimentCatalog
from brain_sentiment.generator import SentimentGenerator
from brain_sentiment.kb import SentimentKnowledgeBase
from brain_sentiment.templates import SentimentCandidate

log = get_logger("brain_sentiment.engine")


class SentimentAlphaEngine:
    """Production execution engine for institutional sentiment alpha generation."""

    def __init__(
        self,
        config: Optional[Config] = None,
        catalog: Optional[SentimentCatalog] = None,
        kb: Optional[SentimentKnowledgeBase] = None,
        decorrelator: Optional[DecorrelationEngine] = None,
    ):
        self.config = config or Config.load_from_env()
        self.catalog = catalog or SentimentCatalog()
        self.kb = kb or SentimentKnowledgeBase()
        self.decorrelator = decorrelator or DecorrelationEngine()
        self.generator = SentimentGenerator(kb=self.kb, catalog=self.catalog)

    def generate_candidates(self, count: int = 10) -> List[SentimentCandidate]:
        """Generate high-conviction sentiment candidates."""
        candidates: List[SentimentCandidate] = []
        for _ in range(count):
            c = self.generator.generate_candidate()
            if c:
                candidates.append(c)
        return candidates

    def decorrelate_candidate(self, candidate: SentimentCandidate, base_sharpe: float = 1.30) -> List[DecorrelationResult]:
        """Apply universal and sentiment decorrelation axes to eliminate market/pool correlation."""
        return self.decorrelator.generate_orthogonal_variants(
            base_expr=candidate.expression,
            archetype=candidate.archetype,
            base_sharpe=base_sharpe,
            context={
                "category": candidate.category,
                "universe": candidate.universe,
                "decay": candidate.decay,
            },
        )
