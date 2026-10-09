"""Data fields for Options Expiration Gamma Pinning & Strike Clustering."""
from __future__ import annotations

FIELDS = [
    "implied_volatility_mean_30",
    "call_breakeven_30",
    "forward_price_30",
    "pcr_oi_30",
    "pcr_vol_30",
    "volume",
    "adv20",
    "close",
    "returns",
]

FIELD_DESCRIPTIONS = {
    "implied_volatility_mean_30": "30-day ATM implied volatility mean",
    "call_breakeven_30": "30-day call breakeven level",
    "forward_price_30": "30-day forward price computed from put-call parity",
    "pcr_oi_30": "30-day put-call open interest ratio",
    "pcr_vol_30": "30-day put-call volume ratio",
    "volume": "Daily share volume executed",
    "adv20": "20-day average daily volume",
    "close": "Daily adjusted closing equity price",
    "returns": "Daily total return",
}
