"""
Tri-Category Apex Cross-Synthesis Engine.
Synthesizes multi-asset-class super-alphas by orthogonally fusing:
- Leg 1: Options Derivatives (option8/9, ValueScore: 6.0)
- Leg 2: Analyst Sentiment & PEAD (sentiment1/2, ValueScore: 8.0)
- Leg 3: Systematic Risk Models (model51/52, ValueScore: 7.0)

Target: 1,500+ In-Sample Points, Sub-0.10 Cross-Platform Correlation, 0.85+ Uniqueness.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List

from brain_core.types import AlphaCandidate

logger = logging.getLogger("brain_synthesis.apex_generator")


@dataclass
class ApexCandidate(AlphaCandidate):
    name: str = ""
    universe: str = "TOP3000"
    neutralization: str = "SUBINDUSTRY"
    decay: int = 15
    category: str = "hybrid_tri_factor"
    value_score: float = 8.0
    generation_source: str = "synthesis"


def generate_apex_candidates() -> List[ApexCandidate]:
    """Generates the 5 Golden Apex Formulations across universes and decay sweeps."""
    candidates: List[ApexCandidate] = []
    universes = ["TOP3000", "TOP2000"]
    groups = ["subindustry", "sector"]
    decays = [10, 12, 15]

    for u in universes:
        for g in groups:
            for d in decays:
                # -------------------------------------------------------------
                # Apex 1: The Institutional Accumulation Triple
                # Options Put Floor (50%) + Analyst Revisions (30%) + Low Beta (20%)
                # -------------------------------------------------------------
                expr_apex1 = (
                    f"group_neutralize(rank("
                    f"0.50 * rank(ts_decay_linear((forward_price_60 - put_breakeven_60) / close, {d})) + "
                    f"0.30 * rank(ts_decay_linear(snt1_d1_netearningsrevision, {d})) - "
                    f"0.20 * rank(ts_decay_linear(beta_last_60_days_spy, {d}))"
                    f"), {g})"
                )
                candidates.append(ApexCandidate(
                    expression=expr_apex1,
                    archetype_name="Apex1_Accumulation_Triple",
                    name=f"Apex1_Accumulation_Triple_d{d}_{u}_{g.upper()}",
                    hypothesis="Combines put support floor (options), sluggish analyst upward revisions (sentiment), and low systematic risk (BAB).",
                    universe=u,
                    neutralization=g.upper(),
                    decay=d,
                ))

                # -------------------------------------------------------------
                # Apex 2: The SUE Volatility Smirk Confluence
                # IV Skew Mean-Reversion (50%) + Earnings Surprise Shock (35%) + F-Score Quality (15%)
                # -------------------------------------------------------------
                expr_apex2 = (
                    f"group_neutralize(rank("
                    f"0.50 * rank(-ts_decay_linear((implied_volatility_put_60 - implied_volatility_call_60) / (implied_volatility_mean_60 + 0.001), {d})) + "
                    f"0.35 * rank(ts_decay_linear(snt1_d1_earningssurprise, {d})) + "
                    f"0.15 * rank(ts_decay_linear(fscore_surface_accel, {d}))"
                    f"), {g})"
                )
                candidates.append(ApexCandidate(
                    expression=expr_apex2,
                    archetype_name="Apex2_SUE_Smirk_Confluence",
                    name=f"Apex2_SUE_Smirk_Confluence_d{d}_{u}_{g.upper()}",
                    hypothesis="Fuses call implied skew undervaluation with fundamental SUE surprise shocks and accounting turnaround momentum.",
                    universe=u,
                    neutralization=g.upper(),
                    decay=d,
                ))

                # -------------------------------------------------------------
                # Apex 3: The Target Drift Term Slope
                # IV Term Structure Slope (45%) + Net Target Revisions (35%) + Low SPY Beta (20%)
                # -------------------------------------------------------------
                expr_apex3 = (
                    f"group_neutralize(rank("
                    f"0.45 * rank(ts_decay_linear(implied_volatility_mean_180 - implied_volatility_mean_30, {d})) + "
                    f"0.35 * rank(ts_decay_linear(snt1_d1_nettargetpercent, {d})) - "
                    f"0.20 * rank(ts_decay_linear(beta_last_90_days_spy, {d}))"
                    f"), {g})"
                )
                candidates.append(ApexCandidate(
                    expression=expr_apex3,
                    archetype_name="Apex3_Target_Term_Slope",
                    name=f"Apex3_Target_Term_Slope_d{d}_{u}_{g.upper()}",
                    hypothesis="Exploits positive volatility term premium combined with equity price target upgrades and low equity beta.",
                    universe=u,
                    neutralization=g.upper(),
                    decay=d,
                ))

                # -------------------------------------------------------------
                # Apex 4: The Earnings Torpedo Quality Drift
                # Disappointment Vulnerability (40%) + Accounting Quality (35%) + Call Breakeven Basis (25%)
                # -------------------------------------------------------------
                expr_apex4 = (
                    f"group_neutralize(rank("
                    f"0.40 * rank(ts_decay_linear(snt1_d1_earningstorpedo, {d})) + "
                    f"0.35 * rank(ts_decay_linear(fscore_bfl_quality, {d})) + "
                    f"0.25 * rank(ts_decay_linear((call_breakeven_90 - forward_price_90) / close, {d}))"
                    f"), {g})"
                )
                candidates.append(ApexCandidate(
                    expression=expr_apex4,
                    archetype_name="Apex4_Torpedo_Quality_Drift",
                    name=f"Apex4_Torpedo_Quality_Drift_d{d}_{u}_{g.upper()}",
                    hypothesis="Anticipates earnings torpedo re-rating supported by high balance sheet quality and call breakeven cushion.",
                    universe=u,
                    neutralization=g.upper(),
                    decay=d,
                ))

                # -------------------------------------------------------------
                # Apex 5: Low-Risk Attention Asymmetry
                # Forward Put Cushion (40%) + Dynamic Analyst Attention (30%) + Low SPY Correlation (30%)
                # -------------------------------------------------------------
                expr_apex5 = (
                    f"group_neutralize(rank("
                    f"0.40 * rank(ts_decay_linear((forward_price_120 - put_breakeven_120) / close, {d})) + "
                    f"0.30 * rank(ts_decay_linear(snt1_d1_dynamicfocusrank, {d})) - "
                    f"0.30 * rank(ts_decay_linear(correlation_last_60_days_spy, {d}))"
                    f"), {g})"
                )
                candidates.append(ApexCandidate(
                    expression=expr_apex5,
                    archetype_name="Apex5_LowRisk_Attention_Asymmetry",
                    name=f"Apex5_LowRisk_Attention_Asymmetry_d{d}_{u}_{g.upper()}",
                    hypothesis="Combines deep put floor with focused institutional analyst attention and low market correlation.",
                    universe=u,
                    neutralization=g.upper(),
                    decay=d,
                ))

    return candidates
