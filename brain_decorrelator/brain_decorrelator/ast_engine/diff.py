"""
AST Difference & Motif Extraction Engine.
Implements the AST-diff motif mining methodology from AlphaMemo (Yu et al., 2026).
"""
from __future__ import annotations

import hashlib
from typing import List, Optional, Tuple
from brain_decorrelator.ast_engine.parser import ASTNode


def compute_ast_hash(node: ASTNode) -> str:
    """Computes a canonical SHA-256 hash of an AST subtree."""
    expr_repr = node.to_expr()
    return hashlib.sha256(expr_repr.encode("utf-8")).hexdigest()[:16]


def find_differing_subtrees(node_a: ASTNode, node_b: ASTNode) -> List[Tuple[ASTNode, ASTNode]]:
    """
    Recursively compares two AST trees to isolate differing subtrees.
    Returns a list of (subtree_a, subtree_b) pairs representing differing operational motifs.
    """
    if node_a.node_type != node_b.node_type or node_a.value != node_b.value:
        return [(node_a, node_b)]

    if len(node_a.args) != len(node_b.args):
        return [(node_a, node_b)]

    diffs = []
    for child_a, child_b in zip(node_a.args, node_b.args):
        child_diffs = find_differing_subtrees(child_a, child_b)
        diffs.extend(child_diffs)
    return diffs


def extract_motif_signature(node: ASTNode) -> str:
    """Extracts the operational motif signature (e.g., 'ts_decay_linear(ts_delta)') for veto matching."""
    return node.signature()
