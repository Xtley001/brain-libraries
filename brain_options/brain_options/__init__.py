"""
brain_options — Institutional options-trading alpha generation pipeline.
"""
from brain_options.pipeline.engine import OptionsAlphaEngine
from brain_options.templates import (
    OptionCandidate,
    compile_fitness_invariant,
    generate_template_candidates,
    generate_high_capacity_candidates,
)
from brain_options.catalog import OptionsCatalog, OptionField
from brain_options.archetypes import ARCHETYPES, OptionArchetype
from brain_options.kb import OptionsKnowledgeBase, KnowledgeCard
from brain_options.generator import OptionsGenerator
from brain_options.evaluation.filter import passes_quality_gates

__all__ = [
    "OptionsAlphaEngine",
    "OptionCandidate",
    "compile_fitness_invariant",
    "generate_template_candidates",
    "generate_high_capacity_candidates",
    "OptionsCatalog",
    "OptionField",
    "ARCHETYPES",
    "OptionArchetype",
    "OptionsKnowledgeBase",
    "KnowledgeCard",
    "OptionsGenerator",
    "passes_quality_gates",
]
