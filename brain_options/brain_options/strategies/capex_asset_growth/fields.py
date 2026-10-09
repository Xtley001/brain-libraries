"""Data fields for Capital Investment & Asset Growth Anomalies."""
from __future__ import annotations

FIELDS = [
    "returns",
    "close",
    "volume",
    "adv20",
    "capx",
    "total_assets",
    "sales",
    "implied_volatility_mean_30",
]

FIELD_DESCRIPTIONS = {
    "returns": "Daily total return",
    "close": "Daily adjusted closing equity price",
    "volume": "Daily share volume executed",
    "adv20": "20-day average daily volume",
    "capx": "Quarterly capital expenditures",
    "total_assets": "Quarterly balance sheet total assets",
    "sales": "Quarterly total revenue/sales",
    "implied_volatility_mean_30": "30-day ATM implied volatility mean",
}
