"""
DecorrelationEngine — applies all registered AxisPlugins to a base expression.

Strategy-agnostic: works for options, sentiment, risk-model, or any other
domain that registers its own AxisPlugin subclasses.
"""
from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from brain_decorrelator.plugin import get_registered_axes

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
    """
    expression: str
    axis_name: str
    archetype_name: str
    hypothesis: str
    base_alpha_id: Optional[str] = None


class DecorrelationEngine:
    """
    Applies all registered AxisPlugins to *base_expr* and returns
    a deduplicated list of DecorrelationResult objects.

    Usage
    -----
    The engine is stateless between calls. Create once; call many times.

        engine = DecorrelationEngine()
        results = engine.generate_orthogonal_variants(
            base_expr="ts_decay_linear(implied_volatility_mean_30, 10)",
            archetype="iv_term_structure",
            base_sharpe=1.6,
        )
    """

    def generate_orthogonal_variants(
        self,
        base_expr: str,
        archetype: str,
        base_sharpe: float = 1.5,
        colliding_id: Optional[str] = None,
        colliding_factor: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[DecorrelationResult]:
        """
        Run all registered AxisPlugins on *base_expr*.

        Parameters
        ----------
        base_expr        : The expression that failed the correlation gate.
        archetype        : Strategy archetype label.
        base_sharpe      : Sharpe of the base alpha (attached to hypothesis).
        colliding_id     : BRAIN alpha_id of the correlated peer.
        colliding_factor : Factor type of the peer (e.g. "pcr", "skew").
        context          : Extra metadata forwarded to every plugin's apply().

        Returns
        -------
        Deduplicated list of DecorrelationResult, one per successful variant.
        """
        ctx: Dict[str, Any] = {
            "archetype": archetype,
            "base_sharpe": base_sharpe,
            "colliding_id": colliding_id,
            "colliding_factor": colliding_factor,
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
                "Import domain axis modules (e.g. brain_decorrelator.axes.universal) to enable."
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
                results.append(
                    DecorrelationResult(
                        expression=clean,
                        axis_name=plugin.name,
                        archetype_name=f"Decorrelated({archetype})",
                        hypothesis=f"[{plugin.name}] Salvaged from base Sharpe={base_sharpe:.2f}",
                        base_alpha_id=colliding_id,
                    )
                )

        log.info(
            "brain_decorrelator: Generated %d variants for %s (axes=%d)",
            len(results), archetype, len(axes),
        )
        return results
