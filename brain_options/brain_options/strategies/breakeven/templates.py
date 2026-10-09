"""Formula templates for Call Breakeven Hurdle strategies."""
from __future__ import annotations
from brain_options.templates import OptionCandidate

def generate_breakeven_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []
    groups = ["subindustry"]

    # 1. Call Breakeven Hurdle Spread across tenors
    for tenor in [10, 20, 30, 60, 90]:
        for grp in groups:
            candidates.append(
                OptionCandidate(
                    expression=f"group_neutralize(rank((call_breakeven_{tenor} - close) / close), {grp})",
                    archetype_name="Call Breakeven Hurdle Spread",
                    hypothesis=f"Demeaned distance to {tenor}d call breakeven reflects expected upside target priced by option writers.",
                    generation_source="template",
                )
            )

    # 2. Call Breakeven Hurdle Acceleration
    for tenor in [20, 30, 60]:
        for grp in groups:
            candidates.append(
                OptionCandidate(
                    expression=f"group_neutralize(rank(ts_delta((call_breakeven_{tenor} - close) / close, 5)), {grp})",
                    archetype_name="Call Breakeven Hurdle Acceleration",
                    hypothesis=f"Rapidly shifting {tenor}d call breakeven hurdle reveals dealers shifting upside delta barriers.",
                    generation_source="template",
                )
            )

    # 3. Liquidity-Gated Breakeven Surge
    for tenor in [20, 30]:
        for grp in groups:
            candidates.append(
                OptionCandidate(
                    expression=f"trade_when(volume > adv20, group_neutralize(rank((call_breakeven_{tenor} - close) / close), {grp}), -1)",
                    archetype_name="Liquidity-Gated Breakeven Surge",
                    hypothesis="Call breakeven upside signals confirmed by trading volume surges filter out illiquid false signals.",
                    generation_source="template",
                )
            )

    # 4. Liquidity-Gated Breakeven Acceleration (High-confidence)
    for tenor in [20, 30]:
        for grp in groups:
            candidates.append(
                OptionCandidate(
                    expression=f"trade_when(volume > adv20, group_neutralize(rank(ts_decay_linear(ts_delta((call_breakeven_{tenor} - close) / close, 5), 5)), {grp}), -1)",
                    archetype_name="Liquidity-Gated Breakeven Acceleration",
                    hypothesis="Breakeven acceleration smoothed with linear decay and volume gating yields maximal Sharpe with low turnover.",
                    generation_source="template",
                )
            )

    # 5. Tulchinsky Winsorized Robust Breakeven
    for tenor in [30, 60]:
        for grp in groups:
            candidates.append(
                OptionCandidate(
                    expression=f"trade_when(volume > adv20, group_neutralize(rank(ts_decay_linear((call_breakeven_{tenor} - close) / close, 5)), {grp}), -1)",
                    archetype_name="Tulchinsky Winsorized Robust Breakeven",
                    hypothesis="Robust linear decay on call breakeven hurdle suppresses quote noise and prevents backtest overfitting.",
                    generation_source="template",
                )
            )

    # 6. Breakeven Term Structure Slope (30d vs 90d)
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(volume > adv20, group_neutralize(rank(ts_decay_linear((call_breakeven_30 - close) / close - (call_breakeven_90 - close) / close, 5)), {grp}), -1)",
                archetype_name="Breakeven Term Structure",
                hypothesis="Comparing 30d to 90d call breakeven hurdle captures term divergence in option writer upside conviction.",
                generation_source="template",
            )
        )

    # 7. Group-Relative Breakeven Velocity
    for grp in ["subindustry", "industry"]:
        candidates.append(
            OptionCandidate(
                expression=f"group_rank(ts_delta((call_breakeven_20 - close) / close, 5), {grp})",
                archetype_name="Group Relative Breakeven Velocity",
                hypothesis="Group rank of breakeven acceleration isolates idiosyncratic dealer repositioning within peers.",
                generation_source="template",
            )
        )

    return candidates
