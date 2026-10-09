# Institutional 13F Ownership Breadth & Smart-Money Dynamics

## 1. Economic Hypothesis
Chen, Hong, & Stein (2002) and Sias, Starks, & Titman (2006) demonstrate that changes in the **breadth of institutional owners** (the number of distinct funds holding an equity) contain greater return predictability than the aggregate raw volume of shares held. When breadth expands across a cross-section of institutional investors, short-sale constraints are relieved and positive consensus leads future quarterly returns.

## 2. Key Mathematical Operators
- **Breadth Delta:** `(inst_owners_count - ts_delay(inst_owners_count, 60)) / (ts_delay(inst_owners_count, 60) + 1.0)`
- **Institutional Velocity:** `ts_decay_linear(ts_delta(inst_holding_pct, 20), 20)`
- **Breadth-to-Holdings Asymmetry:** `ts_zscore(inst_owners_count, 60) - ts_zscore(inst_holding_shares, 60)`

## 3. Literature Citations
- **Chen, J., Hong, H., & Stein, J.C. (2002)**. *Breadth of Ownership and Stock Returns*. Journal of Financial Economics.
- **Sias, R.W., Starks, L.T., & Titman, S. (2006)**. *Changes in Institutional Ownership and Stock Returns: Assessment and Methodology*. Journal of Business.
