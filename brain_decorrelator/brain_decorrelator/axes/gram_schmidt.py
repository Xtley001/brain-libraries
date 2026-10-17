"""
Gram-Schmidt Factor Deflation Axis.
Orthogonalizes alpha candidate against market equity beta (SPY beta proxy).
"""
from __future__ import annotations

import re
from typing import List
from brain_decorrelator.plugin import AxisPlugin, register_axis


@register_axis
class GramSchmidtAxis(AxisPlugin):
    """
    Deflates alpha signals from broad equity market beta (BAB proxy)
    to isolate true idiosyncratic alpha.
    """
    name = "Axis 9 (Gram-Schmidt Beta Deflation)"

    def apply(self, expr: str, context: dict) -> List[str]:
        clean = expr.strip()
        if "beta_last_" in clean or "returns / market" in clean:
            return []

        # Target inner signal if group_neutralize is present
        m = re.match(r"^group_neutralize\s*\(\s*(.+?)\s*,\s*([a-zA-Z_]+)\s*\)$", clean, re.DOTALL)
        if m:
            inner, group = m.group(1).strip(), m.group(2).strip()
            deflated = f"group_neutralize(rank(rank({inner}) - 0.25 * rank(beta_last_60_days_spy)), {group})"
            return [deflated]

        return [
            f"rank(rank({clean}) - 0.25 * rank(beta_last_60_days_spy))"
        ]
