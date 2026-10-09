"""Templates for Extreme Tail Risk Asymmetry & OTM Put Jump Diffusion."""
from __future__ import annotations

from brain_options.templates import OptionCandidate


def generate_extreme_tail_risk_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []
    groups = ["subindustry"]

    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(ts_zscore(skew_smirk, 60), {grp}) * -1",
                archetype_name="Skew Smirk Downside Drag",
                hypothesis="Extreme negative skew smirk reflects institutional disaster insurance buying and impending crash risk.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_decay_linear(iv_otm_put_30 - iv_atm_call_30, 10)) * -1, {grp})",
                archetype_name="OTM Put Volatility Premium",
                hypothesis="Deep out-of-the-money put volatility premium over ATM call volatility prices severe asymmetric downside jump risk.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(group_rank(vol_surface_convexity, {grp}) * -1, {grp})",
                archetype_name="Volatility Surface Convexity",
                hypothesis="Heightened surface convexity across strike space indicates concentrated hedging demand for tail-risk options.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_delta(skew_smirk, 5)) * rank(put_call_volume_ratio) * -1, {grp})",
                archetype_name="Smirk Steepening Flow",
                hypothesis="Concurrence of rapid smirk steepening and heavy put volume surges confirms smart-money protective hedging.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(-(iv_skew_call_put * vol_surface_convexity)), {grp})",
                archetype_name="BKM Higher-Moment Kurtosis Proxy",
                hypothesis="Interaction of call-put skew and volatility surface convexity captures non-linear kurtosis disaster hedging.",
                generation_source="template",
            )
        )

    # Standalone pure surface convexity
    for grp in ["industry", "subindustry"]:
        candidates.append(
            OptionCandidate(
                expression=f"group_rank(-vol_surface_convexity, {grp})",
                archetype_name="Standalone Surface Convexity",
                hypothesis="Pure negative surface convexity ranks assets with excessive out-of-the-money variance pricing.",
                generation_source="template",
            )
        )

    return candidates
