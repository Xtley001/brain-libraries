"""
Telegram notifier for brain_options.

Design principles:
- Clean, minimalist, straight to the point.
- No inline links (they break on alpha IDs with underscores).
- No raw formula expressions in alerts.
- Proper MarkdownV2 escaping to prevent silent send failures.
- Three alert tiers:
    1. send_telegram_batch_summary  → fires only when a batch yields ≥1 qualified alpha.
    2. send_telegram_drip_alert     → fires immediately when an alpha is submitted.
    3. send_telegram_health_check   → hourly system heartbeat (called by health.yml).
    4. send_telegram_daily_digest   → end-of-day full summary (called by daily_digest.yml).
"""
from __future__ import annotations

import datetime
import logging
import os
import re
import time
from typing import Any, Optional, Tuple

import requests

from brain_core.config import Config as OptionsConfig
from brain_core.types import SimMetrics, SimSettings

log = logging.getLogger("brain_options.notifier")

WAT_TZ = datetime.timezone(datetime.timedelta(hours=1))  # UTC+1 (WAT / Lagos time)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _escape(text: str) -> str:
    """Escapes a string for Telegram MarkdownV2 parse mode."""
    # Characters that must be escaped in MarkdownV2 outside code spans
    special = r"\_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(special)}])", r"\\\1", str(text))


def _now_wat() -> datetime.datetime:
    return datetime.datetime.now(WAT_TZ)


def _post_with_retry(
    url: str,
    payload: dict,
    max_attempts: int = 2,
    backoff_seconds: float = 1.5,
) -> Optional[requests.Response]:
    """
    POSTs to Telegram, retrying once (with a short backoff) on connection/timeout
    exceptions. Returns the Response on a completed request (any status code), or
    None if every attempt raised an exception.
    """
    last_exc: Optional[Exception] = None
    for attempt in range(1, max_attempts + 1):
        try:
            return requests.post(url, json=payload, timeout=10)
        except Exception as exc:
            last_exc = exc
            if attempt < max_attempts:
                log.warning(
                    "Telegram request exception (attempt %d/%d), retrying in %.1fs: %s",
                    attempt,
                    max_attempts,
                    backoff_seconds,
                    exc,
                )
                time.sleep(backoff_seconds)
    log.warning("Telegram notification exception after %d attempt(s): %s", max_attempts, last_exc)
    return None


def _send(text: str, config: OptionsConfig, db: Any = None) -> Tuple[bool, str]:
    """
    Sends a MarkdownV2 message to Telegram with plain-text fallback, 429 backoff,
    and connection-error retry.

    Returns (success, reason). reason is "" on success; otherwise a short
    machine-readable code ("not_configured", "rate_limited", "request_exception",
    "http_<code>") describing why the message was not delivered.
    """
    if not config.telegram_bot_token or not config.telegram_chat_id:
        return False, "not_configured"

    if db is not None and hasattr(db, "acquire_telegram_send_lease"):
        try:
            db.acquire_telegram_send_lease(min_gap_seconds=1.2, max_wait_seconds=6.0)
        except Exception as exc:
            log.debug("Telegram send-lease acquisition skipped: %s", exc)

    url = f"https://api.telegram.org/bot{config.telegram_bot_token}/sendMessage"
    payload = {"chat_id": config.telegram_chat_id, "text": text, "parse_mode": "MarkdownV2"}

    resp = _post_with_retry(url, payload)
    if resp is None:
        return False, "request_exception"

    if resp.status_code == 200:
        log.info("Telegram message sent.")
        return True, ""

    if resp.status_code == 429:
        retry_after = 3.0
        try:
            retry_after = float((resp.json() or {}).get("parameters", {}).get("retry_after", retry_after))
        except Exception:
            pass
        log.warning("Telegram rate-limited (429). Backing off %.1fs before one retry.", retry_after)
        time.sleep(retry_after)
        resp = _post_with_retry(url, payload, max_attempts=1)
        if resp is None:
            return False, "request_exception"
        if resp.status_code == 200:
            log.info("Telegram message sent (after 429 backoff).")
            return True, ""
        if resp.status_code == 429:
            log.warning("Telegram still rate-limited (429) after backoff; dropping message.")
            return False, "rate_limited"
        # fall through to the plain-text fallback below with whatever error this was

    # Fallback: strip parse_mode and retry with plain text (handles MarkdownV2 escaping bugs)
    payload.pop("parse_mode", None)
    payload["text"] = re.sub(r"\\([_*\[\]()~`>#+\-=|{}.!])", r"\1", text)
    resp2 = _post_with_retry(url, payload, max_attempts=1)
    if resp2 is None:
        return False, "request_exception"
    if resp2.status_code == 200:
        log.info("Telegram message sent (plain text fallback).")
        return True, ""
    if resp2.status_code == 429:
        log.warning("Telegram still rate-limited (429) after fallback; dropping message.")
        return False, "rate_limited"

    log.warning("Telegram send failed: %s %s", resp2.status_code, resp2.text[:200])
    return False, f"http_{resp2.status_code}"


