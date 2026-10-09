"""
Mathematical archetypes and quantitative hypotheses for Systematic Risk Models & Factor Surface Alpha generation.
WorldQuant BRAIN Category: 'model' (ValueScore: 7.0 / 10 | Low Crowding)
Incorporates theorems from Frazzini & Pedersen (2014), Ang et al. (2006), Black (1972),
Baker, Bradley, & Wurgler (2011), Piotroski (2000), Novy-Marx (2013), and Blitz & van Vliet (2007).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class RiskModelArchetype:
    name: str
    category: str
    description: str
    economic_rationale: str
    formula_template: str
    typical_horizons: list[int]
    typical_decays: list[int]
    neutralization_groups: list[str]
    academic_citation: str
    is_high_confidence: bool = False


RISK_MODEL_ARCHETYPES: list[RiskModelArchetype] = [
    # -------------------------------------------------------------------------
    # 1. Betting Against Beta (BAB) - Frazzini & Pedersen (2014)
    # -------------------------------------------------------------------------
    RiskModelArchetype(
        name="Betting Against Beta Anomaly",
        category="betting_against_beta",
        description="Fading high-beta equities relative to market benchmark (SPY).",
        economic_rationale="Frazzini & Pedersen (2014): Leverage-constrained investors (retail, mutual funds) are restricted from applying leverage to low-beta assets. To boost nominal returns, they over-allocate to high-beta stocks, causing high-beta assets to be fundamentally overpriced. Going long low-beta assets yields an alpha Sharpe ratio > 1.50.",
        formula_template="group_neutralize(rank(- ts_decay_linear(beta_last_{horizon}_days_spy, {decay})), {group})",
        typical_horizons=[60, 90, 360],
        typical_decays=[10, 12, 15],
        neutralization_groups=["subindustry", "sector"],
        academic_citation="Frazzini & Pedersen (2014), Journal of Financial Economics",
        is_high_confidence=True,
    ),
    RiskModelArchetype(
        name="Multi-Dimensional Low-Risk Factor Engine",
        category="betting_against_beta",
        description="Synthesizes rolling market beta with SPY correlation.",
        economic_rationale="Baker, Bradley, & Wurgler (2011): Institutional benchmark-tracking mandates prevent arbitrageurs from exploiting the low-beta anomaly. Blending beta with correlation creates an unconstrained low-risk alpha.",
        formula_template="group_neutralize(rank(- 0.60 * rank(ts_decay_linear(beta_last_{horizon}_days_spy, {decay})) - 0.40 * rank(ts_decay_linear(correlation_last_{horizon}_days_spy, {decay}))), {group})",
        typical_horizons=[60, 90],
        typical_decays=[10, 12, 15],
        neutralization_groups=["subindustry", "sector"],
        academic_citation="Baker, Bradley, & Wurgler (2011), Financial Analysts Journal",
        is_high_confidence=True,
    ),

    # -------------------------------------------------------------------------
    # 2. Market Decoupling & Idiosyncratic Variance - Ang et al. (2006)
    # -------------------------------------------------------------------------
    RiskModelArchetype(
        name="Idiosyncratic Volatility Discount",
        category="idiosyncratic_variance",
        description="Decomposing market correlation from total realized variance.",
        economic_rationale="Ang, Hodrick, Xing, & Zhang (2006): Stocks with high idiosyncratic volatility relative to SPY exhibit anomalously low future returns. Decomposing systematic market covariance isolates this underperformance.",
        formula_template="group_neutralize(rank(ts_decay_linear(correlation_last_{horizon}_days_spy * (ts_std_dev(returns, {horizon}) * sqrt(252)), {decay})), {group})",
        typical_horizons=[60, 90],
        typical_decays=[10, 12, 15],
        neutralization_groups=["subindustry", "sector"],
        academic_citation="Ang, Hodrick, Xing, & Zhang (2006), Journal of Finance",
        is_high_confidence=True,
    ),

    # -------------------------------------------------------------------------
    # 3. Multi-Horizon Beta Term Divergence - Black (1972)
    # -------------------------------------------------------------------------
    RiskModelArchetype(
        name="Beta Term Structure Divergence",
        category="beta_term_structure",
        description="Spread between short-term rolling beta (30d) and long-term structural beta (360d).",
        economic_rationale="Black (1972): When borrowing is restricted, the security market line is flatter. Transient spikes in short-term beta revert to the long-term equilibrium beta.",
        formula_template="group_neutralize(rank(- ts_decay_linear(beta_last_30_days_spy - beta_last_360_days_spy, {decay})), {group})",
        typical_horizons=[30],
        typical_decays=[10, 12, 15],
        neutralization_groups=["subindustry", "sector"],
        academic_citation="Black (1972), Journal of Business",
        is_high_confidence=True,
    ),

    # -------------------------------------------------------------------------
    # 4. Fundamental Quality Surface Acceleration - Piotroski (2000)
    # -------------------------------------------------------------------------
    RiskModelArchetype(
        name="Quality Surface Acceleration Derivative",
        category="quality_acceleration",
        description="Acceleration derivative of the pentagon fundamental factor surface.",
        economic_rationale="Piotroski (2000): Tracking the second derivative (acceleration) of the fundamental factor surface isolates companies crossing the positive inflection point from balance-sheet stress to rapid recovery.",
        formula_template="group_neutralize(rank(0.60 * rank(ts_decay_linear(fscore_surface_accel, {decay})) + 0.40 * rank(ts_decay_linear(fscore_bfl_quality, {decay}))), {group})",
        typical_horizons=[0],
        typical_decays=[10, 12, 15],
        neutralization_groups=["subindustry", "sector"],
        academic_citation="Piotroski (2000), Journal of Accounting Research",
        is_high_confidence=True,
    ),
    RiskModelArchetype(
        name="Momentum Style Surface Acceleration",
        category="quality_acceleration",
        description="Acceleration of the multi-factor surface combined with analyst revision momentum.",
        economic_rationale="Carhart (1997); Tulchinsky et al. (2019): Quality surface acceleration confirmed by revision momentum eliminates false value-trap breakouts.",
        formula_template="group_neutralize(rank(0.50 * rank(ts_decay_linear(fscore_surface_accel, {decay})) + 0.50 * rank(ts_decay_linear(fscore_bfl_momentum, {decay}))), {group})",
        typical_horizons=[0],
        typical_decays=[10, 12, 15],
        neutralization_groups=["subindustry", "sector"],
        academic_citation="Carhart (1997); Piotroski (2000)",
        is_high_confidence=True,
    ),

    # -------------------------------------------------------------------------
    # 5. Operational Cashflow Efficiency & Profitability - Novy-Marx (2013)
    # -------------------------------------------------------------------------
    RiskModelArchetype(
        name="Gross Profitability Cashflow Momentum",
        category="cashflow_profitability",
        description="Gross profitability composite blended with cashflow efficiency derivative.",
        economic_rationale="Novy-Marx (2013): Highly profitable firms earn persistent excess risk-adjusted returns. Combining profitability with cashflow efficiency derivatives purges accrual distortions.",
        formula_template="group_neutralize(rank(0.50 * rank(ts_decay_linear(fscore_bfl_profitability, {decay})) + 0.50 * rank(ts_decay_linear(cashflow_efficiency_rank_derivative, {decay}))), {group})",
        typical_horizons=[0],
        typical_decays=[10, 12, 15],
        neutralization_groups=["subindustry", "sector"],
        academic_citation="Novy-Marx (2013), Journal of Financial Economics",
        is_high_confidence=True,
    ),
]
