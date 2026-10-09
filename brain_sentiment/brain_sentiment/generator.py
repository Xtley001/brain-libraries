"""
Multi-tier Institutional Sentiment Candidate Generator.
Orchestrates:
1. Deterministic high-confidence templates (Tier 1)
2. Modular Strategy Sub-Systems (Tier 2)
3. Mechanical Mutation Tier with decay and operator sweeps (Tier 3)
"""
from __future__ import annotations

import logging
import random
from typing import Any, List, Optional, Set

from brain_core.llm import clean_json_array
from brain_sentiment.catalog import SentimentCatalog
from brain_sentiment.dedup import SentimentDeduplicator
from brain_sentiment.kb import SentimentKnowledgeBase
from brain_sentiment.prompts import (
    build_sentiment_reasoning_prompt,
    build_sentiment_system_prompt,
)
from brain_sentiment.templates import (
    SentimentCandidate,
    compile_sentiment_invariant,
    generate_template_candidates,
)
from brain_sentiment.strategies import generate_modular_candidates

log = logging.getLogger("brain_sentiment.generator")


class SentimentGenerator:
    def __init__(
        self,
        kb: Optional[SentimentKnowledgeBase] = None,
        catalog: Optional[SentimentCatalog] = None,
        db: Optional[Any] = None,
        llm_adapter: Optional[Any] = None,
    ):
        self.kb = kb or SentimentKnowledgeBase()
        self.catalog = catalog or SentimentCatalog()
        self.deduplicator = SentimentDeduplicator()
        self.db = db
        self.llm_adapter = llm_adapter

        seen_hashes = set()
        queue: list[SentimentCandidate] = []
        for c in generate_template_candidates() + generate_modular_candidates():
            h = self.deduplicator.hash(c.expression)
            if h not in seen_hashes:
                seen_hashes.add(h)
                queue.append(c)

        self._template_queue: list[SentimentCandidate] = queue
        self._llm_queue: list[SentimentCandidate] = []
        self._archetype_idx = 0

        # Multi-Armed Bandit prior weights across sentiment archetypes.
        # Keys MUST match the `category` field in SENTIMENT_ARCHETYPES so that
        # db.get_empirical_archetype_weights() can aggregate rewards correctly.
        self.archetype_priors: dict[str, float] = {
            "pead_revision": 0.30,
            "sue_shock": 0.25,
            "target_revisions": 0.20,
            "forecast_dispersion": 0.15,
            "dynamic_attention": 0.10,
        }

    def get_current_weights(self) -> dict[str, float]:
        """Calculates dynamic MAB sampling weights from RL state or returns base priors."""
        if self.db and hasattr(self.db, "get_empirical_archetype_weights"):
            try:
                return self.db.get_empirical_archetype_weights(
                    list(self.archetype_priors.keys()),
                    self.archetype_priors,
                )
            except Exception as e:
                log.warning("Failed to fetch empirical weights, falling back to priors: %s", e)
        return dict(self.archetype_priors)

    def _generate_llm_batch(self, count: int = 4) -> bool:
        """Invokes multi-provider LLM tier to synthesize novel institutional sentiment expressions."""
        if not self.llm_adapter:
            return False

        weights_dict = self.get_current_weights()
        archetypes = list(weights_dict.keys())
        weights = list(weights_dict.values())
        chosen_archetype = random.choices(archetypes, weights=weights, k=1)[0]
        card = self.kb.get_card(chosen_archetype)
        cards = [card] if card else []

        system_prompt = build_sentiment_system_prompt()
        prompt = build_sentiment_reasoning_prompt(chosen_archetype, cards, n=count)

        try:
            raw_output = self.llm_adapter.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
            )
            if not raw_output:
                return False

            parsed = clean_json_array(raw_output)
            added = 0
            for item in parsed:
                expr = item.get("expression", "").strip()
                if not expr:
                    continue

                decay = random.choice([10, 12, 14, 15])
                group = random.choice(["subindustry", "sector"])
                valid_expr = compile_sentiment_invariant(expr, default_decay=decay, default_group=group)
                if not self.deduplicator.is_duplicate(valid_expr):
                    self._llm_queue.append(
                        SentimentCandidate(
                            expression=valid_expr,
                            archetype=item.get("archetype", chosen_archetype),
                            family=f"LLM_Sentiment_{chosen_archetype}",
                            hypothesis=item.get("hypothesis", f"LLM synthesized reasoning for {chosen_archetype}"),
                            universe=random.choice(["TOP3000", "TOP2000"]),
                            neutralization=group.upper(),
                            decay=decay,
                        )
                    )
                    added += 1
            return added > 0
        except Exception as e:
            log.warning("Sentiment LLM generation failed: %s", e)
            return False

    def generate_candidate(self) -> SentimentCandidate:
        """Pulls next deterministic candidate, LLM synthesized candidate, or mutates an existing archetype."""
        # Tier 1: Deterministic golden templates
        if self._template_queue:
            return self._template_queue.pop(0)

        # Tier 2: Knowledge-injected LLM reasoning tier
        if self.llm_adapter:
            if not self._llm_queue:
                self._generate_llm_batch()
            if self._llm_queue:
                return self._llm_queue.pop(0)

        # Tier 3: Systematic parameter & operator mutation
        weights_dict = self.get_current_weights()
        archetypes = list(weights_dict.keys())
        weights = list(weights_dict.values())
        chosen_archetype = random.choices(archetypes, weights=weights, k=1)[0]
        card = self.kb.get_card(chosen_archetype)
        base_expr = card.formula_sketch if card else "group_neutralize(rank(ts_decay_linear(snt1_d1_netearningsrevision, 12)), subindustry)"

        mutated_decay = random.choice([8, 10, 12, 14, 16, 20])
        mutated_group = random.choice(["subindustry", "sector", "industry"])
        mutated_expr = compile_sentiment_invariant(base_expr, default_decay=mutated_decay, default_group=mutated_group)

        return SentimentCandidate(
            expression=mutated_expr,
            archetype=chosen_archetype,
            family="Mutated_Sentiment",
            hypothesis=f"Systematic exploration of {chosen_archetype} with decay={mutated_decay} and group={mutated_group}.",
            universe=random.choice(["TOP3000", "TOP2000"]),
            neutralization=mutated_group.upper(),
            decay=mutated_decay,
        )

    def total_queued(self) -> int:
        return len(self._template_queue)