def _send_bool(text: str, config: OptionsConfig, db: Any = None, label: str = "notification") -> bool:
    """
    Thin wrapper around _send() that preserves the existing bool-returning public
    API (callers and tests check `if success:` / `assert result is True`) while
    surfacing delivery failures as errors so silent drops don't happen.
    """
    success, reason = _send(text, config, db=db)
    if not success:
        log.warning("Telegram %s not delivered (reason=%s).", label, reason)
        log.error("Telegram %s not delivered after all retries (reason=%s).", label, reason)
    return success


# ---------------------------------------------------------------------------
# Public notification functions
# ---------------------------------------------------------------------------

def send_telegram_startup(
    config: OptionsConfig,
    mode: str = "Single Batch",
    db: Any = None,
) -> bool:
    """Startup ping — only sent when NOTIFY_ON_STARTUP=true to prevent cron noise."""
    if os.environ.get("NOTIFY_ON_STARTUP", "false").lower() != "true":
        return True
    text = f"🚀 *Pipeline started* — {_escape(mode)}"
    return _send_bool(text, config, db=db, label="startup ping")


def send_telegram_batch_summary(
    passed_count: int,
    total_candidates: int,
    config: OptionsConfig,
    stats: Optional[dict[str, Any]] = None,
    db: Any = None,
) -> bool:
    """
    Fires at the end of a batch ONLY when at least 1 alpha qualifies (passed_count > 0).
    Zero-pass batches remain completely silent to eliminate notification noise.
    """
    if passed_count <= 0 or total_candidates <= 0:
        return True

    stats = stats or {}
    today_q = stats.get("today_qualified", 0)
    reserve = stats.get("reserve_count", 0)
    today_sub = stats.get("today_submitted", 0)
    today_eval = stats.get("today_evaluated", 0)
    ts = _now_wat().strftime("%H:%M")

    icon = "✅"
    headline = f"{_escape(str(passed_count))} alpha{'s' if passed_count > 1 else ''} qualified"

    lines = [
        f"{icon} *{headline}* · {_escape(ts)} UTC\\+1",
        "",
        f"Batch: {_escape(str(passed_count))}/{_escape(str(total_candidates))} passed",
        f"Today total: {_escape(str(today_eval))} sims · {_escape(str(today_q))} qualified · {_escape(str(today_sub))} submitted · {_escape(str(reserve))} reserve",
    ]
    return _send_bool("\n".join(lines), config, db=db, label="batch summary")


def send_telegram_worker_batch_ping(
    strategy: str,
    passed_count: int,
    total_evaluated: int,
    archetype: str,
    config: OptionsConfig,
    stats: Optional[dict[str, Any]] = None,
    db: Any = None,
) -> bool:
    """
    Batch completion ping — ONLY fires when a batch produces >= 1 qualified alpha
    to completely eliminate 0-yield message noise from the chat.
    """
    if passed_count <= 0:
        return True

    ts = _now_wat().strftime("%H:%M")
    stats = stats or {}
    today_eval = stats.get("today_evaluated", total_evaluated)
    today_q = stats.get("today_qualified", passed_count)
    reserve = stats.get("reserve_count", 0)
    status_text = f"{passed_count}/{total_evaluated} qualified"
    summary_suffix = f" · {_escape(str(reserve))} reserve" if reserve > 0 else ""
    lines = [
        f"🎯 *Batch Yield* · {_escape(ts)} WAT",
        f"Strategy: `{_escape(strategy or 'general')}`",
        f"Result: *{_escape(status_text)}*",
        f"Today: {_escape(str(today_eval))} sims · {_escape(str(today_q))} qualified{summary_suffix}",
    ]
    return _send_bool("\n".join(lines), config, db=db, label=f"batch ping ({strategy})")


