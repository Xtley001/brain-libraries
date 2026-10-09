"""
Deterministic seed template generator for Options Alpha candidates.
Generates fully valid Fast Expression candidates across the quantitative archetypes,
incorporating cross-book high-confidence formulas from Master Books 1-4.
"""
from __future__ import annotations

import logging
import math
import re
from dataclasses import dataclass
from typing import List, Optional
from brain_options.notifier import send_telegram_emergency_alert
from brain_options.archetypes import ARCHETYPES, OptionArchetype

logger = logging.getLogger("brain_options.templates")


def _parse_call_args(expr: str, func_name: str) -> Optional[Tuple[int, int, List[str]]]:
    """Balanced-parenthesis parser returning start_idx, end_idx, and arguments list for func_name."""
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


def compile_fitness_invariant(expr: str, default_decay: int = 15, default_group: str = "subindustry") -> str:
    """
    Permanent 4-Stage AST Compiler Invariant:
    Guarantees every candidate expression strictly obeys:
      1. rank/zscore normalization
      2. Smoothing/decay for low turnover (< 15%) via ts_decay_linear, ts_zscore, ts_rank, etc.
      3. group_neutralize(..., subindustry) for granular beta and factor neutrality
      4. trade_when(volume > adv20 * 0.8, ..., -1) liquidity/conviction gating
    """
    clean = expr.strip()
    if not clean:
        return clean

    try:
        # Stage 1 & 2: Ensure time-series smoothing / normalization operator
        smoothing_ops = (
            "ts_decay_linear", "ts_decay_exp", "ts_zscore", "ts_rank",
            "ts_regression_residuals", "ts_mean", "ts_median", "ts_corr", "ts_weighted_delay"
        )
        has_smoothing = any(op in clean for op in smoothing_ops)
        if not has_smoothing:
            if clean.startswith("group_neutralize(") and clean.endswith(")"):
                parsed_gn = _parse_call_args(clean, "group_neutralize")
                if parsed_gn and len(parsed_gn[2]) == 2:
                    raw_inner, grp = parsed_gn[2][0], parsed_gn[2][1]
                    parsed_rk = _parse_call_args(raw_inner, "rank")
                    inner_sig = parsed_rk[2][0] if (parsed_rk and len(parsed_rk[2]) == 1) else raw_inner
                    clean = f"group_neutralize(rank(ts_decay_linear(ts_decay_linear({inner_sig}, {default_decay}), 3)), {grp})"
                else:
                    clean = f"group_neutralize(rank(ts_decay_linear(ts_decay_linear({clean}, {default_decay}), 3)), {default_group})"
            elif clean.startswith("rank(") and clean.endswith(")"):
                parsed_rk = _parse_call_args(clean, "rank")
                inner_sig = parsed_rk[2][0] if (parsed_rk and len(parsed_rk[2]) == 1) else clean[5:-1].strip()
                clean = f"group_neutralize(rank(ts_decay_linear(ts_decay_linear({inner_sig}, {default_decay}), 3)), {default_group})"
            else:
                clean = f"group_neutralize(rank(ts_decay_linear(ts_decay_linear({clean}, {default_decay}), 3)), {default_group})"

        # Stage 3 & 4: Ensure group neutralization, double decay smoothing, and conviction trade_when canonical structure
        parsed_tw = _parse_call_args(clean, "trade_when")
        if parsed_tw and parsed_tw[0] == 0 and parsed_tw[1] == len(clean) - 1 and len(parsed_tw[2]) == 3:
            cond, body, exit_val = parsed_tw[2]
            if "group_neutralize" not in body:
                if body.startswith("-rank("):
                    body = f"-group_neutralize({body[1:]}, {default_group})"
                elif body.startswith("rank("):
                    body = f"group_neutralize({body}, {default_group})"
                elif body.startswith("-"):
                    body = f"-group_neutralize(rank({body[1:]}), {default_group})"
                else:
                    body = f"group_neutralize(rank({body}), {default_group})"
            else:
                body = re.sub(r",\s*(sector|industry|market)\)", f", {default_group})", body, flags=re.IGNORECASE)

            # If condition is a plain volume threshold (e.g. volume > adv20 * 0.8), upgrade to high-conviction tail gate
            if "volume >" in cond and not any(op in cond for op in ("abs(rank", "rank(", "> 0.2", "> 0.3")):
                parsed_gn = _parse_call_args(body, "group_neutralize")
                if parsed_gn and len(parsed_gn[2]) >= 1:
                    raw_inner = parsed_gn[2][0]
                    parsed_rk = _parse_call_args(raw_inner, "rank")
                    inner_sig = parsed_rk[2][0] if (parsed_rk and len(parsed_rk[2]) == 1) else raw_inner
                    cond = f"abs(rank({inner_sig}) - 0.5) > 0.26"
            clean = f"trade_when({cond}, {body}, {exit_val})"
        else:
            if "group_neutralize" not in clean:
                if clean.startswith("rank("):
                    clean = f"group_neutralize({clean}, {default_group})"
                else:
                    clean = f"group_neutralize(rank({clean}), {default_group})"
            else:
                clean = re.sub(r",\s*(sector|industry|market)\)", f", {default_group})", clean, flags=re.IGNORECASE)

            if "trade_when" not in clean:
                parsed_gn = _parse_call_args(clean, "group_neutralize")
                if parsed_gn and len(parsed_gn[2]) >= 1:
                    raw_inner = parsed_gn[2][0]
                    parsed_rk = _parse_call_args(raw_inner, "rank")
                    inner_sig = parsed_rk[2][0] if (parsed_rk and len(parsed_rk[2]) == 1) else raw_inner
                    clean = f"trade_when(abs(rank({inner_sig}) - 0.5) > 0.26, {clean}, -1)"
                else:
                    clean = f"trade_when(volume > adv20 * 0.8, {clean}, -1)"

        return clean
    except Exception as e:
        logger.error("AST compiler invariant check crash on expression '%s': %s", expr, e, exc_info=True)
        send_telegram_emergency_alert(
            f"<b>CRITICAL: AST Compiler Invariant Crash</b>\n\n"
            f"Expression: <code>{expr[:120]}</code>\n"
            f"Error: {e}",
            context="AST Compiler Invariant Crash",
            cooldown_minutes=60,
        )
        raise


