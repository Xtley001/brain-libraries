"""
Modular Risk Model Strategy Registry.
Aggregates all institutional systematic risk and multi-factor strategy sub-systems.
"""
from __future__ import annotations

from typing import Dict, List
from brain_risk_model.templates import RiskModelCandidate
from brain_risk_model.strategies.base import BaseRiskStrategy
from brain_risk_model.strategies.betting_against_beta import BettingAgainstBetaStrategy
from brain_risk_model.strategies.beta_divergence import BetaDivergenceStrategy
from brain_risk_model.strategies.low_risk_engine import LowRiskEngineStrategy
from brain_risk_model.strategies.surface_acceleration import SurfaceAccelerationStrategy
from brain_risk_model.strategies.gross_profitability import GrossProfitabilityStrategy
from brain_risk_model.strategies.blitz_volatility import BlitzVolatilityStrategy

RISK_STRATEGY_REGISTRY: dict[str, BaseRiskStrategy] = {
    "betting_against_beta": BettingAgainstBetaStrategy(),
    "beta_divergence": BetaDivergenceStrategy(),
    "low_risk_engine": LowRiskEngineStrategy(),
    "surface_acceleration": SurfaceAccelerationStrategy(),
    "gross_profitability": GrossProfitabilityStrategy(),
    "blitz_volatility": BlitzVolatilityStrategy(),
}

# Aliases for consistent naming
RISK_MODEL_STRATEGY_REGISTRY = RISK_STRATEGY_REGISTRY
BaseRiskModelStrategy = BaseRiskStrategy


def generate_modular_candidates() -> List[RiskModelCandidate]:
    """Generates all candidates across all registered modular risk model strategies."""
    all_candidates: List[RiskModelCandidate] = []
    for strategy in RISK_STRATEGY_REGISTRY.values():
        all_candidates.extend(strategy.generate_candidates())
    return all_candidates
