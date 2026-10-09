# Patent Innovation Efficiency & R&D Network Momentum

## 1. Economic Hypothesis
Cohen, Diether, & Malloy (2013) and Hirshleifer, Hsu, & Li (2013) prove that equity markets fail to accurately value intangible technological innovation. Scaling patent grants and forward citation impact against cumulative R&D investment (*Innovative Efficiency*) isolates companies with superior capital conversion that outperform industry peers over long holding periods.

## 2. Key Mathematical Operators
- **Innovative Efficiency (IE):** `group_neutralize(rank(ts_decay_linear(patent_count / (ts_decay_linear(rd_expenditure, 252) + 1.0), 60)), industry)`
- **Citation Acceleration:** `ts_decay_linear(ts_delta(patent_citations / (total_assets + 1.0), 40), 30)`
- **Innovation Intensity:** `trade_when(rd_expenditure > 0, group_neutralize(rank(ts_decay_linear((rd_expenditure / (sales + 1.0)) * (patent_count / (adv20 + 1.0)), 40)), subindustry), -1)`

## 3. Literature Citations
- **Cohen, L., Diether, K., & Malloy, C. (2013)**. *Misvaluing Innovation*. Review of Financial Studies.
- **Kogan, L., Papanikolaou, D., Seru, A., & Stoffman, N. (2017)**. *Technological Innovation, Resource Allocation, and Growth*. Quarterly Journal of Economics.
- **Hirshleifer, D., Hsu, P.H., & Li, D. (2013)**. *Innovative Efficiency and Stock Returns*. Journal of Financial Economics.
