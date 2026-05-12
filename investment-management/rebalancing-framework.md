# Rebalancing Framework

Detailed specification of the active rebalancing protocol — scheduled rebalancing cadence, trigger-based overrides, transaction cost thresholds, tax-aware execution, and the state machine governing portfolio transitions.

---

## 1. Rebalancing Philosophy

**Core principle:** A portfolio decays without maintenance. Price movements cause drift (winners grow, losers shrink), regimes change, and new information emerges. But excessive rebalancing destroys alpha through transaction costs. The optimal approach is **calendar-based with event-triggered overrides** — scheduled reviews at fixed intervals, with the ability to act immediately when material changes occur.

**Academic evidence:**
- Optimal rebalancing frequency for multi-factor equity portfolios: monthly (Novy-Marx & Velikov 2016)
- More frequent (weekly/daily) rebalancing adds cost without improving Sharpe
- Less frequent (quarterly/annual) misses regime transitions and allows excessive drift
- Trigger-based rebalancing outperforms calendar-only by 0.3-0.5% annually (Masters 2003)

---

## 2. Scheduled Rebalancing Cadence

### Monthly Review (Primary Cycle)

Run on the first trading day of each month:

| Step | Action | Decision Rule |
|------|--------|---------------|
| 1 | Fetch current weights | Compute drift from target |
| 2 | Re-score all holdings | Update factor scores with latest data |
| 3 | Check against universe | Are there better candidates than bottom holdings? |
| 4 | Check macro regime | Has the regime changed since last review? |
| 5 | Compute rebalancing cost | Sum transaction costs for proposed trades |
| 6 | Execute only if: improvement > 2× cost | Break-even gate |

**Monthly output:** Updated portfolio weights, any swaps, factor score changes, cost incurred.

### Quarterly Deep Review

Every 3 months (January, April, July, October first week):

- Full re-run of Phases 2-7 from the SKILL.md Mode A workflow
- Re-optimize portfolio weights (not just adjust at the margin)
- Update covariance matrix with most recent 2-year window
- Re-assess macro regime and adjust factor weights accordingly
- Evaluate whether any position should be replaced (not just trimmed)

### Annual Reset

Once per year (January):

- Challenge all mandate parameters: Is the benchmark still appropriate? Has risk tolerance changed?
- Full universe re-screening from scratch
- Factor model parameter review (did the factor premiums hold last year?)
- Tax optimization: harvest accumulated losses before year-end
- Produce annual performance report vs. benchmark

---

## 3. Trigger-Based Rebalancing (Event-Driven)

Triggers override the calendar. When a trigger fires, execute immediately regardless of the next scheduled rebalance date.

### Position-Level Triggers

| Trigger | Threshold | Action | Rationale |
|---------|-----------|--------|-----------|
| **Drift Up** | Position weight > target + 3% absolute | Trim to target weight | Prevent over-concentration from appreciation |
| **Drift Down** | Position weight < target - 3% absolute | Evaluate: add if thesis intact, sell if broken | Avoid passive underweight of conviction |
| **Large Win** | Position up > 50% from entry | Trim 30-50% of position, reset target lower | Lock gains, reduce single-name risk |
| **Thesis Break** | Micro thesis invalidated (earnings miss + downgrade + moat erosion) | Sell 100% immediately | Capital preservation |
| **Stop-Loss** | Position down > 20% from entry (or trailing 15%) | Re-evaluate: sell if fundamental reason. Hold ONLY if micro thesis fully intact AND drawdown is macro-driven | Avoid catastrophic losses |
| **Earnings Catalyst** | Major earnings beat/miss + revision change | Adjust weight: beat + upgrade → add to target+2%. Miss + downgrade → trim or sell | PEAD: price will continue drifting in the direction of the surprise |

### Portfolio-Level Triggers

| Trigger | Threshold | Action | Rationale |
|---------|-----------|--------|-----------|
| **Sector Drift** | Any sector > `max_sector_weight` | Trim lowest-conviction position in the overweight sector | Maintain diversification |
| **Volatility Spike** | Portfolio vol > `risk_budget` × 1.2 | Reduce highest-vol positions until vol ≤ budget | Risk budget discipline |
| **Correlation Break** | Average portfolio correlation rises > 0.7 | Add uncorrelated position or reduce concentrated cluster | Diversification preservation |
| **Factor Concentration** | Single factor > 50% of composite score contribution | Diversify: add positions from underrepresented factor | Avoid unintended factor bets |

### Market-Level Triggers

