"""Data fields for Dynamic Short Squeeze & Borrow Fee Convexity."""
from __future__ import annotations

FIELDS = [
    "borrow_fee",
    "short_interest",
    "shares_out",
    "volume",
    "adv20",
    "close",
    "returns",
    "implied_volatility_mean_30",
    "implied_volatility_mean_skew_30",
]

FIELD_DESCRIPTIONS = {
    "borrow_fee": "Annualized cost of borrowing equity for short positioning (bps)",
    "short_interest": "Total shares sold short reported by exchanges",
    "shares_out": "Total ordinary shares outstanding",
    "volume": "Daily share volume executed",
    "adv20": "20-day average daily volume",
    "close": "Daily adjusted closing equity price",
    "returns": "Daily total return",
    "implied_volatility_mean_30": "30-day ATM implied volatility mean",
    "implied_volatility_mean_skew_30": "30-day 25-delta OTM put/call implied volatility skew",
}
