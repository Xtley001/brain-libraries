"""Formula templates for Capital Investment & Asset Growth Anomalies."""
from __future__ import annotations
from brain_options.templates import OptionCandidate

def generate_capex_asset_growth_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []
    groups = ["subindustry"]

    # 1. Total Asset Growth Anomaly (Cooper, Gulen, Schill 2008)
    # Asset growth is negatively correlated with future stock returns (overinvestment / empire building)
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(volume > adv20 * 0.8, group_neutralize(rank(ts_decay_linear(-ts_delta(total_assets, 252) / (ts_delay(total_assets, 252) + 1.0), 20)), {grp}), -1)",
                archetype_name="Total Asset Growth Inversion",
                hypothesis="Firms with high total asset growth persistently underperform due to corporate empire building, misallocation, and earnings dilution.",
                generation_source="template",
            )
        )

    # 2. Abnormal Capex Spike Penalty (Titman, Wei, Xie 2004)
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(volume > adv20 * 0.8, group_neutralize(rank(ts_decay_linear(-((capx / (sales + 1.0)) - ts_mean(capx / (sales + 1.0), 252)), 15)), {grp}), -1)",
                archetype_name="Abnormal Capex Spike Penalty",
                hypothesis="Firms substantially increasing capital expenditures relative to sales benchmark experience negative long-run post-capex abnormal returns.",
                generation_source="template",
            )
        )

    # 3. Capital Investment to Implied Volatility Efficiency
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(volume > adv20 * 0.8, group_neutralize(rank(ts_decay_linear(ts_delta(sales / (capx + 1.0), 60) * (1.0 / (implied_volatility_mean_30 + 0.01)), 20)), {grp}), -1)",
                archetype_name="Capex Payoff Efficiency Ratio",
                hypothesis="Firms exhibiting rapid revenue conversion per unit of capital investment conditioned by low options volatility produce persistent alpha.",
                generation_source="template",
            )
        )

    return candidates
