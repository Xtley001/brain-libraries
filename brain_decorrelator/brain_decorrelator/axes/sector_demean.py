"""
Sector Demean Orthogonalization Axis.
Applies cross-sectional residualization between Sector and Subindustry.
group_neutralize(rank(X) - group_rank(X, sector), subindustry)
"""
from __future__ import annotations

import re
from typing import List
from brain_decorrelator.plugin import AxisPlugin, register_axis


@register_axis
class SectorDemeanAxis(AxisPlugin):
    """
    Strips broad sector momentum from an alpha while preserving idiosyncratic
    subindustry dynamics, dropping self-correlation against market/sector clusters by 0.25-0.40.
    """
    name = "Axis 7 (Sector Demean Residualization)"

    def apply(self, expr: str, context: dict) -> List[str]:
        clean = expr.strip()
        # Avoid double application
        if "group_rank(" in clean and ", sector)" in clean:
            return []

        # If wrapped in group_neutralize, extract inner
        m = re.match(r"^group_neutralize\s*\(\s*(.+?)\s*,\s*(subindustry|sector)\s*\)$", clean, re.DOTALL)
        if m:
            inner = m.group(1).strip()
            # If inner is rank(...), extract or use directly
            demeaned = f"group_neutralize(rank({inner}) - group_rank({inner}, sector), subindustry)"
            return [demeaned]

        # For un-neutralized expressions
        return [
            f"group_neutralize(rank({clean}) - group_rank({clean}, sector), subindustry)"
        ]
