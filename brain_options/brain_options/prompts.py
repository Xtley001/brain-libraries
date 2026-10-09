"""
Prompt engineering for Options Alpha generation.
Embeds genuine derivatives financial economics from Options Master Knowledge Base (Books 1-4),
live BRAIN option fields, and Fast Expression syntax rules.
"""
from __future__ import annotations

from typing import List, Optional
from brain_options.kb import KnowledgeCard

OPTIONS_SYSTEM_PROMPT = """You are an elite quantitative derivatives researcher designing WorldQuant BRAIN alpha expressions for USA Equities using the OPTIONS category.

### FAST EXPRESSION SYNTAX RULES:
1. Every expression must be cross-sectionally ranked or neutralized at the outer layer:
   - `group_neutralize(rank(...), sector)` or `group_neutralize(rank(...), subindustry)`
   - or conditional trade: `trade_when(condition, group_neutralize(rank(...), sector), -1)`
2. Valid Operators:
   - Cross-Sectional: `rank(x)`, `group_neutralize(x, group)`, `group_rank(x, group)`, `group_zscore(x, group)`
   - Time-Series: `ts_rank(x, d)`, `ts_zscore(x, d)`, `ts_decay_linear(x, d)`, `ts_delta(x, d)`, `ts_delay(x, d)`, `ts_mean(x, d)`, `ts_std_dev(x, d)`, `ts_max(x, d)`, `ts_min(x, d)`
   - Conditioning & Math: `trade_when(cond, alpha, -1)`, `signed_power(x, p)`, `min(x, y)`, `max(x, y)`, `abs(x)`, `sqrt(x)`
3. Valid Groups: `sector`, `industry`, `subindustry`
4. NEVER invent variables. Use ONLY the valid options and equity fields provided below.

### VALID BRAIN OPTIONS FIELDS:
- Forward Prices: `forward_price_10`, `forward_price_20`, `forward_price_30`, `forward_price_60`, `forward_price_90`, `forward_price_120`, `forward_price_150`, `forward_price_180`, `forward_price_270`, `forward_price_360`
- Call Breakevens: `call_breakeven_10`, `call_breakeven_20`, `call_breakeven_30`, `call_breakeven_60`, `call_breakeven_90`, `call_breakeven_120`, `call_breakeven_180`
- Put-Call Volume Ratios: `pcr_vol_10`, `pcr_vol_20`, `pcr_vol_30`, `pcr_vol_60`, `pcr_vol_90`, `pcr_vol_120`, `pcr_vol_180`, `pcr_vol_all`
- Put-Call OI Ratios: `pcr_oi_10`, `pcr_oi_20`, `pcr_oi_30`, `pcr_oi_60`, `pcr_oi_90`, `pcr_oi_120`, `pcr_oi_180`, `pcr_oi_all`
- Implied Volatility Skew: `implied_volatility_mean_skew_10`, `implied_volatility_mean_skew_20`, `implied_volatility_mean_skew_30`, `implied_volatility_mean_skew_60`, `implied_volatility_mean_skew_90`
- ATM Implied Volatility: `implied_volatility_mean_10`, `implied_volatility_mean_20`, `implied_volatility_mean_30`, `implied_volatility_mean_60`, `implied_volatility_mean_90`, `implied_volatility_mean_180`, `implied_volatility_mean_360`
- Equity Reference Fields: `close`, `returns`, `volume`, `adv20`, `cap`

### INSTITUTIONAL QUANTITATIVE DERIVATIVES PRINCIPLES (FROM MASTER BOOKS 1-4):
1. Skew Square-Root Time Scaling: Skew decays proportional to sqrt(T). Normalize cross-tenor skew by `* sqrt(tenor/252.0)`.
2. NEVER divide fixed-strike skew by ATM IV (it double-counts volatility effects).
3. Mean-Reversion Entry: For mean-reverting spreads, the optimal entry threshold is ~0.75 standard deviations (`abs(ts_zscore(x, window)) > 0.75`), balancing edge size with trade opportunity frequency.
4. Forward-Basis Anchor: Synthetic forward basis `(forward_price - close) / close` captures borrow/dividend pricing and consensus drift.
5. PCR Volume-to-OI Flow Velocity: Volume relative to open interest `pcr_vol_{tenor} / (pcr_oi_{tenor} + 0.001)` reveals aggressive institutional order flow.
6. Jensen's Inequality Debiasing: Short-window rolling realized volatility (`ts_std_dev(returns, win) * 15.87`) underestimates true vol for small windows.
"""

