# Post-Earnings Announcement Volatility Drift (PEAVD)

## 1. Economic Hypothesis
Ball & Brown (1968) and Bernard & Thomas (1989) established that markets under-react to quarterly earnings surprises (Standardized Unexpected Earnings / SUE), producing persistent multi-week post-earnings announcement drift. Combining SUE with implied volatility term structure slopes (Patel & Wolfson 1984) isolates firms where market-makers maintain high IV demand, confirming institutional participation.

## 2. Key Mathematical Operators
- **SUE x IV Ratio:** `group_neutralize(rank(ts_decay_linear(ts_zscore(eps_surprise, 60) * (implied_volatility_mean_30 / (implied_volatility_mean_90 + 0.001)), 20)), subindustry)`
- **PEAD Under-Reaction:** `ts_decay_linear(ts_zscore(eps_surprise, 60) - ts_zscore(ts_decay_linear(returns, 10), 20), 15)`
- **Conviction Gated Drift:** `trade_when(abs(rank(ts_decay_linear(ts_zscore(eps_surprise, 60), 20)) - 0.5) > 0.35, ...)`

## 3. Literature Citations
- **Ball, R., & Brown, P. (1968)**. *An Empirical Evaluation of Accounting Income Numbers*. Journal of Accounting Research.
- **Bernard, V.L., & Thomas, J.K. (1989)**. *Post-Earnings-Announcement Drift: Delayed Price Response or Risk Premium?* Journal of Accounting and Economics.
- **Patel, J.M., & Wolfson, M.A. (1984)**. *The Ex-Ante and Ex-Post Price Effects of Quarterly Earnings Announcements*.
