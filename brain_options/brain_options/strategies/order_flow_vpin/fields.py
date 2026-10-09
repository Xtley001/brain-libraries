"""Data fields for Institutional Order Flow Toxicity & VPIN."""
from __future__ import annotations

FIELDS = [
    "volume",
    "adv20",
    "close",
    "returns",
    "high",
    "low",
    "open",
    "vwap",
    "pcr_vol_20",
    "pcr_oi_20",
]

FIELD_DESCRIPTIONS = {
    "volume": "Daily share volume executed",
    "adv20": "20-day average daily volume",
    "close": "Daily adjusted closing equity price",
    "returns": "Daily total return",
    "high": "Daily high price",
    "low": "Daily low price",
    "open": "Daily opening price",
    "vwap": "Volume-weighted average price",
    "pcr_vol_20": "20-day put-call volume ratio",
    "pcr_oi_20": "20-day put-call open interest ratio",
}
