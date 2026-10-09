"""Formula templates for Model-Free Jump Variance & Risk-Neutral Moments."""
from __future__ import annotations
from brain_options.templates import OptionCandidate

def generate_jump_variance_moments_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []
    groups = ["subindustry"]

    # 1. Carr-Madan Discontinuous Jump Variance Curvature (Carr & Madan 2001, Bollerslev 2009)
    for tenor in [30, 60]:
        for grp in groups:
            candidates.append(
                OptionCandidate(
                    expression=f"group_neutralize(rank(ts_decay_linear(implied_volatility_put_{tenor} * implied_volatility_put_{tenor} - 2.0 * implied_volatility_mean_{tenor} * implied_volatility_mean_{tenor} + implied_volatility_call_{tenor} * implied_volatility_call_{tenor}, 15)), {grp})",
                    archetype_name="Model-Free Jump Variance Curvature",
                    hypothesis=f"Decomposing {tenor}d implied variance isolates jump-tail premia demanded by institutional investors.",
                    generation_source="template",
                )
            )

    # 2. Risk-Neutral Kurtosis Proxy Spread (Bakshi, Kapadia, Madan 2003)
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_decay_linear((implied_volatility_put_60 + implied_volatility_call_60 - 2.0 * implied_volatility_mean_60) / (implied_volatility_mean_60 + 0.001), 20)), {grp})",
                archetype_name="Risk-Neutral Kurtosis Proxy",
                hypothesis="Fat-tail risk-neutral kurtosis spreads capture extreme jump compensation unpriced in linear equity returns.",
                generation_source="template",
            )
        )

    # 3. High-Conviction Jump Tail Premium Gate
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(abs(rank(ts_decay_linear(implied_volatility_put_30 * implied_volatility_put_30 - implied_volatility_call_30 * implied_volatility_call_30, 20)) - 0.5) > 0.35, group_neutralize(rank(ts_decay_linear(implied_volatility_put_30 * implied_volatility_put_30 - implied_volatility_call_30 * implied_volatility_call_30, 20)), {grp}), -1)",
                archetype_name="Conviction Gated Jump Asymmetry",
                hypothesis="High-conviction tail positioning on asymmetric jump variance reduces turnover while expanding Sharpe.",
                generation_source="template",
            )
        )

    # 4. Variance Risk Premium Term Structure Slope
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_decay_linear((implied_volatility_mean_30 * implied_volatility_mean_30 - ts_std_dev(returns, 20) * ts_std_dev(returns, 20) * 252.0) - (implied_volatility_mean_90 * implied_volatility_mean_90 - ts_std_dev(returns, 60) * ts_std_dev(returns, 60) * 252.0), 20)), {grp})",
                archetype_name="VRP Term Structure Slope",
                hypothesis="Front-to-back slope in Variance Risk Premium isolates mean-reverting term structure dislocations.",
                generation_source="template",
            )
        )

    return candidates
