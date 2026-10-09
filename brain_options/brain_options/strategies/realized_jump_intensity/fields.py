"""Data fields for Realized High-Frequency Jump Intensity & Skew."""
from __future__ import annotations

FIELDS = [
    "returns",
    "close",
    "open",
    "high",
    "low",
    "volume",
    "adv20",
    "historical_volatility_10",
    "historical_volatility_30",
    "implied_volatility_mean_30",
    "implied_volatility_skew_30",
]

FIELD_DESCRIPTIONS = {
    "returns": "Daily total return",
    "close": "Daily adjusted closing equity price",
    "open": "Daily opening equity price",
    "high": "Daily highest equity price",
    "low": "Daily lowest equity price",
    "volume": "Daily share volume executed",
    "adv20": "20-day average daily volume",
    "historical_volatility_10": "10-day realized historical volatility",
    "historical_volatility_30": "30-day realized historical volatility",
    "implied_volatility_mean_30": "30-day ATM implied volatility mean",
    "implied_volatility_skew_30": "30-day 25-delta put minus call implied volatility skew",
}
