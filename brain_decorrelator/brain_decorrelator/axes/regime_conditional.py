"""
Volatility Regime Scaling Axis.
Normalizes alpha signal by historical volatility:
ts_decay_linear(X / (ts_std_dev(returns, 60) + 0.001), 20)
"""
from __future__ import annotations

import re
from typing import List
from brain_decorrelator.plugin import AxisPlugin, register_axis


@register_axis
class VolatilityRegimeScalingAxis(AxisPlugin):
    """
    Normalizes candidate alpha by realized return volatility to prevent false breakouts
    and stabilize performance across calm and crisis regimes.
    """
    name = "Axis 8 (Volatility Regime Scaling)"

    def apply(self, expr: str, context: dict) -> List[str]:
        clean = expr.strip()
        if "ts_std_dev(returns" in clean or "ts_std_dev(close" in clean:
            return []

        # Target inner signal if already group-neutralized
        m = re.match(r"^group_neutralize\s*\(\s*(.+?)\s*,\s*([a-zA-Z_]+)\s*\)$", clean, re.DOTALL)
        if m:
            inner, group = m.group(1).strip(), m.group(2).strip()
            scaled_inner = f"ts_decay_linear(({inner}) / (ts_std_dev(returns, 60) + 0.001), 20)"
            return [f"group_neutralize(rank({scaled_inner}), {group})"]

        return [
            f"ts_decay_linear(({clean}) / (ts_std_dev(returns, 60) + 0.001), 20)"
        ]
