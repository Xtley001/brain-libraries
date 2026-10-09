"""Data fields for R&D Capitalization & Technology Spillovers."""
from __future__ import annotations

FIELDS = [
    "returns",
    "close",
    "volume",
    "adv20",
    "rd_expense",
    "total_assets",
    "sales",
    "capx",
    "implied_volatility_mean_30",
]

FIELD_DESCRIPTIONS = {
    "returns": "Daily total return",
    "close": "Daily adjusted closing equity price",
    "volume": "Daily share volume executed",
    "adv20": "20-day average daily volume",
    "rd_expense": "Quarterly Research and Development expenditure",
    "total_assets": "Quarterly balance sheet total assets",
    "sales": "Quarterly total revenue/sales",
    "capx": "Quarterly capital expenditures",
    "implied_volatility_mean_30": "30-day ATM implied volatility mean",
}
