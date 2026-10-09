"""
Risk Model AST Deduplication module.
Delegates to canonical ASTDeduplicator in brain_core.utils.dedup.
"""
from brain_core.utils.dedup import RiskModelDeduplicator, ASTDeduplicator, _ASTConstantNormalizer

__all__ = ["RiskModelDeduplicator", "ASTDeduplicator", "_ASTConstantNormalizer"]