| Trigger | Threshold | Action | Rationale |
|---------|-----------|--------|-----------|
| **Benchmark Drawdown** | Benchmark down > 10% from 52-week high | Phase 1: Increase cash to 10-15%. Cut momentum to 0. Add to Quality + LowVol. | Drawdown protection; momentum crash avoidance |
| **Benchmark Drawdown (Severe)** | Benchmark down > 20% from peak | Phase 2: Increase cash to 20-25%. Maximum defensive positioning. Begin shopping list for recovery additions. | Capital preservation in bear market |
| **Volatility Regime Change** | VIX > 30 (or India VIX > 25) for 5+ consecutive days | Reduce gross exposure by 20%. Widen mental stops. Reduce position count to max 10. | Volatility scaling (Moreira-Muir) |
| **Macro Regime Change** | Regime transitions per `macro-research-analyst` (e.g., Goldilocks → Late Cycle) | Re-run Phase 3 factor weight adjustment. Potentially swap 2-4 positions aligned to new regime. | Regime-adaptive management |
| **Trend Filter** | Benchmark crosses below 200-day MA | Move 30% of equity to cash/bonds. Resume full equity when benchmark crosses above 200-day MA. | Faber trend filter — reduces max drawdown 40-60% |
| **Recovery Signal** | Benchmark 200-day MA cross-up after > 10% drawdown | Begin re-deploying cash. Add deepest-value names first. Increase momentum weight gradually over 2 months. | Early recovery positioning |

---

## 4. Transaction Cost Gate

**The cardinal rule:** Never rebalance if the expected benefit doesn't exceed the cost with a safety margin.

### Cost Computation

For each proposed trade:
```
Cost = |ΔWeight| × Portfolio_Value × Round_Trip_Cost%

Where Round_Trip_Cost% =
    India delivery: 0.40% (brokerage + STT + slippage)
    US equity: 0.10% (commission-free, slippage only)
    India F&O: 0.15% (lower STT + tighter spreads)
```

### Break-Even Gate

```
EXECUTE trade IF:
    Expected_Improvement_Annual × Holding_Period_Fraction > 2 × Transaction_Cost

Where:
    Expected_Improvement = |New_Factor_Score - Old_Factor_Score| × Factor_Premium_Annual
    Factor_Premium_Annual ≈ 4-6% (top vs. bottom quintile spread)
    Holding_Period_Fraction = min(1, expected_holding_months / 12)
```

**Example:**
- Swapping a stock with factor score 0.3 for one with score 0.8
- Expected improvement: |0.8 - 0.3| × 5% = 2.5% annually
- Holding period: 6 months → fraction = 0.5 → expected improvement this period = 1.25%
- Transaction cost (sell + buy): 0.4% + 0.4% = 0.8%
- 1.25% > 2 × 0.8%? No (1.25% < 1.6%). **DON'T TRADE.**
- Wait for a larger score difference or lower cost.

### Batch Optimization

When multiple trades are proposed:
1. Rank by (Expected_Improvement - Transaction_Cost) descending
2. Execute from highest to lowest until marginal trade breaks even
3. Stop when the next trade's benefit < 2× its cost

---

## 5. Tax-Aware Rebalancing (India-Specific)

### Capital Gains Tax Regime (India FY2025-26)

| Holding Period | Tax Rate | Exemption |
|---------------|----------|-----------|
| **STCG** (< 12 months) | 20% of gains | None |
| **LTCG** (≥ 12 months) | 12.5% of gains | ₹1.25 lakh exempt per year |

### Tax-Loss Harvesting Protocol

Monthly check for tax-loss harvesting opportunities:

```
IF position_loss > 5% AND position has been held < 12 months:
    Sell to realize Short-Term Capital Loss
    Replace with a correlated substitute (same factor exposure, different stock)
    Wait 30 days before repurchasing the original (wash-sale concept)
    Net benefit: STCL offsets STCG elsewhere in the portfolio at 20% rate
```

**Constraints:**
- Only harvest if a suitable substitute exists (same sector, similar factor score)
- The substitute must not violate portfolio constraints (sector cap, correlation)
- Track all harvested losses in the rebalancing log

### Gain Deferral Protocol

When a rebalancing trade would generate a large taxable gain:

```
IF unrealized_gain > 20% AND holding_period < 10 months:
    Defer the trade if possible — wait until LTCG eligibility (12 months)
    Exception: SELL IMMEDIATELY if thesis-break trigger fires (capital preservation > tax)

IF unrealized_gain > 20% AND holding_period ≥ 12 months:
    Proceed with trade (LTCG at 12.5% — acceptable cost for portfolio improvement)
    Utilize ₹1.25L exemption on highest-gain positions first
```

---

## 6. Rebalancing State Machine

