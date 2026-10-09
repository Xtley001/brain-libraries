"""
Mathematical archetypes and quantitative hypotheses for Sentiment & Analyst Expectations Alpha generation.
WorldQuant BRAIN Category: 'sentiment' (ValueScore: 8.0 / 10 | Highest on Platform)
Incorporates theorems from Chan et al. (1996), Bernard & Thomas (1989, 1990),
Givoly & Lakonishok (1979), Diether et al. (2002), Brav & Lehavy (2003), and Da et al. (2011).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class SentimentArchetype:
    name: str
    category: str
    description: str
    economic_rationale: str
    formula_template: str
    typical_decays: list[int]
    neutralization_groups: list[str]
    academic_citation: str
    is_high_confidence: bool = False


SENTIMENT_ARCHETYPES: list[SentimentArchetype] = [
    # -------------------------------------------------------------------------
    # 1. Post-Earnings Announcement Drift (PEAD) Revision Momentum
    # -------------------------------------------------------------------------
    SentimentArchetype(
        name="PEAD Net Revision Momentum",
        category="pead_revision",
        description="Net percentage of analysts raising minus lowering earnings estimates smoothed by linear decay.",
        economic_rationale="Chan, Jegadeesh, & Lakonishok (1996): Analysts revise earnings projections gradually rather than instantaneously due to cognitive conservatism and career risk.",
        formula_template="group_neutralize(rank(ts_decay_linear(snt1_d1_netearningsrevision, {decay})), {group})",
        typical_decays=[10, 12, 15],
        neutralization_groups=["subindustry", "sector"],
        academic_citation="Chan, Jegadeesh, & Lakonishok (1996), Journal of Finance",
        is_high_confidence=True,
    ),
    SentimentArchetype(
        name="Filtered High-Conviction PEAD Revision",
        category="pead_revision",
        description="Selective execution on upper/lower quintiles of net analyst revision velocity.",
        economic_rationale="Isolating extreme institutional revision tails cuts turnover below 8% while preserving multi-month drift.",
        formula_template="trade_when(abs(rank(ts_decay_linear(snt1_d1_netearningsrevision, {decay})) - 0.5) > 0.20, group_neutralize(rank(ts_decay_linear(snt1_d1_netearningsrevision, {decay})), {group}), -1)",
        typical_decays=[10, 12, 15],
        neutralization_groups=["subindustry", "sector"],
        academic_citation="Chan, Jegadeesh, & Lakonishok (1996); Tulchinsky et al. (2019)",
        is_high_confidence=True,
    ),
    SentimentArchetype(
        name="Coverage-Weighted Revision Latency Drift",
        category="pead_revision",
        description="Analyst revisions scaled by the inverse of analyst coverage count.",
        economic_rationale="Gleason & Lee (2003): Price discovery is slower in low-coverage firms, causing prolonged post-revision drift.",
        formula_template="group_neutralize(rank(ts_decay_linear(snt1_d1_netearningsrevision / (snt1_d1_analystcoverage + 1), {decay})), {group})",
        typical_decays=[10, 12, 15],
        neutralization_groups=["subindustry", "sector"],
        academic_citation="Gleason & Lee (2003), Journal of Accounting Research",
        is_high_confidence=True,
    ),

    # -------------------------------------------------------------------------
    # 2. Standardized Unexpected Earnings (SUE) Shocks
    # -------------------------------------------------------------------------
    SentimentArchetype(
        name="Standardized Unexpected Earnings Shock",
        category="sue_shock",
        description="Reported quarterly earnings surprise relative to consensus consensus expectations.",
        economic_rationale="Bernard & Thomas (1989, 1990): The market systematically underreacts to fundamental earnings surprises.",
        formula_template="group_neutralize(rank(ts_decay_linear(snt1_d1_earningssurprise, {decay})), {group})",
        typical_decays=[10, 12, 15],
        neutralization_groups=["subindustry", "sector"],
        academic_citation="Bernard & Thomas (1989, 1990), Journal of Accounting and Economics",
        is_high_confidence=True,
    ),
    SentimentArchetype(
        name="Material SUE Threshold Shock",
        category="sue_shock",
        description="Executes exclusively when actual reported earnings exceed expectations by over 5%.",
        economic_rationale="Large fundamental shocks trigger institutional capital reallocation and prolonged re-rating.",
        formula_template="trade_when(abs(snt1_d1_earningssurprise) > 0.05, group_neutralize(rank(ts_decay_linear(snt1_d1_earningssurprise, {decay})), {group}), -1)",
        typical_decays=[10, 12, 15],
        neutralization_groups=["subindustry", "sector"],
        academic_citation="Bernard & Thomas (1990)",
        is_high_confidence=True,
    ),
    SentimentArchetype(
        name="Earnings Torpedo Seasonal Mean-Reversion",
        category="sue_shock",
        description="Spread between FY1 expected earnings and trailing four quarters actual earnings.",
        economic_rationale="Bernard & Thomas (1990): Earnings follow an autoregressive seasonal process; fading extreme torpedo divergences captures mean-reverting revaluation.",
        formula_template="group_neutralize(rank(ts_decay_linear(snt1_d1_earningstorpedo, {decay})), {group})",
        typical_decays=[10, 12, 15],
        neutralization_groups=["subindustry", "sector"],
        academic_citation="Bernard & Thomas (1990); Kothari, So, & Verdi (2016)",
        is_high_confidence=True,
    ),

    # -------------------------------------------------------------------------
    # 3. Target Price Revisions & Recommendation Confluence
    # -------------------------------------------------------------------------
    SentimentArchetype(
        name="Net Target Price Revision Drift",
        category="target_revisions",
        description="Net percentage of analysts raising minus lowering price targets.",
        economic_rationale="Brav & Lehavy (2003): Price target revisions contain incremental predictive power beyond earnings forecasts and rating changes.",
        formula_template="group_neutralize(rank(ts_decay_linear(snt1_d1_nettargetpercent, {decay})), {group})",
        typical_decays=[10, 12, 15],
        neutralization_groups=["subindustry", "sector"],
        academic_citation="Brav & Lehavy (2003), Journal of Finance",
        is_high_confidence=True,
    ),
    SentimentArchetype(
        name="Dual Target & Recommendation Alignment",
        category="target_revisions",
        description="Confluence of positive price target raises and buy recommendation upgrades.",
        economic_rationale="Asquith, Mikhail, & Au (2005): Simultaneous agreement across targets and recommendations produces the highest information content.",
        formula_template="group_neutralize(rank(0.55 * rank(ts_decay_linear(snt1_d1_nettargetpercent, {decay})) + 0.45 * rank(ts_decay_linear(snt1_d1_netrecpercent, {decay}))), {group})",
        typical_decays=[10, 12, 15],
        neutralization_groups=["subindustry", "sector"],
        academic_citation="Asquith, Mikhail, & Au (2005), Journal of Financial Economics",
        is_high_confidence=True,
    ),
    SentimentArchetype(
        name="Target Price Revision Velocity",
        category="target_revisions",
        description="First derivative (acceleration) of analyst consensus price targets over trailing 5 days.",
        economic_rationale="Elton, Gruber, & Gultekin (1981): Excess returns are earned by anticipating changes in consensus expectations.",
        formula_template="group_neutralize(rank(ts_delta(ts_decay_linear(snt1_d1_nettargetpercent, {decay}), 5)), {group})",
        typical_decays=[10, 12],
        neutralization_groups=["subindustry", "sector"],
        academic_citation="Elton, Gruber, & Gultekin (1981), Journal of Finance",
        is_high_confidence=False,
    ),

    # -------------------------------------------------------------------------
    # 4. Forecast Dispersion & Divergence
    # -------------------------------------------------------------------------
    SentimentArchetype(
        name="Analyst Forecast Dispersion Penalty",
        category="forecast_dispersion",
        description="Scaled standard deviation of analysts' earnings forecasts.",
        economic_rationale="Diether, Malloy, & Scherbina (2002): High dispersion in earnings forecasts indicates overpricing due to short-sale constraints and predicts future underperformance.",
        formula_template="trade_when(volume > adv20 * 0.8, group_neutralize(rank(- ts_decay_linear(ts_decay_linear(snt1_d1_dtstsespe / (close + 0.001), {decay}), 3)) * rank(ts_decay_linear(ts_decay_linear(snt1_d1_netearningsrevision, {decay}), 3)), {group}), -1)",
        typical_decays=[10, 12, 14, 16],
        neutralization_groups=["subindustry", "sector"],
        academic_citation="Diether, Malloy, & Scherbina (2002), Journal of Finance",
        is_high_confidence=True,
    ),

    # -------------------------------------------------------------------------
    # 5. Dynamic Attention & Behavioral Mood Indices
    # -------------------------------------------------------------------------
    SentimentArchetype(
        name="Dynamic Institutional Attention",
        category="dynamic_attention",
        description="Volume-confirmed dynamic analyst focus ranking.",
        economic_rationale="Da, Engelberg, & Gao (2011): High institutional attention accompanied by volume expansion isolates high-conviction accumulation.",
        formula_template="trade_when(volume > adv20 * 0.85, group_neutralize(rank(ts_decay_linear(snt1_d1_dynamicfocusrank, {decay})), {group}), -1)",
        typical_decays=[10, 12],
        neutralization_groups=["subindustry", "sector"],
        academic_citation="Da, Engelberg, & Gao (2011), Journal of Finance",
        is_high_confidence=True,
    ),
    SentimentArchetype(
        name="Broad Equity Mood Contrarian Reversal",
        category="dynamic_attention",
        description="Fading extreme sentiment waves on individual equities.",
        economic_rationale="Baker & Wurgler (2006, 2007): Broad sentiment disproportionately impacts speculative assets. Fading sentiment extremes captures mean-reverting alpha.",
        formula_template="trade_when(abs(daily_equity_mood_indicator - 50.0) > 20.0, group_neutralize(rank(- ts_decay_linear(daily_equity_mood_indicator - 50.0, {decay})), {group}), -1)",
        typical_decays=[8, 10, 12],
        neutralization_groups=["subindustry", "sector"],
        academic_citation="Baker & Wurgler (2006, 2007), Journal of Economic Perspectives",
        is_high_confidence=True,
    ),
]
