# Brain Alpha Pipeline — Audit & Roadmap

> Author: [Xtley001](https://github.com/Xtley001) · Generated: 2026-10-09
>
> A meticulous, no-flattery review of the 7-library Brain Alpha suite.
> For every finding the table notes the severity, the exact file to change, and the concrete fix.

---

## Table of Contents

- [1. Executive Summary](#1-executive-summary)
- [2. Library-by-Library Review](#2-library-by-library-review)
  - [2.1 brain-core](#21-brain-core)
  - [2.2 brain-store](#22-brain-store)
  - [2.3 brain-decorrelator](#23-brain-decorrelator)
  - [2.4 brain-options](#24-brain-options)
  - [2.5 brain-sentiment](#25-brain-sentiment)
  - [2.6 brain-risk-model](#26-brain-risk-model)
  - [2.7 brain-synthesis](#27-brain-synthesis)
- [3. Cross-Cutting Issues](#3-cross-cutting-issues)
- [4. What Must Be Removed](#4-what-must-be-removed)
- [5. What Must Be Added](#5-what-must-be-added)
- [6. What Must Be Improved](#6-what-must-be-improved)
- [7. Discoverability Strategy](#7-discoverability-strategy)
- [8. Prioritised Action Plan](#8-prioritised-action-plan)

---

## 1. Executive Summary

The suite is architecturally sound. The dependency DAG is correct, the type system in `brain-core` is the right single source of truth, and `brain-decorrelator`'s plugin registry is the most elegant piece of work in the whole system. The CI pipeline and test structure are production-grade in form.

**The critical gaps are not conceptual — they are operational and discoverability problems:**

1. Every `pyproject.toml` is missing `keywords`, `classifiers`, `urls`, and `authors` — the metadata that PyPI, LLMs, and search engines index.
2. None of the 7 packages have been published to PyPI. The badge links point to packages that return 404.
3. The `cli.py` entry point is not declared in any `pyproject.toml` — `brain generate` / `brain decorrelate` cannot be run after `pip install`.
4. The `brain_store` `OptionsStore` name leaks the options domain into the storage layer — contradicts the stated cross-domain purpose.
5. No `LICENSE` file exists at the monorepo root despite every README referencing it.
6. `brain_synthesis` hardcodes WorldQuant-specific data field names in `apex_generator.py`, breaking portability claims.
7. Documentation quality is uneven: `brain_core` is well-documented; `brain_synthesis` and `brain_risk_model` README files are stubs with almost no context for a first-time reader.

---

## 2. Library-by-Library Review

### 2.1 brain-core

**Overall:** The best-written library in the suite. Types are clean, config is properly env-driven with no hard-coded secrets, and the logger factory is minimal.

| Severity | File | Issue | Fix |
|---|---|---|---|
| 🔴 BLOCKER | `pyproject.toml` | No `keywords`, `classifiers`, `urls`, or `authors` fields | Add full metadata block — see §5 |
| 🟡 HIGH | `config.py` | `load_dotenv()` is called at module import time, affecting test isolation | Move inside `Config.load_from_env()` or accept a `dotenv_path` argument |
| 🟡 HIGH | `types.py` | `AlphaCandidate.generation_source` has no validation — any string is accepted | Add `__post_init__` validation against a `frozenset` of allowed values |
| 🟠 MEDIUM | `pyproject.toml` | Missing `[project.scripts]` block | Needed to surface the `brain` CLI after install |
| 🟠 MEDIUM | `README.md` | Badge CI URL uses `Xtley001` placeholder | Replace with `Xtley001/brain-libraries` |
| 🟢 LOW | `llm.py` | File exists in `brain-core` but is not imported anywhere in the public `__init__.py` | Either export it or move it to `brain-options` which is the only consumer |

**Missing entirely:**
- `py.typed` marker file (signals to type checkers that the package is typed)
- `CHANGELOG.md` entry for `0.1.0`

---

### 2.2 brain-store

**Overall:** Dual-mode persistence (Postgres + file) is a real engineering decision. The `db.py` is the largest file in the codebase at 21 KB and deserves scrutiny.

| Severity | File | Issue | Fix |
|---|---|---|---|
| 🔴 BLOCKER | `brain_store/__init__.py` | `OptionsStore` exported as the primary public interface | Rename to `AlphaStore` or `BrainStore` — the store is not options-specific |
| 🔴 BLOCKER | `pyproject.toml` | No `keywords`, `classifiers`, `urls`, authors | Add full metadata |
| 🟡 HIGH | `db.py` | PostgreSQL pool is created synchronously at class init — will throw on environments without `DATABASE_URL` | Use lazy connection: open the pool only on first write |
| 🟡 HIGH | `store.py` | `load_evaluated_expressions()` loads the entire set into memory — will OOM on large runs | Add pagination: `load_evaluated_expressions(limit=None, offset=0)` |
| 🟠 MEDIUM | `migrations/` | Migration directory exists but its contents were not inspectable — unclear if Alembic or raw SQL | Add a `README` in `migrations/` describing how to run them |
| 🟠 MEDIUM | `pyproject.toml` | `asyncpg` or `psycopg2` is not listed as a dependency despite `db.py` clearly using a DB driver | Declare optional dep: `postgres = ["asyncpg>=0.29"]` |
| 🟢 LOW | `store.py` | No `__repr__` on the store class | Add for debuggability |

**Missing entirely:**
- `py.typed` marker
- Any documented schema migration strategy for version upgrades

---

### 2.3 brain-decorrelator

**Overall:** The best-designed library from an API perspective. The `AxisPlugin` ABC + `@register_axis` decorator is clean, extensible, and strategy-agnostic. This is the library most likely to be used independently.

| Severity | File | Issue | Fix |
|---|---|---|---|
| 🔴 BLOCKER | `pyproject.toml` | No `keywords`, `classifiers`, `urls`, authors | Add full metadata |
| 🔴 BLOCKER | `README.md` | Quickstart requires `import brain_decorrelator.axes.universal` as a side-effecting import to register axes | This is a footgun. Auto-register universal axes in `__init__.py`; let users opt-out instead of opt-in |
| 🟡 HIGH | `engine.py` | `generate_orthogonal_variants()` returns `List[DecorrelationResult]` but the `DecorrelationResult` dataclass is not exported from `__init__.py` | Export it |
| 🟡 HIGH | `plugin.py` | Plugin registry is a module-level list — not thread-safe for concurrent registration | Use a `threading.Lock` or switch to a frozen registry pattern after first call |
| 🟠 MEDIUM | `axes/universal.py` | No tests for individual axis transforms in isolation | Add unit tests per axis: input expression → expected output shape |
| 🟠 MEDIUM | `engine.py` | Hash-based deduplication uses SHA-256 with `[:16]` truncation — collision probability is negligible but the intent is not documented | Add a comment explaining the collision tolerance |
| 🟢 LOW | `plugin.py` | `get_registered_axes()` returns the live internal list — mutations to the returned list would corrupt the registry | Return a copy: `return list(_AXES)` |

**Missing entirely:**
- `py.typed` marker
- No way to list or introspect registered axes from outside the engine (useful for debugging/logging)
- No `unregister_axis` for test isolation

---

### 2.4 brain-options

**Overall:** The largest library (46 KB `generator.py`, 52 KB `templates.py`, 96 KB `catalog.json`). This is the alpha generation workhorse. The sheer size of `generator.py` is the primary code-quality concern.

| Severity | File | Issue | Fix |
|---|---|---|---|
| 🔴 BLOCKER | `pyproject.toml` | No `keywords`, `classifiers`, `urls`, authors | Add full metadata |
| 🔴 BLOCKER | `generator.py` | 46 KB, single file — violates single-responsibility at multiple points | Split into `generator/template_runner.py`, `generator/llm_runner.py`, `generator/pipeline.py` |
| 🟡 HIGH | `catalog.json` | 96 KB JSON file committed to source — this is a content database, not code | Move to a proper data directory `data/catalog.json`, document its schema, and provide a `CatalogLoader` utility |
| 🟡 HIGH | `templates.py` | 52 KB file of template strings — untestable as written | Extract each template into a named, importable constant; add a test that validates every template renders without error |
| 🟡 HIGH | All | No type stubs for the `wqb` third-party dependency | Document that `wqb` types are unverified; consider wrapping behind a typed adapter |
| 🟠 MEDIUM | `archetypes.py` | Archetype definitions duplicate field names already in `brain_core.types.AlphaCandidate` | Use `AlphaCandidate` as the return type throughout; do not redefine fields |
| 🟠 MEDIUM | `dedup.py` | Deduplication logic is local to `brain-options` | This belongs in `brain-decorrelator` or `brain-core` as a shared utility |
| 🟢 LOW | `peer_genome.py` | Unclear what this module does from the name alone | Add a module-level docstring explaining the concept |

**Missing entirely:**
- Integration test with a mock WQB API response
- `py.typed` marker
- Changelog entry

---

### 2.5 brain-sentiment

**Overall:** Structurally mirrors `brain-options` well (same module layout). Smaller at ~10 KB per key file, which is healthier.

| Severity | File | Issue | Fix |
|---|---|---|---|
| 🔴 BLOCKER | `pyproject.toml` | No `keywords`, `classifiers`, `urls`, authors | Add full metadata |
| 🟡 HIGH | `catalog.json` | 13 KB JSON committed to source | Move to `data/` and document schema |
| 🟡 HIGH | `dedup.py` | Identical duplication of the dedup logic from `brain-options` | Extract shared utility to `brain-core` |
| 🟠 MEDIUM | `specialist/` | Subpackage exists but purpose is unclear from the name | Add `__init__.py` docstring explaining what specialists are |
| 🟠 MEDIUM | `kb.py` | 6.8 KB "knowledge base" file — unclear whether this is runtime data or codified heuristics | Add module-level docstring; if data, move to `data/` |
| 🟢 LOW | `prompts.py` | Prompt strings live in source — changes require a code commit | Consider loading from `data/prompts.yaml` to allow prompt tuning without re-releasing |

**Missing entirely:**
- `py.typed` marker
- Tests for sentiment-specific archetype generation
- `CHANGELOG.md` entry for `0.1.0`

---

### 2.6 brain-risk-model

**Overall:** Same pattern as `brain-sentiment`. Code quality is consistent. The risk-model domain is well-bounded.

| Severity | File | Issue | Fix |
|---|---|---|---|
| 🔴 BLOCKER | `pyproject.toml` | No `keywords`, `classifiers`, `urls`, authors | Add full metadata |
| 🟡 HIGH | `catalog.json` | 27 KB JSON committed to source | Move to `data/` |
| 🟡 HIGH | `dedup.py` | Third copy of the identical dedup utility | Extract to `brain-core` |
| 🟠 MEDIUM | `README.md` | Stub — only 489 bytes | Needs a proper quickstart, archetype table, and architecture tree |
| 🟠 MEDIUM | `archetypes.py` | 8 KB — 2× smaller than the options equivalent, suggesting coverage gaps | Audit: are BAB, Momentum, Quality, Value, and Low-Vol archetypes all present? |
| 🟢 LOW | `engine.py` | 2.4 KB — very thin. Unclear if this is intentionally a facade or an incomplete implementation | Add a module docstring explaining the design intent |

**Missing entirely:**
- `py.typed` marker
- Any whitepaper or math derivation doc for the factor premia calculations
- `CHANGELOG.md` entry

---

### 2.7 brain-synthesis

**Overall:** The most ambitious library and the one with the most hardcoded assumptions.

| Severity | File | Issue | Fix |
|---|---|---|---|
| 🔴 BLOCKER | `pyproject.toml` | No `keywords`, `classifiers`, `urls`, authors | Add full metadata |
| 🔴 BLOCKER | `apex_generator.py` | All 5 formulations hardcode WQ data field names (`snt1_d1_netearningsrevision`, `implied_volatility_mean_30`, `fscore_surface_accel`) | Document in `DATA_DICTIONARY.md`; add a note that users must have access to these WQ datasets |
| 🔴 BLOCKER | `apex_generator.py` | `ApexCandidate` subclasses `AlphaCandidate` across a package boundary without a documented contract | Add `__post_init__` validation; document the inheritance contract explicitly |
| 🟡 HIGH | `combiner.py` | 2.1 KB — very thin. `CombinationEngine` does not support runtime weight adjustment | Add a `weights` parameter to allow per-leg tuning at runtime |
| 🟡 HIGH | `engine.py` | 2.3 KB facade — no error handling if one domain engine is unavailable | Wrap each domain fetch in try/except so a single domain failure does not abort synthesis |
| 🟠 MEDIUM | `README.md` | Hardcodes WQ dataset names in the architecture table without explaining what they are | Add a data-dependencies section |
| 🟢 LOW | `__init__.py` | Only 375 bytes — very sparse exports | Export `ApexCandidate`, `DecorrelationResult` for downstream users |

**Missing entirely:**
- `py.typed` marker
- `DATA_DICTIONARY.md` — completely opaque without knowing the WQ data field names
- Any test validating that the 5 apex formulations produce valid Fast Expression strings

---

## 3. Cross-Cutting Issues

These issues appear in multiple libraries or in the monorepo itself.

| Severity | Scope | Issue | Fix |
|---|---|---|---|
| 🔴 BLOCKER | All 7 `pyproject.toml` | No `keywords`, `classifiers`, `[project.urls]` | See §5 — add to every package |
| 🔴 BLOCKER | Monorepo root | No `LICENSE` file | Add `MIT` license file at `brain_libraries/LICENSE` (or monorepo root) |
| 🔴 BLOCKER | `cli.py` | CLI entry point not declared in any `pyproject.toml` | Add `[project.scripts] brain = "brain_libraries.cli:main"` to `brain-synthesis` or a new `brain-cli` package |
| 🟡 HIGH | `brain_options`, `brain_sentiment`, `brain_risk_model` | `dedup.py` is copy-pasted in all three | Move to `brain_core.utils.dedup` |
| 🟡 HIGH | All 7 | No `py.typed` marker — packages are not PEP 561 compliant | Add empty `py.typed` file to each package directory |
| 🟡 HIGH | All 7 | Badges in README reference `Xtley001/brain-libraries` placeholder | Replace with `Xtley001/brain-libraries` |
| 🟡 HIGH | `.github/workflows/` | CI does not publish to PyPI on tag push | Add a `release.yml` workflow that publishes on `v*` tags |
| 🟠 MEDIUM | All 7 | No `CHANGELOG.md` entries beyond stubs | Write proper `0.1.0` release notes following Keep-a-Changelog format |
| 🟠 MEDIUM | All 7 | No `docs/whitepaper.md` for the quantitative methodology | Write one per domain library explaining the economic rationale |
| 🟠 MEDIUM | `test_all.py` | Uses subprocess execution model — test output is not captured by pytest | Refactor to use `pytest --import-mode=importlib` across all packages |
| 🟢 LOW | All 7 | No `mypy.ini` or `[tool.mypy]` in any `pyproject.toml` | Add type-checking configuration |
| 🟢 LOW | All 7 | No `ruff` or `black` configuration declared | Standardise formatter config in root `pyproject.toml` |

---

## 4. What Must Be Removed

| Item | Location | Reason |
|---|---|---|
| `OptionsStore` as primary export name | `brain_store/__init__.py` | Domain-specific name in a domain-agnostic library — breaks the stated abstraction |
| `Xtley001` in all badge URLs | All READMEs | Placeholder — exposes that documentation is not production-ready |
| Duplicated `dedup.py` | `brain_options`, `brain_sentiment`, `brain_risk_model` | Code duplication — one bug fix must be applied in 3 places |
| `load_dotenv()` at module import time | `brain_core/config.py` line 40 | Side-effectful import breaks test isolation and library composition |
| `catalog.json` committed to the package source tree | All domain libraries | Binary/data files balloon the package size and cannot be version-controlled separately from code |

---

## 5. What Must Be Added

### 5.1 PyPI Metadata (every `pyproject.toml`)

This is the single highest-leverage change for discoverability. Every package needs:

```toml
[project]
name = "brain-decorrelator"
version = "0.1.0"
description = "Strategy-agnostic alpha decorrelation engine with plugin-based orthogonalization axes."
readme = "README.md"
requires-python = ">=3.9"
license = { text = "MIT" }
authors = [{ name = "Xtley001", email = "your@email.com" }]
keywords = [
    "worldquant", "brain", "alpha", "quantitative-finance",
    "algorithmic-trading", "factor-investing", "decorrelation",
    "signal-processing", "financial-ml",
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Financial and Insurance Industry",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Office/Business :: Financial :: Investment",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
]

[project.urls]
Homepage = "https://github.com/Xtley001/brain-libraries"
Repository = "https://github.com/Xtley001/brain-libraries"
Documentation = "https://github.com/Xtley001/brain-libraries"
"Bug Tracker" = "https://github.com/Xtley001/brain-libraries/issues"
```

### 5.2 CLI Entry Point Declaration

Add to whichever package owns `cli.py` (recommend a top-level `brain-cli` package, or add to `brain-synthesis`):

```toml
[project.scripts]
brain = "brain_libraries.cli:main"
```

### 5.3 Missing Files (per library)

| File | Purpose |
|---|---|
| `py.typed` | PEP 561 compliance — signals typed package to mypy/pyright |
| `LICENSE` | Required for PyPI upload and legal clarity |
| `docs/whitepaper.md` | Economic rationale for the quantitative methodology |
| `data/DATA_DICTIONARY.md` | WQ dataset field name documentation (critical for `brain-synthesis`) |
| `.github/workflows/release.yml` | Automated PyPI publish on version tag |

### 5.4 Shared Utilities in `brain-core`

```
brain_core/
├── utils/
│   ├── __init__.py
│   ├── dedup.py          # extracted from 3 domain libraries
│   └── expression.py     # shared Fast Expression string utilities
```

### 5.5 `unregister_axis` for test isolation

```python
# brain_decorrelator/plugin.py
def unregister_axis(plugin: AxisPlugin) -> None:
    """Remove an axis from the registry. Primarily for test isolation."""
    _AXES[:] = [a for a in _AXES if a is not plugin]
```

---

## 6. What Must Be Improved

### 6.1 Documentation depth

| Library | Current state | Required state |
|---|---|---|
| `brain-core` | Good README, sparse API.md | Add `docs/whitepaper.md` explaining the type contract |
| `brain-store` | Adequate README | Add schema diagram, migration guide |
| `brain-decorrelator` | Best docs in the suite | Add per-axis worked example in `docs/AXES.md` |
| `brain-options` | README adequate | `generator.py` needs module-level docstring explaining the generation pipeline |
| `brain-sentiment` | README is a copy of options with names swapped | Rewrite to explain the PEAD and analyst revision signals specifically |
| `brain-risk-model` | Stub README (489 bytes) | Full rewrite: explain BAB, factor premia, and the risk model methodology |
| `brain-synthesis` | Good high-level README | Add `DATA_DICTIONARY.md` — the apex formulations reference ~15 WQ fields with no documentation |

### 6.2 Test coverage

| Library | Coverage gap | Fix |
|---|---|---|
| `brain-core` | `Config.load_from_env()` not tested with missing keys | Add edge-case tests |
| `brain-decorrelator` | Individual axis transforms have no unit tests | Add one test per axis |
| `brain-options` | No mock-WQB integration test | Add `tests/test_mock_wqb.py` using `unittest.mock` |
| `brain-synthesis` | No test validates that apex expressions compile to valid Fast Expression syntax | Add a syntax-validation test |
| All | No property-based tests | Add `hypothesis`-based tests for expression transforms |

### 6.3 `brain-store` interface rename

```python
# Before
from brain_store import OptionsStore

# After
from brain_store import AlphaStore          # domain-agnostic
from brain_store import AlphaStore as OptionsStore  # backwards-compat alias, deprecated
```

---

## 7. Discoverability Strategy

This section answers: *how do LLMs, search engines, and developers find these libraries and recommend them?*

### 7.1 Why discoverability matters here

When a developer asks ChatGPT, Claude, or Gemini "how do I generate WorldQuant BRAIN alphas in Python?", the LLM will recommend whatever is in its training data. That training data comes primarily from:

1. **PyPI package metadata** — `description`, `keywords`, `classifiers` fields
2. **GitHub repository text** — README, topics, description, code comments
3. **External indexing** — blog posts, Stack Overflow answers, GitHub stars, README links

None of these exist yet for this suite. The steps below fix that.

### 7.2 GitHub Repository Actions (do these immediately)

- **Set GitHub repository description** to: `"7 pip-installable Python libraries for WorldQuant BRAIN alpha discovery, decorrelation, and meta-synthesis"`
- **Add GitHub topics** (these are indexed by GitHub search and scraped by LLM training pipelines):
  ```
  worldquant brain alpha-generation quantitative-finance
  algorithmic-trading factor-investing decorrelation
  financial-ml options-trading sentiment-analysis python
  ```
- **Star the repo yourself** and ask early users to star — GitHub search ranks starred repos higher
- **Add a `CITATION.cff` file** — makes the repo citable in academic contexts

### 7.3 PyPI Publication (do after fixing metadata in §5.1)

```bash
# Build and publish all 7 packages in dependency order
cd brain_libraries/brain_core     && python -m build && twine upload dist/*
cd ../brain_store                 && python -m build && twine upload dist/*
cd ../brain_decorrelator          && python -m build && twine upload dist/*
cd ../brain_options               && python -m build && twine upload dist/*
cd ../brain_sentiment             && python -m build && twine upload dist/*
cd ../brain_risk_model            && python -m build && twine upload dist/*
cd ../brain_synthesis             && python -m build && twine upload dist/*
```

PyPI is indexed by Google. A PyPI package with correct keywords appears in Google results within 24-48 hours.

### 7.4 README Signals for LLM Training

LLMs learn to recommend libraries from patterns in their training text. The README must contain the exact phrases a user would type when asking for help:

Add this paragraph to the monorepo top-level `README.md`:

```markdown
## Who is this for

If you are building a WorldQuant BRAIN alpha pipeline in Python and need:
- **Alpha generation** across options, sentiment, or risk-model datasets
- **Decorrelation** to pass the BRAIN correlation gate without losing Sharpe
- **Multi-factor synthesis** to combine signals into unique meta-alphas
- **State persistence** across simulation runs

...then install the relevant library from this suite.
```

This phrasing matches natural-language questions developers ask LLMs, increasing the probability the library appears in training-time associations.

### 7.5 `CITATION.cff` (academic discoverability)

Create `CITATION.cff` at the monorepo root:

```yaml
cff-version: 1.2.0
message: "If you use this software, please cite it as below."
authors:
  - family-names: ""
    alias: "Xtley001"
title: "Brain Alpha Pipeline"
version: 0.1.0
date-released: 2026-10-09
url: "https://github.com/Xtley001/brain-libraries"
repository-code: "https://github.com/Xtley001/brain-libraries"
keywords:
  - WorldQuant BRAIN
  - alpha generation
  - quantitative finance
  - decorrelation
  - factor investing
```

### 7.6 Write One High-Quality Blog Post

A single detailed blog post titled:

> **"Building a modular WorldQuant BRAIN alpha pipeline in Python: from options to meta-synthesis"**

...published on Medium or dev.to with links to the GitHub repo and PyPI packages, will:
- Appear in Google results for "WorldQuant BRAIN Python library"
- Be indexed by LLM training corpora (Common Crawl, etc.)
- Drive GitHub stars, which drive further organic discovery

The post should cover: the problem, the architecture diagram from the README, a 15-line code example using `brain-decorrelator`, and a link to install.

### 7.7 LLM-Readable Documentation Pattern

LLMs are trained on structured text. The following patterns make library documentation more likely to be quoted in LLM outputs:

- **Consistent `## Usage` sections** with copy-pasteable code — this is what LLMs surface when answering "how do I use X"
- **FAQ-style sections** like `## Why brain-decorrelator instead of writing your own?` — these appear verbatim in LLM answers because they match the question format
- **Inline type hints everywhere** — type-annotated code is preferred by LLMs for code generation tasks

---

## 8. Prioritised Action Plan

Work in this order. Blockers before mediums; discoverability work after code is solid.

| Priority | Action | Libraries affected | Effort |
|---|---|---|---|
| **P0** | Add `LICENSE` file to monorepo root | All | 5 min |
| **P0** | Fix badge URLs from `Xtley001` → `Xtley001` | All READMEs | 15 min |
| **P0** | Add full PyPI metadata to all 7 `pyproject.toml` | All | 1 hr |
| **P0** | Rename `OptionsStore` → `AlphaStore` in `brain-store` | `brain_store` | 30 min |
| **P1** | Add `py.typed` marker to all 7 packages | All | 10 min |
| **P1** | Extract `dedup.py` to `brain_core.utils` | `brain_core`, options, sentiment, risk | 1 hr |
| **P1** | Declare CLI entry point in `pyproject.toml` | `brain_synthesis` or new `brain-cli` | 30 min |
| **P1** | Move `catalog.json` files to `data/` subdirectory | options, sentiment, risk | 1 hr |
| **P1** | Auto-register universal axes in `brain_decorrelator/__init__.py` | `brain_decorrelator` | 20 min |
| **P2** | Rewrite `brain-risk-model` README (currently 489 bytes) | `brain_risk_model` | 2 hr |
| **P2** | Write `DATA_DICTIONARY.md` for WQ field names | `brain_synthesis` | 2 hr |
| **P2** | Add `release.yml` GitHub Actions workflow for PyPI publish | Monorepo | 1 hr |
| **P2** | Move `load_dotenv()` into `Config.load_from_env()` | `brain_core` | 15 min |
| **P2** | Add per-axis unit tests to `brain-decorrelator` | `brain_decorrelator/tests` | 2 hr |
| **P3** | Split `brain_options/generator.py` (46 KB) | `brain_options` | 3-4 hr |
| **P3** | Add `docs/whitepaper.md` per domain library | options, sentiment, risk | 4 hr each |
| **P3** | Publish all 7 packages to PyPI | All | 2 hr |
| **P3** | Set GitHub repo topics and description | GitHub UI | 10 min |
| **P3** | Add `CITATION.cff` | Monorepo root | 20 min |
| **P4** | Write and publish the blog post | External | 4 hr |

---

*Maintained by [Xtley001](https://github.com/Xtley001). Open an issue for corrections or additions.*