def check_and_send_hourly_health(
    store: Any,
    config: OptionsConfig,
    min_interval_minutes: int = 55,
    active_strategy: Optional[str] = None,
) -> bool:
    """
    Hourly health trigger for the unified Xtley001 runner.
    Atomically checks if >= min_interval_minutes have elapsed since the last health check
    was sent. If so, claims the slot in PostgreSQL and sends the 🟢 Hourly Health report.

    Guarantees exactly one heartbeat per hour, regardless of GitHub Actions cron jitter.
    """
    can_send = False
    if hasattr(store, "claim_hourly_health_slot"):
        can_send = store.claim_hourly_health_slot(min_interval_minutes=min_interval_minutes)
    elif hasattr(store, "db") and store.db and hasattr(store.db, "claim_hourly_health_slot"):
        can_send = store.db.claim_hourly_health_slot(min_interval_minutes=min_interval_minutes)

    if not can_send:
        return False

    log.info("[HOURLY HEALTH] Slot claimed. Sending hourly health heartbeat to Telegram...")
    stats = store.get_options_stats() if hasattr(store, "get_options_stats") else {}
    if not stats:
        log.error("Health check DB query returned no stats (store query broken)!")
        send_telegram_emergency_alert(
            error_summary="Health check DB query returned no stats (store query broken).",
            config=config,
            context="Health Check Query Empty",
            db=store,
            cooldown_minutes=60,
        )
    return send_telegram_health_check(config, stats=stats, active_strategy=active_strategy, db=store)



def send_telegram_alert(
    expression: str,
    settings: SimSettings,
    metrics: SimMetrics,
    max_corr: float,
    config: OptionsConfig,
    db: Any = None,
) -> bool:
    """
    Instant alert when a new alpha passes all gates and enters the qualified pool.
    No expression shown — just the numbers that matter.
    """
    if not config.telegram_bot_token or not config.telegram_chat_id:
        return False

    alpha_id = metrics.alpha_id or "unknown"
    margin_bps = (metrics.margin or 0.0) * 10_000.0
    ts = _now_wat().strftime("%H:%M")

    lines = [
        f"🎯 *Alpha qualified* · {_escape(ts)} UTC\\+1",
        "",
        f"`{_escape(alpha_id)}`",
        "",
        f"Sharpe `{_escape(f'{metrics.sharpe:.2f}')}` · "
        f"Fitness `{_escape(f'{metrics.fitness:.2f}')}` · "
        f"TO `{_escape(f'{metrics.turnover * 100:.1f}')}%`",
        f"Margin `{_escape(f'{margin_bps:.1f}')} bps` · "
        f"Corr `{_escape(f'{max_corr:.2f}')}` \\< 0\\.70 ✓",
        f"Universe `{_escape(settings.universe)}` · Delay `{_escape(str(settings.delay))}` · Decay `{_escape(str(settings.decay))}`",
    ]
    return _send_bool("\n".join(lines), config, db=db, label="alpha qualified alert")


