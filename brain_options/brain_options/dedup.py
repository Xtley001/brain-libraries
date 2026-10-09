"""
Options AST Deduplication module.
Delegates to canonical ASTDeduplicator in brain_core.utils.dedup.
"""
from brain_core.utils.dedup import ASTDeduplicator, _ASTConstantNormalizer

__all__ = ["ASTDeduplicator", "_ASTConstantNormalizer"]
