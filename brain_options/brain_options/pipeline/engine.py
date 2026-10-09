"""
OptionsAlphaEngine — orchestrates the full options pipeline.

Pipeline stages
---------------
1. Generate candidates from templates / LLM / procedural sources.
2. Simulate each candidate via the BRAIN API (Stage 0 fast screen).
3. Filter Stage 0 survivors through quality gates.
4. Decorrelate failed-correlation candidates via brain_decorrelator.
5. Update MAB RL state in brain_store.
6. Persist qualified alphas.
"""
from __future__ import annotations

import logging
from typing import List, Optional

from brain_core.config import Config
from brain_core.logger import get_logger
from brain_core.types import SimMetrics
from brain_decorrelator import DecorrelationEngine, DecorrelationResult
from brain_store.store import OptionsStore
from brain_options.catalog import OptionsCatalog
from brain_options.evaluation.filter import passes_quality_gates
from brain_options.generator import OptionsGenerator
from brain_options.kb import OptionsKnowledgeBase
from brain_options.templates import OptionCandidate

log = get_logger("brain_options.pipeline.engine")


class OptionsAlphaEngine:
    """
    Top-level orchestrator for the options alpha discovery pipeline.

    Parameters
    ----------
    config       : brain_core.Config instance. Defaults to Config.load_from_env().
    store        : brain_store.OptionsStore instance. Defaults to OptionsStore().
    catalog      : OptionsCatalog instance. Defaults to OptionsCatalog().
    kb           : OptionsKnowledgeBase instance. Defaults to OptionsKnowledgeBase().
    decorrelator : DecorrelationEngine instance. Defaults to DecorrelationEngine().
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        store: Optional[OptionsStore] = None,
        catalog: Optional[OptionsCatalog] = None,
        kb: Optional[OptionsKnowledgeBase] = None,
        decorrelator: Optional[DecorrelationEngine] = None,
    ) -> None:
        self.config = config or Config.load_from_env()
        self.store = store or OptionsStore(database_url=self.config.database_url)
        self.catalog = catalog or OptionsCatalog()
        self.kb = kb or OptionsKnowledgeBase()
        self.decorrelator = decorrelator or DecorrelationEngine()
        self.generator = OptionsGenerator(
            kb=self.kb,
            catalog=self.catalog,
            db=self.store.db,
        )
        log.info(
            "OptionsAlphaEngine initialised (universe=%s, delay=%d)",
            self.config.universe,
            self.config.delay,
        )

    def generate_candidates(self, count: int = 10) -> List[OptionCandidate]:
        """Generate high-conviction options alpha candidates."""
        candidates: List[OptionCandidate] = []
        for _ in range(count):
            c = self.generator.generate_candidate()
            if c:
                candidates.append(c)
        return candidates

    def decorrelate_candidate(self, candidate: OptionCandidate, base_sharpe: float = 1.30) -> List[DecorrelationResult]:
        """Apply universal and options decorrelation axes to eliminate market/pool correlation."""
        return self.decorrelator.generate_orthogonal_variants(
            base_expr=candidate.expression,
            archetype=candidate.archetype_name or candidate.archetype,
            base_sharpe=base_sharpe,
            context={
                "category": candidate.category,
                "universe": candidate.universe,
                "decay": candidate.decay,
            },
        )

    def evaluate_gates(self, metrics: SimMetrics) -> tuple[bool, str]:
        """Verify if simulation metrics satisfy quality threshold gates."""
        return passes_quality_gates(
            metrics,
            min_sharpe=self.config.filter_min_sharpe,
            min_fitness=self.config.filter_min_fitness,
            min_turnover=self.config.filter_min_turnover,
            max_turnover=self.config.filter_max_turnover,
        )