The portfolio is always in one of these states:

```
┌─────────────────┐    drift < tolerance    ┌─────────────────┐
│   ON-TARGET     │ ◄───────────────────── │   DRIFTED       │
│  (no action)    │                         │  (monitor)      │
└────────┬────────┘                         └────────┬────────┘
         │                                           │
         │ time = scheduled review                   │ drift > tolerance OR trigger fires
         ▼                                           ▼
┌─────────────────┐                         ┌─────────────────┐
│   REVIEWING     │                         │  REBALANCING    │
│  (scoring)      │                         │  (trading)      │
└────────┬────────┘                         └────────┬────────┘
         │                                           │
         │ proposed trades pass cost gate            │ trades executed
         ▼                                           ▼
┌─────────────────┐                         ┌─────────────────┐
│  REBALANCING    │ ────────────────────── │   ON-TARGET     │
│  (trading)      │    trades complete      │  (reset drift)  │
└─────────────────┘                         └─────────────────┘
```

**State: DEFENSIVE** (special state — entered from any state when market-level trigger fires)

```
Normal state ──► VIX > 30 or Benchmark -10% ──► DEFENSIVE
DEFENSIVE ──► VIX < 25 sustained 5 days AND benchmark above 200-day MA ──► Normal state
```

In DEFENSIVE state:
- No new positions opened
- Scheduled rebalancing suspended (only trigger-based exits allowed)
- Cash allocation increased per trigger table
- Re-entry only when exit conditions met

---

## 7. Rebalancing Log Format

Every rebalancing action is logged as an HTML file to `docs/rebalancing-log/YYYY-MM-DD-rebalance.html`. Use the same dark-theme CSS from the report templates. The HTML log must include:

**Required sections:**
1. **Header** — Date, Type (Scheduled/Trigger), Trigger details, Pre-rebalance state
2. **Trades Executed table** — Action, Ticker, Shares, Price, Weight Change, Cost, Reason
3. **Portfolio State comparison** — Before vs. After for key metrics (positions, sector weight, vol, beta)
4. **Factor Scores Change** — table of changed positions with old/new scores
5. **Cost Summary** — total cost, expected improvement, break-even ratio
6. **Next Review** — date + active triggers list

Example structure (data to fill per rebalance event):

```
Trades: [# | Action | Ticker | Shares | Price | Weight Change | Cost | Reason]
State:  [Metric | Before | After | Change]
Costs:  [Total: $X | Improvement: X% | Break-even: X.X]
Next:   [Date + triggers]
```

---

## 8. Recovery Protocol (After Drawdown)

When the portfolio has experienced a significant drawdown (> 10%) and recovery signals appear:

### Phase 1: Stabilization (drawdown in progress)
- No new buys
- Tighten stops on all positions
- Increase cash allocation per trigger table
- Document the drawdown narrative (what caused it)

### Phase 2: Base Formation (drawdown halted, flat/bouncing)
- Begin research on recovery candidates (deep value names that sold off indiscriminately)
- Rank current holdings by thesis-integrity (which are damaged vs. which just followed the market)
- Prepare shopping list but don't buy yet

### Phase 3: Recovery Deployment (trend filter turns positive)
- Re-deploy cash in tranches: 25% per week over 4 weeks (not all at once)
- Prioritize: deepest value first, highest quality second, momentum last (momentum needs 2+ months of uptrend before it's safe)
- Position sizes start at 50% of target; increase to full over 8 weeks as recovery confirms
- Document recovery decisions in rebalancing log

---

## 9. Backtest Overfitting Safeguards

Per Bailey, Borwein, López de Prado & Zhu (2014):

**Rules to prevent curve-fitting in the rebalancing framework:**

1. All thresholds in this document are from academic literature, not from backtesting this specific portfolio
2. No parameter in the framework has been "optimized" against historical data for this portfolio
3. The factor weights come from regime-mapping (macro analysis), not from return-maximization on past data
4. Triggers use round numbers (20%, 30%, 50%) from research — not suspiciously precise thresholds (17.3%, 28.7%)
5. Transaction cost gates use 2× safety factor (not 1.1× or 1.5× — round, conservative)
6. Any user-proposed "improvement" that requires fitting to historical returns should be rejected unless it has independent out-of-sample validation

**The Deflated Sharpe Ratio test:**
Before celebrating any strategy modification:
```
DSR = SR_observed × √(1 - skewness × SR/3 + (kurtosis-3) × SR²/8) > DSR_threshold(N_trials)
```
Where N_trials = number of parameter combinations tested. With 10+ trials, you need a much higher observed Sharpe to claim statistical significance.
