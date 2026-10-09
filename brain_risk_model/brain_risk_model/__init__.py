"""
brain-risk-model — Institutional Systematic Risk Models & Factor Premia Alpha Pipeline.
"""
from brain_risk_model.catalog import RiskModelCatalog, RiskModelField
from brain_risk_model.archetypes import RISK_MODEL_ARCHETYPES, RiskModelArchetype
from brain_risk_model.dedup import RiskModelDeduplicator
from brain_risk_model.kb import RiskModelKnowledgeBase, RiskModelKnowledgeCard, RISK_MODEL_CARDS
from brain_risk_model.templates import RiskModelCandidate, compile_risk_model_invariant, generate_template_candidates
from brain_risk_model.generator import RiskModelGenerator
from brain_risk_model.engine import RiskModelAlphaEngine
from brain_risk_model.strategies import (
    RISK_MODEL_STRATEGY_REGISTRY,
    BaseRiskModelStrategy,
    generate_modular_candidates,
)

__all__ = [
    "RiskModelCatalog",
    "RiskModelField",
    "RISK_MODEL_ARCHETYPES",
    "RiskModelArchetype",
    "RiskModelDeduplicator",
    "RiskModelKnowledgeBase",
    "RiskModelKnowledgeCard",
    "RISK_MODEL_CARDS",
    "RiskModelCandidate",
    "compile_risk_model_invariant",
    "generate_template_candidates",
    "RiskModelGenerator",
    "RiskModelAlphaEngine",
    "RISK_MODEL_STRATEGY_REGISTRY",
    "BaseRiskModelStrategy",
    "generate_modular_candidates",
]
