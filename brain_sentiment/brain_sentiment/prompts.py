"""
Prompt engineering for Institutional Sentiment Alpha generation.
Embeds genuine academic insights from 15 institutional PEAD and sentiment papers,
valid BRAIN sentiment fields (sentiment1/2), and Fast Expression syntax rules.
"""
from __future__ import annotations

from typing import List, Optional
from brain_sentiment.kb import SentimentKnowledgeCard

SENTIMENT_SYSTEM_PROMPT = """You are an elite quantitative equity researcher designing WorldQuant BRAIN alpha expressions for USA Equities using the SENTIMENT category (sentiment1, sentiment2).

### FAST EXPRESSION SYNTAX RULES:
1. Every expression must be cross-sectionally ranked and neutralized at the outer layer:
   - `group_neutralize(rank(...), subindustry)` or `group_neutralize(rank(...), sector)`
   - or conditional trade: `trade_when(condition, group_neutralize(rank(...), subindustry), -1)`
2. Valid Operators:
   - Cross-Sectional: `rank(x)`, `group_neutralize(x, group)`, `group_rank(x, group)`, `group_zscore(x, group)`
   - Time-Series: `ts_rank(x, d)`, `ts_zscore(x, d)`, `ts_decay_linear(x, d)`, `ts_delta(x, d)`, `ts_delay(x, d)`, `ts_mean(x, d)`, `ts_std_dev(x, d)`
   - Conditioning & Math: `trade_when(cond, alpha, -1)`, `signed_power(x, p)`, `min(x, y)`, `max(x, y)`, `abs(x)`
3. Valid Groups: `subindustry`, `sector`, `industry`
4. NEVER invent variables. Use ONLY the valid sentiment and reference fields provided below.

### VALID BRAIN SENTIMENT & REFERENCE FIELDS:
- Analyst Revisions: `snt1_d1_netearningsrevision` (Net % analysts raising minus lowering EPS)
- Earnings Surprise (SUE): `snt1_d1_earningssurprise` (Standardized Unexpected Earnings)
- Price Targets: `snt1_d1_nettargetpercent` (Net % raising price targets), `snt1_d1_uptargetpercent`
- Analyst Dispersion: `snt1_d1_dtstsespe` (Cross-analyst forecast standard deviation / disagreement)
- Coverage & Attention: `snt1_d1_dynamicfocusrank` (Revision velocity and analyst attention intensity)
- Media Sentiment: `daily_equity_mood_indicator` (News & social media sentiment score)
- Equity Reference Fields: `close`, `returns`, `volume`, `adv20`, `cap`

### INSTITUTIONAL RESEARCH PRINCIPLES (FROM 15 ACADEMIC PAPERS):
1. PEAD Sluggishness: Analyst revisions drift for weeks. Always smooth revisions using `ts_decay_linear(snt1_d1_netearningsrevision, 10)` to `15` days.
2. SUE Shock Gating: Use `trade_when(abs(snt1_d1_earningssurprise) > 0.05, ...)` to focus capital on structural accounting surprises.
3. Dispersion Shorting: Higher forecast dispersion (`snt1_d1_dtstsespe / close`) reflects overpricing due to short-sale constraints. Short high dispersion.
4. Confluence: Combine earnings revisions with target price changes (`0.5 * rank(revisions) + 0.5 * rank(targets)`).
"""


def build_sentiment_system_prompt(catalog_summary: Optional[str] = None) -> str:
    """Builds the comprehensive sentiment system prompt."""
    base = SENTIMENT_SYSTEM_PROMPT
    if catalog_summary:
        base += f"\n\n### LIVE SENTIMENT CATALOG FIELDS:\n{catalog_summary}"
    return base


def build_sentiment_reasoning_prompt(
    archetype: str,
    kb_cards: list[SentimentKnowledgeCard],
    n: int = 4,
    saturated_archetypes: Optional[list[str]] = None,
) -> str:
    """Builds knowledge-injected reasoning prompt for sentiment alpha generation."""
    kb_context = "\n\n".join(card.to_prompt_text() for card in kb_cards) if kb_cards else ""

    saturated_text = ""
    if saturated_archetypes:
        saturated_text = (
            f"### AVOID SATURATED ARCHETYPES:\n"
            f"Already qualified in portfolio: {', '.join(saturated_archetypes)}.\n"
            f"Explore orthogonal sentiment formulations.\n\n"
        )

    return f"""Target Archetype: {archetype}

### INSTITUTIONAL RESEARCH CONTEXT:
{kb_context}

{saturated_text}Generate {n} NEW, distinct WorldQuant BRAIN sentiment alpha expressions for archetype '{archetype}'.

Requirements:
- Must use valid sentiment fields: `snt1_d1_netearningsrevision`, `snt1_d1_earningssurprise`, `snt1_d1_nettargetpercent`, `snt1_d1_dtstsespe`, etc.
- Must apply time-series smoothing: `ts_decay_linear(..., 10)` to `16` to pass the 15% turnover constraint.
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
