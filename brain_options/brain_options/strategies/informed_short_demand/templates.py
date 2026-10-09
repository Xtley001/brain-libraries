"""Templates for Informed Short Demand vs. Loan Supply Friction."""
from __future__ import annotations

from brain_options.templates import OptionCandidate


def generate_informed_short_demand_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []
    groups = ["subindustry"]

    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(ts_delta(borrow_fee_spike, 5) * ts_decay_linear(loan_utilization_ratio, 10), {grp}) * -1",
                archetype_name="Informed Short Demand Shift",
                hypothesis="Informed institutional short demand shifts outward while available lendable shares drop, predicting negative returns.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_zscore(short_interest_shares / (lendable_shares + 0.001), 60)) * -1, {grp})",
                archetype_name="Constrained Pool Utilization",
                hypothesis="Elevated loan utilization against static institutional lending pools reflects acute downside conviction.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(group_rank(ts_delta(loan_utilization_ratio, 20), {grp}) * -1, {grp})",
                archetype_name="Rapid Utilization Surge",
                hypothesis="Rapid 20-day surges in equity loan utilization signal concentrated institutional hedge fund short accumulation.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(days_to_cover * ts_delta(borrow_fee_spike, 10)) * -1, {grp})",
                archetype_name="Borrow Friction Squeeze Drag",
                hypothesis="High days-to-cover interacting with rapid borrow fee increases magnifies borrow friction and institutional exit pressure.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(-ts_delta(lendable_shares / (float_shares + 1.0), 10) * ts_delta(loan_utilization_ratio, 5)), {grp})",
                archetype_name="Lendable Inventory Contraction",
                hypothesis="Lendable share contraction interacting with utilization surge isolates high-conviction short supply withdrawal.",
                generation_source="template",
            )
        )

    return candidates
