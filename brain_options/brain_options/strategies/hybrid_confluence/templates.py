"""Formula templates for Multi-Tenor & Cross-Asset Hybrid Confluence."""
from __future__ import annotations
from brain_options.templates import OptionCandidate

def generate_hybrid_confluence_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []
    groups = ["subindustry"]

    # 1. Volatility Smirk Borrow Fee Hybrid
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(-ts_decay_linear((implied_volatility_mean_skew_30 * sqrt(30 / 252.0)) * (borrow_fee + 1.0), 20)), {grp})",
                archetype_name="Volatility Smirk Borrow Fee Hybrid",
                hypothesis="Cross-market confluence: Downside put skew coupled with high borrow fees indicates maximum downside institutional conviction.",
                generation_source="template",
            )
        )

    # 2. Revision vs Skew Divergence Hybrid
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_decay_linear((est_eps - ts_delay(est_eps, 20)) / (abs(ts_delay(est_eps, 20)) + 0.01) - (implied_volatility_mean_skew_30 * sqrt(30 / 252.0)), 20)), {grp})",
                archetype_name="Revision vs Skew Divergence Hybrid",
                hypothesis="Options market participants lead cash analyst revisions by 10-20 days; fading upgrades met with put skew expansion exploits structural lag.",
                generation_source="template",
            )
        )

    # 3. Term Structure Inversion x Put Flow Confluence
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_decay_linear(-(implied_volatility_mean_30 / (implied_volatility_mean_90 + 0.001) - 1.0) * ts_zscore(pcr_vol_30, 20), 15)), {grp})",
                archetype_name="Term Structure x Put Flow Confluence",
                hypothesis="Inverted IV term structures coupled with put capitulation volume maximize mean-reversion Sharpe.",
                generation_source="template",
            )
        )

    # 4. Multi-Factor 4-Way Confluence (Skew + Borrow + Revision + Flow)
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(-ts_zscore(implied_volatility_mean_skew_30, 30) - ts_zscore(borrow_fee, 60) + ts_zscore(est_eps - ts_delay(est_eps, 20), 20) - ts_zscore(pcr_vol_30, 20)), {grp})",
                archetype_name="4-Way Multi-Factor Confluence",
                hypothesis="Simultaneous alignment of skew smirk, borrow fee tightness, positive EPS revision, and put flow capitulation produces maximal Sharpe alpha.",
                generation_source="template",
            )
        )

    return candidates
