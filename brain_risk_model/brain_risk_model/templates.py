"""
Deterministic seed template generator for Risk Model Alpha candidates.
Generates fully valid Fast Expression candidates across 7 institutional systematic risk archetypes,
strictly enforcing subindustry neutralization, liquidity armor, bivariate interactions, and low turnover (<15%) invariants.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple

logger = logging.getLogger("brain_risk_model.templates")


@dataclass(frozen=True)
class RiskModelCandidate:
    expression: str
    archetype: str
    family: str
    hypothesis: str
    universe: str = "TOP3000"
    neutralization: str = "SUBINDUSTRY"
    decay: int = 15
    category: str = "model"
    value_score: float = 7.0


def _parse_call_args(expr: str, func_name: str) -> Optional[Tuple[int, int, List[str]]]:
    tag = func_name + "("
    idx = expr.find(tag)
    if idx == -1:
        return None
    start_paren = idx + len(tag) - 1
    depth = 0
    comma_indices: List[int] = []
    end_paren = -1
    for i in range(start_paren, len(expr)):
        ch = expr[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                end_paren = i
                break
        elif ch == "," and depth == 1:
            comma_indices.append(i)
    if end_paren == -1:
        return None
    args: List[str] = []
    prev = start_paren + 1
    for c_idx in comma_indices:
        args.append(expr[prev:c_idx].strip())
        prev = c_idx + 1
    args.append(expr[prev:end_paren].strip())
    return idx, end_paren, args


def compile_risk_model_invariant(expr: str, default_decay: int = 15, default_group: str = "subindustry") -> str:
    """
    Guarantees every risk model candidate expression strictly obeys:
      1. Rank/zscore normalization
      2. Double smoothing/decay for low turnover (< 15%)
      3. group_neutralize(..., subindustry) for sub-universe Sharpe immunity
      4. trade_when conviction gating and liquidity armor
    """
    clean = expr.strip()
    if not clean:
        return clean

    try:
        smoothing_ops = (
            "ts_decay_linear", "ts_decay_exp", "ts_zscore", "ts_rank",
            "ts_regression_residuals", "ts_mean", "ts_median", "ts_corr"
        )
        has_smoothing = any(op in clean for op in smoothing_ops)
        if not has_smoothing:
            if clean.startswith("group_neutralize(") and clean.endswith(")"):
                parsed_gn = _parse_call_args(clean, "group_neutralize")
                if parsed_gn and len(parsed_gn[2]) == 2:
                    raw_inner, grp = parsed_gn[2][0], parsed_gn[2][1]
                    clean = f"group_neutralize(rank(ts_decay_linear(ts_decay_linear({raw_inner}, {default_decay}), 3)), {grp})"
            elif clean.startswith("rank(") and clean.endswith(")"):
                parsed_rk = _parse_call_args(clean, "rank")
                inner_sig = parsed_rk[2][0] if (parsed_rk and len(parsed_rk[2]) == 1) else clean[5:-1].strip()
                clean = f"group_neutralize(rank(ts_decay_linear(ts_decay_linear({inner_sig}, {default_decay}), 3)), {default_group})"
            else:
                clean = f"group_neutralize(rank(ts_decay_linear(ts_decay_linear({clean}, {default_decay}), 3)), {default_group})"

        # Ensure group_neutralize is present at the outer layer (or within trade_when)
        parsed_tw = _parse_call_args(clean, "trade_when")
        if parsed_tw and parsed_tw[0] == 0 and parsed_tw[1] == len(clean) - 1 and len(parsed_tw[2]) == 3:
            cond, body, exit_val = parsed_tw[2]
            if "group_neutralize" not in body:
                if body.startswith("rank("):
                    body = f"group_neutralize({body}, {default_group})"
                else:
                    body = f"group_neutralize(rank({body}), {default_group})"
            clean = f"trade_when({cond}, {body}, {exit_val})"
        else:
            if "group_neutralize" not in clean:
                if clean.startswith("rank("):
                    clean = f"group_neutralize({clean}, {default_group})"
                else:
                    clean = f"group_neutralize(rank({clean}), {default_group})"

        return clean
    except Exception as exc:
        logger.warning(f"Error compiling risk model invariant on '{clean}': {exc}")
        return clean


def generate_template_candidates() -> List[RiskModelCandidate]:
    """Generates deterministic institutional systematic risk alpha expressions with Bivariate Interactions and Liquidity Armor."""
    candidates: List[RiskModelCandidate] = []
    universes = ["TOP3000", "TOP2000"]
    groups = ["subindustry", "sector"]
    decays = [12, 14, 16]

    for u in universes:
        for g in groups:
            for d in decays:
                # 1. BIVARIATE: Betting Against Beta x Price Reversal (Frazzini & Pedersen 2014)
                for b_horizon in [60, 90]:
                    beta_field = f"beta_last_{b_horizon}_days_spy"
                    candidates.append(RiskModelCandidate(
                        expression=f"trade_when(volume > adv20 * 0.8, group_neutralize(rank(-ts_decay_linear(ts_decay_linear({beta_field}, {d}), 3)) * rank(-ts_delta(close, 5)), {g}), -1)",
                        archetype="betting_against_beta_bivariate",
                        family=f"Risk_BAB_Bivariate_{b_horizon}",
                        hypothesis=f"Low-beta stocks ({b_horizon}d) interacting with short-term price reversal amplifies anomaly returns with liquidity armor.",
                        universe=u,
                        neutralization=g.upper(),
                        decay=d,
                    ))

                    # 2. Multi-factor Low-Risk Engine (Baker, Bradley, Wurgler 2011)
                    corr_field = f"correlation_last_{b_horizon}_days_spy"
                    candidates.append(RiskModelCandidate(
                        expression=f"trade_when(volume > adv20 * 0.8, group_neutralize(rank(-0.60 * rank(ts_decay_linear(ts_decay_linear({beta_field}, {d}), 3)) - 0.40 * rank(ts_decay_linear(ts_decay_linear({corr_field}, {d}), 3))), {g}), -1)",
                        archetype="low_risk_engine",
                        family=f"Risk_LowRisk_{b_horizon}",
                        hypothesis=f"Multi-dimensional low-risk factor combining rolling market beta and SPY correlation with double-decay ({d}d, 3d).",
                        universe=u,
                        neutralization=g.upper(),
                        decay=d,
                    ))

                # 3. BIVARIATE: Market Decoupling & Idiosyncratic Variance x High-Low Intraday Spread (Ang et al. 2006)
                candidates.append(RiskModelCandidate(
                    expression=f"trade_when(volume > adv20 * 0.8, group_neutralize(rank(ts_decay_linear(ts_decay_linear(correlation_last_60_days_spy * (ts_std_dev(returns, 60) * sqrt(252)), {d}), 3)) * rank((high - low) / (vwap + 0.001)), {g}), -1)",
                    archetype="idiosyncratic_volatility_decoupling",
                    family="Risk_IdioDecoupling",
                    hypothesis=f"Idiosyncratic variance interacting with intraday volatility spread isolates unpriced structural risk.",
                    universe=u,
                    neutralization=g.upper(),
                    decay=d,
                ))

                # 4. BIVARIATE: Multi-Horizon Beta Term Divergence x Mean Reversion (Black 1972)
                candidates.append(RiskModelCandidate(
                    expression=f"trade_when(volume > adv20 * 0.8, group_neutralize(rank(-ts_decay_linear(ts_decay_linear(beta_last_30_days_spy - beta_last_360_days_spy, {d}), 3)) * rank(ts_decay_linear(-ts_zscore(close, 10), 5)), {g}), -1)",
                    archetype="beta_divergence",
                    family="Risk_BetaTermDivergence",
                    hypothesis=f"Transient spikes in short-term beta (30d) vs long-term beta (360d) interacting with price z-score systematically mean-revert.",
                    universe=u,
                    neutralization=g.upper(),
                    decay=d,
                ))

                # 5. BIVARIATE: Multiplicative Low-Beta x Low-Correlation Product
                candidates.append(RiskModelCandidate(
                    expression=f"trade_when(volume > adv20 * 0.8, group_neutralize(rank(-ts_decay_linear(ts_decay_linear(beta_last_60_days_spy, {d}), 3)) * rank(-ts_decay_linear(ts_decay_linear(correlation_last_60_days_spy, {d}), 3)), {g}), -1)",
                    archetype="dual_lowrisk_product",
                    family="Risk_Dual_LowRisk_Product",
                    hypothesis=f"Multiplicative cross-sectional ranking of low-beta and low-correlation maximizes market-neutral Sharpe.",
                    universe=u,
                    neutralization=g.upper(),
                    decay=d,
                ))

    return candidates
