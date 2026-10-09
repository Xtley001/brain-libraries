"""Formula templates for Structural Credit Risk & Distance to Default."""
from __future__ import annotations
from brain_options.templates import OptionCandidate

def generate_distance_to_default_debt_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []
    groups = ["subindustry"]

    # 1. Merton Distance-to-Default Structural Proxy (Merton 1974, Bharath & Shumway 2008)
    # DD ~ (Assets - Debt) / (Assets * Volatility)
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(volume > adv20 * 0.8, group_neutralize(rank(ts_decay_linear(((assets - debt_total) / (assets + 1.0)) / (implied_volatility_mean_30 + 0.01), 20)), {grp}), -1)",
                archetype_name="Structural Distance to Default",
                hypothesis="Firms with high equity cushion relative to total debt scaled by options implied volatility possess minimal default hazard and command safety premia.",
                generation_source="template",
            )
        )

    # 2. Net Debt to Operating Cash Coverage Deterioration
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(volume > adv20 * 0.8, group_neutralize(rank(ts_decay_linear(-ts_delta((debt_total - cash_and_equivalents) / (ebit + 1.0), 60), 18)), {grp}), -1)",
                archetype_name="Net Debt Coverage Improvement",
                hypothesis="Rapid deleveraging and expansion of operating earnings relative to net debt commitments spurs institutional debt-equity upgrades.",
                generation_source="template",
            )
        )

    # 3. Credit Distress Volatility Interaction
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(abs(rank(debt_total / (assets + 1.0)) - 0.5) > 0.35, group_neutralize(rank(ts_decay_linear(-(debt_total / (assets + 1.0)) * implied_volatility_mean_30, 16)), {grp}), -1)",
                archetype_name="Leverage Volatility Insolvency Risk",
                hypothesis="Highly leveraged balance sheets coupled with elevated options implied volatility flag high tail insolvency risk and persistent negative drift.",
                generation_source="template",
            )
        )

    return candidates
