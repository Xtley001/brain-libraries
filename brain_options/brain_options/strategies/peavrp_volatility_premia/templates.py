"""Formula templates for Post-Earnings Announcement Volatility Risk Premium Drift."""
from __future__ import annotations
from brain_options.templates import OptionCandidate

def generate_peavrp_volatility_premia_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []
    groups = ["subindustry"]

    # 1. PEAVRP (Variance Risk Premium Overhang Post-Earnings)
    # VRP = IV30 - HV30. High VRP post earnings collapse indicates overpriced insurance -> bullish rebound drift
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(volume > adv20 * 0.8, group_neutralize(rank(ts_decay_linear(ts_delta(implied_volatility_mean_30 - historical_volatility_30, 5) * sign(ts_delta(eps, 60)), 15)), {grp}), -1)",
                archetype_name="Post-Earnings VRP Compression Drift",
                hypothesis="Rapid compression of the variance risk premium following positive earnings surprise unleashes sustained directional drift.",
                generation_source="template",
            )
        )

    # 2. Earnings Implied Volatility Dislocation
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(abs(rank(implied_volatility_mean_30 / (historical_volatility_30 + 0.001)) - 0.5) > 0.35, group_neutralize(rank(ts_decay_linear((implied_volatility_mean_30 / (historical_volatility_30 + 0.001)) * returns, 12)), {grp}), -1)",
                archetype_name="Earnings Volatility Dislocation Followthrough",
                hypothesis="Momentum reinforced during extreme implied-to-realized volatility dislocations captures institutional rebalancing flows.",
                generation_source="template",
            )
        )

    # 3. Call-Put IV Asymmetry around Earnings Shocks
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(volume > adv20 * 0.8, group_neutralize(rank(ts_decay_linear((implied_volatility_call_30 - implied_volatility_put_30) * ts_delta(sales, 60), 16)), {grp}), -1)",
                archetype_name="Earnings Skew-Revenue Interaction",
                hypothesis="Upside call volatility demand paired with accelerating quarterly revenue growth identifies high-conviction fundamental expansion.",
                generation_source="template",
            )
        )

    return candidates