def send_telegram_drip_alert(
    alpha_id: str,
    date_label: str,
    metrics: dict[str, Any],
    config: OptionsConfig,
    slot_num: int = 1,
    max_daily: int = 3,
    next_unlock_str: Optional[str] = None,
    db: Any = None,
) -> bool:
    """
    Fires the moment an automated drip submission is confirmed live on BRAIN.
    Clean, slot-aware, no links, no formula noise.
    """
    if not config.telegram_bot_token or not config.telegram_chat_id:
        return False

    now_wat = _now_wat()
    ts = now_wat.strftime("%H:%M")
    sharpe = float(metrics.get("sharpe") or 0.0)
    fitness = float(metrics.get("fitness") or 0.0)
    turnover = float(metrics.get("turnover") or 0.0) * 100.0
    margin_bps = float(metrics.get("margin") or 0.0) * 10_000.0

    if next_unlock_str:
        next_msg = _escape(next_unlock_str)
    elif slot_num < max_daily:
        next_dt = now_wat + datetime.timedelta(hours=4)
        next_msg = f"Next slot opens at {_escape(next_dt.strftime('%H:%M'))} UTC\\+1"
    else:
        next_msg = f"Daily quota full \\({_escape(str(slot_num))}/{_escape(str(max_daily))}\\) · Next window tomorrow 05:00 UTC\\+1"

    lines = [
        f"📬 *Submitted* · Slot {_escape(str(slot_num))}/{_escape(str(max_daily))} · {_escape(ts)} UTC\\+1",
        "",
        f"`{_escape(alpha_id)}`",
        "",
        f"Sharpe `{_escape(f'{sharpe:.2f}')}` · Fitness `{_escape(f'{fitness:.2f}')}` · TO `{_escape(f'{turnover:.1f}')}%` · Margin `{_escape(f'{margin_bps:.1f}')} bps`",
        "",
        f"_{next_msg}_",
    ]
    return _send_bool("\n".join(lines), config, db=db, label="drip submission alert")


def send_telegram_health_check(
    config: OptionsConfig,
    stats: Optional[dict[str, Any]] = None,
    active_strategy: Optional[str] = None,
    db: Any = None,
    **kwargs: Any,
) -> bool:
    """
    Hourly system heartbeat. Shows today's complete discovery funnel across all pipeline stages.
    Called by the health.yml workflow every hour.
    """
    if not config.telegram_bot_token or not config.telegram_chat_id:
        return False

    stats = stats or {}
    ts = _now_wat().strftime("%H:%M")
    today_eval = stats.get("today_evaluated", 0)
    today_s0 = stats.get("today_stage0_pass", 0)
    today_q = stats.get("today_qualified", 0)
    today_sub = stats.get("today_submitted", 0)
    reserve = stats.get("reserve_count", 0)
    today_corr = stats.get("today_correlated", 0)
    top_blocker = stats.get("top_corr_partner", "")
    top_blocker_cnt = stats.get("top_corr_partner_count", 0)
    max_daily = 3

    # Stage 0 pass rate percentage
    s0_pct_str = f" \\({today_s0 * 100 // today_eval}%\\)" if today_eval > 0 else ""

    # Submission slot indicator (Stage 3)
    slot_bar = ""
    for i in range(1, max_daily + 1):
        slot_bar += "\u25cf" if i <= today_sub else "\u25cb"

    # Qualified progress toward daily target (Stage 1-2)
    target = 5
    q_bar = ""
    for i in range(1, target + 1):
        q_bar += "\u25cf" if i <= today_q else "\u25cb"

    lines = [
        f"🟢 *Hourly Health* · {_escape(ts)} WAT",
        "",
        f"Simulated today: `{_escape(str(today_eval))}`",
        f"Stage 0 \\(Fast Screen\\): `{_escape(str(today_s0))}`{s0_pct_str}",
        f"Stage 1\\-2 \\(Qualified\\): `{_escape(str(today_q))}/{_escape(str(target))}` {_escape(q_bar)}",
        f"Stage 3 \\(Submitted\\): `{_escape(str(today_sub))}/{_escape(str(max_daily))}` {_escape(slot_bar)}",
        f"Reserve \\(Ready to Drip\\): `{_escape(str(reserve))}`",
        f"Corr\\-rejected today: `{_escape(str(today_corr))}`",
    ]
    if top_blocker and today_corr >= 3:
        lines.append(f"Top blocker: `{_escape(top_blocker)}` \\({_escape(str(top_blocker_cnt))}/{_escape(str(today_corr))}\\)")
    if active_strategy:
        lines.extend(["", f"Strategy Rotation: `{_escape(active_strategy)}`"])
    return _send_bool("\n".join(lines), config, db=db, label="hourly health check")


