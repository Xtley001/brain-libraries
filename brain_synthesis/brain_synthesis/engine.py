"""
Tri-Factor Synthesis Execution Engine.
Orchestrates generation of golden apex formulations, dynamic cross-domain synthesis,
orthogonal decorrelation, and persistence.
"""
from __future__ import annotations

import logging
from typing import List, Optional, Tuple

from brain_core.config import Config
from brain_core.logger import get_logger
from brain_core.types import AlphaCandidate, SimMetrics
from brain_decorrelator import DecorrelationEngine, DecorrelationResult
from brain_synthesis.apex_generator import ApexCandidate, generate_apex_candidates
from brain_synthesis.combiner import DynamicSynthesizer

log = get_logger("brain_synthesis.engine")


class SynthesisEngine:
    """Production execution engine for cross-domain apex alpha synthesis."""

    def __init__(
        self,
        config: Optional[Config] = None,
        decorrelator: Optional[DecorrelationEngine] = None,
        synthesizer: Optional[DynamicSynthesizer] = None,
    ):
        self.config = config or Config.load_from_env()
        self.decorrelator = decorrelator or DecorrelationEngine()
        self.synthesizer = synthesizer or DynamicSynthesizer()
        self._golden_candidates: List[ApexCandidate] = generate_apex_candidates()

    def get_golden_candidates(self) -> List[ApexCandidate]:
        """Returns the pre-computed set of institutional golden apex formulations."""
        return list(self._golden_candidates)

    def synthesize_cross_domain(
        self,
        legs: List[Tuple[AlphaCandidate, float]],
        name: str = "CrossDomain_Synthesis",
    ) -> ApexCandidate:
        """Dynamically synthesize arbitrary multi-domain candidate signals."""
        return self.synthesizer.synthesize(legs, name=name)

    def decorrelate_candidate(self, candidate: ApexCandidate, base_sharpe: float = 1.40) -> List[DecorrelationResult]:
        """Apply orthogonal decorrelation axes across market, volatility, and sector dimensions."""
        return self.decorrelator.generate_orthogonal_variants(
            base_expr=candidate.expression,
            archetype=candidate.archetype_name,
            base_sharpe=base_sharpe,
            context={
                "category": candidate.category,
                "universe": candidate.universe,
                "decay": candidate.decay,
            },
        )

    def generate_domain_candidates(self, count: int = 3) -> dict[str, List[AlphaCandidate]]:
        """
        Safely fetch candidates from each available domain engine with error isolation.
        Failure in one domain does not abort synthesis.
        """
        results: dict[str, List[AlphaCandidate]] = {
            "options": [],
            "sentiment": [],
            "risk_model": [],
        }

        try:
            from brain_options import OptionsAlphaEngine
            results["options"] = OptionsAlphaEngine().generate_candidates(count=count)
        except Exception as exc:
            log.warning("Options domain candidate generation failed: %s", exc)

        try:
            from brain_sentiment import SentimentAlphaEngine
            results["sentiment"] = SentimentAlphaEngine().generate_candidates(count=count)
        except Exception as exc:
            log.warning("Sentiment domain candidate generation failed: %s", exc)

        try:
            from brain_risk_model import RiskModelAlphaEngine
            results["risk_model"] = RiskModelAlphaEngine().generate_candidates(count=count)
        except Exception as exc:
            log.warning("Risk model domain candidate generation failed: %s", exc)

        return results
