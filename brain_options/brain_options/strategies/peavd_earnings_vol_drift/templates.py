"""Formula templates for Post-Earnings Announcement Volatility Drift (PEAVD)."""
from __future__ import annotations
from brain_options.templates import OptionCandidate

def generate_peavd_earnings_vol_drift_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []
    groups = ["subindustry"]

    # 1. Earnings Surprise x Options IV Slope (Ball & Brown 1968, Patel & Wolfson 1984)
    for window in [40, 60]:
        for grp in groups:
            candidates.append(
                OptionCandidate(
                    expression=f"group_neutralize(rank(ts_decay_linear(ts_zscore(eps_surprise, {window}) * (implied_volatility_mean_30 / (implied_volatility_mean_90 + 0.001)), 20)), {grp})",
                    archetype_name="PEAVD Surprise IV Ratio",
                    hypothesis=f"Earnings surprises scaled by front-to-back IV term structure slope identify persistent post-earnings drift over {window}d lookback.",
                    generation_source="template",
                )
            )

    # 2. Conviction-Gated Earnings Surprise Drift
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(abs(rank(ts_decay_linear(ts_zscore(eps_surprise, 60), 20)) - 0.5) > 0.35, group_neutralize(rank(ts_decay_linear(ts_zscore(eps_surprise, 60), 20)), {grp}), -1)",
                archetype_name="Conviction Gated PEAD Drift",
                hypothesis="High-conviction tail earnings surprises isolate top/bottom 15% earners, reducing churn and boosting Fitness.",
                generation_source="template",
            )
        )

    # 3. Earnings Surprise x Forward Parity Confluence
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_decay_linear(ts_zscore(eps_surprise, 40) * (call_breakeven_30 - forward_price_30) / close, 15)), {grp})",
                archetype_name="Earnings Surprise Forward Basis Confluence",
                hypothesis="Firms with positive earnings surprises and cheap options forward parity drift deliver maximal risk-adjusted Sharpe.",
                generation_source="template",
            )
        )

    # 4. Earnings Surprise vs Price Reaction Lag
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_decay_linear(ts_zscore(eps_surprise, 60) - ts_zscore(ts_decay_linear(returns, 10), 20), 15)), {grp})",
                archetype_name="PEAD Price Under-Reaction Spread",
                hypothesis="Stocks where earnings surprises exceed short-term price adjustments exploit delayed market incorporation.",
                generation_source="template",
            )
        )

    return candidates
