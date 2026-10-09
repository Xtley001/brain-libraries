"""
Brain Alpha Pipeline — Unified Cross-Domain CLI.

Provides a unified interface across all 7 libraries:
- Candidate generation across domains (options, sentiment, risk, synthesis)
- Strategy-agnostic decorrelation transformations
- Dual-mode storage inspection and health checks
- Multi-library test runner
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from typing import List, Optional

# Prioritize installed editable packages over workspace root directories
_curr_file = os.path.abspath(__file__)
_brain_lib_dir = os.path.abspath(os.path.join(os.path.dirname(_curr_file), "..", ".."))
_workspace_root = os.path.dirname(_brain_lib_dir)
sys.path = [p for p in sys.path if os.path.abspath(p) not in (_brain_lib_dir, _workspace_root)]
_editables = [f for f in sys.meta_path if "Editable" in getattr(f, "__name__", "")]
for f in _editables:
    sys.meta_path.remove(f)
    sys.meta_path.insert(0, f)

log = logging.getLogger("brain_cli")


def cmd_generate(args: argparse.Namespace) -> int:
    domain = args.domain.lower()
    count = args.count

    results = []

    if domain in ("options", "all"):
        try:
            from brain_options import OptionsAlphaEngine
            engine = OptionsAlphaEngine()
            cands = engine.generate_candidates(count=count)
            for c in cands:
                results.append({
                    "domain": "options",
                    "archetype": getattr(c, "archetype_name", None) or getattr(c, "archetype", "unknown"),
                    "expression": c.expression,
                    "universe": getattr(c, "universe", "TOP3000"),
                    "decay": getattr(c, "decay", 8),
                })
        except Exception as exc:
            log.warning("Could not generate options candidates: %s", exc)

    if domain in ("sentiment", "all"):
        try:
            from brain_sentiment import SentimentAlphaEngine
            engine = SentimentAlphaEngine()
            cands = engine.generate_candidates(count=count)
            for c in cands:
                results.append({
                    "domain": "sentiment",
                    "archetype": getattr(c, "archetype_name", None) or getattr(c, "archetype", "unknown"),
                    "expression": c.expression,
                    "universe": getattr(c, "universe", "TOP3000"),
                    "decay": getattr(c, "decay", 8),
                })
        except Exception as exc:
            log.warning("Could not generate sentiment candidates: %s", exc)

    if domain in ("risk", "all"):
        try:
            from brain_risk_model import RiskModelAlphaEngine
            engine = RiskModelAlphaEngine()
            cands = engine.generate_candidates(count=count)
            for c in cands:
                results.append({
                    "domain": "risk_model",
                    "archetype": getattr(c, "archetype_name", None) or getattr(c, "archetype", "unknown"),
                    "expression": c.expression,
                    "universe": getattr(c, "universe", "TOP3000"),
                    "decay": getattr(c, "decay", 8),
                })
        except Exception as exc:
            log.warning("Could not generate risk model candidates: %s", exc)

    if domain in ("synthesis", "all"):
        try:
            from brain_synthesis.engine import SynthesisEngine
            engine = SynthesisEngine()
            cands = engine.get_golden_candidates()[:count]
            for c in cands:
                results.append({
                    "domain": "synthesis",
                    "archetype": getattr(c, "archetype_name", None) or getattr(c, "name", "synthesis_apex"),
                    "expression": c.expression,
                    "universe": getattr(c, "universe", "TOP3000"),
                    "decay": getattr(c, "decay", 15),
                })
        except Exception as exc:
            log.warning("Could not generate synthesis candidates: %s", exc)

    if getattr(args, "json", False):
        print(json.dumps(results, indent=2))
    else:
        print(f"\nGenerated {len(results)} Alpha Candidates:")
        print("=" * 80)
        for i, r in enumerate(results, 1):
            print(f"[{i:02d}] Domain   : {r['domain']}")
            print(f"     Archetype: {r['archetype']}")
            print(f"     Universe : {r['universe']} | Decay: {r['decay']}")
            print(f"     Formula  : {r['expression']}")
            print("-" * 80)

    return 0


def cmd_decorrelate(args: argparse.Namespace) -> int:
    from brain_decorrelator import DecorrelationEngine
    engine = DecorrelationEngine()
    results = engine.generate_orthogonal_variants(
        base_expr=args.expression,
        archetype=args.archetype,
        base_sharpe=args.base_sharpe,
    )

    if getattr(args, "json", False):
        out = [
            {
                "axis": r.axis_name,
                "archetype": r.archetype_name,
                "expression": r.expression,
                "hypothesis": r.hypothesis,
            }
            for r in results
        ]
        print(json.dumps(out, indent=2))
    else:
        print(f"\nGenerated {len(results)} Orthogonal Variants for: {args.expression}")
        print("=" * 80)
        for r in results:
            print(f"Axis     : {r.axis_name}")
            print(f"Archetype: {r.archetype_name}")
            print(f"Formula  : {r.expression}")
            print("-" * 80)

    return 0


def cmd_store_status(args: argparse.Namespace) -> int:
    from brain_core.config import Config
    from brain_store import AlphaStore
    cfg = Config.load_from_env()
    store = AlphaStore(database_url=cfg.database_url)
    known = store.load_evaluated_expressions()

    print("\nStorage Subsystem Status:")
    print(f"  Mode                  : {'PostgreSQL Pool' if store.db.is_available() else 'Local File Cache'}")
    print(f"  Cached Evaluations    : {len(known)}")
    print(f"  Data Directory        : {store.data_dir}\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="brain",
        description="WorldQuant BRAIN Alpha Pipeline — Unified CLI",
    )
    subparsers = parser.add_subparsers(dest="subcommand")

    # 1. generate
    p_gen = subparsers.add_parser("generate", help="Generate alpha candidates across domains")
    p_gen.add_argument(
        "--domain",
        choices=["options", "sentiment", "risk", "synthesis", "all"],
        default="all",
        help="Target domain to generate for (default: all)",
    )
    p_gen.add_argument("--count", type=int, default=3, help="Number of candidates to generate per domain")
    p_gen.add_argument("--json", action="store_true", help="Output JSON formatted response")
    p_gen.set_defaults(func=cmd_generate)

    # 2. decorrelate
    p_dec = subparsers.add_parser("decorrelate", help="Apply orthogonal decorrelation transforms")
    p_dec.add_argument("expression", help="Base Fast Expression to decorrelate")
    p_dec.add_argument("--archetype", default="generic", help="Archetype identifier")
    p_dec.add_argument("--base-sharpe", type=float, default=1.5, help="Base candidate Sharpe ratio")
    p_dec.add_argument("--json", action="store_true", help="Output JSON formatted response")
    p_dec.set_defaults(func=cmd_decorrelate)

    # 3. store
    p_st = subparsers.add_parser("store", help="Inspect storage and state subsystem")
    p_st.set_defaults(func=cmd_store_status)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    if argv is None and len(sys.argv) <= 1:
        parser.print_help()
        return 0
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
