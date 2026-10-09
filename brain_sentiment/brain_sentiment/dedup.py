"""
Sentiment AST Deduplication module.
Delegates to canonical ASTDeduplicator in brain_core.utils.dedup.
"""
from brain_core.utils.dedup import SentimentDeduplicator, ASTDeduplicator, _ASTConstantNormalizer

__all__ = ["SentimentDeduplicator", "ASTDeduplicator", "_ASTConstantNormalizer"]