def send_telegram_daily_digest(
    config: OptionsConfig,
    stats: Optional[dict[str, Any]] = None,
    db: Any = None,
) -> bool:
    """
    End-of-day full summary. Called once daily at 22:50 UTC by daily_digest.yml.
    Covers the full picture across all pipeline stages, submissions, reserve, and lifetime totals.
    """
    if not config.telegram_bot_token or not config.telegram_chat_id:
        return False

    stats = stats or {}
    now = _now_wat()
    date_label = _escape(now.strftime("%a %d %b"))
    max_daily = 3

    today_eval = stats.get("today_evaluated", 0)
    today_s0 = stats.get("today_stage0_pass", 0)
    today_q = stats.get("today_qualified", 0)
    today_sub = stats.get("today_submitted", 0)
    reserve = stats.get("reserve_count", 0)
    today_corr = stats.get("today_correlated", 0)
    today_rej = stats.get("today_rejected", 0)
    top_blocker = stats.get("top_corr_partner", "")
    all_eval = stats.get("all_time_evaluated", 0)
    all_s0 = stats.get("all_time_stage0_pass", 0)
    all_pool = stats.get("all_time_pool_alphas", 0)
    all_corr = stats.get("all_time_correlated", 0)

    s0_pct_str = f" \\({today_s0 * 100 // today_eval}%\\)" if today_eval > 0 else ""

    # Daily goal assessment
    if today_q >= 5:
        goal_icon = "✅"
        goal_note = "Daily target met"
    elif today_q >= 3:
        goal_icon = "🟡"
        goal_note = "Partial — below 5 target"
    else:
        goal_icon = "🔴"
        goal_note = "Below target"

    sub_status = f"{today_sub}/{max_daily} submitted"
    if today_sub >= max_daily:
        sub_status += " ✅"

    lines = [
        f"📊 *Daily Report* · {date_label}",
        "",
        f"*Pipeline Stages*",
        f"Simulated: `{_escape(str(today_eval))}`",
        f"Stage 0 Screen: `{_escape(str(today_s0))}`{s0_pct_str}",
        f"Stage 1\\-2 Qualified: `{_escape(str(today_q))}`",
        f"Stage 3 Submitted: `{_escape(str(today_sub))}/{_escape(str(max_daily))}`",
        f"Corr\\-rejected: `{_escape(str(today_corr))}`",
    ]
    if today_rej > 0:
        lines.append(f"Checklist\\-rejected: `{_escape(str(today_rej))}`")
    if top_blocker:
        lines.append(f"Dominant Blocker: `{_escape(str(top_blocker))}`")

    lines.extend([
        "",
        f"*Submissions*",
        f"{_escape(sub_status)}",
        f"Ready \\(drip reserve\\): `{_escape(str(reserve))}`",
        "",
        f"*Daily goal: 5 qualified* · {_escape(goal_icon)} {_escape(goal_note)}",
        "",
        f"*All\\-time Totals*",
        f"Evaluated: `{_escape(str(all_eval))}` · Stage 0: `{_escape(str(all_s0))}`",
        f"Pool: `{_escape(str(all_pool))}` · Ready: `{_escape(str(reserve))}` · Corr\\-archive: `{_escape(str(all_corr))}`",
    ])
    return _send_bool("\n".join(lines), config, db=db, label="daily digest")


