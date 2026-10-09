# Model-Free Jump Variance & Risk-Neutral Moments

## 1. Economic Hypothesis
Carr & Madan (2001) and Bollerslev, Tauchen, & Zhou (2009) prove that option prices can be decomposed into continuous diffusive variance and discontinuous jump variance. Cross-sectional variations in model-free jump variance measure the market's pricing of tail risk, generating high-capacity cross-sectional equity alpha.

## 2. Key Mathematical Operators
- **Jump Variance Curvature:** `implied_volatility_put_30^2 - 2.0 * implied_volatility_mean_30^2 + implied_volatility_call_30^2`
- **Risk-Neutral Kurtosis Spread:** `(implied_volatility_put_60 + implied_volatility_call_60 - 2.0 * implied_volatility_mean_60) / (implied_volatility_mean_60 + 0.001)`
- **VRP Term Slope:** `ts_decay_linear((IV_30^2 - RV_20^2) - (IV_90^2 - RV_60^2), 20)`

## 3. Literature Citations
- **Carr, P., & Madan, D. (2001)**. *Towards a Theory of Volatility Trading*. Cambridge University Press.
- **Bollerslev, T., Tauchen, G., & Zhou, H. (2009)**. *Expected Stock Returns and Variance Risk Premia*. Review of Financial Studies.
- **Bakshi, G., Kapadia, N., & Madan, D. (2003)**. *Stock Return Characteristics, Option Prices, and Higher Moments*. Review of Financial Studies.
