"""Templates for Accounting Quality, Sloan Cash Flow Divergence & Accruals Anomaly."""
from __future__ import annotations

from brain_options.templates import OptionCandidate


def generate_accruals_cashflow_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []
    groups = ["subindustry"]

    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(operating_cashflow / total_assets) - rank(net_income / total_assets), {grp})",
                archetype_name="Sloan Accruals Divergence",
                hypothesis="Sloan accrual anomaly: Firms with high cash flow backing net income significantly outperform accrual-heavy earnings.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(group_rank((operating_cashflow - capex) / total_assets, {grp}) - group_rank(net_income / total_assets, {grp}), {grp})",
                archetype_name="Free Cash Flow Yield Divergence",
                hypothesis="Free cash flow yield divergence from accounting book yield predicts fundamental equity outperformance.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_zscore(operating_cashflow / (net_income + 0.001), 252)), {grp})",
                archetype_name="Cash Flow Coverage Persistence",
                hypothesis="High historical z-score of cash flow coverage relative to net income signals sustainable high-quality earnings.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_delta(operating_cashflow, 60)) - rank(ts_delta(working_capital, 60)), {grp})",
                archetype_name="Working Capital Growth Drag",
                hypothesis="Working capital expansion outpacing cash flow growth indicates inventory bloat or delayed receivables collections.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(working_capital / (total_assets + 1.0) - (net_income - operating_cashflow) / (total_assets + 1.0)), {grp})",
                archetype_name="Richardson Working Capital Decomposition",
                hypothesis="Richardson et al. (2005): Disentangling working-capital accruals from operating cash flow yields superior earnings quality forecast.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank((net_income - operating_cashflow - capex) / (total_assets + debt + 1.0)), {grp})",
                archetype_name="Leverage-Adjusted Free Cash Flow Accrual",
                hypothesis="Scaling non-cash earnings by total enterprise capital structure (assets + debt) isolates balance sheet financing distortion.",
                generation_source="template",
            )
        )

    return candidates
