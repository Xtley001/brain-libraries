"""
Abstract Base Class for Brain Pipeline Sentiment Strategies.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional
from brain_sentiment.templates import SentimentCandidate


@dataclass(frozen=True)
class SentimentStrategyMetadata:
    strategy_id: str
    display_name: str
    category: str = "sentiment"
    theory_summary: str = ""
    academic_references: list[str] = field(default_factory=list)
    preferred_universes: list[str] = field(default_factory=lambda: ["TOP3000", "TOP2000", "TOP1000"])
    preferred_neutralizations: list[str] = field(default_factory=lambda: ["SUBINDUSTRY", "SECTOR"])
    preferred_decays: list[int] = field(default_factory=lambda: [10, 12, 15, 20])


class BaseSentimentStrategy(ABC):
    """Base class for all sentiment strategy modules."""

    @property
    @abstractmethod
    def metadata(self) -> SentimentStrategyMetadata:
        pass

    @property
    def strategy_id(self) -> str:
        return self.metadata.strategy_id

    @property
    def display_name(self) -> str:
        return self.metadata.display_name

    @abstractmethod
    def get_fields(self) -> list[str]:
        pass

    @abstractmethod
    def generate_candidates(self) -> list[SentimentCandidate]:
        pass
