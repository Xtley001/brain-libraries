"""
Veto Gate for filtering candidate expressions based on VetoMemory.
"""
from __future__ import annotations

import logging
from typing import List, Optional
from brain_decorrelator.ast_engine.parser import parse_ast
from brain_decorrelator.ast_engine.diff import extract_motif_signature
from brain_decorrelator.veto_memory.store import VetoMemory

log = logging.getLogger("brain_decorrelator.veto_memory.gate")


class VetoGate:
    """Filters candidate orthogonal expressions against historical veto records."""

    def __init__(self, memory: Optional[VetoMemory] = None):
        self.memory = memory or VetoMemory()

    def filter_candidates(self, candidates: List[str], universe: str = "TOP3000") -> List[str]:
        """
        Parses candidates and prunes any that match active veto motifs.
        """
        retained: List[str] = []
        for expr in candidates:
            try:
                ast = parse_ast(expr)
                sig = extract_motif_signature(ast)
                if self.memory.is_vetoed(sig, universe=universe):
                    log.info("VetoGate: Pruning candidate matching vetoed motif: %s", sig)
                    continue
                retained.append(expr)
            except Exception:
                # If AST parsing fails on a non-standard syntax, retain to avoid false rejection
                retained.append(expr)
        return retained
