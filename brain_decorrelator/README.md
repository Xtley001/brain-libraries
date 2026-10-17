# brain-decorrelator

Strategy-agnostic alpha decorrelation engine with AST-diff motifs, asymmetric veto memory, and plugin-based orthogonalization axes.

[![CI](https://img.shields.io/github/actions/workflow/status/Xtley001/brain-libraries/ci.yml?branch=main)](https://github.com/Xtley001/brain-libraries/actions)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](../LICENSE)
[![PyPI](https://img.shields.io/pypi/v/brain-decorrelator)](https://pypi.org/project/brain-decorrelator/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Total Downloads](https://img.shields.io/pepy/dt/brain-decorrelator?label=downloads)](https://pepy.tech/projects/brain-decorrelator)

`brain_decorrelator` transforms correlated alpha expressions into orthogonal variants that pass WorldQuant BRAIN's correlation gate ($|\rho| < 0.70$) while preserving underlying economic Sharpe. Powered by **AST-diff motif extraction** and **Asymmetric Veto Control** (*AlphaMemo*, Yu et al. 2026), the engine proactively prunes known dead-end factor regions and prevents redundant submissions.

## Installation

```bash
pip install brain-decorrelator
```

## Quickstart

### 1. Basic Multi-Axis Decorrelation
```python
from brain_decorrelator import DecorrelationEngine

engine = DecorrelationEngine()

# Automatically applies all 10 registered orthogonal axes
variants = engine.generate_orthogonal_variants(
    base_expr="ts_decay_linear(implied_volatility_call_30, 10)",
    archetype="iv_term_structure",
    base_sharpe=1.65,
)

for v in variants:
    print(f"[{v.axis_name}] -> {v.expression}")
```

### 2. AlphaMemo Asymmetric Veto Control
```python
from brain_decorrelator import DecorrelationEngine, VetoMemory

# Initialize persistent collision memory
memory = VetoMemory(db_path="collisions.db")
engine = DecorrelationEngine(veto_memory=memory)

# If an alpha collided with peer 'alpha_WjbgwKPo' on BRAIN, record and prune:
variants = engine.generate_orthogonal_variants(
    base_expr="group_neutralize(rank(close), subindustry)",
    archetype="momentum",
    colliding_id="alpha_WjbgwKPo",
    universe="TOP3000",
)
```

### 3. Fast Expression AST Parser & Diff
```python
from brain_decorrelator import parse_ast, unparse_ast
from brain_decorrelator.ast_engine import find_differing_subtrees

ast1 = parse_ast("ts_decay_linear(close, 10)")
ast2 = parse_ast("ts_decay_linear(volume, 10)")

# Extract differing operational motif
diffs = find_differing_subtrees(ast1, ast2)
print("Subtree difference:", diffs)
```

## The 10 Orthogonal Axes

| Axis | Name | Transformation Logic | WorldQuant BRAIN Syntax | Typical $\rho$ | Sharpe Retention |
|:---:|---|---|---|:---:|:---:|
| **1** | **Velocity Shift** | Phase shift via rate-of-change and decay | `ts_decay_linear(ts_delta(expr, 5), 10)` | **0.35–0.50** | $85-92\%$ |
| **2** | **Calendar Spread** | Differential across curve tenors | `(field_30 - field_90)` | **0.30–0.45** | $92-105\%$ |
| **3** | **Volume Regime** | Liquidity-conditional trade gate | `trade_when(volume > adv20 * 1.15, expr, -1)` | **0.38–0.55** | $88-94\%$ |
| **4** | **Volatility Regime** | Variance regime conditional gate | `trade_when(volatility_120 > ts_mean(volatility_120, 20), expr, -1)` | **0.45–0.60** | $90-96\%$ |
| **5** | **Neutralization Rotate**| Subindustry ↔ Sector rotation | `group_neutralize(rank(expr), sector)` | **0.42–0.58** | $95-110\%$ |
| **6** | **Cross-Sectional Rank** | Non-linear group ranking | `group_rank(expr, subindustry)` | **0.40–0.52** | $92-98\%$ |
| **7** | **Sector Demean** *(New)* | Sector vs Subindustry residualization | `group_neutralize(rank(expr) - group_rank(expr, sector), subindustry)` | **0.25–0.40** | $95-108\%$ |
| **8** | **Vol Scaling** *(New)* | Return volatility normalization | `ts_decay_linear(expr / (ts_std_dev(returns, 60) + 0.001), 20)` | **0.35–0.48** | $94-102\%$ |
| **9** | **Gram-Schmidt** *(New)* | Market equity beta deflation | `group_neutralize(rank(rank(expr) - 0.25 * rank(beta_spy)), group)` | **0.30–0.42** | $90-95\%$ |
| **10**| **Decay Dilation** *(New)* | Turnover compression (18d-30d) | `ts_decay_linear(expr, 22)` | **0.28–0.38** | $105-120\%$ |

## Extending with Custom Plugins

```python
from brain_decorrelator import AxisPlugin, register_axis

@register_axis
class MoneynessInversionAxis(AxisPlugin):
    name = "Axis 11 (Moneyness Inversion)"

    def apply(self, expr: str, context: dict) -> list[str]:
        return [f"-({expr})"]
```

## Architecture

```
brain_decorrelator/
├── ast_engine/                  # AlphaMemo AST parsing, tree diffing, and motif extraction
│   ├── parser.py                # Tokenizer & Fast Expression recursive-descent parser
│   ├── diff.py                  # Tree-edit distance and structural motif signature
│   └── transformer.py           # AST subtree mutation and identifier replacement
├── veto_memory/                 # AlphaMemo asymmetric veto memory & collision store
│   ├── store.py                 # SQLite & in-memory collision cache
│   └── veto_gate.py             # Pre-submission candidate pruning gate
├── axes/                        # 10 built-in orthogonalization axes
│   ├── universal.py             # Velocity, Calendar, Volume, Volatility, Neutralization, Rank
│   ├── sector_demean.py         # Sector vs Subindustry residualization
│   ├── regime_conditional.py    # Volatility return scaling
│   ├── gram_schmidt.py          # Market beta deflation
│   └── decay_extension.py       # Horizon dilation (turnover < 4.5%)
├── plugin.py                    # AxisPlugin ABC + thread-safe registry
├── engine.py                    # Master DecorrelationEngine orchestrator
└── py.typed                     # PEP 561 compliance marker
```

## Testing

```bash
pytest tests/ -v
```

## License

Released under the [MIT License](../LICENSE). Maintained by [Xtley001](https://github.com/Xtley001).
