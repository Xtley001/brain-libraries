"""
Abstract Base Class and Protocol for Brain Pipeline Quantitative Strategies.
Every strategy is an isolated, self-contained sub-system defining its theoretical basis,
fields, candidate generation, and parameter spaces.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, List, Optional
from brain_options.templates import OptionCandidate


@dataclass(frozen=True)
class StrategyMetadata:
    strategy_id: str
    display_name: str
    category: str
    theory_summary: str
    academic_references: list[str]
    preferred_universes: list[str] = field(default_factory=lambda: ["TOP1000", "TOP2000", "TOP3000", "TOP500", "TOPSP500"])
    preferred_neutralizations: list[str] = field(default_factory=lambda: ["SUBINDUSTRY", "INDUSTRY", "SECTOR", "MARKET", "NONE"])
    preferred_decays: list[int] = field(default_factory=lambda: [16, 20, 24])


class BaseStrategy(ABC):
    """Base class for all quantitative strategy modules."""

    @property
    @abstractmethod
    def metadata(self) -> StrategyMetadata:
        """Returns the strategy metadata."""
        pass

    @property
    def strategy_id(self) -> str:
        return self.metadata.strategy_id

    @property
    def display_name(self) -> str:
        return self.metadata.display_name

    @abstractmethod
    def get_fields(self) -> list[str]:
        """Returns the list of BRAIN platform fields used by this strategy."""
        pass

    @abstractmethod
    def generate_candidates(self) -> list[OptionCandidate]:
        """Generates deterministic and hypothesis-driven candidate expressions."""
        pass

    def mutate_candidate(
        self,
        candidate: OptionCandidate,
        rl_weights: Optional[dict[str, float]] = None,
    ) -> list[OptionCandidate]:
        """Optionally generates RL-guided mutations for a candidate within this strategy family."""
        return []