def send_telegram_emergency_alert(
    error_summary: str,
    config: Optional[OptionsConfig] = None,
    context: str = "Worker Failure",
    db: Any = None,
    cooldown_minutes: int = 240,
) -> bool:
    """
    Sends an immediate high-priority alert when an unhandled exception or
    worker crash occurs.

    Cross-worker dedup: uses cluster_session_cache & pipeline_alerts_log (shared
    across all 4 GH matrix workers) to ensure only ONE alert fires per context per cooldown
    window, even when all 4 workers hit the same error simultaneously.

    cooldown_minutes (default 4h):
      - Schema Migration Failure: 360 min (6h) — same failures fire every run
      - Lock DB Error: 60 min — important but resolves quickly
      - Generator Zero-Yield: 120 min — fires at most twice a day
      - All others: 240 min (4h)
    """
    if config is None:
        try:
            from brain_core.config import Config as OptionsConfig
            config = OptionsConfig.from_env()
        except Exception:
            pass

    if not config or not config.telegram_bot_token or not config.telegram_chat_id:
        log.error(
            "[ALERT SILENT] Telegram credentials missing! Critical alert dropped: [%s] %s",
            context,
            error_summary,
        )
        return False

    # --- Cross-worker dedup check ---
    # Resolve the db object regardless of whether it's an OptionsStore or OptionsDatabase
    _db = None
    if db is not None:
        if hasattr(db, "alert_dedup_ok"):
            _db = db
        elif hasattr(db, "db") and hasattr(db.db, "alert_dedup_ok"):
            _db = db.db

    if _db is None and config and config.database_url:
        try:
            from brain_store.db import OptionsDatabase
            _db = OptionsDatabase(config.database_url)
        except Exception:
            pass

    if _db is not None:
        try:
            if not _db.alert_dedup_ok(context, cooldown_minutes=cooldown_minutes):
                log.debug("Alert suppressed (dedup): context=%s cooldown=%dmin", context, cooldown_minutes)
                return False  # Already fired by another worker within cooldown
        except Exception:
            pass  # fail-open: still send the alert

    ts = _now_wat().strftime("%H:%M")
    clean_err = str(error_summary).strip()
    if len(clean_err) > 300:
        clean_err = clean_err[:297] + "..."

    footer = "Worker process exception. Investigation recommended." if "Crash" in context or "Exception" in context else "Diagnostic threshold alert. Pipeline continues operating."
    lines = [
        f"🚨 *PIPELINE CRITICAL ALERT* · {_escape(ts)} WAT",
        "",
        f"*Context:* `{_escape(context)}`",
        f"*Error:* `{_escape(clean_err)}`",
        "",
        _escape(footer),
    ]
    result = _send_bool("\n".join(lines), config, db=db, label="critical alert")

    # --- Log to dedup table so other workers don't repeat it ---
    if _db is not None and result:
        try:
            _db.log_alert_fired(
                context=context,
                message=clean_err[:500],
                severity="CRITICAL",
                cooldown_minutes=cooldown_minutes,
            )
        except Exception:
            pass

    return result


def send_telegram_drip_failure_alert(
    alpha_id: str,
    reason: str,
    config: OptionsConfig,
    db: Any = None,
) -> bool:
    """
    Sends an alert when a scheduled alpha drip submission fails or is rejected by BRAIN.
    """
    if not config.telegram_bot_token or not config.telegram_chat_id:
        return False

    ts = _now_wat().strftime("%H:%M")
    clean_reason = str(reason).strip()
    if len(clean_reason) > 200:
        clean_reason = clean_reason[:197] + "..."

    lines = [
        f"⚠️ *Submission Failed* · {_escape(ts)} WAT",
        "",
        f"Alpha: `{_escape(alpha_id)}`",
        f"Reason: `{_escape(clean_reason)}`",
    ]
    return _send_bool("\n".join(lines), config, db=db, label="drip failure alert")


def send_telegram_correlation_concentration_alert(
    blocking_partner: str,
    collision_count: int,
    total_corr_today: int,
    config: OptionsConfig,
    db: Any = None,
) -> bool:
    """
    Alerts when a single submitted alpha blocks > 70% of correlation-rejected candidates today.
    """
    if not config.telegram_bot_token or not config.telegram_chat_id:
        return False

    ts = _now_wat().strftime("%H:%M")
    pct = (collision_count / total_corr_today * 100) if total_corr_today > 0 else 0.0

    lines = [
        f"🚨 *Correlation Concentration Alert* · {_escape(ts)} WAT",
        "",
        f"Blocker Alpha: `{_escape(blocking_partner)}`",
        f"Today's Collisions: `{_escape(str(collision_count))}/{_escape(str(total_corr_today))}` \\({_escape(f'{pct:.0f}%')}\\)",
        "",
        "⚠️ Excessive correlation against single pool alpha detected\\. Generation auto\\-cooldown triggered\\.",
    ]
    return _send_bool("\n".join(lines), config, db=db, label="correlation concentration alert")

