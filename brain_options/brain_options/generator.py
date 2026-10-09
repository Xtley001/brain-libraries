"""
Multi-tier Options Candidate Generator.
Orchestrates:
1. Deterministic high-confidence templates (Tier 1)
2. Quantitative LLM Reasoning Tier with Options Knowledge Base injection (Tier 2)
3. Mechanical Mutation Tier for systematic alpha variations (Tier 3)
"""
from __future__ import annotations

import logging
from typing import List, Optional, Set
from brain_core.llm import LLMAdapter, clean_json_array
from brain_options.prompts import (
    OPTIONS_REASONING_PROMPT,
    OPTIONS_SYSTEM_PROMPT,
    build_mechanical_mutation_prompt,
    build_options_system_prompt,
    build_reasoning_prompt,
)
from brain_options.catalog import OptionsCatalog
from brain_options.dedup import ASTDeduplicator
from brain_options.kb import OptionsKnowledgeBase
from brain_options.templates import (
    OptionCandidate,
    compile_fitness_invariant,
    generate_high_capacity_candidates,
    generate_template_candidates,
)
from brain_options.peer_genome import PeerGenomeGraph, extract_genome
# auto_correct_for_collision provided by brain_decorrelator
#
from brain_options.strategies import generate_modular_candidates
from brain_store.db import map_archetype_to_core
from brain_options.notifier import send_telegram_emergency_alert

log = logging.getLogger("brain_options.generator")

import math
import random

CORE_ARCHETYPES = [
    "term_structure", "skew", "pcr_flow", "breakeven", "forward_basis",
    "short_interest", "analyst_revisions", "hybrid_confluence", "supply_chain",
    "accruals_cashflow", "informed_short_demand", "extreme_tail_risk", "iv_lead_lag",
    "network_momentum", "formulaic_101",
    "peavd_earnings_vol_drift", "jump_variance_moments",
    "dynamic_short_squeeze", "order_flow_vpin",
    "gamma_pinning_clustering", "peavrp_volatility_premia", "realized_jump_intensity",
    "macro_fomc_cpi_drift",
]

ENABLE_MANDATORY_TENOR_BLEND: bool = False  # Feature flag: observed alongside pure tenors before making mandatory


