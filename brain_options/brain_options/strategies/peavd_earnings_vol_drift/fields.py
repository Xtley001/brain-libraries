"""Fields for Post-Earnings Announcement Volatility Drift (PEAVD) Strategy."""

FIELDS: list[str] = [
    "eps_surprise",
    "est_eps",
    "implied_volatility_mean_30",
    "implied_volatility_mean_60",
    "implied_volatility_mean_90",
    "call_breakeven_30",
    "forward_price_30",
    "close",
    "returns",
    "volume",
]
