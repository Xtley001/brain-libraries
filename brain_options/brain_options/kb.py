"""
Options Alpha Knowledge Base Parser and Retrieval Engine.
Parses options-kb-master-books1-4.md to provide structured quantitative derivatives
cards, heuristics, formula sketches, and pitfalls to the LLM agentic tiers.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class KnowledgeCard:
    title: str
    section: str
    archetype: str
    idea: str
    heuristic: str
    expression_sketch: str = ""
    pitfall: str = ""
    notes: str = ""
    source: str = ""
    is_corroborated: bool = False

    def to_prompt_text(self) -> str:
        """Formats the card concisely for injection into LLM prompts."""
        lines = [f"### {self.title}"]
        if self.idea:
            lines.append(f"- Principle: {self.idea}")
        if self.heuristic:
            lines.append(f"- Heuristic: {self.heuristic}")
        if self.expression_sketch:
            lines.append(f"- Formula Sketch: `{self.expression_sketch}`")
        if self.pitfall:
            lines.append(f"- Pitfall Warning: {self.pitfall}")
        return "\n".join(lines)


class OptionsKnowledgeBase:
    """Loads and queries the master options derivatives knowledge base."""

    SECTION_TO_ARCHETYPE = {
        "FORWARD BASIS": "forward_basis",
        "FORWARD-BASIS": "forward_basis",
        "PCR FLOW": "pcr_flow",
        "PCR-FLOW": "pcr_flow",
        "SKEW": "skew",
        "TERM STRUCTURE": "term_structure",
        "TERM-STRUCTURE": "term_structure",
        "BREAKEVEN": "breakeven",
        "SHORT INTEREST": "short_interest",
        "ANALYST REVISIONS": "analyst_revisions",
        "ACCRUALS": "accruals_cashflow",
        "SUPPLY CHAIN": "supply_chain",
        "EXTREME TAIL": "extreme_tail_risk",
        "INFORMED SHORT": "informed_short_demand",
        "IV LEAD LAG": "iv_lead_lag",
        "NETWORK MOMENTUM": "network_momentum",
        "HYBRID CONFLUENCE": "hybrid_confluence",
        "INSTITUTIONAL 13F": "institutional_13f_breadth",
        "13F": "institutional_13f_breadth",
        "INSIDER": "insider_cluster_buying",
        "PEAVD": "peavd_earnings_vol_drift",
        "EARNINGS VOL DRIFT": "peavd_earnings_vol_drift",
        "JUMP VARIANCE": "jump_variance_moments",
        "VARIANCE MOMENTS": "jump_variance_moments",
        "PATENT": "patent_innovation_efficiency",
        "INNOVATION EFFICIENCY": "patent_innovation_efficiency",
        "DYNAMIC SHORT SQUEEZE": "dynamic_short_squeeze",
        "SHORT SQUEEZE": "dynamic_short_squeeze",
        "ORDER FLOW VPIN": "order_flow_vpin",
        "VPIN": "order_flow_vpin",
        "GAMMA PINNING": "gamma_pinning_clustering",
        "CUSTOMER SUPPLIER": "customer_supplier_cascades",
        "CASCADES": "customer_supplier_cascades",
        "RD CAPITALIZATION": "rd_capitalization_spillovers",
        "R&D": "rd_capitalization_spillovers",
        "CAPEX ASSET GROWTH": "capex_asset_growth",
        "ASSET GROWTH": "capex_asset_growth",
        "PEAVRP": "peavrp_volatility_premia",
        "REALIZED JUMP": "realized_jump_intensity",
        "JUMP INTENSITY": "realized_jump_intensity",
        "DISTANCE TO DEFAULT": "distance_to_default_debt",
        "MERTON": "distance_to_default_debt",
        "MACRO FOMC": "macro_fomc_cpi_drift",
        "EVENT DRIFT": "macro_fomc_cpi_drift",
        "FORMULAIC": "formulaic_101",
        "OTHER": "other",
    }

    def __init__(self, kb_path: Optional[str] = None):
        if kb_path is None:
            # Default to docs/options/options-kb-master.md or root options-kb-master.md
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            candidates = [
                os.path.join(root_dir, "docs", "options", "options-kb-master.md"),
                os.path.join(root_dir, "docs", "options-kb-master.md"),
                os.path.join(root_dir, "options-kb-master.md"),
                os.path.join(root_dir, "options-kb-master-books1-4.md"),
            ]
            kb_path = next((p for p in candidates if os.path.exists(p)), candidates[0])
        self.kb_path = kb_path
        self.cards: list[KnowledgeCard] = []
        self._cards_by_archetype: dict[str, list[KnowledgeCard]] = {}
        self.high_confidence_themes: list[str] = []
        self._load()

    def _load(self):
        if not os.path.exists(self.kb_path):
            return

        with open(self.kb_path, "r", encoding="utf-8") as f:
            content = f.read()

        current_section = "GENERAL"
        current_archetype = "general"

        # Split into sections by ## headers
        sections = re.split(r"\n##\s+", content)
        for sec in sections:
            sec_lines = sec.strip().split("\n")
            if not sec_lines:
                continue
            sec_header = sec_lines[0].strip()

            # Check if this is the high-confidence themes section
            if "Cross-book high-confidence themes" in sec_header:
                for line in sec_lines[1:]:
                    line = line.strip()
                    if line and re.match(r"^\d+\.", line):
                        self.high_confidence_themes.append(line)
                continue

            # Identify section archetype
            for key, arch in self.SECTION_TO_ARCHETYPE.items():
                if key in sec_header.upper():
                    current_section = key
                    current_archetype = arch
                    break

            # Now parse cards (### Header) within section
            card_blocks = re.split(r"\n###\s+", "\n".join(sec_lines[1:]))
            for block in card_blocks:
                block = block.strip()
                if not block:
                    continue

                card_lines = block.split("\n")
                title = card_lines[0].strip()
                body = "\n".join(card_lines[1:])

                idea = self._extract_field(body, r"\*\*Idea:\*\*\s*(.*?)(?=\n\*\*[A-Z]|$)")
                heuristic = self._extract_field(body, r"\*\*Heuristic:\*\*\s*(.*?)(?=\n\*\*[A-Z]|$)")
                expr = self._extract_field(body, r"\*\*Expression sketch:\*\*\s*(.*?)(?=\n\*\*[A-Z]|$)")
                pitfall = self._extract_field(body, r"\*\*Pitfall:\*\*\s*(.*?)(?=\n\*\*[A-Z]|$)")
                notes = self._extract_field(body, r"\*\*Note:\*\*\s*(.*?)(?=\n\*\*[A-Z]|$)")
                source = self._extract_field(body, r"\*\*Source:\*\*\s*(.*?)(?=\n\*\*[A-Z]|$)")
                is_corroborated = bool(
                    re.search(r"corroborat|🔁", body, re.IGNORECASE) or "corroborated" in title.lower()
                )

                if idea or heuristic:
                    card = KnowledgeCard(
                        title=title,
                        section=current_section,
                        archetype=current_archetype,
                        idea=idea,
                        heuristic=heuristic,
                        expression_sketch=expr,
                        pitfall=pitfall,
                        notes=notes,
                        source=source,
                        is_corroborated=is_corroborated,
                    )
                    self.cards.append(card)
                    self._cards_by_archetype.setdefault(current_archetype, []).append(card)

    def _extract_field(self, text: str, pattern: str) -> str:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return " ".join(match.group(1).strip().split())
        return ""

    def get_cards_for_archetype(self, archetype: str, max_cards: int = 4) -> list[KnowledgeCard]:
        """Returns relevant cards for a specific archetype."""
        norm_arch = archetype.lower().replace("-", "_").replace(" ", "_")
        matches = self._cards_by_archetype.get(norm_arch, [])
        if not matches:
            # Fuzzy match
            for k, card_list in self._cards_by_archetype.items():
                if k in norm_arch or norm_arch in k:
                    matches = card_list
                    break
        return matches[:max_cards]

    def get_corroborated_cards(self) -> list[KnowledgeCard]:
        """Returns all cross-corroborated, high-confidence cards across books."""
        return [c for c in self.cards if c.is_corroborated]

    def format_cards_for_prompt(self, cards: list[KnowledgeCard]) -> str:
        """Formats a selection of cards into a clean markdown block for prompt context."""
        if not cards:
            return ""
        return "\n\n".join(card.to_prompt_text() for card in cards)
