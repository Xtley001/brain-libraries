"""Formula templates for Analyst Consensus Revisions & PEAD."""
from __future__ import annotations
from brain_options.templates import OptionCandidate

def generate_analyst_revisions_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []
    groups = ["subindustry"]

    # 1. Analyst Consensus Revision Momentum
    for lookback in [15, 30, 60]:
        for grp in groups:
            candidates.append(
                OptionCandidate(
                    expression=f"group_neutralize(rank(ts_decay_linear((est_eps - ts_delay(est_eps, {lookback})) / (abs(ts_delay(est_eps, {lookback})) + 0.01), 15)), {grp})",
                    archetype_name="Analyst Revision Momentum",
                    hypothesis=f"Givoly & Lakonishok (1979): Upward earnings revisions over {lookback}d exhibit persistent post-revision drift.",
                    generation_source="template",
                )
            )

    # 2. Analyst Disagreement / Dispersion Fade
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(-ts_decay_linear(std_dev_eps_est / (abs(est_eps) + 0.01), 15)), {grp})",
                archetype_name="Analyst Dispersion Fade",
                hypothesis="Diether, Malloy & Scherbina (2002): High analyst disagreement indicates price over-optimism; fading dispersion yields alpha.",
                generation_source="template",
            )
        )

    # 3. Momentum-Conditioned Target Price Upside
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(ts_delta(close, 10) > 0, group_neutralize(rank(ts_decay_linear((target_price - close) / close, 15)), {grp}), -1)",
                archetype_name="Price Target Implied Upside",
                hypothesis="Consensus price target upside conditioned on positive price momentum avoids value traps.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_decay_linear((target_price - close) / close, 15)), {grp})",
                archetype_name="Pure Target Price Upside",
                hypothesis="Consensus price target implied return captures fundamental undervaluation and analyst price target conviction.",
                generation_source="template",
            )
        )

    return candidates
