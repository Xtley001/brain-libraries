"""
Risk Model Alpha Generation & Evaluation Engine.
Coordinates candidate generation across systematic risk & factor premia archetypes,
applies orthogonal decorrelation via brain_decorrelator, and records into brain_store.
"""
from __future__ import annotations

import logging
from typing import List, Optional

from brain_core.config import Config
from brain_core.logger import get_logger
from brain_core.types import AlphaCandidate, SimMetrics
from brain_decorrelator import DecorrelationEngine, DecorrelationResult
from brain_risk_model.catalog import RiskModelCatalog
from brain_risk_model.generator import RiskModelGenerator
from brain_risk_model.kb import RiskModelKnowledgeBase
from brain_risk_model.templates import RiskModelCandidate

log = get_logger("brain_risk_model.engine")


class RiskModelAlphaEngine:
    """Production execution engine for institutional systematic risk model alpha generation."""

    def __init__(
        self,
        config: Optional[Config] = None,
        catalog: Optional[RiskModelCatalog] = None,
        kb: Optional[RiskModelKnowledgeBase] = None,
        decorrelator: Optional[DecorrelationEngine] = None,
    ):
        self.config = config or Config.load_from_env()
        self.catalog = catalog or RiskModelCatalog()
        self.kb = kb or RiskModelKnowledgeBase()
        self.decorrelator = decorrelator or DecorrelationEngine()
        self.generator = RiskModelGenerator(kb=self.kb, catalog=self.catalog)

    def generate_candidates(self, count: int = 10) -> List[RiskModelCandidate]:
        """Generate high-conviction risk model candidates."""
        candidates: List[RiskModelCandidate] = []
        for _ in range(count):
            c = self.generator.generate_candidate()
            if c:
                candidates.append(c)
        return candidates

    def decorrelate_candidate(self, candidate: RiskModelCandidate, base_sharpe: float = 1.30) -> List[DecorrelationResult]:
        """Apply universal and risk-model decorrelation axes to eliminate market/pool correlation."""
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
