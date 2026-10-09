"""
brain-synthesis — Tri-Factor Apex Alpha Synthesis Engine.
"""
from brain_decorrelator import DecorrelationResult
from brain_synthesis.apex_generator import ApexCandidate, generate_apex_candidates
from brain_synthesis.combiner import DynamicSynthesizer
from brain_synthesis.engine import SynthesisEngine

__all__ = [
    "ApexCandidate",
    "generate_apex_candidates",
    "DynamicSynthesizer",
    "SynthesisEngine",
    "DecorrelationResult",
]
