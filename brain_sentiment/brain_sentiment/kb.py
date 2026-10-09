"""
Sentiment Alpha Knowledge Base Engine.
Encapsulates structured quantitative cards, heuristics, formula sketches,
and pitfalls derived from the 15 institutional sentiment and PEAD research papers.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class SentimentKnowledgeCard:
    title: str
    archetype: str
    principle: str
    heuristic: str
    formula_sketch: str
    pitfall: str
    papers: list[str]

    def to_prompt_text(self) -> str:
        lines = [f"### {self.title} (Archetype: {self.archetype})"]
        lines.append(f"- Principle: {self.principle}")
        lines.append(f"- Heuristic: {self.heuristic}")
        lines.append(f"- Formula Sketch: `{self.formula_sketch}`")
        lines.append(f"- Pitfall Warning: {self.pitfall}")
        lines.append(f"- References: {', '.join(self.papers)}")
        return "\n".join(lines)


SENTIMENT_CARDS: list[SentimentKnowledgeCard] = [
    SentimentKnowledgeCard(
        title="Post-Earnings Announcement Drift (PEAD) Revision Sluggishness",
        archetype="pead_earnings_drift",
        principle="Sell-side equity analysts adjust earnings forecasts conservatively due to cognitive anchoring and career concerns. Prices underreact initially, producing prolonged multi-month drift.",
        heuristic="Decay net earnings revisions over 12-16 days. Combine with 5d price reversal and liquidity armor. Neutralize strictly by subindustry.",
        formula_sketch="trade_when(volume > adv20 * 0.8, group_neutralize(rank(ts_decay_linear(ts_decay_linear(snt1_d1_netearningsrevision, 14), 3)) * rank(-ts_delta(close, 5)), subindustry), -1)",
        pitfall="Do not use raw daily revision without decay; high turnover will violate the 15% turnover constraint.",
        papers=["Chan, Jegadeesh & Lakonishok (1996)", "Bernard & Thomas (1989, 1990)"],
    ),
    SentimentKnowledgeCard(
        title="Standardized Unexpected Earnings (SUE) Tail Shock",
        archetype="sue_earnings_surprise",
        principle="Earnings surprises exceeding consensus by more than standard historical deviation generate immediate repricing followed by 60 days of institutional re-allocation.",
        heuristic="Gate on meaningful shock magnitude and combine with volatility-adjusted price change using trade_when liquidity armor.",
        formula_sketch="trade_when(volume > adv20 * 0.8, group_neutralize(rank(ts_decay_linear(ts_decay_linear(snt1_d1_earningssurprise, 14), 3)) * rank(-ts_delta(close, 3) / (ts_std_dev(close, 20) + 0.001)), subindustry), -1)",
        pitfall="Avoid un-gated small surprises; minor deviations (<0.01) represent accounting noise, not structural fundamental surprises.",
        papers=["Bernard & Thomas (1989)", "Givoly & Lakonishok (1979)"],
    ),
    SentimentKnowledgeCard(
        title="Analyst Forecast Dispersion Anomaly",
        archetype="analyst_revision_dispersion",
        principle="High dispersion among analyst EPS estimates indicates severe disagreement. Because short-sale constraints impede pessimists, high-dispersion stocks reflect only optimistic buyers and underperform.",
        heuristic="Go short/underweight high dispersion scaled by stock price and interact with upward revision momentum, smoothed over 14 days.",
        formula_sketch="trade_when(volume > adv20 * 0.8, group_neutralize(rank(-ts_decay_linear(ts_decay_linear(snt1_d1_dtstsespe / (close + 0.001), 14), 3)) * rank(ts_decay_linear(ts_decay_linear(snt1_d1_netearningsrevision, 14), 3)), subindustry), -1)",
        pitfall="Raw standard deviation scales with share price; always divide by close to isolate dimensionless percentage dispersion.",
        papers=["Diether, Malloy & Scherbina (2002)"],
    ),
    SentimentKnowledgeCard(
        title="Target Price Revision Spread",
        archetype="net_target_price_revisions",
        principle="Target price revisions carry incremental information orthogonal to earnings estimates, reflecting valuation multiple re-ratings.",
        heuristic="Take the difference between percentage of upward and downward target revisions, smoothed with linear decay and interacted with intraday spread.",
        formula_sketch="trade_when(volume > adv20 * 0.8, group_neutralize(rank(ts_decay_linear(ts_decay_linear(snt1_d1_uptargetpercent - snt1_d1_downtargetpercent, 14), 3)) * rank((high - low) / (close + 0.001)), subindustry), -1)",
        pitfall="Target prices have wider revisions around quarterly report dates; ensure subindustry neutralization to neutralize reporting clusters.",
        papers=["Brav & Lehavy (2003)", "Asquith, Mikhail & Au (2005)"],
    ),
    SentimentKnowledgeCard(
        title="Dynamic Attention & Search Surge Reversal",
        archetype="media_attention_buzz",
        principle="Retail attention surges create temporary buying pressure and overvaluation that reverses within 2-3 weeks, whereas persistent institutional analyst focus leads to durable drift.",
        heuristic="Trade when volume confirms active trading, combining dynamic analyst focus with price mean-reversion.",
        formula_sketch="trade_when(volume > adv20 * 0.8, group_neutralize(rank(ts_decay_linear(ts_decay_linear(snt1_d1_dynamicfocusrank, 14), 3)) * rank(ts_decay_linear(-ts_zscore(close, 10), 5)), subindustry), -1)",
        pitfall="Do not trade attention signals during market halts or extreme illiquidity.",
        papers=["Da, Engelberg & Gao (2011)", "Barber & Odean (2008)", "Tetlock (2007)"],
    ),
    SentimentKnowledgeCard(
        title="Extreme Lexical Mood Reversal",
        archetype="extreme_sentiment_reversal",
        principle="Extreme aggregate media optimism or pessimism is an emotional overreaction. Stocks experiencing extreme negative news sentiment systematically revert to fair value.",
        heuristic="Apply a contrarian threshold and interact with short-term return reversal under liquidity armor.",
        formula_sketch="trade_when(volume > adv20 * 0.8, group_neutralize(rank(-ts_decay_linear(ts_decay_linear(daily_equity_mood_indicator, 14), 3)) * rank(-ts_delta(close, 5)), subindustry), -1)",
        pitfall="Ensure negative polarity is intended when betting on reversion; do not short continuous deterioration without decay safeguards.",
        papers=["Baker & Wurgler (2006, 2007)", "Tetlock (2007)"],
    ),
]


class SentimentKnowledgeBase:
    def __init__(self):
        self.cards = SENTIMENT_CARDS
        self._cards_by_archetype = {c.archetype: c for c in self.cards}

    def get_card(self, archetype: str) -> Optional[SentimentKnowledgeCard]:
        return self._cards_by_archetype.get(archetype)

    def all_cards(self) -> list[SentimentKnowledgeCard]:
        return self.cards

    def format_all_for_prompt(self) -> str:
        return "\n\n".join(card.to_prompt_text() for card in self.cards)
