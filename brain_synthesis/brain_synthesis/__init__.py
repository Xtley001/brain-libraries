"""
brain-synthesis — Tri-Factor Apex Alpha Synthesis Engine (v0.2.0).
Combines options, sentiment, and risk-model alphas into high-capacity composite super-alphas.
"""
from brain_decorrelator import DecorrelationResult
from brain_synthesis.apex_generator import ApexCandidate, generate_apex_candidates
from brain_synthesis.combiner import DynamicSynthesizer
from brain_synthesis.engine import SynthesisEngine
from brain_synthesis.hrp.clustering import (
    compute_correlation_distance_matrix,
    hierarchical_cluster_indices,
)
from brain_synthesis.hrp.bisection import recursive_bisection
from brain_synthesis.regime_engine.detector import MarketRegime, MarketRegimeDetector
from brain_synthesis.regime_engine.dynamic_weights import RegimeAwareWeightTuner

__all__ = [
    "ApexCandidate",
    "generate_apex_candidates",
    "DynamicSynthesizer",
    "SynthesisEngine",
    "DecorrelationResult",
    "MarketRegime",
    "MarketRegimeDetector",
    "RegimeAwareWeightTuner",
    "compute_correlation_distance_matrix",
    "hierarchical_cluster_indices",
    "recursive_bisection",
]
