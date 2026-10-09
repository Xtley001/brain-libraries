"""Data fields for Macroeconomic & Scheduled Event Drift."""
from __future__ import annotations

FIELDS = [
    "returns",
    "close",
    "volume",
    "adv20",
    "implied_volatility_mean_30",
    "implied_volatility_call_30",
    "implied_volatility_put_30",
    "historical_volatility_30",
]

FIELD_DESCRIPTIONS = {
    "returns": "Daily total return",
    "close": "Daily adjusted closing equity price",
    "volume": "Daily share volume executed",
    "adv20": "20-day average daily volume",
    "implied_volatility_mean_30": "30-day ATM implied volatility mean",
    "implied_volatility_call_30": "30-day ATM call implied volatility",
    "implied_volatility_put_30": "30-day ATM put implied volatility",
    "historical_volatility_30": "30-day realized historical volatility",
}
