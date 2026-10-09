"""
Peer Genome Graph: derives {tenor, moneyness, factor, decay} for every live/reserve
alpha so the generator and decorrelator can reason about collision risk *before*
paying for a simulation, instead of discovering it after.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

log = logging.getLogger(__name__)

TENOR_RE = re.compile(r"_(\d+)\b")

MONEYNESS_PATTERNS = {
    "put": re.compile(r"put_breakeven"),
    "call": re.compile(r"call_breakeven"),
}

FACTOR_PATTERNS = {
    "pcr": re.compile(r"pcr_vol|pcr_oi"),
    "iv_term_structure": re.compile(
        r"implied_volatility_mean_\d+\s*/\s*\(?\s*implied_volatility_mean_\d+"
    ),
    "call_put_iv_ratio": re.compile(
        r"implied_volatility_call_\d+\s*/\s*\(?\s*implied_volatility_put_\d+"
    ),
    "skew": re.compile(r"implied_volatility_mean_skew"),
}


@dataclass(frozen=True)
class AlphaGenome:
    alpha_id: str
    tenors: List[int]
    moneyness: List[str]   # e.g. ["call"], ["put"], ["call", "put"] for blends
    factors: List[str]     # e.g. ["pcr"], ["iv_term_structure"]
    decay: int


def extract_genome(alpha_id: str, expression: str, decay: int) -> AlphaGenome:
    tenors = sorted({int(t) for t in TENOR_RE.findall(expression) if int(t) >= 10})
    moneyness = [name for name, pat in MONEYNESS_PATTERNS.items() if pat.search(expression)]
    factors = [name for name, pat in FACTOR_PATTERNS.items() if pat.search(expression)]
    return AlphaGenome(
        alpha_id=alpha_id,
        tenors=tenors,
        moneyness=moneyness or ["unknown"],
        factors=factors or ["unknown"],
        decay=decay,
    )


class PeerGenomeGraph:
    """Loaded once per generation batch from options_alphas (SUBMITTED + QUALIFIED)."""

    def __init__(self, genomes: List[AlphaGenome]):
        self.genomes = genomes

    @classmethod
    def load(cls, db: Any) -> "PeerGenomeGraph":
        if hasattr(db, "get_all_active_alpha_rows"):
            rows = db.get_all_active_alpha_rows()
        elif hasattr(db, "db") and hasattr(db.db, "get_all_active_alpha_rows"):
            rows = db.db.get_all_active_alpha_rows()
        else:
            rows = []
        genomes = [
            extract_genome(r["alpha_id"], r["expression"], r.get("decay", 8))
            for r in rows
            if r.get("expression")
        ]
        return cls(genomes)

    def find_collision_risk(
        self, tenor: int, moneyness: str, factor: str, decay: int = 8
    ) -> Optional[AlphaGenome]:
        """
        Returns the first peer genome that shares tenor + moneyness + factor
        (an exact-cell collision, the case that produced npdm7vWa's 0.77 corr fail),
        or a peer that additionally shares a close decay (the tighter, riskier case).
        Returns None if the cell is free.
        """
        for g in self.genomes:
            if tenor in g.tenors and moneyness in g.moneyness and factor in g.factors:
                return g
        return None

    def decay_too_close(self, decay: int, peer: AlphaGenome, min_gap: int = 7) -> bool:
        return abs(decay - peer.decay) < min_gap
