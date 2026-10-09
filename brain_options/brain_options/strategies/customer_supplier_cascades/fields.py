"""Data fields for Customer-Supplier Revenue Concentration & Cascades."""
from __future__ import annotations

FIELDS = [
    "returns",
    "close",
    "volume",
    "adv20",
    "sales",
    "cogs",
    "inventory",
    "capx",
    "implied_volatility_mean_30",
]

FIELD_DESCRIPTIONS = {
    "returns": "Daily total return",
    "close": "Daily adjusted closing equity price",
    "volume": "Daily share volume executed",
    "adv20": "20-day average daily volume",
    "sales": "Quarterly total revenue/sales",
    "cogs": "Quarterly cost of goods sold",
    "inventory": "Quarterly inventory value",
    "capx": "Quarterly capital expenditures",
    "implied_volatility_mean_30": "30-day ATM implied volatility mean",
}