OPTIONS_REASONING_PROMPT = """Generate {n} NEW, distinct WorldQuant BRAIN options alpha expressions.

Requirements:
- Target varied tenors (e.g. 10d, 20d, 30d, 60d, 90d).
- Mix different options dynamics: Forward basis, PCR flow, Skew acceleration, Breakeven spread, or Term structure.
- Combine options metrics with time-series operators (`ts_zscore`, `ts_decay_linear`, `ts_delta`) or volume gating (`trade_when(volume > adv20, ..., -1)`).
- Provide a clear, 1-sentence causal economic hypothesis for each idea.

Respond with ONLY a JSON array of objects (no markdown fences, no text before or after):
[
  {{
    "expression": "...",
    "archetype": "...",
    "hypothesis": "..."
  }}
]
"""


def build_options_system_prompt(catalog_summary: Optional[str] = None) -> str:
    """Builds the comprehensive options system prompt with optional live field catalog summary."""
    base = OPTIONS_SYSTEM_PROMPT
    if catalog_summary:
        base += f"\n\n### LIVE OPTIONS CATALOG FIELDS:\n{catalog_summary}"
    return base


def build_reasoning_prompt(
    archetype: str,
    kb_cards: list[KnowledgeCard],
    n: int = 5,
    top_exemplars: Optional[list[dict]] = None,
    failure_guidance: Optional[str] = None,
    saturated_archetypes: Optional[list[str]] = None,
) -> str:
    """
    Builds a knowledge-injected reasoning prompt for generating novel alpha expressions
    grounded in specific institutional derivatives cards, formula sketches, and RL exemplars,
    while strictly avoiding saturated archetypes to defeat self-correlation.
    """
    kb_context = "\n\n".join(card.to_prompt_text() for card in kb_cards) if kb_cards else ""

    exemplars_text = ""
    if top_exemplars:
        lines = ["### HALL OF FAME: HIGH-PERFORMING ALPHAS IN THIS UNIVERSE (REINFORCEMENT LEARNING EXEMPLARS):"]
        for ex in top_exemplars[:4]:
            expr = ex.get("expression", "")
            sh = ex.get("sharpe", 0.0)
            fit = ex.get("fitness", 0.0)
            arch = ex.get("archetype", "")
            lines.append(f"- Archetype: {arch} | Sharpe: {sh:.2f} | Fitness: {fit:.2f}\n  Formula: `{expr}`")
        exemplars_text = "\n".join(lines) + "\n\n"

    saturated_text = ""
    if saturated_archetypes:
        saturated_text = (
            f"### CRITICAL ANTI-CORRELATION CONSTRAINT (SATURATED SIGNAL DOMAINS):\n"
            f"The following archetypes/mechanisms ALREADY have accepted alphas in our portfolio: {', '.join(saturated_archetypes)}.\n"
            f"DO NOT generate formulas that correlate with these archetypes. You MUST explore orthogonal formulations, "
            f"different lookbacks, alternative data fields, or cross-asset interactions.\n\n"
        )

    negative_guidance = failure_guidance or """### PROVEN FAILURE PATTERNS TO STRICTLY AVOID:
1. Do NOT generate raw Put-Call Ratio contrarian reversals (e.g. -ts_zscore(pcr_vol_10, 20)); they consistently produce negative Sharpe (-0.80).
2. Do NOT generate raw unsmoothed ts_delta without linear decay; it generates 50%+ turnover which crushes Fitness. Always wrap signals with `ts_decay_linear(..., 5)` or `ts_decay_linear(..., 10)`.
3. Do NOT generate raw forward basis levels `(forward_price - close) / close`; they are static and have near-zero Sharpe."""

    prompt = f"""Generate {n} NOVEL, mathematically precise WorldQuant BRAIN options alpha expressions for the ARCHETYPE: '{archetype}'.

{exemplars_text}{saturated_text}### KNOWLEDGE BASE INSTITUTIONAL CARDS & FORMULAS (BOOKS 1-4):
{kb_context if kb_context else "Apply standard quantitative derivatives theory for " + archetype}

{negative_guidance}

### RIGOROUS REQUIREMENTS:
1. Ground your expressions in the principles and formula sketches from the knowledge base cards above.
2. Comply strictly with Fast Expression syntax rules (outer layer `group_neutralize(rank(...), subindustry)` or `trade_when(...)`).
3. Apply smoothing (`ts_decay_linear(..., 5)` or `ts_decay_linear(..., 10)`) inside the rank to keep turnover under 30% and ensure Fitness >= 1.0.
4. Use realistic lookback windows (3 to 60 days) and valid options tenors (10, 20, 30, 60, 90).
5. For each candidate, formulate a 1-sentence causal economic hypothesis explaining WHY the edge exists.

Respond with ONLY a JSON array of objects (no markdown fences, no surrounding commentary):
[
  {{
    "expression": "group_neutralize(rank(ts_decay_linear(ts_delta((call_breakeven_20 - close) / close, 5), 5)), subindustry)",
    "archetype": "{archetype}",
    "hypothesis": "Economic mechanism explaining the edge..."
  }}
]
"""
    return prompt


