"""
Universal decorrelation axes — work for ANY strategy / dataset type.

These 6 axes are domain-agnostic mathematical transforms:
1. Velocity Shift        (Level  → ts_delta rate-of-change)
2. Calendar Spread       (Single-tenor → cross-tenor differential)
3. Volume Regime Gate    (Unconditional → liquidity-conditional)
4. Volatility Regime Gate(Unconditional → vol-conditional via trade_when)
5. Neutralization Rotate (sector ↔ subindustry group_neutralize swap)
6. Cross-Sectional Rank  (Raw signal → group_rank normalization)

Automatically registered on module import.
Domain libraries add their own domain-specific axes via @register_axis.
"""
from __future__ import annotations

import math
import re
from typing import List

from brain_decorrelator.plugin import AxisPlugin, register_axis


# ── Helper utilities ──────────────────────────────────────────────────────

def _inject_gate(gate_cond: str, expr: str) -> str:
    """
    Wrap *expr* in a trade_when gate condition.
    If *expr* already has trade_when at root, AND the new gate into it.
    """
    expr_clean = expr.strip()
    tw = re.match(
        r"^trade_when\s*\(\s*(.+?)\s*,\s*(.+)\s*,\s*(-?1)\s*\)$",
        expr_clean, re.DOTALL
    )
    if tw:
        return f"trade_when(({gate_cond}) && ({tw.group(1)}), {tw.group(2)}, {tw.group(3)})"
    return f"trade_when({gate_cond}, {expr_clean}, -1)"


# ── Axis 1: Velocity Shift ────────────────────────────────────────────────

@register_axis
class VelocityShiftAxis(AxisPlugin):
    """
    Wraps the inner argument of ts_decay_linear with ts_delta to convert
    a level signal into a rate-of-change signal.
    Lookbacks tried: 3, 5, 8 days.
    """
    name = "Axis 1 (Velocity Shift)"

    def apply(self, expr: str, context: dict) -> List[str]:
        m = re.search(r"ts_decay_linear\s*\(\s*(.+?)\s*,\s*(\d+)\s*\)", expr)
        if not m:
            return []
        inner = m.group(1).strip()
        if "ts_delta(" in inner:
            return []
        results = []
        for win in (3, 5, 8):
            sub = f"ts_decay_linear(ts_delta({inner}, {win}), 5)"
            new_expr = expr[: m.start()] + sub + expr[m.end() :]
            if new_expr != expr:
                results.append(new_expr)
        return results


# ── Axis 2: Calendar Curve Spread ─────────────────────────────────────────

@register_axis
class CalendarSpreadAxis(AxisPlugin):
    """
    Replaces a single-tenor numeric field (e.g. field_30) with a
    cross-tenor differential (field_30 - field_90) to remove market-wide drift.
    Tenors probed: 10, 20, 30, 60, 90, 120, 180, 270, 360.
    Alternate tenors tried: up to 2 per field.
    """
    name = "Axis 2 (Calendar Curve Spread)"

    _TENOR_RE = re.compile(r"\b([a-z_]+)_(10|20|30|60|90|120|180|270|360)\b")

    def apply(self, expr: str, context: dict) -> List[str]:
        results = []
        for m in self._TENOR_RE.finditer(expr):
            prefix, tenor_str = m.group(1), m.group(2)
            current = int(tenor_str)
            alts = [t for t in (10, 20, 30, 60, 90) if t != current][:2]
            for alt in alts:
                diff = f"({prefix}_{current} - {prefix}_{alt})"
                new_expr = re.sub(rf"\b{prefix}_{current}\b", diff, expr, count=1)
                if new_expr != expr:
                    results.append(new_expr)
            if results:
                break  # diff on first eligible field only
        return results


# ── Axis 3: Volume Regime Gate ────────────────────────────────────────────

@register_axis
class VolumeRegimeAxis(AxisPlugin):
    """
    Gates the signal on volume > adv20 * multiplier (1.0, 1.15, 1.25).
    Skipped if the expression already contains "volume > adv20".
    """
    name = "Axis 3 (Volume Regime Gate)"

    def apply(self, expr: str, context: dict) -> List[str]:
        if "volume > adv20" in expr:
            return []
        return [
            _inject_gate(f"volume > adv20 * {mult}", expr)
            for mult in ("1.0", "1.15", "1.25")
        ]


# ── Axis 4: Volatility Regime Gate ────────────────────────────────────────

@register_axis
class VolatilityRegimeAxis(AxisPlugin):
    """
    Gates the signal on a volatility regime condition using ts_mean comparison.
    Windows tried: 20, 60 days.
    Skipped if expression already has a vol gate.
    """
    name = "Axis 4 (Volatility Regime Gate)"

    def apply(self, expr: str, context: dict) -> List[str]:
        if "ts_mean(volatility" in expr or "ts_mean(realized_vol" in expr:
            return []
        return [
            _inject_gate(
                f"volatility_120 > ts_mean(volatility_120, {win})",
                expr,
            )
            for win in (20, 60)
        ]


# ── Axis 5: Neutralization Rotation ──────────────────────────────────────

@register_axis
class NeutralizationRotationAxis(AxisPlugin):
    """
    Swaps group_neutralize(..., subindustry) ↔ group_neutralize(..., sector).
    """
    name = "Axis 5 (Neutralization Rotation)"

    def apply(self, expr: str, context: dict) -> List[str]:
        results = []
        if "group_neutralize(" in expr:
            if ", subindustry)" in expr:
                results.append(expr.replace(", subindustry)", ", sector)", 1))
            elif ", sector)" in expr:
                results.append(expr.replace(", sector)", ", subindustry)", 1))
        return results


# ── Axis 6: Cross-Sectional Rank Normalization ────────────────────────────

@register_axis
class CrossSectionalRankAxis(AxisPlugin):
    """
    Wraps an un-ranked or un-normalized signal in group_rank(…, subindustry)
    to orthogonalize from the market beta.
    Skipped if expression already has rank() or group_rank() at root.
    """
    name = "Axis 6 (Cross-Sectional Rank)"

    def apply(self, expr: str, context: dict) -> List[str]:
        clean = expr.strip()
        if clean.startswith("rank(") or clean.startswith("group_rank("):
            return []
        return [
            f"group_rank({clean}, subindustry)",
            f"rank({clean})",
        ]