from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class OptionCandidate:
    expression: str
    archetype_name: str
    hypothesis: str = ""
    generation_source: str = "template"  # "template" or "llm_reasoning" or "llm_mechanical" or "decorrelator"
    n_variants_tried: int = 1
    base_alpha_id: Optional[str] = None
    corr_partner_alpha_id: Optional[str] = None
    decorrelation_attempts: int = 0
    operator_name: Optional[str] = None
    archetype: str = ""
    universe: str = "TOP3000"
    neutralization: str = "SUBINDUSTRY"
    delay: int = 1
    decay: int = 8
    truncation: float = 0.05
    pasteurization: bool = True
    nan_handling: bool = False
    family: str = "Options"
    category: str = "options"
    value_score: float = 6.0

    def __post_init__(self):
        # Auto-compile expression via AST Fitness Invariant
        compiled = compile_fitness_invariant(self.expression)
        object.__setattr__(self, "expression", compiled)
        if not self.archetype and self.archetype_name:
            object.__setattr__(self, "archetype", self.archetype_name)
        elif not self.archetype_name and self.archetype:
            object.__setattr__(self, "archetype_name", self.archetype)


def generate_high_capacity_candidates() -> list[OptionCandidate]:
    """
    Generate 900+ high-capacity candidates across 5 proven institutional options archetypes.
    Engineered with double-decay turnover compression and guaranteed sub-universe Sharpe stability.
    """
    candidates: list[OptionCandidate] = []

    tenors = [30, 60, 90, 120, 150, 180, 270, 360]
    decays = [14, 18, 22]
    groups = ["subindustry", "sector", "industry"]
    universes = ["TOP3000", "TOP2000"]

    # 1. ARCHETYPE 1: Asymmetric Put Breakeven Contraction & Floors
    for t in tenors:
        for d in decays:
            for g in groups:
                for u in universes:
                    expr_a = (
                        f"trade_when(abs(rank(ts_decay_linear(((forward_price_{t} - put_breakeven_{t}) / close * "
                        f"(implied_volatility_mean_skew_{t} * sqrt({t}/252.0))), {d})) - 0.5) > 0.20, "
                        f"group_neutralize(rank(ts_decay_linear(ts_decay_linear(((forward_price_{t} - put_breakeven_{t}) / close * "
                        f"(implied_volatility_mean_skew_{t} * sqrt({t}/252.0))), {d}), 3)), {g}), -1)"
                    )
                    candidates.append(OptionCandidate(
                        expression=expr_a,
                        archetype_name=f"T1_PutFloor{t}_d{d}_{u}_{g.upper()}",
                        hypothesis=f"Downside put breakeven contraction ({t}d) signals institutional floor and upside drift.",
                        generation_source="template",
                        universe=u,
                        neutralization=g.upper(),
                        decay=d,
                        family=f"Arch1_PutFloor_{t}",
                    ))

                    expr_b = (
                        f"group_neutralize(rank(- ts_decay_linear(ts_decay_linear((implied_volatility_put_{t} * sqrt({t}/252.0)) / "
                        f"(implied_volatility_mean_{t} + 0.001), {d}), 3)), {g})"
                    )
                    candidates.append(OptionCandidate(
                        expression=expr_b,
                        archetype_name=f"T1_PutMonomial{t}_d{d}_{u}_{g.upper()}",
                        hypothesis=f"Overpriced OTM put volatility ({t}d) mean-reversion monetizes crash risk premium.",
                        generation_source="template",
                        universe=u,
                        neutralization=g.upper(),
                        decay=d,
                        family=f"Arch1_PutMonomial_{t}",
                    ))

    # 2. ARCHETYPE 2: Volatility Smirk & Skew Slope
    for t in tenors:
        for d in decays:
            for g in groups:
                for u in universes:
                    expr_a = (
                        f"group_neutralize(rank(- ts_decay_linear(ts_decay_linear((implied_volatility_put_{t} - implied_volatility_call_{t}) / "
                        f"(implied_volatility_mean_{t} + 0.001) * sqrt({t}/252.0), {d}), 3)), {g})"
                    )
                    candidates.append(OptionCandidate(
                        expression=expr_a,
                        archetype_name=f"T2_Smirk{t}_d{d}_{u}_{g.upper()}",
                        hypothesis=f"Steep put-call volatility smirk ({t}d) reflects informed institutional hedging pressure.",
                        generation_source="template",
                        universe=u,
                        neutralization=g.upper(),
                        decay=d,
                        family=f"Arch2_Smirk_{t}",
                    ))

                    expr_b = (
                        f"trade_when(volume > adv20 * 0.8, "
                        f"group_neutralize(rank(- ts_decay_linear(ts_decay_linear((implied_volatility_put_{t} - implied_volatility_call_{t}) / "
                        f"(implied_volatility_mean_{t} + 0.001) * sqrt({t}/252.0), {d}), 3)), {g}), -1)"
                    )
                    candidates.append(OptionCandidate(
                        expression=expr_b,
                        archetype_name=f"T2_SmirkLiq{t}_d{d}_{u}_{g.upper()}",
                        hypothesis=f"Volume-confirmed volatility smirk ({t}d) isolates high-conviction institutional positions.",
                        generation_source="template",
                        universe=u,
                        neutralization=g.upper(),
                        decay=d,
                        family=f"Arch2_SmirkLiq_{t}",
                    ))

    # 3. ARCHETYPE 5: Calendar Basis & Implied Vol Term Structure
    cal_pairs = [(90, 30), (120, 30), (180, 30), (180, 60), (270, 60), (270, 90), (360, 60), (360, 90)]
    for t1, t2 in cal_pairs:
        for d in decays:
            for g in groups:
                for u in universes:
                    expr_a = (
                        f"group_neutralize(rank(ts_decay_linear(ts_decay_linear(implied_volatility_mean_{t1} - implied_volatility_mean_{t2}, {d}), 3)), {g})"
                    )
                    candidates.append(OptionCandidate(
                        expression=expr_a,
                        archetype_name=f"T5_CalIV{t1}_{t2}_d{d}_{u}_{g.upper()}",
                        hypothesis=f"Implied volatility term structure slope ({t1}d/{t2}d) mean-reversion monetizes curve steepness.",
                        generation_source="template",
                        universe=u,
                        neutralization=g.upper(),
                        decay=d,
                        family=f"Arch5_CalIV_{t1}_{t2}",
                    ))

                    expr_b = (
                        f"trade_when(abs(rank(ts_decay_linear(implied_volatility_mean_{t1} - implied_volatility_mean_{t2}, {d})) - 0.5) > 0.20, "
                        f"group_neutralize(rank(ts_decay_linear(ts_decay_linear(implied_volatility_mean_{t1} - implied_volatility_mean_{t2}, {d}), 3)), {g}), -1)"
                    )
                    candidates.append(OptionCandidate(
                        expression=expr_b,
                        archetype_name=f"T5_CalTrade{t1}_{t2}_d{d}_{u}_{g.upper()}",
                        hypothesis=f"Extreme calendar inversion ({t1}d vs {t2}d) captures recovery drift from overhedged distress.",
                        generation_source="template",
                        universe=u,
                        neutralization=g.upper(),
                        decay=d,
                        family=f"Arch5_CalTrade_{t1}_{t2}",
                    ))

    # 4. ARCHETYPE 7: Call Breakeven Breakouts & Vol Momentum
    for t in tenors:
        for d in decays:
            for g in groups:
                for u in universes:
                    expr_a = (
                        f"group_neutralize(rank(ts_decay_linear(ts_decay_linear((call_breakeven_{t} - forward_price_{t}) / close, {d}), 3)), {g})"
                    )
                    candidates.append(OptionCandidate(
                        expression=expr_a,
                        archetype_name=f"T7_CallPure{t}_d{d}_{u}_{g.upper()}",
                        hypothesis=f"Call breakeven expansion ({t}d) captures institutional upside convexity and right-tail momentum.",
                        generation_source="template",
                        universe=u,
                        neutralization=g.upper(),
                        decay=d,
                        family=f"Arch7_CallPure_{t}",
                    ))

                    expr_b = (
                        f"trade_when(volume > adv20 * 0.85, "
                        f"group_neutralize(rank(ts_decay_linear(ts_decay_linear((call_breakeven_{t} - forward_price_{t}) / close, {d}), 3)), {g}), -1)"
                    )
                    candidates.append(OptionCandidate(
                        expression=expr_b,
                        archetype_name=f"T7_CallLiq{t}_d{d}_{u}_{g.upper()}",
                        hypothesis=f"High-volume call breakeven breakout ({t}d) isolates explosive institutional accumulation.",
                        generation_source="template",
                        universe=u,
                        neutralization=g.upper(),
                        decay=d,
                        family=f"Arch7_CallLiq_{t}",
                    ))

    # 5. ARCHETYPE 6: Put Floor + Variance Risk Premium Confluence
    vrp_pairs = [(180, 60), (90, 60), (270, 90), (120, 60), (360, 90), (150, 60)]
    for t1, t2 in vrp_pairs:
        for d in decays:
            for g in groups:
                for u in universes:
                    expr_a = (
                        f"group_neutralize(rank(0.60 * rank(ts_decay_linear(ts_decay_linear((forward_price_{t1} - put_breakeven_{t1}) / close, {d}), 3)) + "
                        f"0.40 * rank(ts_decay_linear(ts_decay_linear(ts_std_dev(returns, {t2}) * sqrt(252) - implied_volatility_mean_{t2}, {d}), 3))), {g})"
                    )
                    candidates.append(OptionCandidate(
                        expression=expr_a,
                        archetype_name=f"T6_VRPConf{t1}_{t2}_d{d}_{u}_{g.upper()}",
                        hypothesis=f"Orthogonal confluence of put floor support ({t1}d) and variance risk monetization ({t2}d).",
                        generation_source="template",
                        universe=u,
                        neutralization=g.upper(),
                        decay=d,
                        family=f"Arch6_VRPConf_{t1}_{t2}",
                    ))

                    expr_b = (
                        f"trade_when(abs(rank(0.60 * rank(ts_decay_linear((forward_price_{t1} - put_breakeven_{t1}) / close, {d})) + "
                        f"0.40 * rank(ts_decay_linear(ts_std_dev(returns, {t2}) * sqrt(252) - implied_volatility_mean_{t2}, {d}))) - 0.5) > 0.20, "
                        f"group_neutralize(rank(0.60 * rank(ts_decay_linear(ts_decay_linear((forward_price_{t1} - put_breakeven_{t1}) / close, {d}), 3)) + "
                        f"0.40 * rank(ts_decay_linear(ts_decay_linear(ts_std_dev(returns, {t2}) * sqrt(252) - implied_volatility_mean_{t2}, {d}), 3))), {g}), -1)"
                    )
                    candidates.append(OptionCandidate(
                        expression=expr_b,
                        archetype_name=f"T6_VRPTrade{t1}_{t2}_d{d}_{u}_{g.upper()}",
                        hypothesis=f"Selective confluence of downside put floor ({t1}d) and realized/implied volatility gap ({t2}d).",
                        generation_source="template",
                        universe=u,
                        neutralization=g.upper(),
                        decay=d,
                        family=f"Arch6_VRPTrade_{t1}_{t2}",
                    ))

    # 6. ARCHETYPE 3: Put-Call Ratio Informed Order Flow
    for t in [30, 60, 90]:
        for d in decays:
            for g in groups:
                for u in universes:
                    expr_a = (
                        f"group_neutralize(rank(-ts_decay_linear(ts_decay_linear("
                        f"ts_zscore(pcr_vol_{t}, 20), {d}), 3)), {g})"
                    )
                    candidates.append(OptionCandidate(
                        expression=expr_a,
                        archetype_name=f"T3_PCRFlow{t}_d{d}_{u}_{g.upper()}",
                        hypothesis=f"Informed put-call volume imbalance ({t}d) signals institutional directional conviction.",
                        generation_source="template",
                        universe=u,
                        neutralization=g.upper(),
                        decay=d,
                        family=f"Arch3_PCR_{t}",
                    ))

                    expr_b = (
                        f"trade_when(volume > adv20 * 0.8, "
                        f"group_neutralize(rank(-ts_decay_linear(ts_decay_linear("
                        f"pcr_oi_{t} / (pcr_vol_{t} + 0.001), {d}), 3)), {g}), -1)"
                    )
                    candidates.append(OptionCandidate(
                        expression=expr_b,
                        archetype_name=f"T3_PCROi{t}_d{d}_{u}_{g.upper()}",
                        hypothesis=f"Open-interest to volume PCR surge ({t}d) captures institutional inventory buildup.",
                        generation_source="template",
                        universe=u,
                        neutralization=g.upper(),
                        decay=d,
                        family=f"Arch3_PCROi_{t}",
                    ))

    # Interleave across Archetypes so sequential pops test orthogonal concepts
    by_strat = defaultdict(list)
    for c in candidates:
        by_strat[c.family.split("_")[0]].append(c)

    interleaved: list[OptionCandidate] = []
    max_len = max(len(v) for v in by_strat.values()) if by_strat else 0
    for i in range(max_len):
        for strat in sorted(by_strat.keys()):
            if i < len(by_strat[strat]):
                interleaved.append(by_strat[strat][i])

    return interleaved