class OptionsGenerator:
    def __init__(
        self,
        llm_adapter: Optional[LLMAdapter] = None,
        kb: Optional[OptionsKnowledgeBase] = None,
        catalog: Optional[OptionsCatalog] = None,
        db: Optional[Any] = None,
    ):
        self.llm_adapter = llm_adapter
        self.kb = kb or OptionsKnowledgeBase()
        self.catalog = catalog or OptionsCatalog()
        self.db = db
        self.deduplicator = ASTDeduplicator()
        self.evaluated_expressions: Set[str] = set()
        # Seed queue: Prioritize virgin uncorrelated strategies at the front of the queue
        seen_hashes = set()
        queue: list[OptionCandidate] = []
        virgin_strategies = [
            "pcr_flow",
            "macro_fomc_cpi_drift",
            "peavrp_volatility_premia",
            "jump_variance_moments",
            "term_structure",
            "order_flow_vpin",
            "gamma_pinning_clustering",
            "realized_jump_intensity",
            "dynamic_short_squeeze",
            "forward_basis",
            "peavd_earnings_vol_drift",
            "analyst_revisions",
            "accruals_cashflow",
            "extreme_tail_risk",
            "iv_lead_lag",
            "network_momentum",
            "formulaic_101",
            "hybrid_confluence",
        ]
        goldmine_seeds = [
            OptionCandidate(
                expression="group_neutralize(rank(-ts_decay_linear(ts_delta(pcr_oi_30, 10), 5)), sector)",
                archetype_name="Put Open Interest Buildup (ZYAPYvqY Base)",
                hypothesis="Accumulation of 30d put open interest predicts negative options overhang.",
                generation_source="template",
                decay=15,
                neutralization="SECTOR",
                universe="TOP3000",
            ),
            OptionCandidate(
                expression="group_neutralize(rank(-ts_decay_linear(ts_delta(pcr_oi_30, 8), 5)), sector)",
                archetype_name="Put Open Interest Buildup (ZYAPYvqY d=8)",
                hypothesis="Fast delta accumulation of 30d put open interest predicts negative options overhang.",
                generation_source="template",
                decay=12,
                neutralization="SECTOR",
                universe="TOP3000",
            ),
            OptionCandidate(
                expression="group_neutralize(rank(-ts_decay_linear(ts_delta(pcr_oi_30, 12), 6)), sector)",
                archetype_name="Put Open Interest Buildup (ZYAPYvqY d=12)",
                hypothesis="12-day delta accumulation of 30d put open interest predicts structural options overhang.",
                generation_source="template",
                decay=14,
                neutralization="SECTOR",
                universe="TOP3000",
            ),
            OptionCandidate(
                expression="trade_when(volume > adv20 * 0.8, group_neutralize(rank(-ts_decay_linear(ts_delta(pcr_oi_30, 10), 5)), sector), -1)",
                archetype_name="Put Open Interest Buildup (Liquidity Gated)",
                hypothesis="Accumulation of 30d put open interest gated by underlying liquidity.",
                generation_source="template",
                decay=18,
                neutralization="SECTOR",
                universe="TOP3000",
            ),
            OptionCandidate(
                expression="group_neutralize(rank(-ts_decay_linear(ts_delta(pcr_oi_30, 10), 5)), subindustry)",
                archetype_name="Put Open Interest Buildup (Subindustry)",
                hypothesis="Accumulation of 30d put open interest neutralized by subindustry.",
                generation_source="template",
                decay=16,
                neutralization="SUBINDUSTRY",
                universe="TOP3000",
            ),
            OptionCandidate(
                expression="group_neutralize(signed_power(rank(-ts_decay_linear(ts_delta(pcr_oi_30, 10), 5)) - 0.5, 1.5), sector)",
                archetype_name="Put Open Interest Buildup (Signed Power)",
                hypothesis="Signed power transformation on 30d put open interest delta.",
                generation_source="template",
                decay=15,
                neutralization="SECTOR",
                universe="TOP3000",
            ),
        ]
        all_candidates = (
            goldmine_seeds
            + generate_modular_candidates(virgin_strategies)
            + generate_modular_candidates()
            + generate_template_candidates()
            + generate_high_capacity_candidates()
        )
        for c in all_candidates:
            h = self.deduplicator.hash(c.expression)
            if h not in seen_hashes:
                seen_hashes.add(h)
                queue.append(c)
        self._template_queue: list[OptionCandidate] = queue
        self._archetype_idx = 0

        # Multi-Armed Bandit prior weights across research domains (Heavy weights on proven virgin strategies)
        self.archetype_priors: dict[str, float] = {
            "pcr_flow": 0.16,
            "macro_fomc_cpi_drift": 0.14,
            "peavrp_volatility_premia": 0.12,
            "dynamic_short_squeeze": 0.10,
            "order_flow_vpin": 0.10,
            "gamma_pinning_clustering": 0.10,
            "realized_jump_intensity": 0.08,
            "jump_variance_moments": 0.08,
            "forward_basis": 0.06,
            "term_structure": 0.06,
            "peavd_earnings_vol_drift": 0.05,
            "analyst_revisions": 0.04,
            "accruals_cashflow": 0.04,
            "extreme_tail_risk": 0.03,
            "informed_short_demand": 0.02,
            "iv_lead_lag": 0.02,
            "network_momentum": 0.02,
            "short_interest": 0.02,
            "formulaic_101": 0.01,
            "hybrid_confluence": 0.01,
            "supply_chain": 0.01,
            "breakeven": 0.00,
            "skew": 0.00,
        }

    def mark_evaluated(self, expression: str):
        cleaned = compile_fitness_invariant(expression.strip())
        self.evaluated_expressions.add(cleaned)
        self.deduplicator.add(cleaned)

    def is_evaluated(self, expression: str) -> bool:
        cleaned = compile_fitness_invariant(expression.strip())
        return cleaned in self.evaluated_expressions or self.deduplicator.is_duplicate(cleaned)

    def generate_candidate(self) -> OptionCandidate:
        """Pulls next candidate from high-capacity template queue, LLM reasoning tier, or procedural mutation."""
        # Tier 1: Deterministic golden templates & high-capacity matrix
        if self._template_queue:
            return self._template_queue.pop(0)

        # Tier 2: Quantitative LLM reasoning tier
        if self.llm_adapter:
            try:
                batch = self.get_reasoning_batch(count=5)
                if batch:
                    cand = batch.pop(0)
                    self._template_queue.extend(batch)
                    return cand
            except Exception as e:
                log.warning("Options LLM generation failed: %s", e)

        # Tier 3: Procedural mutation fallback
        batch = self.get_procedural_batch(count=5)
        if batch:
            cand = batch.pop(0)
            self._template_queue.extend(batch)
            return cand

        # Tier 4: Systematic parameter variation fallback
        t = random.choice([30, 60, 90, 120, 180])
        d = random.choice([14, 18, 22])
        g = random.choice(["subindustry", "sector", "industry"])
        u = random.choice(["TOP3000", "TOP2000"])
        expr = f"group_neutralize(rank(ts_decay_linear(ts_decay_linear((forward_price_{t} - put_breakeven_{t}) / close, {d}), 3)), {g})"
        return OptionCandidate(
            expression=expr,
            archetype_name=f"T1_PutFloor{t}_d{d}_{u}_{g.upper()}",
            archetype=f"T1_PutFloor{t}_d{d}_{u}_{g.upper()}",
            hypothesis=f"Systematic put breakeven exploration ({t}d) with decay {d}.",
            universe=u,
            neutralization=g.upper(),
            decay=d,
            family=f"Arch1_PutFloor_{t}",
            generation_source="procedural_fallback",
        )

    def total_queued(self) -> int:
        return len(self._template_queue)

    def choose_archetype(
        self,
        archetype_summary: Optional[dict[str, dict[str, float]]] = None,
        saturated_archetypes: Optional[list[str]] = None,
    ) -> str:
        """
        Multi-Armed Bandit (MAB) archetype selection across all 15 strategies with empirical
        pass-rate weighting, repeat-collision penalties, and Dynamic Archetype Daily Caps.
        Applies a client-side hard ceiling: no single archetype family exceeds 30% of sampling share.
        """
        weights = dict(self.archetype_priors)

        if archetype_summary:
            for arch_key in CORE_ARCHETYPES:
                # Find matching entries in DB summary
                matched_pass_rate = 0.0
                recent_collisions = 0
                for db_arch, stats in archetype_summary.items():
                    if arch_key.lower() in db_arch.lower() or map_archetype_to_core(db_arch) == arch_key:
                        matched_pass_rate = max(matched_pass_rate, stats.get("pass_rate", 0.0))
                        recent_collisions += int(stats.get("corr_count", 0) or stats.get("correlated", 0))

                # Boost weight proportional to pass rate (exploration floor 0.04)
                weights[arch_key] = max(0.04, weights[arch_key] + matched_pass_rate * 0.5)

                # Priority 1: Multi-Armed Bandit repeat-collision penalty
                if recent_collisions >= 3:
                    weights[arch_key] *= 0.20
                elif recent_collisions >= 1:
                    weights[arch_key] *= 0.50

        # Dynamic Archetype Daily Caps (Pillar 1): Drop saturated archetypes to 0.02
        if saturated_archetypes:
            sat_cores = {map_archetype_to_core(s) for s in saturated_archetypes}
            for arch_key in CORE_ARCHETYPES:
                if arch_key in sat_cores or any(arch_key in s.lower() for s in saturated_archetypes):
                    weights[arch_key] = 0.02

        # Priority 1: Client-side family cap — no single archetype exceeds 30% of a batch
        total = sum(weights.values())
        clamped_weights = [min(weights[a] / total, 0.30) for a in CORE_ARCHETYPES]
        clamped_total = sum(clamped_weights)
        norm_weights = [w / clamped_total for w in clamped_weights]

        chosen = random.choices(CORE_ARCHETYPES, weights=norm_weights, k=1)[0]
        return chosen

    def _apply_peer_genome_lookahead(
        self, clean_expr: str, peer_graph: Optional[PeerGenomeGraph]
    ) -> tuple[str, Optional[str]]:
        """Checks for cell/family collisions and auto-corrects before simulation."""
        if peer_graph is None:
            return clean_expr, None
        cand_genome = extract_genome("candidate", clean_expr, decay=8)
        for tenor in cand_genome.tenors:
            for moneyness in cand_genome.moneyness:
                for factor in cand_genome.factors:
                    collision = peer_graph.find_collision_risk(tenor, moneyness, factor, decay=8)
                    if collision:
                        corrected = auto_correct_for_collision(clean_expr, collision)
                        if corrected != clean_expr:
                            log.info(
                                "Pre-sim auto-corrected candidate on occupied cell (%dd, %s, %s) vs peer %s",
                                tenor, moneyness, factor, collision.alpha_id,
                            )
                            return corrected, collision.alpha_id
                        break
        return clean_expr, None

    def get_template_batch(
        self,
        count: int = 5,
        archetype: Optional[str] = None,
        saturated_archetypes: Optional[list[str]] = None,
    ) -> list[OptionCandidate]:
        """Tier 1: Deterministic seed template candidates filtered by AST deduplication and saturation caps."""
        peer_graph = PeerGenomeGraph.load(self.db) if getattr(self, "db", None) else None
        batch: list[OptionCandidate] = []
        batch_hashes: set[str] = set()
        tokens = [t.strip().lower() for t in archetype.split(",")] if archetype else []
        sat_cores = {map_archetype_to_core(s) for s in saturated_archetypes} if saturated_archetypes else set()

        i = 0
        while i < len(self._template_queue) and len(batch) < count:
            cand = self._template_queue[i]
            cand_core = map_archetype_to_core(cand.archetype_name)

            # Steer away from saturated daily channels if unsaturated ones remain
            if sat_cores and cand_core in sat_cores:
                i += 1
                continue

            if tokens:
                matches = any(
                    tok in cand.archetype_name.lower() or tok in cand.expression.lower() or tok == cand_core
                    for tok in tokens
                )
                if not matches:
                    i += 1
                    continue
            cand = self._template_queue.pop(i)

            clean_expr = cand.expression
            corrected, colliding_id = self._apply_peer_genome_lookahead(clean_expr, peer_graph)
            if colliding_id:
                clean_expr = corrected
                cand = OptionCandidate(
                    expression=clean_expr,
                    archetype_name=f"{cand.archetype_name} (genome-corrected)",
                    hypothesis=f"{cand.hypothesis} [Auto-corrected for collision with {colliding_id}]",
                    generation_source=cand.generation_source,
                    operator_name="peer_genome_correction",
                )

            if not self.is_evaluated(cand.expression):
                ast_h = self.deduplicator.hash(cand.expression)
                if ast_h not in batch_hashes:
                    batch_hashes.add(ast_h)
                    batch.append(cand)
        return batch

    def get_reasoning_batch(
        self,
        count: int = 5,
        archetype: Optional[str] = None,
        top_exemplars: Optional[list[dict]] = None,
        archetype_summary: Optional[dict] = None,
        saturated_archetypes: Optional[list[str]] = None,
    ) -> list[OptionCandidate]:
        """
        Tier 2: Knowledge-injected LLM reasoning tier.
        Injects targeted institutional cards, formula sketches, and top RL exemplars
        from Master Books 1-4 and PostgreSQL learning memory, actively avoiding saturated archetypes.
        """
        peer_graph = PeerGenomeGraph.load(self.db) if getattr(self, "db", None) else None
        candidates: list[OptionCandidate] = []
        batch_hashes: set[str] = set()
        chunk_size = 4
        needed = count

        while needed > 0 and len(candidates) < count:
            batch_n = min(chunk_size, needed)
            target_arch = archetype or self.choose_archetype(
                archetype_summary=archetype_summary,
                saturated_archetypes=saturated_archetypes,
            )
            if "," in target_arch:
                arch_choices = [t.strip() for t in target_arch.split(",") if t.strip()]
                target_arch = random.choice(arch_choices)
            kb_cards = self.kb.get_cards_for_archetype(target_arch, max_cards=3)
            catalog_summary = self.catalog.summarize_for_prompt()

            system_prompt = build_options_system_prompt(catalog_summary)
            prompt = build_reasoning_prompt(
                target_arch,
                kb_cards,
                n=batch_n,
                top_exemplars=top_exemplars,
                saturated_archetypes=saturated_archetypes,
            )

            raw_output = self.llm_adapter.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
            )
            if raw_output:
                parsed = clean_json_array(raw_output)
                for item in parsed:
                    expr = item.get("expression", "").strip()
                    if not expr or self.is_evaluated(expr):
                        continue

                    clean_expr = expr
                    corrected, colliding_id = self._apply_peer_genome_lookahead(clean_expr, peer_graph)
                    if colliding_id:
                        clean_expr = corrected
                        cand_arch = f"{item.get('archetype', target_arch.title())} (genome-corrected)"
                        cand_hyp = f"{item.get('hypothesis', f'Knowledge-guided reasoning on {target_arch}')} [Auto-corrected for collision with {colliding_id}]"
                    else:
                        cand_arch = item.get("archetype", target_arch.title())
                        cand_hyp = item.get("hypothesis", f"Knowledge-guided reasoning on {target_arch}")

                    ast_h = self.deduplicator.hash(clean_expr)
                    if ast_h in batch_hashes or self.is_evaluated(clean_expr):
                        continue
                    batch_hashes.add(ast_h)
                    candidates.append(
                        OptionCandidate(
                            expression=clean_expr,
                            archetype_name=cand_arch,
                            hypothesis=cand_hyp,
                            generation_source="llm_reasoning",
                            operator_name=item.get("mutation_type"),
                        )
                    )
                    if len(candidates) >= count:
                        break

            needed -= batch_n

        return candidates


    def get_procedural_batch(
        self,
        count: int = 10,
        archetype: Optional[str] = None,
        saturated_archetypes: Optional[list[str]] = None,
    ) -> list[OptionCandidate]:
        """
        Tier 4 Fail-Safe: Dynamic Procedural Options Generator.
        Generates mathematically valid, institutionally grounded options alphas across
        combinatoric parameter dimensions (tenors, windows, operators, neutralizations, gating).
        Guarantees that the pipeline never starves or evaluates 0 candidates even when
        static templates are exhausted and LLM providers are unavailable.
        """
        peer_graph = PeerGenomeGraph.load(self.db) if getattr(self, "db", None) else None
        procedural: list[OptionCandidate] = []
        batch_hashes: set[str] = set()
        tokens = [t.strip().lower() for t in archetype.split(",")] if archetype else []
        sat_cores = {map_archetype_to_core(s) for s in saturated_archetypes} if saturated_archetypes else set()

        def _add(expr: str, arch: str, hyp: str):
            clean_expr = compile_fitness_invariant(expr.strip())
            arch_core = map_archetype_to_core(arch)
            if sat_cores and arch_core in sat_cores:
                return
            if tokens:
                matches = any(
                    tok in arch.lower() or tok in clean_expr.lower() or tok in hyp.lower() or tok == arch_core
                    for tok in tokens
                )
                if not matches:
                    return

            # Genome lookahead collision check and pre-sim auto-correction
            corrected, colliding_id = self._apply_peer_genome_lookahead(clean_expr, peer_graph)
            if colliding_id:
                clean_expr = corrected
                arch = f"{arch} (genome-corrected)"
                hyp = f"{hyp} [Auto-corrected for collision with {colliding_id}]"

            if not self.is_evaluated(clean_expr) and not any(c.expression == clean_expr for c in procedural):
                ast_h = self.deduplicator.hash(clean_expr)
                if ast_h in batch_hashes:
                    return
                batch_hashes.add(ast_h)
                procedural.append(
                    OptionCandidate(
                        expression=clean_expr,
                        archetype_name=arch,
                        hypothesis=hyp,
                        generation_source="procedural",
                    )
                )

        # 1. Forward Basis Spreads & Momentum across expanded tenors & neutralizations
        for tenor in [10, 20, 30, 60, 90, 120, 150, 180, 270, 360]:
            for grp in ["subindustry"]:
                _add(
                    f"group_neutralize(rank((forward_price_{tenor} - close) / close), {grp})",
                    "Forward Basis Spread",
                    f"Synthetic forward basis at {tenor}d tenor demeaned by {grp} captures institutional drift.",
                )
            for window in [2, 3, 5, 10, 15, 20]:
                for grp in ["subindustry"]:
                    _add(
                        f"group_neutralize(rank(ts_delta((forward_price_{tenor} - close) / close, {window})), {grp})",
                        "Forward Basis Velocity",
                        f"Acceleration in {tenor}d forward basis over {window}d demeaned by {grp} indicates institutional positioning.",
                    )
                    _add(
                        f"group_neutralize(rank(ts_zscore((forward_price_{tenor} - close) / close, {window * 2})), {grp})",
                        "Forward Basis Z-Score",
                        f"Normalized deviation of {tenor}d forward basis against {window * 2}d mean captures pricing misalignments.",
                    )

        # 2. Sqrt(T) Normalized Volatility Skew Shifts & Accelerations
        for tenor in [10, 20, 30, 60, 90, 120, 150, 180]:
            sqrt_t = round(math.sqrt(tenor / 252.0), 4)
            for window in [2, 3, 5, 8, 10, 15]:
                for grp in ["subindustry"]:
                    _add(
                        f"group_neutralize(rank(-ts_delta(implied_volatility_mean_skew_{tenor} * {sqrt_t}, {window})), {grp})",
                        "Sqrt-T Normalized Skew Acceleration",
                        f"Decay-normalized sqrt(T) downside skew shift at {tenor}d over {window}d isolates tail risk repricing.",
                    )
                    _add(
                        f"group_neutralize(rank(-ts_zscore(implied_volatility_mean_skew_{tenor} * {sqrt_t}, {window * 3})), {grp})",
                        "Sqrt-T Normalized Skew Z-Score",
                        f"Decay-normalized sqrt(T) skew z-score at {tenor}d over {window * 3}d flags extreme tail crowding.",
                    )

        # 3. Cross-Tenor Skew Curvature & Calendar Spreads
        for t1, t2 in [(10, 30), (20, 60), (30, 90), (60, 180)]:
            sq1 = round(math.sqrt(t1 / 252.0), 4)
            sq2 = round(math.sqrt(t2 / 252.0), 4)
            for grp in ["subindustry"]:
                _add(
                    f"group_neutralize(rank(-(implied_volatility_mean_skew_{t1} * {sq1} - implied_volatility_mean_skew_{t2} * {sq2})), {grp})",
                    "Cross-Tenor Skew Curvature Spread",
                    f"Calendar skew differential between {t1}d and {t2}d tenors demeaned by {grp}.",
                )
                _add(
                    f"group_neutralize(rank(-ts_delta(implied_volatility_mean_skew_{t1} * {sq1} - implied_volatility_mean_skew_{t2} * {sq2}, 5)), {grp})",
                    "Cross-Tenor Skew Spread Velocity",
                    f"5-day acceleration in calendar skew differential between {t1}d and {t2}d tenors.",
                )

        # 4. Volatility Term Structure Slopes & Inversions
        for t1, t2 in [(10, 30), (20, 60), (30, 90), (60, 180), (90, 360)]:
            for grp in ["subindustry"]:
                _add(
                    f"group_neutralize(rank(-(implied_volatility_mean_{t1} / (implied_volatility_mean_{t2} + 0.001) - 1.0)), {grp})",
                    "Volatility Term Structure Slope",
                    f"Fade extreme slope inversion between {t1}d and {t2}d ATM implied volatility demeaned by {grp}.",
                )

        # 5. PCR Smart-Money Flow to Open Interest Surge with Gating
        for tenor in [10, 20, 30, 60, 90, 120]:
            for window in [3, 5, 10, 15, 20]:
                for grp in ["subindustry"]:
                    _add(
                        f"group_neutralize(rank(-ts_rank(pcr_vol_{tenor} / (pcr_oi_{tenor} + 0.001), {window})), {grp})",
                        "PCR Volume-to-OI Flow Surge",
                        f"Surge in {tenor}d put volume relative to open interest over {window}d flags institutional positioning.",
                    )
                    _add(
                        f"trade_when(volume > adv20, group_neutralize(rank(-ts_delta(pcr_vol_{tenor} / (pcr_oi_{tenor} + 0.001), {window})), {grp}), -1)",
                        "Liquidity-Gated PCR Flow Acceleration",
                        f"Acceleration in {tenor}d put volume-to-OI flow over {window}d conditioned on liquid trading volume.",
                    )

        # 6. Call Breakeven Hurdle Rates & Repricing
        for tenor in [10, 20, 30, 60, 90, 120, 180]:
            for grp in ["subindustry"]:
                _add(
                    f"group_neutralize(rank((call_breakeven_{tenor} - close) / close), {grp})",
                    "Call Breakeven Hurdle Spread",
                    f"OI-weighted call breakeven hurdle rate at {tenor}d tenor demeaned by {grp}.",
                )
                for window in [2, 3, 5, 10]:
                    _add(
                        f"group_neutralize(rank(ts_delta((call_breakeven_{tenor} - close) / close, {window})), {grp})",
                        "Call Breakeven Hurdle Acceleration",
                        f"Acceleration in {tenor}d call breakeven hurdle rate over {window}d signals target repricing.",
                    )

        # 7. Variance Risk Premium (IV vs RV) with Jensen-Debiasing & Entry Gating
        for tenor, win, mult in [(10, 10, 15.65), (20, 20, 16.53), (30, 30, 15.87), (60, 60, 15.87)]:
            for grp in ["subindustry"]:
                _add(
                    f"group_neutralize(rank(-(implied_volatility_mean_{tenor} - ts_std_dev(returns, {win}) * {mult})), {grp})",
                    "Jensen-Debiased Variance Risk Premium",
                    f"Short over-priced {tenor}d IV relative to debiased rolling {win}d realized volatility.",
                )
                _add(
                    f"trade_when(abs(ts_zscore(implied_volatility_mean_{tenor} - ts_std_dev(returns, {win}) * {mult}, 40)) > 0.75, group_neutralize(rank(-(implied_volatility_mean_{tenor} - ts_std_dev(returns, {win}) * {mult})), {grp}), -1)",
                    "Threshold-Gated VRP Mean Reversion",
                    f"Enter {tenor}d variance risk premium only when crossing 0.75 SD mean-reversion threshold.",
                )

        # 8. Analyst Estimates & Earnings Revisions (Expanded Combinatorics)
        for win in [5, 10, 15, 20, 30, 45, 60, 90]:
            for dcy in [3, 5, 8, 10, 15, 20]:
                for grp in ["subindustry"]:
                    _add(
                        f"group_neutralize(rank(ts_decay_linear((est_eps - ts_delay(est_eps, {win})) / (abs(ts_delay(est_eps, {win})) + 0.01), {dcy})), {grp})",
                        "Analyst Revision Momentum",
                        f"Givoly & Lakonishok (1979): {win}d revision drift in consensus EPS with decay={dcy} demeaned by {grp}.",
                    )
        for win in [10, 20, 30, 60]:
            for dcy in [5, 10, 15, 20]:
                for grp in ["subindustry"]:
                    _add(
                        f"group_neutralize(rank(ts_decay_linear((est_sales - ts_delay(est_sales, {win})) / (abs(ts_delay(est_sales, {win})) + 0.01), {dcy})), {grp})",
                        "Sales Revision Momentum",
                        f"Consensus sales revision drift over {win}d with decay={dcy} demeaned by {grp}.",
                    )
        for win in [10, 20, 40, 60, 90, 120]:
            for dcy in [3, 5, 8, 10, 15, 20]:
                for grp in ["subindustry"]:
                    _add(
                        f"group_neutralize(rank(-ts_decay_linear(ts_zscore(std_dev_eps_est / (abs(est_eps) + 0.01), {win}), {dcy})), {grp})",
                        "Analyst Dispersion Fade",
                        f"Diether et al. (2002): Fade stocks with extreme {win}d analyst forecast dispersion with decay={dcy}.",
                    )
        for mom_win in [3, 5, 10, 15, 20]:
            for dcy in [3, 5, 8, 10, 15, 20]:
                for grp in ["subindustry"]:
                    _add(
                        f"trade_when(ts_delta(close, {mom_win}) > 0, group_neutralize(rank(ts_decay_linear((target_price - close) / close, {dcy})), {grp}), -1)",
                        "Price Target Implied Upside",
                        f"Fabozzi et al. (2010): Consensus price target upside conditioned on positive {mom_win}d price momentum (decay={dcy}).",
                    )
        for win in [60, 120, 252]:
            for dcy in [5, 10, 20]:
                for grp in ["subindustry"]:
                    _add(
                        f"group_neutralize(rank(ts_decay_linear((est_eps - ts_mean(est_eps, {win})) / (ts_std_dev(est_eps, {win}) + 0.01), {dcy})), {grp})",
                        "Normalized Analyst Consensus Drift",
                        f"Long-term {win}d normalized earnings revision drift with decay={dcy} demeaned by {grp}.",
                    )

        # 9. Short Interest & Securities Lending Flow (Vastly Expanded Multi-Speed Grid)
        for dcy in [3, 5, 8, 10, 15, 20, 30]:
            for grp in ["subindustry"]:
                _add(
                    f"group_neutralize(rank(-ts_decay_linear(borrow_fee * (short_interest / (float_shares + 0.001)), {dcy})), {grp})",
                    "Short Demand Borrow Surge",
                    f"Cohen et al. (2007): Elevated institutional borrow cost and high short interest with decay={dcy}.",
                )
                _add(
                    f"group_neutralize(rank(-ts_decay_linear(short_interest / (adv20 + 0.001), {dcy})), {grp})",
                    "Short Interest to Volume Ratio",
                    f"High short interest relative to 20d average daily volume with decay={dcy}.",
                )
        for delta_win in [3, 5, 10, 15]:
            for dcy in [5, 10, 15, 20]:
                for grp in ["subindustry"]:
                    _add(
                        f"group_neutralize(rank(-ts_decay_linear(ts_delta(borrow_fee, {delta_win}) * (short_interest / (float_shares + 0.001)), {dcy})), {grp})",
                        "Borrow Fee Acceleration Squeeze Risk",
                        f"Acceleration in institutional borrow cost over {delta_win}d weighted by short interest.",
                    )
                    _add(
                        f"group_neutralize(rank(-ts_decay_linear(ts_delta(short_interest / (float_shares + 0.001), {delta_win}), {dcy})), {grp})",
                        "Short Interest Flow Acceleration",
                        f"Rate of change in short interest as percentage of float over {delta_win}d.",
                    )
        for win in [20, 40, 60, 90, 126, 252]:
            for dcy in [5, 10, 15, 20]:
                for grp in ["subindustry"]:
                    _add(
                        f"group_neutralize(rank(-ts_decay_linear(ts_zscore(short_interest / (float_shares + 0.001), {win}), {dcy})), {grp})",
                        "De-Trended Short Interest Z-Score",
                        f"Rapach et al. (2016): De-trended {win}d short interest Z-score measures abnormal positioning (decay={dcy}).",
                    )
                    _add(
                        f"group_neutralize(rank(-ts_decay_linear(ts_rank(short_interest / (adv20 + 0.001), {win}), {dcy})), {grp})",
                        "Rolling Short Interest Percentile",
                        f"Rolling {win}d percentile rank of short interest relative to liquidity.",
                    )
        for win in [20, 60, 120]:
            for dcy in [5, 10, 20]:
                for grp in ["subindustry"]:
                    _add(
                        f"group_neutralize(rank(-ts_decay_linear(borrow_fee / (ts_mean(borrow_fee, {win}) + 0.01), {dcy})), {grp})",
                        "Relative Borrow Fee Dislocation",
                        f"Institutional borrow fee relative to its {win}d baseline mean.",
                    )
        for dtc in [2.0, 3.0, 4.0, 5.0, 6.0, 8.0]:
            for mom in [3, 5, 10, 20]:
                for dcy in [3, 5, 8, 10, 15, 20]:
                    for grp in ["subindustry"]:
                        _add(
                            f"trade_when((close > ts_mean(close, {mom * 2})) & (days_to_cover > {dtc}), group_neutralize(rank(ts_decay_linear(days_to_cover * ts_delta(close, {mom}), {dcy})), {grp}), -1)",
                            "Days-to-Cover Short Squeeze Breakout",
                            f"Asquith et al. (2005): Short squeeze breakout trigger on high days-to-cover names (decay={dcy}).",
                        )

        # 10. Cross-Asset Hybrids (Options + Shorts + Analyst Estimates - Multi-Speed)
        for tenor in [10, 20, 30, 60, 90, 120, 180]:
            sqrt_t = round(math.sqrt(tenor / 252.0), 4)
            for dcy in [3, 5, 8, 10, 15, 20]:
                for grp in ["subindustry"]:
                    _add(
                        f"group_neutralize(rank(-ts_decay_linear((implied_volatility_mean_skew_{tenor} * {sqrt_t}) * (borrow_fee + 1.0), {dcy})), {grp})",
                        "Volatility Smirk Borrow Fee Hybrid",
                        f"Cross-Asset Confluence: Confluence of steep {tenor}d downside put skew and high borrow fees (decay={dcy}).",
                    )
                    _add(
                        f"group_neutralize(rank(ts_decay_linear((target_price - close) / close - (implied_volatility_mean_skew_{tenor} * {sqrt_t}), {dcy})), {grp})",
                        "Revision vs Skew Divergence Hybrid",
                        f"Cross-Asset Divergence: Target price upside vs {tenor}d options downside hedging (decay={dcy}).",
                    )
                    _add(
                        f"group_neutralize(rank(-ts_decay_linear((pcr_vol_{tenor} / (pcr_oi_{tenor} + 0.001)) * (borrow_fee + 1.0), {dcy})), {grp})",
                        "PCR Borrow Fee Confluence Hybrid",
                        f"Surging {tenor}d put/call volume ratio paired with elevated borrow cost (decay={dcy}).",
                    )
                    _add(
                        f"group_neutralize(rank(-ts_decay_linear((implied_volatility_mean_{tenor} - ts_mean(implied_volatility_mean_{tenor}, 60)) * (short_interest / (float_shares + 0.001)), {dcy})), {grp})",
                        "IV Surge Short Interest Confluence",
                        f"Confluence of abnormal {tenor}d IV expansion and heavy short interest positioning.",
                    )

        # Fail-Safe Backfill: If the targeted archetype filter produced fewer than count candidates
        # (e.g. all specific variations evaluated), backfill from the broader cross-asset pool so workers NEVER starve
        if len(procedural) < count and tokens:
            log.info("Specialized procedural set yielded %d/%d candidates for '%s'. Backfilling from cross-asset pool...",
                     len(procedural), count, archetype)
            # Temporarily clear tokens to allow backfill
            saved_tokens = tokens
            tokens = []
            # Call Section 10 Cross-Asset and Section 2 Skew backfill
            for tenor in [10, 20, 30, 60, 90, 120]:
                sqrt_t = round(math.sqrt(tenor / 252.0), 4)
                for dcy in [5, 10, 15, 20]:
                    for grp in ["subindustry"]:
                        _add(
                            f"group_neutralize(rank(-ts_decay_linear((implied_volatility_mean_skew_{tenor} * {sqrt_t}) * (borrow_fee + 1.0), {dcy})), {grp})",
                            "Cross-Asset Backfill Hybrid",
                            f"Fail-safe backfill: Volatility skew and lending fee confluence (decay={dcy}).",
                        )
                        if len(procedural) >= count:
                            break
                    if len(procedural) >= count:
                        break
                if len(procedural) >= count:
                    break
            tokens = saved_tokens

        return procedural[:count]


    def get_mutation_batch(
        self,
        base_candidates: list[OptionCandidate],
        count_per_base: int = 2,
        top_exemplars: Optional[list[dict]] = None,
    ) -> list[OptionCandidate]:
        """
        Tier 3: Mechanical mutation tier.
        Generates structured operator, tenor, and neutralization variations of base candidates.
        """
        if not base_candidates:
            return []

        mutations: list[OptionCandidate] = []
        batch_hashes: set[str] = set()
        system_prompt = (
            "You are a WorldQuant BRAIN quantitative research assistant specializing in Equity Options alpha expressions. "
            "Your job is to apply systematic mathematical mutations to existing options alphas to explore adjacent parameter space.\n"
            "Return valid JSON array of objects with keys: expression, hypothesis, mutation_type."
        )

        for base in base_candidates:
            kb_cards = self.kb.get_cards_for_archetype(base.archetype_name, max_cards=2)
            prompt = build_mechanical_mutation_prompt(
                candidate_expression=base.expression,
                candidate_hypothesis=base.hypothesis,
                kb_cards=kb_cards,
                n=count_per_base,
                top_exemplars=top_exemplars,
            )
            raw_output = self.llm_adapter.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.6,
            )
            if not raw_output:
                continue

            peer_graph = PeerGenomeGraph.load(self.db) if getattr(self, "db", None) else None
            parsed = clean_json_array(raw_output)
            for item in parsed:
                expr = item.get("expression", "").strip()
                if not expr or self.is_evaluated(expr):
                    continue

                clean_expr = expr
                corrected, colliding_id = self._apply_peer_genome_lookahead(clean_expr, peer_graph)
                if colliding_id:
                    clean_expr = corrected
                    cand_arch = f"Mutation({base.archetype_name}) (genome-corrected)"
                    cand_hyp = f"{item.get('hypothesis', f'Mutation of {base.expression}')} [Auto-corrected for collision with {colliding_id}]"
                else:
                    cand_arch = f"Mutation({base.archetype_name})"
                    cand_hyp = item.get("hypothesis", f"Mutation of {base.expression}")

                ast_h = self.deduplicator.hash(clean_expr)
                if ast_h in batch_hashes or self.is_evaluated(clean_expr):
                    continue
                batch_hashes.add(ast_h)
                mutations.append(
                    OptionCandidate(
                        expression=clean_expr,
                        archetype_name=cand_arch,
                        hypothesis=cand_hyp,
                        generation_source="llm_mechanical",
                        operator_name=item.get("mutation_type"),
                    )
                )
        return mutations

    def get_next_batch(
        self,
        target_count: int = 10,
        template_ratio: float = 0.3,
        seed_candidates_for_mutation: Optional[list[OptionCandidate]] = None,
        top_exemplars: Optional[list[dict]] = None,
        archetype_summary: Optional[dict] = None,
        target_archetype: Optional[str] = None,
        saturated_archetypes: Optional[list[str]] = None,
    ) -> list[OptionCandidate]:
        """
        Assembles a balanced candidate batch across the generation tiers:
        1. Deterministic high-confidence templates (Tier 1)
        2. Tier 3 Mutations (seeded by top performing historical alphas from memory)
        3. Tier 2 Knowledge-injected LLM reasoning (conditioned on MAB weights, RL exemplars, and saturated exclusions)
        4. Dynamic procedural generator fallback (Tier 4) guarantees non-empty batch
        """
        template_count = max(1, int(target_count * template_ratio))
        remaining = target_count - template_count

        candidates: list[OptionCandidate] = self.get_template_batch(
            template_count,
            archetype=target_archetype,
            saturated_archetypes=saturated_archetypes,
        )

        # 1. Tier 3 Mutations: if no explicit seeds, auto-seed from top exemplars in memory
        active_seeds = seed_candidates_for_mutation
        if not active_seeds and top_exemplars:
            active_seeds = [
                OptionCandidate(
                    expression=ex["expression"],
                    archetype_name=ex.get("archetype", "TopExemplar"),
                    hypothesis=ex.get("hypothesis", "Top performing alpha from learning memory"),
                    generation_source="learning_memory_seed",
                )
                for ex in top_exemplars[:3]
                if ex.get("expression")
            ]
            if target_archetype:
                tokens = [t.strip().lower() for t in target_archetype.split(",")]
                active_seeds = [
                    s for s in active_seeds
                    if any(t in s.archetype_name.lower() or t in s.expression.lower() for t in tokens)
                ]

        if active_seeds:
            mutation_slots = max(1, remaining // 2)
            mutations = self.get_mutation_batch(active_seeds, count_per_base=2, top_exemplars=top_exemplars)
            candidates.extend(mutations[:mutation_slots])

        # 2. Tier 2 LLM Reasoning (conditioned on target archetype or bandit weights)
        needed_reasoning = target_count - len(candidates)
        if needed_reasoning > 0:
            llm_candidates = self.get_reasoning_batch(
                needed_reasoning,
                archetype=target_archetype,
                top_exemplars=top_exemplars,
                archetype_summary=archetype_summary,
                saturated_archetypes=saturated_archetypes,
            )
            candidates.extend(llm_candidates)

        # 3. Fallback top-up from static templates if any remain
        if len(candidates) < target_count:
            shortfall = target_count - len(candidates)
            extra_templates = self.get_template_batch(
                shortfall,
                archetype=target_archetype,
                saturated_archetypes=saturated_archetypes,
            )
            candidates.extend(extra_templates)

        # 4. Fail-safe Tier 4: Dynamic procedural generator guarantees batch is never empty
        if len(candidates) < target_count:
            shortfall = target_count - len(candidates)
            log.info("Top-up: generating %d fresh procedural options candidates (%s)...", shortfall, target_archetype or "all")
            procedural_candidates = self.get_procedural_batch(
                shortfall,
                archetype=target_archetype,
                saturated_archetypes=saturated_archetypes,
            )
            candidates.extend(procedural_candidates)

        if target_count >= 5 and len(candidates) < 5:
            log.error("Candidate batch size (%d) fell below threshold (< 5 candidates generated, target=%d)", len(candidates), target_count)
            send_telegram_emergency_alert(
                f"<b>CRITICAL: Candidate Generation Starvation</b>\n\n"
                f"Generated only {len(candidates)} candidates (target: {target_count}). Generator pipeline starved.",
                context="Candidate Generation Starvation",
                cooldown_minutes=60,
            )
        elif not candidates:
            log.error("Candidate batch size is 0 (target=%d)", target_count)
            send_telegram_emergency_alert(
                f"<b>CRITICAL: Candidate Generation Starvation</b>\n\n"
                f"Generated 0 candidates (target: {target_count}). Generator pipeline completely starved.",
                context="Candidate Generation Starvation",
                cooldown_minutes=60,
            )

        return candidates

