"""Templates for WorldQuant Classic Formulaic Alpha Synthesis."""
from __future__ import annotations

from brain_options.templates import OptionCandidate


def generate_formulaic_101_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []
    groups = ["subindustry"]

    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_corr(open, volume, 10)) * -1, {grp})",
                archetype_name="Alpha 6 Price Volume Correlation",
                hypothesis="Alpha #6: Inverse correlation between opening price changes and volume reflects liquidity exhaustion at market open.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(power(high * low, 0.5) - vwap), {grp})",
                archetype_name="Alpha 41 Geometric Mean Skew",
                hypothesis="Alpha #41: Geometric mean of extreme intraday prices relative to volume-weighted average price captures trade skewness.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(group_rank(ts_rank(volume, 20), {grp}) * group_rank(ts_delta(close, 5), {grp}) * -1, {grp})",
                archetype_name="Alpha 54 Volume Weighted Reversal",
                hypothesis="Alpha #54 derivative: High relative volume accompanying rapid short-term price jumps triggers cross-sectional price reversal.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_decay_linear(ts_rank(ts_corr(close, volume, 10), 10), 5)) * -1, {grp})",
                archetype_name="Smoothed Volume Price Distribution",
                hypothesis="Decay-smoothed rank of price-volume correlation detects smart money distribution at cyclical peaks.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(sign(ts_delta(volume, 1)) * (-1 * ts_delta(close, 1))), {grp})",
                archetype_name="Alpha 12 Volume Sign Delta Reversal",
                hypothesis="Alpha #12: Volume expansion coupled with opposite price direction reflects liquidity absorption.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(-ts_max(ts_corr(ts_rank(volume, 5), ts_rank(high, 5), 5), 3)), {grp})",
                archetype_name="Alpha 26 High Volume Max Correlation",
                hypothesis="Alpha #26: High correlation between intraday volume rank and high price rank signals cyclical exhaustion.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(-((ts_delay(close, 20) - ts_delay(close, 10)) / 10.0 - (ts_delay(close, 10) - close) / 10.0)), {grp})",
                archetype_name="Alpha 46 Multi-Horizon Trend Reversal",
                hypothesis="Alpha #46: Multi-horizon velocity differential detects deceleration in equity momentum trend.",
                generation_source="template",
            )
        )

    return candidates