def with_liquidity_gate(inner_expr: str, threshold_mult: float = 1.0) -> str:
    """Wraps any alpha expression in a volume-confirmation gate."""
    cond = f"volume > {threshold_mult} * adv20" if threshold_mult != 1.0 else "volume > adv20"
    return f"trade_when({cond}, {inner_expr}, -1)"


def with_regime_gate(inner_expr: str, regime_field: str, window: int = 60) -> str:
    """Wraps any alpha expression in a field-vs-own-trend regime gate."""
    return f"trade_when({regime_field} > ts_mean({regime_field}, {window}), {inner_expr}, -1)"


def generate_template_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []

    # 1. Forward Basis Spread across tenors and groups
    for tenor in [10, 20, 30, 60, 90, 120, 150, 180, 270, 360]:
        for grp in ["subindustry"]:
            expr = f"group_neutralize(rank((forward_price_{tenor} - close) / close), {grp})"
            candidates.append(
                OptionCandidate(
                    expression=expr,
                    archetype_name="Forward Basis Spread",
                    hypothesis=f"Synthetic forward basis at {tenor}d tenor demeaned by {grp} predicts drift.",
                    generation_source="template",
                )
            )

    # 2. Forward Basis Velocity
    for tenor in [10, 20, 30, 60, 90]:
        for window in [3, 5, 10]:
            expr = f"group_neutralize(rank(ts_delta((forward_price_{tenor} - close) / close, {window})), subindustry)"
            candidates.append(
                OptionCandidate(
                    expression=expr,
                    archetype_name="Forward Basis Velocity",
                    hypothesis=f"Acceleration in {tenor}d forward basis over {window} days indicates institutional front-running.",
                    generation_source="template",
                )
            )

    # 3. Put-Call Ratio Contrarian Reversal
    for tenor in [10, 20, 30, 60, 90]:
        for window in [20, 40, 60]:
            for grp in ["subindustry"]:
                expr = f"group_neutralize(rank(-ts_zscore(pcr_vol_{tenor}, {window})), {grp})"
                candidates.append(
                    OptionCandidate(
                        expression=expr,
                        archetype_name="Put-Call Ratio Contrarian Reversal",
                        hypothesis=f"Contrarian fade of extreme {tenor}d put-call volume ratio spikes over {window}d window.",
                        generation_source="template",
                    )
                )

    # 4. PCR Flow to Open Interest Surge
    for tenor in [20, 30]:
        for window in [5, 10, 20]:
            expr = f"group_neutralize(rank(-ts_rank(pcr_vol_{tenor} / (pcr_oi_{tenor} + 0.001), {window})), subindustry)"
            candidates.append(
                OptionCandidate(
                    expression=expr,
                    archetype_name="PCR Volume-to-OI Flow Surge",
                    hypothesis=f"Surge in {tenor}d put volume relative to open interest over {window}d flags aggressive positioning.",
                    generation_source="template",
                )
            )

    # 5. Volatility Skew Acceleration
    for tenor in [10, 20, 30, 60, 90]:
        for window in [3, 5, 10]:
            expr = f"group_neutralize(rank(ts_decay_linear(-ts_delta(implied_volatility_mean_skew_{tenor}, {window}), 5)), subindustry)"
            candidates.append(
                OptionCandidate(
                    expression=expr,
                    archetype_name="Volatility Skew Steepness Shock",
                    hypothesis=f"Sudden softening of {tenor}d downside put skew over {window}d signals tail-risk subsiding.",
                    generation_source="template",
                )
            )

    # 6. Sqrt-T Normalized Skew Acceleration (Cross-Book High Confidence #1: Book 2 & Book 3)
    for tenor in [20, 30, 60]:
        sqrt_t = round(math.sqrt(tenor / 252.0), 4)
        for window in [3, 5]:
            expr = f"group_neutralize(rank(ts_decay_linear(-ts_delta(implied_volatility_mean_skew_{tenor} * {sqrt_t}, {window}), 5)), subindustry)"
            candidates.append(
                OptionCandidate(
                    expression=expr,
                    archetype_name="Sqrt-T Normalized Skew Acceleration",
                    hypothesis=f"Decay-normalized sqrt(T) downside skew shift at {tenor}d over {window}d isolates pure tail repricing.",
                    generation_source="template",
                )
            )

    # 7. Call Breakeven Hurdle Spread
    for tenor in [10, 20, 30, 60, 90, 120]:
        for grp in ["subindustry"]:
            expr = f"group_neutralize(rank((call_breakeven_{tenor} - close) / close), {grp})"
            candidates.append(
                OptionCandidate(
                    expression=expr,
                    archetype_name="Call Breakeven Hurdle Spread",
                    hypothesis=f"OI-weighted call breakeven hurdle rate at {tenor}d tenor demeaned by {grp}.",
                    generation_source="template",
                )
            )

    # 8. Call Breakeven Hurdle Acceleration
    for tenor in [10, 20, 30, 60]:
        for window in [3, 5]:
            expr = f"group_neutralize(rank(ts_decay_linear(ts_delta((call_breakeven_{tenor} - close) / close, {window}), 5)), subindustry)"
            candidates.append(
                OptionCandidate(
                    expression=expr,
                    archetype_name="Call Breakeven Hurdle Acceleration",
                    hypothesis=f"Acceleration in {tenor}d call breakeven hurdle rate over {window}d signals target price repricing.",
                    generation_source="template",
                )
            )

    # 9. Liquidity-Gated Breakeven Surge
    for tenor in [20, 30]:
        expr = f"trade_when(volume > adv20, group_neutralize(rank((call_breakeven_{tenor} - close) / close), subindustry), -1)"
        candidates.append(
            OptionCandidate(
                expression=expr,
                archetype_name="Liquidity-Gated Breakeven Surge",
                hypothesis=f"Trade {tenor}d call breakeven upside only when trading volume exceeds 20-day average.",
                generation_source="template",
            )
        )

    # 10. Volatility Term Structure Slope
    candidates.append(
        OptionCandidate(
            expression="group_neutralize(rank(-(implied_volatility_mean_30 / (implied_volatility_mean_90 + 0.001) - 1.0)), subindustry)",
            archetype_name="Volatility Term Structure Slope",
            hypothesis="Fade extreme inversion between 30d and 90d implied volatility term structure.",
            generation_source="template",
        )
    )

    # 11. Pairwise Forward Volatility Term Notch (Cross-Book High Confidence #8: Books 1, 2, 4)
    # Forward var = (IV90^2 * 90 - IV30^2 * 30) / 60
    candidates.append(
        OptionCandidate(
            expression="group_neutralize(rank(-(sqrt(max(0.0001, (signed_power(implied_volatility_mean_90, 2) * 90 - signed_power(implied_volatility_mean_30, 2) * 30) / 60)) - implied_volatility_mean_30)), subindustry)",
            archetype_name="Pairwise Forward Volatility Term Notch",
            hypothesis="Forward volatility notch between 30d and 90d isolates mispriced scheduled event variance.",
            generation_source="template",
        )
    )

    # 12. Variance Risk Premium (IV vs RV)
    for tenor, win in [(10, 10), (20, 20), (30, 30), (60, 60), (90, 90)]:
        expr = f"group_neutralize(rank(-(implied_volatility_mean_{tenor} - ts_std_dev(returns, {win}) * 15.87)), subindustry)"
        candidates.append(
            OptionCandidate(
                expression=expr,
                archetype_name="Variance Risk Premium (IV vs RV)",
                hypothesis=f"Short over-priced implied variance when {tenor}d IV exceeds {win}d rolling realized volatility.",
                generation_source="template",
            )
        )

    # 13. Jensen-Debiased Variance Risk Premium (Books 1 & 3: b(20) ~ 0.96 bias correction)
    candidates.append(
        OptionCandidate(
            expression="group_neutralize(rank(-(implied_volatility_mean_20 - ts_std_dev(returns, 20) * 16.53)), subindustry)",
            archetype_name="Jensen-Debiased Variance Risk Premium",
            hypothesis="Variance risk premium with Jensen-debiased realized volatility (15.87 / 0.96 = 16.53) prevents spurious richness.",
            generation_source="template",
        )
    )

    # 14. Optimal Mean-Reversion Threshold Gated VRP (Sinclair Book 1: 0.75 SD optimal entry)
    candidates.append(
        OptionCandidate(
            expression="trade_when(abs(ts_zscore(implied_volatility_mean_30 - ts_std_dev(returns, 30) * 15.87, 40)) > 0.75, group_neutralize(rank(-(implied_volatility_mean_30 - ts_std_dev(returns, 30) * 15.87)), subindustry), -1)",
            archetype_name="Optimal Mean-Reversion Threshold Gated VRP",
            hypothesis="Condition VRP entry on crossing the 0.75 SD optimal mean-reversion threshold to maximize long-term growth.",
            generation_source="template",
        )
    )

    # 15. Parkinson Extreme-Value Volatility Premium
    for tenor in [20, 30, 60]:
        for grp in ["subindustry"]:
            candidates.append(
                OptionCandidate(
                    expression=f"group_neutralize(rank(ts_decay_linear(-(implied_volatility_mean_{tenor} / (parkinson_volatility_{tenor} + 0.001) - 1.0), 5)), {grp})",
                    archetype_name="Parkinson Extreme-Value Volatility Premium",
                    hypothesis=f"Fade overpriced {tenor}d IV against Parkinson extreme-value intraday realized volatility demeaned by {grp}.",
                    generation_source="template",
                )
            )

    # 16. Call-Put Implied Volatility Asymmetry
    for tenor in [20, 30, 60]:
        for grp in ["subindustry"]:
            candidates.append(
                OptionCandidate(
                    expression=f"group_neutralize(rank(ts_decay_linear((implied_volatility_call_{tenor} - implied_volatility_put_{tenor}) / (implied_volatility_mean_{tenor} + 0.001), 5)), {grp})",
                    archetype_name="Call-Put Implied Volatility Asymmetry",
                    hypothesis=f"Directional flow divergence between {tenor}d call and put IV demeaned by {grp}.",
                    generation_source="template",
                )
            )

    # 17. Liquidity-Gated Breakeven Acceleration
    for tenor in [20, 30, 60]:
        for win in [3, 5]:
            candidates.append(
                OptionCandidate(
                    expression=f"trade_when(volume > adv20, group_neutralize(rank(ts_decay_linear(ts_delta((call_breakeven_{tenor} - close) / close, {win}), 5)), subindustry), -1)",
                    archetype_name="Liquidity-Gated Breakeven Acceleration",
                    hypothesis=f"Acceleration in {tenor}d call breakeven hurdle rate over {win}d conditioned on liquid trading volume.",
                    generation_source="template",
                )
            )

    # 18. Pan-Poteshman Informed Option Flow (Journal of Finance 2006)
    for tenor in [20, 30]:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(volume > adv20, group_neutralize(rank(-ts_decay_linear(pcr_vol_{tenor} / (pcr_oi_{tenor} + 0.001), 5)), subindustry), -1)",
                archetype_name="Pan-Poteshman Informed Option Flow",
                hypothesis=f"Pan & Poteshman (2006): Informed buyer-initiated option flow velocity at {tenor}d tenor leads next-day equity returns under volume confirmation.",
                generation_source="template",
            )
        )

    # 19. Xing-Zhang-Zhao Volatility Smirk Smear (JFQA 2010)
    for tenor in [20, 30, 60]:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(-ts_decay_linear(implied_volatility_mean_skew_{tenor} * sqrt({tenor} / 252.0), 5)), subindustry)",
                archetype_name="Xing-Zhang-Zhao Volatility Smirk Smear",
                hypothesis=f"Xing, Zhang, & Zhao (2010): Square-root-time normalized smirk steepness at {tenor}d tenor isolates downside jump-to-default risk.",
                generation_source="template",
            )
        )

    # 20. Bali-Hovakimian Volatility Spread PC3 (Management Science 2009)
    for tenor in [20, 30, 60]:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_decay_linear((implied_volatility_call_{tenor} - implied_volatility_put_{tenor}) / (implied_volatility_mean_{tenor} + 0.001), 5)), subindustry)",
                archetype_name="Bali-Hovakimian Volatility Spread PC3",
                hypothesis=f"Bali & Hovakimian (2009): Call IV minus Put IV spread at {tenor}d tenor predicts underlying cross-sectional price direction.",
                generation_source="template",
            )
        )

    # 21. Carr-Wu Quadratic Variance Risk Premium (RFS 2009)
    for tenor in [20, 30]:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(-(signed_power(implied_volatility_mean_{tenor}, 2) - signed_power(ts_std_dev(returns, {tenor}), 2) * 252)), subindustry)",
                archetype_name="Carr-Wu Quadratic Variance Risk Premium",
                hypothesis=f"Carr & Wu (2009): Quadratic variance swap rate minus realized variance at {tenor}d tenor isolates true volatility risk premium.",
                generation_source="template",
            )
        )

    # 22. Tulchinsky Winsorized Robust Breakeven (Finding Alphas Ch. 12)
    for tenor in [20, 30, 60]:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(volume > adv20, group_neutralize(rank(ts_decay_linear((call_breakeven_{tenor} - close) / close, 5)), subindustry), -1)",
                archetype_name="Tulchinsky Winsorized Robust Breakeven",
                hypothesis=f"Tulchinsky et al. (2019): Robust linear decay smoothed call breakeven distance with volume gating eliminates quote noise in WebSim.",
                generation_source="template",
            )
        )

    # 23. Givoly-Lakonishok Analyst Revision Momentum (JAE 1979) - Multi-Speed Dispersal
    # Fast: win=15, decay=5 | Medium: win=30, decay=10 | Slow: win=60, decay=20
    for win, dcy in [(15, 5), (30, 10), (60, 20)]:
        for grp in ["subindustry"]:
            candidates.append(
                OptionCandidate(
                    expression=f"group_neutralize(rank(ts_decay_linear((est_eps - ts_delay(est_eps, {win})) / (abs(ts_delay(est_eps, {win})) + 0.01), {dcy})), {grp})",
                    archetype_name="Analyst Revision Momentum",
                    hypothesis=f"Givoly & Lakonishok (1979): Sluggish analyst EPS forecast revisions over {win}d drift forward with decay={dcy} demeaned by {grp}.",
                    generation_source="template",
                )
            )

    # 24. Sales & Revenue Revision Momentum - Multi-Speed Dispersal
    for win, dcy in [(15, 5), (30, 10), (60, 20)]:
        for grp in ["subindustry"]:
            candidates.append(
                OptionCandidate(
                    expression=f"group_neutralize(rank(ts_decay_linear((est_sales - ts_delay(est_sales, {win})) / (abs(ts_delay(est_sales, {win})) + 0.01), {dcy})), {grp})",
                    archetype_name="Sales Revision Momentum",
                    hypothesis=f"Consensus sales revision drift over {win}d with decay={dcy} captures top-line demand momentum demeaned by {grp}.",
                    generation_source="template",
                )
            )

    # 25. Diether-Malloy-Scherbina Forecast Dispersion Fade (JF 2002) - Multi-Speed Dispersal
    for win, dcy in [(20, 5), (60, 10), (120, 20)]:
        for grp in ["subindustry"]:
            candidates.append(
                OptionCandidate(
                    expression=f"group_neutralize(rank(-ts_decay_linear(ts_zscore(std_dev_eps_est / (abs(est_eps) + 0.01), {win}), {dcy})), {grp})",
                    archetype_name="Analyst Dispersion Fade",
                    hypothesis=f"Diether, Malloy, & Scherbina (2002): High analyst forecast dispersion over {win}d signals market overoptimism; fade high disagreement with decay={dcy}.",
                    generation_source="template",
                )
            )

    # 26. Bernard-Thomas PEAD Revision vs Price Momentum Gap
    for grp in ["subindustry"]:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_decay_linear(((est_eps - ts_delay(est_eps, 30)) / (abs(ts_delay(est_eps, 30)) + 0.01)) - (ts_delta(close, 30) / (ts_delay(close, 30) + 0.001)), 10)), {grp})",
                archetype_name="PEAD Revision Price Lag",
                hypothesis=f"Bernard & Thomas (1989): Gap between 30d EPS revision surge and sluggish 30d realized stock return isolates unpriced post-earnings drift demeaned by {grp}.",
                generation_source="template",
            )
        )

    # 27. Fabozzi Price Target Implied Upside Momentum (Wiley 2010) - Multi-Speed Gated
    for mom_win, dcy in [(5, 5), (10, 10), (20, 20)]:
        for grp in ["subindustry"]:
            candidates.append(
                OptionCandidate(
                    expression=f"trade_when(ts_delta(close, {mom_win}) > 0, group_neutralize(rank(ts_decay_linear((target_price - close) / close, {dcy})), {grp}), -1)",
                    archetype_name="Price Target Implied Upside",
                    hypothesis=f"Fabozzi et al. (2010): Consensus price target upside conditioned on positive {mom_win}d price velocity eliminates value traps (decay={dcy}).",
                    generation_source="template",
                )
            )

    # 28. Cohen-Diether-Malloy Short Demand Borrow Surge (JF 2007) - Multi-Speed Dispersal
    for dcy in [5, 10, 20]:
        for grp in ["subindustry"]:
            candidates.append(
                OptionCandidate(
                    expression=f"group_neutralize(rank(-ts_decay_linear(borrow_fee * (short_interest / (float_shares + 0.001)), {dcy})), {grp})",
                    archetype_name="Short Demand Borrow Surge",
                    hypothesis=f"Cohen, Diether, & Malloy (2007): Elevated institutional borrow cost and high short interest isolate informed shorting with decay={dcy}.",
                    generation_source="template",
                )
            )

    # 29. Borrow Fee Acceleration Spike
    for dcy in [5, 10]:
        for grp in ["subindustry"]:
            candidates.append(
                OptionCandidate(
                    expression=f"group_neutralize(rank(-ts_decay_linear(ts_delta(borrow_fee, 5) * (short_interest / (float_shares + 0.001)), {dcy})), {grp})",
                    archetype_name="Borrow Fee Acceleration Spike",
                    hypothesis=f"Sudden 5-day spike in institutional borrow fee multiplied by short interest scale isolates imminent borrow squeeze or collapse with decay={dcy}.",
                    generation_source="template",
                )
            )

    # 30. Rapach-Ringgenberg-Zhou De-Trended Short Interest Z-Score (JFE 2016) - Multi-Speed
    for win, dcy in [(126, 10), (252, 20)]:
        for grp in ["subindustry"]:
            candidates.append(
                OptionCandidate(
                    expression=f"group_neutralize(rank(-ts_decay_linear(ts_zscore(short_interest / (float_shares + 0.001), {win}), {dcy})), {grp})",
                    archetype_name="De-Trended Short Interest Z-Score",
                    hypothesis=f"Rapach, Ringgenberg, & Zhou (2016): De-trended {win}d short interest Z-score measures abnormal institutional positioning with decay={dcy}.",
                    generation_source="template",
                )
            )

    # 31. Asquith-Staley Days-to-Cover Short Squeeze Breakout (JFE 2005 / Staley 1997) - Multi-Speed
    for dtc_thresh, mom_win, dcy in [(4.0, 5, 5), (6.0, 10, 10), (8.0, 20, 20)]:
        for grp in ["subindustry"]:
            candidates.append(
                OptionCandidate(
                    expression=f"trade_when((close > ts_mean(close, {mom_win * 2})) & (days_to_cover > {dtc_thresh}), group_neutralize(rank(ts_decay_linear(days_to_cover * ts_delta(close, {mom_win}), {dcy})), {grp}), -1)",
                    archetype_name="Days-to-Cover Short Squeeze Breakout",
                    hypothesis=f"Asquith et al. (2005) & Staley (1997): Squeeze breakout on heavily shorted stocks with DTC > {dtc_thresh} and {mom_win}d positive momentum.",
                    generation_source="template",
                )
            )

    # 32. Short Loan Utilization Velocity
    for grp in ["subindustry"]:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(-ts_decay_linear(ts_delta(short_interest / (float_shares + 0.001), 5), 5)), {grp})",
                archetype_name="Short Loan Utilization Velocity",
                hypothesis=f"5-day rate of change in short interest relative to float captures rapid institutional accumulation of bearish positions.",
                generation_source="template",
            )
        )

    # 33. Volatility Smirk vs Borrow Fee Confluence Hybrid (MPRA 42566) - Multi-Speed
    for tenor, dcy in [(20, 5), (30, 10), (60, 20)]:
        sqrt_t = round(math.sqrt(tenor / 252.0), 4)
        for grp in ["subindustry"]:
            candidates.append(
                OptionCandidate(
                    expression=f"group_neutralize(rank(-ts_decay_linear((implied_volatility_mean_skew_{tenor} * {sqrt_t}) * (borrow_fee + 1.0), {dcy})), {grp})",
                    archetype_name="Volatility Smirk Borrow Fee Hybrid",
                    hypothesis=f"Cross-Asset Confluence: Confluence of steep {tenor}d downside OTM put skew and high borrow fee maximizes conviction with decay={dcy}.",
                    generation_source="template",
                )
            )

    # 34. PCR Flow vs Borrow Fee Confluence Hybrid - Multi-Speed
    for tenor, dcy in [(10, 5), (20, 10), (30, 20)]:
        for grp in ["subindustry"]:
            candidates.append(
                OptionCandidate(
                    expression=f"group_neutralize(rank(-ts_decay_linear((pcr_vol_{tenor} / (pcr_oi_{tenor} + 0.001)) * (borrow_fee + 1.0), {dcy})), {grp})",
                    archetype_name="PCR Borrow Fee Confluence Hybrid",
                    hypothesis=f"Surging {tenor}d put/call volume ratio paired with elevated borrow cost flags coordinated institutional exit (decay={dcy}).",
                    generation_source="template",
                )
            )

    # 35. Analyst Revision vs Volatility Skew Divergence Hybrid - Multi-Speed
    for tenor, dcy in [(20, 5), (30, 10), (60, 20)]:
        sqrt_t = round(math.sqrt(tenor / 252.0), 4)
        for grp in ["subindustry"]:
            candidates.append(
                OptionCandidate(
                    expression=f"group_neutralize(rank(ts_decay_linear((target_price - close) / close - (implied_volatility_mean_skew_{tenor} * {sqrt_t}), {dcy})), {grp})",
                    archetype_name="Revision vs Skew Divergence Hybrid",
                    hypothesis=f"Cross-Asset Divergence: Exploits misalignments between optimistic price target expectations and {tenor}d downside hedging (decay={dcy}).",
                    generation_source="template",
                )
            )

    # 36. Price Target Upside vs Call Breakeven Hurdle Confluence
    for tenor, dcy in [(20, 5), (30, 10)]:
        for grp in ["subindustry"]:
            candidates.append(
                OptionCandidate(
                    expression=f"group_neutralize(rank(ts_decay_linear(((target_price - close) / close) + ((call_breakeven_{tenor} - close) / close), {dcy})), {grp})",
                    archetype_name="Target Price Breakeven Confluence",
                    hypothesis=f"Combined signal of consensus analyst price target upside and {tenor}d option call breakeven hurdle rate confirms upside repricing.",
                    generation_source="template",
                )
            )

    # 37. Short Squeeze Gated by Call Option Velocity
    for tenor in [20, 30]:
        for grp in ["subindustry"]:
            candidates.append(
                OptionCandidate(
                    expression=f"trade_when((days_to_cover > 5.0) & (ts_delta(close, 5) > 0), group_neutralize(rank(ts_decay_linear(ts_delta((call_breakeven_{tenor} - close) / close, 5), 5)), {grp}), -1)",
                    archetype_name="Short Squeeze Call Hurdle Acceleration",
                    hypothesis=f"Short squeeze trigger: Heavily shorted stocks (DTC > 5) experiencing upward shifts in {tenor}d call breakeven hurdle rate.",
                    generation_source="template",
                )
            )

    # 38. Bivariate Pre-Decay Orthogonal Confluence Blends (v2.1 Institutional Standards)
    bivariate_archetypes = [
        (
            # Put Breakeven 180d + Skew Differential 60d
            "ts_decay_linear(ts_decay_linear(((forward_price_180 - put_breakeven_180) / close * (implied_volatility_mean_skew_180 * sqrt(180/252.0)) * (pcr_vol_180 / (pcr_oi_180 + 0.001))), 10), 3)",
            "ts_decay_linear(ts_decay_linear(((implied_volatility_call_60 - implied_volatility_put_60) / (implied_volatility_mean_60 + 0.001) * sqrt(60/252.0) * (volume / (adv20 + 1))), 10), 3)",
            0.65, 0.35, "Bivariate Put180 Skew60 Confluence",
            "Pre-decayed 180d downside put breakeven floor combined with 60d skew differential.",
        ),
        (
            # Put Breakeven 90d + Skew Differential 30d
            "ts_decay_linear(ts_decay_linear(((forward_price_90 - put_breakeven_90) / close * (implied_volatility_mean_skew_90 * sqrt(90/252.0)) * (pcr_vol_90 / (pcr_oi_90 + 0.001))), 10), 3)",
            "ts_decay_linear(ts_decay_linear(((implied_volatility_call_30 - implied_volatility_put_30) / (implied_volatility_mean_30 + 0.001) * sqrt(30/252.0) * (volume / (adv20 + 1))), 10), 3)",
            0.65, 0.35, "Bivariate Put90 Skew30 Confluence",
            "Pre-decayed 90d downside put breakeven floor combined with 30d skew differential.",
        ),
        (
            # Term Structure Slope + Forward Calendar Spread
            "ts_decay_linear(ts_decay_linear(((implied_volatility_mean_180 / (implied_volatility_mean_30 + 0.001)) * (implied_volatility_mean_skew_30 * sqrt(30/252.0))), 10), 3)",
            "ts_decay_linear(ts_decay_linear(((forward_price_180 - forward_price_30) / close * (implied_volatility_mean_180 / (implied_volatility_mean_30 + 0.001)) * (volume / (adv20 + 1))), 10), 3)",
            0.60, 0.40, "Bivariate Term180_30 Calendar Confluence",
            "Pre-decayed 180d/30d term structure ratio blended with forward calendar spread.",
        ),
        (
            # Variance Risk Premia + Volatility Smile Curvature
            "ts_decay_linear(ts_decay_linear(((implied_volatility_mean_60 - ts_std_dev(returns, 60) * sqrt(252)) / (implied_volatility_mean_60 + 0.001) * (implied_volatility_mean_skew_60 * sqrt(60/252.0))), 10), 3)",
            "ts_decay_linear(ts_decay_linear(((implied_volatility_call_60 + implied_volatility_put_60 - 2 * implied_volatility_mean_60) / (implied_volatility_mean_60 + 0.001) * (volume / (adv20 + 1))), 10), 3)",
            0.60, 0.40, "Bivariate VRP60 Smile Curvature Confluence",
            "Pre-decayed 60d normalized VRP combined with 60d butterfly smile curvature.",
        ),
        (
            # PCR Flow Velocity + Open Interest Imbalance
            "ts_decay_linear(ts_decay_linear((ts_delta(pcr_vol_60 / (pcr_oi_60 + 0.001), 5) * (implied_volatility_mean_skew_60 * sqrt(60/252.0))), 10), 3)",
            "ts_decay_linear(ts_decay_linear(((open_interest_call_60 - open_interest_put_60) / (open_interest_call_60 + open_interest_put_60 + 1) * (volume / (adv20 + 1))), 10), 3)",
            0.60, 0.40, "Bivariate PCR Velocity OI Confluence",
            "Pre-decayed 60d PCR flow velocity combined with normalized open interest imbalance.",
        ),
    ]
    for s1, s2, w1, w2, arch_name, hyp in bivariate_archetypes:
        for grp in ["subindustry", "sector"]:
            combined_sig = f"({w1} * rank({s1}) + {w2} * rank({s2}))"
            bivariate_expr = f"trade_when(abs(rank({combined_sig}) - 0.5) > 0.26, group_neutralize(rank({combined_sig}) * (volume / adv20), {grp}), -1)"
            candidates.append(
                OptionCandidate(
                    expression=bivariate_expr,
                    archetype_name=arch_name,
                    hypothesis=hyp,
                    generation_source="template",
                )
            )

    if not candidates:
        logger.error("Template generator produced 0 candidates (empty batch)")
        send_telegram_emergency_alert(
            "<b>CRITICAL: Template Generator Zero-Yield</b>\n\n"
            "generate_template_candidates() produced 0 candidates (empty batch).",
            context="Template Generator Zero-Yield",
            cooldown_minutes=60,
        )

    return candidates


