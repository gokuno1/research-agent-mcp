# Quantitative Models Reference

Detailed specifications for the quantitative methods used in the investment-management skill. Each model includes its formula, inputs, interpretation, and known limitations.

---

## 1. Factor Scoring Models

### 1.1 Value Factor — Composite Score

**Components (equal-weighted within the factor):**

```
Value_Z = 0.30 × zscore(E/P) + 0.30 × zscore(FCF/EV) + 0.20 × zscore(EBITDA/EV) + 0.20 × zscore(B/P)
```

**Z-scoring protocol:**
- Compute within sector (not cross-sector — banks can't be compared to tech on B/P)
- Winsorize at 1st/99th percentile before scoring (prevents outlier domination)
- Higher Z = cheaper = more attractive

**Value Trap Filter:**
```
IF (Value_Z > 0.5) AND (ROIC < WACC for 3+ consecutive years):
    EXCLUDE — this is a value trap, not a mispricing
```

**Academic basis:** Fama-French (1992, 1993), Asness-Moskowitz-Pedersen (2013)

---

### 1.2 Quality Factor — QMJ Decomposition

Based on Asness, Frazzini & Pedersen (2018) "Quality Minus Junk":

```
Quality_Z = 0.35 × Profitability_Z + 0.25 × Growth_Z + 0.25 × Safety_Z + 0.15 × Payout_Z
```

**Profitability sub-score:**
```
Profitability_Z = zscore(GP/Assets) + zscore(ROE) + zscore(ROA) + zscore(CFO/Assets)
                  ─────────────────────────────────────────────────────────────────────
                                                    4
```

**Growth sub-score:**
```
Growth_Z = zscore(5yr_EPS_CAGR) + zscore(5yr_Revenue_CAGR) + zscore(Δ(GP/Assets)_5yr)
           ─────────────────────────────────────────────────────────────────────────────
                                                3
```

**Safety sub-score:**
```
Safety_Z = zscore(-Beta) + zscore(-Volatility_60d) + zscore(-Leverage) + zscore(Altman_Z)
           ─────────────────────────────────────────────────────────────────────────────────
                                                4
```

**Payout sub-score:**
```
Payout_Z = zscore(Dividend_Yield + Buyback_Yield + Net_Debt_Paydown_Yield)
```

---

### 1.3 Momentum Factor

```
Momentum_Z = 0.50 × zscore(Return_12m_minus_1m) + 0.30 × zscore(Earnings_Revision_3m) + 0.20 × zscore(Price/52wk_High)
```

**12-1 month return:** Skip the most recent month (short-term reversal effect).

**Earnings revision momentum:**
```
ERM = (# analysts revising up - # analysts revising down) / total analysts covering
```
Measured over the last 90 days. Range: -1 to +1.

**Market-state filter (MANDATORY):**
```
IF benchmark_close < 200_day_MA(benchmark):
    Momentum_weight = 0
    Redistribute to Quality
```

**Academic basis:** Carhart (1997), Jegadeesh & Titman (1993), Cooper-Gutierrez-Hameed (2004)

---

### 1.4 Low Volatility Factor

```
LowVol_Z = 0.40 × zscore(-Volatility_60d) + 0.40 × zscore(-Beta_2yr) + 0.20 × zscore(-MaxDD_12m)
```

Note: Negative sign on all inputs because LOWER volatility = HIGHER score.

**Academic basis:** Frazzini-Pedersen (2014) "Betting Against Beta", Baker-Bradley-Wurgler (2011)

---

## 2. Portfolio Optimization

### 2.1 Mean-Variance (Markowitz with Constraints)

**Objective:**
```
maximize: w'μ - (λ/2) × w'Σw
subject to:
    Σw_i = 1                           (fully invested)
    0 ≤ w_i ≤ w_max                    (position limits)
    Σw_sector ≤ sector_max             (sector cap)
    w'Σw ≤ σ²_budget                   (risk budget)
    N_min ≤ |{i: w_i > 0}| ≤ N_max    (cardinality)
```

**Inputs:**
- `μ` = vector of expected excess returns (from factor model: `μ_i = Σ(factor_weight × factor_score_i × factor_premium)`)
- `Σ` = covariance matrix (2-year weekly returns, Ledoit-Wolf shrinkage applied)
- `λ` = risk aversion parameter, calibrated to achieve target portfolio volatility

**Covariance Estimation — Ledoit-Wolf Shrinkage:**
```
Σ_shrunk = (1 - α) × Σ_sample + α × Σ_target
where:
    Σ_target = avg_correlation × I + (1 - avg_correlation) × diag(σ²)
    α = optimal shrinkage intensity (from Ledoit-Wolf formula)
```

This reduces estimation error from using sample covariance with limited data.

### 2.2 1/N with Tilts (Simplified Alternative)

When full optimization is impractical:
```
w_i = (1/N) × (1 + κ × normalized_score_i)
```
Where:
- `N` = number of positions
- `κ` = tilt intensity (0.3 default — allows ±30% deviation from equal weight)
- `normalized_score_i` = Composite_Factor_Score rescaled to [-1, +1]

Renormalize so `Σw_i = 1` after applying tilts.

---

## 3. Risk Models

### 3.1 Portfolio Volatility

```
σ_portfolio = √(w'Σw) = √(Σ_i Σ_j w_i × w_j × σ_i × σ_j × ρ_ij)
```

Annualized from weekly returns: `σ_annual = σ_weekly × √52`

### 3.2 Value-at-Risk (VaR)

**Parametric VaR (assumes normal distribution):**
```
VaR_95% = μ_portfolio - 1.645 × σ_portfolio (daily)
VaR_99% = μ_portfolio - 2.326 × σ_portfolio (daily)
```

**Historical VaR:**
Sort historical daily returns. VaR_95% = 5th percentile return.

**Known limitation:** Parametric VaR underestimates tail risk because returns are fat-tailed. Always report Conditional VaR alongside.

### 3.3 Conditional VaR (Expected Shortfall)

```
CVaR_95% = E[Loss | Loss > VaR_95%] = average of all returns worse than the 5th percentile
```

More useful than VaR for portfolio risk management because it answers "when things go wrong, how wrong do they go?"

### 3.4 Maximum Drawdown

```
Drawdown_t = (Peak_t - Value_t) / Peak_t
Max_Drawdown = max(Drawdown_t) over all t in the period
```

**Expected Max Drawdown estimate (from volatility):**
```
Expected_MaxDD ≈ σ_annual × 2.5 (for Sharpe ~0.5)
Expected_MaxDD ≈ σ_annual × 2.0 (for Sharpe ~1.0)
```

This is a rough heuristic — actual max drawdown depends on autocorrelation and fat tails.

### 3.5 Beta and Tracking Error

```
β_portfolio = Cov(R_portfolio, R_benchmark) / Var(R_benchmark)
Tracking_Error = σ(R_portfolio - R_benchmark) × √252 (annualized)
Information_Ratio = Alpha / Tracking_Error
```

---

## 4. Position Sizing

### 4.1 Kelly Criterion

**Full Kelly:**
```
f* = (p × b - q) / b
```
Where:
- `p` = win probability
- `q` = 1 - p = loss probability
- `b` = payoff ratio (avg_win / avg_loss)

**For factor investing (typical parameters):**
- `p` = 0.55 to 0.62 (from academic factor quintile studies)
- `b` = 1.3 to 1.8 (avg winner / avg loser from same studies)
- Full Kelly ≈ 15-35% per position (FAR too aggressive)

**Fractional Kelly (what to actually use):**
```
f_actual = f* × safety_factor
where safety_factor ∈ [0.25, 0.50]
```

Quarter-Kelly (safety_factor = 0.25): Conservative, ~4-9% per position
Half-Kelly (safety_factor = 0.50): Moderate, ~8-18% per position

### 4.2 Volatility-Targeted Sizing (Moreira-Muir 2017)

Scale position size inversely to realized volatility:
```
w_i_adjusted = w_i_base × (σ_target / σ_i_realized)
```

Where:
- `σ_target` = target position-level volatility contribution (e.g., 1% of portfolio per position)
- `σ_i_realized` = realized 20-day annualized volatility of stock i

Effect: Volatile stocks get smaller positions; stable stocks get larger positions. Empirically improves Sharpe by 0.1-0.3 across most factor strategies.

### 4.3 Risk Parity (for allocation across asset classes)

If the portfolio spans multiple asset classes:
```
w_i ∝ 1 / σ_i (inverse volatility weighting)
```

Or full risk parity:
```
w_i such that: w_i × σ_i × ρ(i, portfolio) = equal for all i
```

---

## 5. Rebalancing Cost Model

### 5.1 Transaction Cost Estimation

```
Transaction_Cost_per_trade = Brokerage + STT + Exchange_fees + Slippage
```

**India (NSE/BSE):**
- Brokerage: ₹20 flat or 0.03% (discount broker)
- STT: 0.1% (delivery buy+sell)
- Exchange charges: 0.00325%
- Slippage: 0.05-0.15% (depending on liquidity)
- **Total round-trip: ~0.35-0.50%**

**US (NYSE/NASDAQ):**
- Commission: $0 (most retail brokers)
- SEC fee: negligible
- Slippage: 0.02-0.10% (large-caps very liquid)
- **Total round-trip: ~0.05-0.15%**

### 5.2 Break-Even Rebalancing Threshold

Only rebalance a position if expected improvement exceeds cost:
```
Rebalance IF: |current_weight - target_weight| × Expected_Active_Return > 2 × Transaction_Cost
```

This prevents over-trading that destroys alpha through friction.

---

## 6. Performance Attribution

### 6.1 Brinson-Fachler Attribution

Decompose active return into:
```
Active_Return = Allocation_Effect + Selection_Effect + Interaction_Effect

Allocation = Σ(w_portfolio_sector - w_bench_sector) × (R_bench_sector - R_bench_total)
Selection  = Σ w_bench_sector × (R_portfolio_sector - R_bench_sector)
Interaction = Σ(w_portfolio_sector - w_bench_sector) × (R_portfolio_sector - R_bench_sector)
```

This tells you whether your outperformance came from:
- Being in the right sectors (allocation)
- Picking the right stocks within sectors (selection)
- Both (interaction)

### 6.2 Factor Attribution

```
R_portfolio = α + β_value × F_value + β_quality × F_quality + β_momentum × F_momentum + β_lowvol × F_lowvol + ε
```

Running this regression over time reveals:
- How much of your return is factor exposure (systematic) vs. alpha (idiosyncratic skill)
- Whether your "alpha" is just undisclosed factor exposure

---

## 7. Drawdown Control

### 7.1 Volatility Scaling (Moreira-Muir)

When realized volatility exceeds target:
```
IF σ_realized_20d > σ_target × 1.5:
    Reduce gross exposure: new_exposure = target_exposure × (σ_target / σ_realized_20d)
```

### 7.2 Trend Filter (Faber 2007)

Simple but effective drawdown control:
```
IF benchmark_price > 200_day_SMA: fully invested
IF benchmark_price < 200_day_SMA: move 30-50% to cash/short-term bonds
```

Historically reduces max drawdown by 40-60% with modest return sacrifice (0.5-1% annually).

### 7.3 Regime-Based Allocation Shift

| Signal | Action |
|--------|--------|
| VIX crosses above 25 (or India VIX > 20) | Reduce equity allocation by 20% |
| VIX crosses above 35 (or India VIX > 30) | Reduce equity allocation by 40% |
| Credit spreads widen > 100bps in 30 days | Defensive shift: increase Quality/LowVol, cut Momentum |
| Yield curve inverts (3m-10y) | Begin 12-month transition to defensive positioning |

---

## Known Limitations

1. **All factor premiums are time-varying.** Value had a decade of underperformance (2010-2020). Quality is the most consistent but not immune to drawdowns.
2. **Covariance estimates are noisy with limited data.** Ledoit-Wolf helps but doesn't eliminate the problem. With 20 stocks and 2 years of weekly data, you have 104 observations to estimate 210 pairwise correlations — statistically fragile.
3. **Expected returns from factor models are rough.** The factor premium spread (top vs. bottom quintile) averages 4-8% annually but has enormous standard error. Don't over-trust point estimates.
4. **Kelly criterion assumes you know the true parameters.** You don't. This is why fractional Kelly (0.25-0.50×) is essential — it buffers against parameter uncertainty.
5. **These models assume liquid, transparent equity markets.** For illiquid, OTC, or emerging-frontier markets, slippage and market impact dominate — reduce all sizing by 50% minimum.
