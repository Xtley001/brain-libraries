"""
brain_core — foundational building block of the Brain Alpha Engine.

Public API
----------
Config            : load_from_env() with typed fields for every env var.
MissingConfigError: raised when a required env var is absent.
get_logger        : returns a consistently-formatted stdlib logger.
SimSettings       : immutable dataclass describing one BRAIN simulation.
SimMetrics        : immutable dataclass holding results of one simulation.
AlphaCandidate    : generic candidate shared across all domain libraries.
LLMAdapter        : multi-provider LLM adapter with key rotation.
clean_json_array  : resilient JSON extraction from LLM outputs.
"""
from brain_core.config import Config, MissingConfigError
from brain_core.logger import get_logger
from brain_core.types import SimSettings, SimMetrics, AlphaCandidate, VALID_GENERATION_SOURCES
from brain_core.llm import LLMAdapter, clean_json_array
from brain_core.utils.dedup import ASTDeduplicator

__all__ = [
    "Config",
    "MissingConfigError",
    "get_logger",
    "SimSettings",
    "SimMetrics",
    "AlphaCandidate",
    "VALID_GENERATION_SOURCES",
    "LLMAdapter",
    "clean_json_array",
    "ASTDeduplicator",
]