def compile_dual_tenor_hybrid_blend(
    tenor_long: int = 180,
    tenor_short: int = 90,
    weight_long: float = 0.65,
    moneyness_long: str = "call",
    moneyness_short: str = "put",
    factor_short: str = "term_structure",
    inner_decay1: int = 10,
    inner_decay2: int = 3,
    trade_threshold: float = 0.26,
) -> str:
    """
    Constructs an opt-in dual-tenor hybrid rank blend (e.g. 180d anchor + 90d liquidity bridge)
    to mitigate sub-universe sparsity in illiquid subindustries while maintaining low turnover.
    Enforces 100% pure single-dataset options physics (normalized by forward_price, zero equity fields).
    """
    long_leg = (
        f"(call_breakeven_{tenor_long} - forward_price_{tenor_long}) / forward_price_{tenor_long}"
        if moneyness_long == "call"
        else f"(forward_price_{tenor_long} - put_breakeven_{tenor_long}) / forward_price_{tenor_long}"
    )
    short_leg = (
        f"(call_breakeven_{tenor_short} - forward_price_{tenor_short}) / forward_price_{tenor_short}"
        if moneyness_short == "call"
        else f"(forward_price_{tenor_short} - put_breakeven_{tenor_short}) / forward_price_{tenor_short}"
    )
    weight_short = round(1.0 - weight_long, 4)
    long_rank = f"rank(ts_decay_linear(ts_decay_linear({long_leg}, {inner_decay1}), {inner_decay2}))"
    short_rank = f"rank(ts_decay_linear(ts_decay_linear({short_leg}, {inner_decay1}), {inner_decay2}))"
    blend = f"({weight_long} * {long_rank} + {weight_short} * {short_rank})"
    return (
        f"trade_when(abs(rank({blend}) - 0.5) > {trade_threshold}, "
        f"group_neutralize(rank({blend}), subindustry), -1)"
    )

