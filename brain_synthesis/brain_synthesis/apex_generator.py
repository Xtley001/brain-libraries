"""
Tri-Category Apex Cross-Synthesis Engine (v0.2.0).
Synthesizes multi-asset-class super-alphas by orthogonally fusing:
- Leg 1: Options Derivatives (option8/9, Volatility Smirk, VRP, Flow)
- Leg 2: Analyst Sentiment & PEAD (sentiment1/2, SUE, Dispersion)
- Leg 3: Systematic Risk Models & Borrow Dynamics (model51/52, BAB, Short Interest)

Target: 1,600 - 2,100 In-Sample Points, Sub-0.50 Correlation, 0.85+ Uniqueness.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Optional

from brain_core.types import AlphaCandidate

logger = logging.getLogger("brain_synthesis.apex_generator")


@dataclass
class ApexCandidate(AlphaCandidate):
    name: str = ""
    universe: str = "TOP3000"
    neutralization: str = "SUBINDUSTRY"
    decay: int = 15
    category: str = "hybrid_tri_factor"
    value_score: float = 8.5
    generation_source: str = "synthesis"


def generate_apex_candidates(
    universes: Optional[List[str]] = None,
    groups: Optional[List[str]] = None,
    decays: Optional[List[int]] = None,
) -> List[ApexCandidate]:
    """
    Generates the 8 Golden Apex Formulations across universes and decay sweeps.
    Supported Universes: TOP3000, TOP2000, TOP1000, TOP500, TOP200, TOPSP500.
    """
    candidates: List[ApexCandidate] = []
    univ_list = universes or ["TOP3000", "TOP2000"]
    group_list = groups or ["subindustry", "sector"]
    decay_list = decays or [10, 12, 15]

    for u in univ_list:
        for g in group_list:
            for d in decay_list:
                # -------------------------------------------------------------
                # Apex 1: The Institutional Accumulation Triple
                # Options Put Floor (50%) + Analyst Revisions (30%) + Low Beta (20%)
                # Citation: Frazzini & Pedersen (2014)
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
                    hypothesis="Combines put support floor (options), analyst upward revisions (sentiment), and low systematic risk (BAB).",
                    universe=u,
                    neutralization=g.upper(),
                    decay=d,
                ))

                # -------------------------------------------------------------
                # Apex 2: The SUE Volatility Smirk Confluence
                # IV Skew Smirk (50%) + Earnings Surprise Shock (35%) + F-Score Quality (15%)
                # Citation: Xing et al. (2010), Bernard & Thomas (1990)
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
                # Citation: Carr & Wu (2009), Gleason & Lee (2002)
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
                # Citation: Piotroski (2000), Sloan (1996)
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
                # Citation: Da, Engelberg & Gao (2011)
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

                # -------------------------------------------------------------
                # Apex 6: Toxic Flow Squeeze (NEW in v0.2.0)
                # Volume Imbalance / VPIN (40%) - Analyst Dispersion (30%) + Short Squeeze Utilization (30%)
                # Citation: Easley, Lopez de Prado & O'Hara (2012), Diether et al. (2002)
                # -------------------------------------------------------------
                expr_apex6 = (
                    f"group_neutralize(rank("
                    f"0.40 * rank(ts_decay_linear((call_volume_30 - put_volume_30) / (call_volume_30 + put_volume_30 + 1.0), {d})) - "
                    f"0.30 * rank(ts_decay_linear(snt1_d1_dispersion_std, {d})) + "
                    f"0.30 * rank(ts_decay_linear(short_interest_ratio_surge, {d}))"
                    f"), {g})"
                )
                candidates.append(ApexCandidate(
                    expression=expr_apex6,
                    archetype_name="Apex6_Toxic_Flow_Squeeze",
                    name=f"Apex6_Toxic_Flow_Squeeze_d{d}_{u}_{g.upper()}",
                    hypothesis="Exploits directional option volume toxicity, low analyst dispersion consensus, and short interest borrow pressure.",
                    universe=u,
                    neutralization=g.upper(),
                    decay=d,
                ))

                # -------------------------------------------------------------
                # Apex 7: Gross Profitability Basis (NEW in v0.2.0)
                # Synthetic Forward Basis (35%) + Revenue Revision Drift (35%) + Gross Profitability (30%)
                # Citation: Novy-Marx (2013), Derman & Miller (1996)
                # -------------------------------------------------------------
                expr_apex7 = (
                    f"group_neutralize(rank("
                    f"0.35 * rank(ts_decay_linear((forward_price_30 - close) / close, {d})) + "
                    f"0.35 * rank(ts_decay_linear(snt1_d1_netrevenuepercent, {d})) + "
                    f"0.30 * rank(ts_decay_linear(gross_profit_to_assets, {d}))"
                    f"), {g})"
                )
                candidates.append(ApexCandidate(
                    expression=expr_apex7,
                    archetype_name="Apex7_Gross_Profitability_Basis",
                    name=f"Apex7_Gross_Profitability_Basis_d{d}_{u}_{g.upper()}",
                    hypothesis="Fuses synthetic forward basis expansion with top-line revenue drift and Novy-Marx gross profitability.",
                    universe=u,
                    neutralization=g.upper(),
                    decay=d,
                ))

                # -------------------------------------------------------------
                # Apex 8: Borrow Friction Drift (NEW in v0.2.0)
                # Put/Call OI Imbalance (40%) + Institutional Ownership Acceleration (30%) + Loan Fee Momentum (30%)
                # Citation: Kolasinski, Reed & Ringgenberg (2013), Pan & Poteshman (2006)
                # -------------------------------------------------------------
                expr_apex8 = (
                    f"group_neutralize(rank("
                    f"0.40 * rank(-ts_decay_linear((put_open_interest_60 / (call_open_interest_60 + 0.01)), {d})) + "
                    f"0.30 * rank(ts_decay_linear(inst_ownership_delta_60, {d})) + "
                    f"0.30 * rank(ts_decay_linear(borrow_fee_momentum_20, {d}))"
                    f"), {g})"
                )
                candidates.append(ApexCandidate(
                    expression=expr_apex8,
                    archetype_name="Apex8_Borrow_Friction_Drift",
                    name=f"Apex8_Borrow_Friction_Drift_d{d}_{u}_{g.upper()}",
                    hypothesis="Capitalizes on bullish options open interest positioning, institutional accumulation, and equity loan fee momentum.",
                    universe=u,
                    neutralization=g.upper(),
                    decay=d,
                ))

    return candidates
