"""Formula templates for Corporate Insider Cluster Buying & Opportunistic Flow."""
from __future__ import annotations
from brain_options.templates import OptionCandidate

def generate_insider_cluster_buying_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []
    groups = ["subindustry"]

    # 1. Opportunistic Cluster Buying Mask (Cohen, Malloy, Pomorski 2012)
    for min_buyers in [2, 3]:
        for grp in groups:
            candidates.append(
                OptionCandidate(
                    expression=f"trade_when(insider_buy_count >= {min_buyers}, group_neutralize(rank(ts_decay_linear(insider_buy_shares / (adv20 + 1.0), 20)), {grp}), -1)",
                    archetype_name="Opportunistic Insider Cluster Buying",
                    hypothesis=f"Simultaneous open-market purchases by {min_buyers}+ corporate insiders signal high-conviction non-public optimism.",
                    generation_source="template",
                )
            )

    # 2. Net Insider Transaction Intensity Ratio (Lakonishok & Lee 2001)
    for window in [20, 40]:
        for grp in groups:
            candidates.append(
                OptionCandidate(
                    expression=f"group_neutralize(rank(ts_decay_linear((ts_sum(insider_buy_shares, {window}) - ts_sum(insider_sell_shares, {window})) / (ts_sum(insider_buy_shares, {window}) + ts_sum(insider_sell_shares, {window}) + 1.0), 15)), {grp})",
                    archetype_name="Net Insider Transaction Intensity",
                    hypothesis=f"Net positive insider buying balance over {window}d window predicts long-horizon equity appreciation.",
                    generation_source="template",
                )
            )

    # 3. High-Conviction Insider Buy Value Fraction
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(abs(rank(ts_decay_linear(insider_buy_value / (cap + 1.0), 30)) - 0.5) > 0.35, group_neutralize(rank(ts_decay_linear(insider_buy_value / (cap + 1.0), 30)), {grp}), -1)",
                archetype_name="Conviction Gated Insider Buy Fraction",
                hypothesis="Filtering top 15% largest insider purchase values relative to market capitalization isolates high-conviction bets.",
                generation_source="template",
            )
        )

    # 4. Insider Buy-to-Sell Count Velocity
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_decay_linear(ts_delta(insider_buy_count - insider_sell_count, 10), 15)), {grp})",
                archetype_name="Insider Count Acceleration",
                hypothesis="Rapid acceleration in the count of insider buys over sales indicates inflection point in executive sentiment.",
                generation_source="template",
            )
        )

    return candidates
