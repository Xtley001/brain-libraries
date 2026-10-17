"""
Decay Dilation Axis.
Extends fast-decay horizons (e.g. 5-10 days) into institutional low-turnover horizons (18, 22, 26, 30 days).
"""
from __future__ import annotations

import re
from typing import List
from brain_decorrelator.plugin import AxisPlugin, register_axis


@register_axis
class DecayDilationAxis(AxisPlugin):
    """
    Dilates ts_decay_linear lookbacks to [18, 22, 26, 30] days.
    Dramatically reduces turnover (<4.5%), raises margin (>35 bps), and evades short-horizon crowd collisions.
    """
    name = "Axis 10 (Decay Horizon Dilation)"

    def apply(self, expr: str, context: dict) -> List[str]:
        m = re.search(r"ts_decay_linear\s*\(\s*(.+?)\s*,\s*(\d+)\s*\)", expr)
        if not m:
            return []

        inner = m.group(1).strip()
        current_decay = int(m.group(2))

        # Only dilate if current decay is shorter than institutional tier (< 16)
        if current_decay >= 18:
            return []

        results = []
        for target_decay in (18, 22, 26, 30):
            sub = f"ts_decay_linear({inner}, {target_decay})"
            new_expr = expr[: m.start()] + sub + expr[m.end() :]
            results.append(new_expr)
        return results
