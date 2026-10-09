"""Data fields for Structural Credit Risk & Distance to Default."""
from __future__ import annotations

FIELDS = [
    "returns",
    "close",
    "volume",
    "adv20",
    "debt_total",
    "assets",
    "cash_and_equivalents",
    "ebit",
    "implied_volatility_mean_30",
    "historical_volatility_30",
]

FIELD_DESCRIPTIONS = {
    "returns": "Daily total return",
    "close": "Daily adjusted closing equity price",
    "volume": "Daily share volume executed",
    "adv20": "20-day average daily volume",
    "debt_total": "Quarterly total debt obligations",
    "assets": "Quarterly total balance sheet assets",
    "cash_and_equivalents": "Quarterly cash and short term investments",
    "ebit": "Quarterly earnings before interest and taxes",
    "implied_volatility_mean_30": "30-day ATM implied volatility mean",
    "historical_volatility_30": "30-day realized historical volatility",
}
