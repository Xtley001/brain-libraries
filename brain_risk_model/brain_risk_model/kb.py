"""
Risk Model Alpha Knowledge Base Engine.
Encapsulates structured quantitative cards, heuristics, formula sketches,
and pitfalls derived from the 11 institutional systematic risk, BAB, and factor anomaly papers.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class RiskModelKnowledgeCard:
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


RISK_MODEL_CARDS: list[RiskModelKnowledgeCard] = [
    RiskModelKnowledgeCard(
        title="Betting Against Beta (BAB) Anomaly",
        archetype="betting_against_beta",
        principle="Leverage-constrained institutional and retail investors tilt toward high-beta assets to achieve higher expected returns, systematically overpricing high beta. Long low-beta / short high-beta produces superior risk-adjusted alpha.",
        heuristic="Short rolling 60-day or 90-day SPY beta interacted with 5d price reversal and liquidity armor. Neutralize strictly by subindustry.",
        formula_sketch="trade_when(volume > adv20 * 0.8, group_neutralize(rank(-ts_decay_linear(ts_decay_linear(beta_last_60_days_spy, 14), 3)) * rank(-ts_delta(close, 5)), subindustry), -1)",
        pitfall="Do not leave unneutralized; market-level beta swings will inject unhedged directional market beta.",
        papers=["Frazzini & Pedersen (2014) - Betting Against Beta", "Black (1972)"],
    ),
    RiskModelKnowledgeCard(
        title="Idiosyncratic Volatility Puzzle & Decoupling",
        archetype="idiosyncratic_volatility_puzzle",
        principle="Stocks with high idiosyncratic volatility earn anomalously low future returns. Decomposing systematic market correlation from total return variance isolates the low-risk anomaly.",
        heuristic="Smooth rolling 60-day correlation scaled by annualized volatility, interacted with intraday spread and protected with liquidity armor.",
        formula_sketch="trade_when(volume > adv20 * 0.8, group_neutralize(rank(ts_decay_linear(ts_decay_linear(correlation_last_60_days_spy * (ts_std_dev(returns, 60) * sqrt(252)), 14), 3)) * rank((high - low) / (vwap + 0.001)), subindustry), -1)",
        pitfall="Raw volatility has sector clusters (e.g. Biotech, Energy); always use subindustry neutralization.",
        papers=["Ang, Hodrick, Xing & Zhang (2006, 2009)"],
    ),
    RiskModelKnowledgeCard(
        title="Multi-Horizon Beta Divergence",
        archetype="beta_divergence",
        principle="Discrepancies between short-horizon (30-day) and long-horizon (360-day) betas identify transient liquidity shocks and leverage overshoots that revert to the flatter security market line.",
        heuristic="Go short the spread between 30-day and 360-day rolling betas, interacted with price z-score under liquidity armor.",
        formula_sketch="trade_when(volume > adv20 * 0.8, group_neutralize(rank(-ts_decay_linear(ts_decay_linear(beta_last_30_days_spy - beta_last_360_days_spy, 14), 3)) * rank(ts_decay_linear(-ts_zscore(close, 10), 5)), subindustry), -1)",
        pitfall="Check for missing 360d data on recent IPOs; combine with minimum lookback gating.",
        papers=["Black (1972)", "Baker, Bradley & Wurgler (2011)"],
    ),
    RiskModelKnowledgeCard(
        title="Composite Low-Risk Engine (Beta + Correlation Tilt)",
        archetype="low_risk_engine",
        principle="Institutional benchmark constraints force cap-weighted managers to ignore low-beta, low-correlation assets. Fusing rolling beta with market correlation builds a robust multi-dimensional defensive factor.",
        heuristic="Multiplicatively combine low beta and low market correlation into a unified bivariate rank under liquidity armor.",
        formula_sketch="trade_when(volume > adv20 * 0.8, group_neutralize(rank(-ts_decay_linear(ts_decay_linear(beta_last_60_days_spy, 14), 3)) * rank(-ts_decay_linear(ts_decay_linear(correlation_last_60_days_spy, 14), 3)), subindustry), -1)",
        pitfall="Ensure both terms are ranked prior to combination to prevent unit scale distortion.",
        papers=["Baker, Bradley & Wurgler (2011)", "Blitz & van Vliet (2007)"],
    ),
    RiskModelKnowledgeCard(
        title="Piotroski Quality Surface Acceleration",
        archetype="surface_acceleration",
        principle="Tracking the second derivative / acceleration of accounting quality (F-Score) isolates companies transitioning from fundamental distress to rapid institutional turnaround.",
        heuristic="Blend quality surface acceleration with baseline quality score, protected with liquidity armor.",
        formula_sketch="trade_when(volume > adv20 * 0.8, group_neutralize(rank(0.60 * rank(ts_decay_linear(ts_decay_linear(fscore_surface_accel, 14), 3)) + 0.40 * rank(ts_decay_linear(ts_decay_linear(fscore_bfl_quality, 14), 3))), subindustry), -1)",
        pitfall="Avoid quarterly step artifacts by applying ts_decay_linear across the fundamental release.",
        papers=["Piotroski (2000) - Value Investing (F-Score)"],
    ),
    RiskModelKnowledgeCard(
        title="Novy-Marx Gross Profitability Premium",
        archetype="gross_profitability",
        principle="Highly profitable firms generate significantly higher returns than unprofitable firms, even controlling for valuation. Operating profitability is orthogonal to price momentum.",
        heuristic="Combine profitability factor with cash flow efficiency and liquidity armor.",
        formula_sketch="trade_when(volume > adv20 * 0.8, group_neutralize(rank(0.50 * rank(ts_decay_linear(ts_decay_linear(fscore_bfl_profitability, 14), 3)) + 0.50 * rank(ts_decay_linear(ts_decay_linear(cashflow_efficiency_rank_derivative, 14), 3))), subindustry), -1)",
        pitfall="Ensure cash flow efficiency is defined for non-financial companies.",
        papers=["Novy-Marx (2013) - The Other Side of Value"],
    ),
    RiskModelKnowledgeCard(
        title="Blitz Low-Volatility & Earnings Certainty Confluence",
        archetype="blitz_volatility",
        principle="Low-volatility stocks earn superior risk-adjusted returns globally. Combining low SPY beta with high earnings certainty creates an institutional Sharpe-maximizing engine.",
        heuristic="Go long earnings certainty derivative while shorting SPY rolling beta under liquidity armor.",
        formula_sketch="trade_when(volume > adv20 * 0.8, group_neutralize(rank(0.55 * rank(ts_decay_linear(ts_decay_linear(earnings_certainty_rank_derivative, 14), 3)) - 0.45 * rank(ts_decay_linear(ts_decay_linear(beta_last_60_days_spy, 14), 3))), subindustry), -1)",
        pitfall="Low-beta portfolios can take on interest rate duration risk; subindustry neutralization purges utility/bond-proxy tilts.",
        papers=["Blitz & van Vliet (2007) - The Volatility Effect"],
    ),
]


class RiskModelKnowledgeBase:
    def __init__(self):
        self.cards = RISK_MODEL_CARDS
        self._cards_by_archetype = {c.archetype: c for c in self.cards}

    def get_card(self, archetype: str) -> Optional[RiskModelKnowledgeCard]:
        return self._cards_by_archetype.get(archetype)

    def all_cards(self) -> list[RiskModelKnowledgeCard]:
        return self.cards

    def format_all_for_prompt(self) -> str:
        return "\n\n".join(card.to_prompt_text() for card in self.cards)
