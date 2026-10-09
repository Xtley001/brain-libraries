"""Formula templates for Realized High-Frequency Jump Intensity & Skew."""
from __future__ import annotations
from brain_options.templates import OptionCandidate

def generate_realized_jump_intensity_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []
    groups = ["subindustry"]

    # 1. Realized Jump vs Continuous Volatility Ratio (Amaya et al. 2015, Nonejad 2013)
    # Parkinson/Garman-Klass proxy vs close-to-close ratio captures discontinuous jumps
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(volume > adv20 * 0.8, group_neutralize(rank(ts_decay_linear(-((high - low) / (close + 0.001) - historical_volatility_10), 12)), {grp}), -1)",
                archetype_name="Realized Jump Range Discontinuity",
                hypothesis="Discontinuous price jump shocks over-expand bid-ask spreads and create short-term overreaction reversals.",
                generation_source="template",
            )
        )

    # 2. Realized Volatility Term Structure Divergence (HV10 vs HV30)
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(volume > adv20 * 0.8, group_neutralize(rank(ts_decay_linear(ts_delta(historical_volatility_10 / (historical_volatility_30 + 0.001), 5) * returns, 10)), {grp}), -1)",
                archetype_name="HV Term Structure Momentum Jump",
                hypothesis="Rapid acceleration of short-term realized volatility in the direction of underlying returns forecasts continued momentum.",
                generation_source="template",
            )
        )

    # 3. Realized Jump Skew / Implied Skew Divergence
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(volume > adv20 * 0.8, group_neutralize(rank(ts_decay_linear(implied_volatility_skew_30 * ts_decay_linear(returns, 5), 14)), {grp}), -1)",
                archetype_name="Realized-Implied Skew Interaction",
                hypothesis="Divergence between option market skew pricing and realized short-horizon equity trajectory predicts sharp factor mean-reversion.",
                generation_source="template",
            )
        )

    return candidates
