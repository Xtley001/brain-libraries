"""Formula templates for Macroeconomic & Scheduled Event Drift."""
from __future__ import annotations
from brain_options.templates import OptionCandidate

def generate_macro_fomc_cpi_drift_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []
    groups = ["subindustry"]

    # 1. Macro Risk Premium Beta Dispersion (Savor & Wilson 2013)
    # High-beta assets earn disproportionate risk premium during macro resolution windows
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(volume > adv20 * 0.8, group_neutralize(rank(ts_decay_linear(ts_covariance(returns, group_mean(returns, 100, market), 60) * (implied_volatility_call_30 / (implied_volatility_put_30 + 0.001)), 15)), {grp}), -1)",
                archetype_name="Macro Event Beta Risk Drift",
                hypothesis="High systematic beta assets exhibiting bullish options demand capture outsized premium resolution during scheduled macro event cycles.",
                generation_source="template",
            )
        )

    # 2. Pre-FOMC Volatility Uncertainty Resolution (Lucca & Moench 2015)
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(volume > adv20 * 0.8, group_neutralize(rank(ts_decay_linear(-ts_delta(implied_volatility_mean_30, 5) * ts_decay_linear(returns, 10), 12)), {grp}), -1)",
                archetype_name="Pre-Event Volatility Compression Drift",
                hypothesis="Sharply compressing market-wide implied uncertainty catalyzes systematic equity relief rallies in high-liquidity names.",
                generation_source="template",
            )
        )

    # 3. Cross-Sectional Macro Sensitivity Asymmetry
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(abs(rank(implied_volatility_mean_30 / (historical_volatility_30 + 0.001)) - 0.5) > 0.35, group_neutralize(rank(ts_decay_linear((returns - group_mean(returns, 50, {grp})) * (1.0 / (implied_volatility_mean_30 + 0.01)), 16)), {grp}), -1)",
                archetype_name="Macro Spread Volatility Normalization",
                hypothesis="Idiosyncratic return dispersion relative to sector benchmarks normalized by implied risk captures post-announcement mean reversion.",
                generation_source="template",
            )
        )

    return candidates
