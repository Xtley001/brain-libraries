# Corporate Insider Cluster Buying & Opportunistic Flow

## 1. Economic Hypothesis
Cohen, Malloy, & Pomorski (2012) and Lakonishok & Lee (2001) demonstrate that while routine insider sales contain little informational value, **opportunistic open-market cluster purchases by corporate officers (CEO, CFO, Directors)** strongly predict positive future stock returns. Focussing on simultaneous transactions by 2+ insiders isolates genuine asymmetric information from noise.

## 2. Key Mathematical Operators
- **Cluster Buying Gating:** `trade_when(insider_buy_count >= 2, group_neutralize(rank(ts_decay_linear(insider_buy_shares / (adv20 + 1.0), 20)), subindustry), -1)`
- **Net Insider Ratio:** `(ts_sum(insider_buy_shares, 20) - ts_sum(insider_sell_shares, 20)) / (ts_sum(insider_buy_shares, 20) + ts_sum(insider_sell_shares, 20) + 1.0)`
- **Insider Market-Cap Fraction:** `ts_decay_linear(insider_buy_value / (cap + 1.0), 30)`

## 3. Literature Citations
- **Cohen, L., Malloy, C., & Pomorski, L. (2012)**. *Decoding Inside Information*. Journal of Finance.
- **Lakonishok, J., & Lee, I. (2001)**. *Are Insider Trades Informative?* Review of Financial Studies.
- **Seyhun, H.N. (1998)**. *Investment Intelligence from Insider Trading*. MIT Press.
