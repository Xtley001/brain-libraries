"""
Prompt engineering for Systematic Risk Model Alpha generation.
Embeds genuine academic insights from 11 institutional risk, BAB, and factor anomaly papers,
valid BRAIN risk model fields (model51/52), and Fast Expression syntax rules.
"""
from __future__ import annotations

from typing import List, Optional
from brain_risk_model.kb import RiskModelKnowledgeCard

RISK_MODEL_SYSTEM_PROMPT = """You are an elite quantitative risk researcher designing WorldQuant BRAIN alpha expressions for USA Equities using the RISK MODEL category (model51, model52).

### FAST EXPRESSION SYNTAX RULES:
1. Every expression must be cross-sectionally ranked and neutralized at the outer layer:
   - `group_neutralize(rank(...), subindustry)` or `group_neutralize(rank(...), sector)`
   - or conditional trade: `trade_when(condition, group_neutralize(rank(...), subindustry), -1)`
2. Valid Operators:
   - Cross-Sectional: `rank(x)`, `group_neutralize(x, group)`, `group_rank(x, group)`, `group_zscore(x, group)`
   - Time-Series: `ts_rank(x, d)`, `ts_zscore(x, d)`, `ts_decay_linear(x, d)`, `ts_delta(x, d)`, `ts_delay(x, d)`, `ts_mean(x, d)`, `ts_std_dev(x, d)`
   - Conditioning & Math: `trade_when(cond, alpha, -1)`, `signed_power(x, p)`, `min(x, y)`, `max(x, y)`, `abs(x)`
3. Valid Groups: `subindustry`, `sector`, `industry`
4. NEVER invent variables. Use ONLY the valid risk model and reference fields provided below.

### VALID BRAIN RISK MODEL & REFERENCE FIELDS:
- Market Beta: `beta_last_30_days_spy`, `beta_last_60_days_spy`, `beta_last_90_days_spy`, `beta_last_360_days_spy`
- Benchmark Correlation: `correlation_last_60_days_spy`, `correlation_last_90_days_spy`
- Quality & Turnaround: `fscore_surface_accel` (Piotroski accounting improvement momentum)
- Fundamental Stability: `cashflow_solvency_margin` (Operating cash flow coverage)
- Historical Volatility: `ts_std_dev(returns, 20)`, `ts_std_dev(returns, 60)`
- Equity Reference Fields: `close`, `returns`, `volume`, `adv20`, `cap`

### INSTITUTIONAL RESEARCH PRINCIPLES (FROM 11 ACADEMIC PAPERS):
1. Betting Against Beta (Frazzini & Pedersen 2014): Leverage constraints lead investors to overpay for high-beta stocks. Go long low-beta, short high-beta (`-beta_last_60_days_spy`).
2. Dual Beta Divergence: Transient short-term beta expansion (`beta_last_30_days_spy - beta_last_90_days_spy`) signals temporary selling pressure that mean-reverts.
3. Quality at Low Risk: Combine low systematic beta with accounting acceleration (`0.6 * rank(-beta_last_60_days_spy) + 0.4 * rank(fscore_surface_accel)`).
4. Subindustry Neutralization: Always neutralize by `subindustry` to eliminate market-wide sector tilts.
"""


def build_risk_model_system_prompt(catalog_summary: Optional[str] = None) -> str:
    """Builds the comprehensive risk model system prompt."""
    base = RISK_MODEL_SYSTEM_PROMPT
    if catalog_summary:
        base += f"\n\n### LIVE RISK MODEL CATALOG FIELDS:\n{catalog_summary}"
    return base


def build_risk_model_reasoning_prompt(
    archetype: str,
    kb_cards: list[RiskModelKnowledgeCard],
    n: int = 4,
    saturated_archetypes: Optional[list[str]] = None,
) -> str:
    """Builds knowledge-injected reasoning prompt for risk model alpha generation."""
    kb_context = "\n\n".join(card.to_prompt_text() for card in kb_cards) if kb_cards else ""

    saturated_text = ""
    if saturated_archetypes:
        saturated_text = (
            f"### AVOID SATURATED ARCHETYPES:\n"
            f"Already qualified in portfolio: {', '.join(saturated_archetypes)}.\n"
            f"Explore orthogonal risk model formulations.\n\n"
        )

    return f"""Target Archetype: {archetype}

### INSTITUTIONAL RESEARCH CONTEXT:
{kb_context}

{saturated_text}Generate {n} NEW, distinct WorldQuant BRAIN risk model alpha expressions for archetype '{archetype}'.

Requirements:
- Must use valid risk model fields: `beta_last_60_days_spy`, `beta_last_90_days_spy`, `correlation_last_60_days_spy`, `fscore_surface_accel`, etc.
- Must apply time-series smoothing: `ts_decay_linear(..., 10)` to `16` to pass turnover constraint.
- Outer operator MUST be `group_neutralize(rank(...), subindustry)` or `group_neutralize(rank(...), sector)`.
- Provide a clear, 1-sentence causal economic hypothesis for each.

Respond with ONLY a JSON array of objects (no markdown fences, no text before or after):
[
  {{
    "expression": "...",
    "archetype": "{archetype}",
    "hypothesis": "..."
  }}
]
"""
