"""
DecorrelationEngine — applies all registered AxisPlugins to a base expression.

Strategy-agnostic: works for options, sentiment, risk-model, or any other
domain that registers its own AxisPlugin subclasses.
Enhanced in v0.2.0 with AST-Diff motif extraction and AlphaMemo Asymmetric Veto Control.
"""
from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from brain_decorrelator.plugin import get_registered_axes
from brain_decorrelator.ast_engine.parser import parse_ast
from brain_decorrelator.ast_engine.diff import extract_motif_signature
from brain_decorrelator.veto_memory.store import VetoMemory
from brain_decorrelator.veto_memory.veto_gate import VetoGate

log = logging.getLogger("brain_decorrelator.engine")


@dataclass(frozen=True)
class DecorrelationResult:
    """
    One orthogonal variant produced by a single axis plugin.

    Fields
    ------
    expression      : The transformed Fast Expression string.
    axis_name       : Name of the AxisPlugin that produced this variant.
    archetype_name  : Original archetype label, prefixed with "Decorrelated(".
    hypothesis      : Appended with salvage note from base_sharpe.
    base_alpha_id   : BRAIN alpha_id of the source alpha (may be None).
    motif_signature : Structural signature of the generated expression.
    """
    expression: str
    axis_name: str
    archetype_name: str
    hypothesis: str
    base_alpha_id: Optional[str] = None
    motif_signature: str = ""


class DecorrelationEngine:
    """
    Applies all registered AxisPlugins to *base_expr* and returns
    a deduplicated, veto-filtered list of DecorrelationResult objects.

    Usage
    -----
        engine = DecorrelationEngine()
        results = engine.generate_orthogonal_variants(
            base_expr="ts_decay_linear(implied_volatility_mean_30, 10)",
            archetype="iv_term_structure",
            base_sharpe=1.6,
        )
    """

    def __init__(self, veto_memory: Optional[VetoMemory] = None):
        self.veto_memory = veto_memory or VetoMemory()
        self.veto_gate = VetoGate(self.veto_memory)

    def generate_orthogonal_variants(
        self,
        base_expr: str,
        archetype: str,
        base_sharpe: float = 1.5,
        colliding_id: Optional[str] = None,
        colliding_factor: Optional[str] = None,
        universe: str = "TOP3000",
        context: Optional[Dict[str, Any]] = None,
    ) -> List[DecorrelationResult]:
        """
        Run all registered AxisPlugins on *base_expr*, filtering through VetoMemory.

        Parameters
        ----------
        base_expr        : The expression that failed the correlation gate.
        archetype        : Strategy archetype label.
        base_sharpe      : Sharpe of the base alpha (attached to hypothesis).
        colliding_id     : BRAIN alpha_id of the correlated peer.
        colliding_factor : Factor type of the peer (e.g. "pcr", "skew").
        universe         : Universe of candidate (e.g. "TOP3000", "TOP1000").
        context          : Extra metadata forwarded to every plugin's apply().

        Returns
        -------
        Deduplicated, veto-checked list of DecorrelationResult objects.
        """
        # If a collision occurred, record the base motif in VetoMemory
        if colliding_id:
            try:
                base_ast = parse_ast(base_expr)
                base_motif = extract_motif_signature(base_ast)
                self.veto_memory.record_collision(
                    motif_signature=base_motif,
                    colliding_alpha_id=colliding_id,
                    correlation_score=0.85,  # Above platform 0.70 threshold
                    universe=universe,
                )
            except Exception as e:
                log.debug("VetoMemory: Could not extract base motif: %s", e)

        ctx: Dict[str, Any] = {
            "archetype": archetype,
            "base_sharpe": base_sharpe,
            "colliding_id": colliding_id,
            "colliding_factor": colliding_factor,
            "universe": universe,
            "dedup_hashes": set(),
        }
        if context:
            ctx.update(context)

        results: List[DecorrelationResult] = []
        seen: set[str] = set()

        axes = get_registered_axes()
        if not axes:
            log.warning(
                "brain_decorrelator: No axes registered. "
                "Import domain axis modules (e.g. brain_decorrelator.axes) to enable."
            )

        for plugin in axes:
            try:
                variants = plugin.apply(base_expr, ctx)
            except Exception as exc:
                log.error("brain_decorrelator: Axis %r raised: %s", plugin.name, exc)
                continue

            for variant_expr in variants:
                clean = variant_expr.strip()
                if not clean:
                    continue
                h = hashlib.sha256(clean.encode()).hexdigest()[:16]
                if h in seen:
                    continue
                seen.add(h)
                ctx["dedup_hashes"].add(h)

                # Check VetoMemory
                motif_sig = ""
                try:
                    v_ast = parse_ast(clean)
                    motif_sig = extract_motif_signature(v_ast)
                    if self.veto_memory.is_vetoed(motif_sig, universe=universe):
                        log.debug("VetoMemory: Pruning candidate matching %s", motif_sig)
                        continue
                except Exception:
                    pass

                results.append(
                    DecorrelationResult(
                        expression=clean,
                        axis_name=plugin.name,
                        archetype_name=f"Decorrelated({archetype})",
                        hypothesis=f"[{plugin.name}] Salvaged from base Sharpe={base_sharpe:.2f}",
                        base_alpha_id=colliding_id,
                        motif_signature=motif_sig,
                    )
                )

        log.info(
            "brain_decorrelator: Generated %d variants for %s (axes=%d, universe=%s)",
            len(results), archetype, len(axes), universe,
        )
        return results