def build_mechanical_mutation_prompt(
    candidate_expression: str,
    candidate_hypothesis: str,
    kb_cards: Optional[list[KnowledgeCard]] = None,
    n: int = 4,
    top_exemplars: Optional[list[dict]] = None,
) -> str:
    """
    Builds a mechanical tier prompt that generates systematic variations of a promising
    candidate (operator variations, tenor shifts, decay windows, group neutralizations)
    while preserving the core economic mechanism.
    """
    if kb_cards and isinstance(kb_cards, (list, tuple, set)):
        kb_context = "\n\n".join(
            card.to_prompt_text() for card in kb_cards if hasattr(card, "to_prompt_text")
        )
    else:
        kb_context = ""

    exemplars_text = ""
    if top_exemplars:
        lines = ["### BENCHMARK PROVEN WINNERS:"]
        for ex in top_exemplars[:3]:
            lines.append(f"- `{ex.get('expression', '')}` (Sharpe: {ex.get('sharpe', 0.0):.2f})")
        exemplars_text = "\n".join(lines) + "\n\n"

    prompt = f"""Generate {n} HIGH-QUALITY SYSTEMATIC MUTATIONS of the following promising options candidate:

Base Expression: `{candidate_expression}`
Base Hypothesis: {candidate_hypothesis}

{exemplars_text}### RELEVANT KNOWLEDGE BASE GUIDANCE:
{kb_context if kb_context else "Preserve the core economic pricing logic."}

### MUTATION DIRECTIONS:
1. Tenor Variations: Shift between adjacent option tenors (e.g. 20d -> 30d -> 60d) with sqrt(T) scaling.
2. Turnover-Reduction Smoothing: Wrap raw differences in `ts_decay_linear(..., 5)` or `ts_decay_linear(..., 10)` to boost Fitness.
3. Granular Neutralization: Switch from `sector` to `subindustry`.
4. Regime / Volume Gating: Add `trade_when(volume > adv20, ..., -1)` or mean-reversion threshold gating.
5. Maintain valid Fast Expression syntax and avoid syntax errors.

Respond with ONLY a JSON array of objects (no markdown fences):
[
  {{
    "expression": "...",
    "archetype": "Mutation",
    "hypothesis": "Variation hypothesis explaining the structural tweak..."
  }}
]
"""
    return prompt

