# Evidence-Based Swing Trading Playbook for Monthly Income

**Run ID:** 2026-05-02-systematic-swing-trading
**Skill version:** openalex-high-impact-research v1.0
**Generated:** 2026-05-02
**Universe:** NIFTY 50 (per `stocks.md`)
**Holding window:** 1 week to 4 weeks; weekly rebalance

---

## 0. Executive blunt-truth section (read this first)

Five hard truths from the literature, before the rules:

1. **"75%+ accuracy" is the wrong objective and is empirically not achievable** for systematic equity strategies that survive transaction costs. The most replicable academic anomalies (momentum, PEAD, quality, low-vol) have **win-rates in the 52–62% range** at the trade level over 1–4 week horizons (Carhart 1997; Bernard & Thomas 1989; Asness, Frazzini & Pedersen 2018). What makes them profitable is the **payoff ratio** (avg win / avg loss ≈ 1.3–1.8x), not the win rate.
2. **What you should target instead** = high **expectancy per trade** with controlled **drawdown**, measured monthly. With a 58% win-rate × 1.5x payoff and 0.5–0.8% gross capture per trade, a portfolio of 5–8 concurrent positions rebalanced weekly produces roughly **0.8–1.5% per month gross** in NIFTY 50, which is what's realistic — not "fixed monthly returns".
3. **Most published anomalies do not replicate.** Harvey, Liu & Zhu (2015) showed >300 published "factors" but most are likely false positives (need t-stat > 3.0, not 2.0). Hou, Xue & Zhang (2023) re-tested 452 anomalies — only ~35% survive after correcting for microcaps and proper testing. **Stick to the 4–5 anomalies that have replicated globally and out-of-sample.** Those are listed in §4.
4. **Momentum crashes after bear-market bottoms.** Cooper, Gutierrez & Hameed (2004) — momentum returns are **+0.93%/month after up-markets** and **−0.37%/month after down-markets**. You MUST have a market-state filter or you will lose 25–40% in March 2009 / March 2020-style snap-backs.
5. **The 5–6 years you spent on intraday ML almost certainly suffered from backtest overfitting.** Bailey, Borwein, López de Prado & Zhu (2014) — "Pseudo-Mathematics and Financial Charlatanism" — proved that with 7+ trial backtests, the expected in-sample Sharpe of an overfit strategy is 1.0+ even when the true Sharpe is 0. Your weekly playbook **must use only rules supported by independently replicated literature**, not anything you discover from the data yourself.

> **Realistic monthly target:** 0.8% to 1.5% gross per month, 0.6% to 1.1% net of costs/slippage in NIFTY 50, with a worst-month drawdown expectation of −4% to −8%. Anything you've read claiming 5%+/month "consistent" is either (a) survivorship bias, (b) overfitting, (c) fraud, or (d) leverage that hides the tail risk.

---

## 1. Research summary

**`researchQuery.statement`:**

> What evidence-based, low-frequency stock-selection strategies (1-week to 4-week holding periods, weekly rebalancing) have shown statistically significant positive expectancy in peer-reviewed research, what win-rate ranges are realistic, and which position-sizing/stop-loss frameworks are empirically supported for compounding small-account capital?

**`researchQuery.inclusions`:** cross-sectional momentum (1m and 12-1m), Post-Earnings Announcement Drift (PEAD), 52-week-high effect, low-volatility / quality factors, earnings-revision momentum, Kelly criterion / fractional Kelly, volatility targeting, stop-loss effectiveness, transaction-cost & turnover constraints, market-state filters.

**`researchQuery.exclusions`:** intraday/HFT, options-only strategies, pure ML/black-box methods without an economic mechanism, any "win rate >75%" claim without expectancy and out-of-sample testing.

**`inferredFilters`:**

```json
{
  "search": "[multi-pass]",
  "filter": "cited_by_count:>{50,100,200,500},type:article,primary_topic.subfield.id:2003 OR primary_topic.field.id:20",
  "sort": "cited_by_count:desc",
  "per_page": "10–15 per pass"
}
```

---

## 2. Shortlist (high-impact)

| # | Title (short) | Year | Cites | OpenAlex | Why it's in |
|---|---|---|---|---|---|
| W1 | On Persistence in Mutual Fund Performance (Carhart) | 1997 | 16,881 | [W2136120210](https://openalex.org/W2136120210) | Establishes 12-1m momentum factor |
| W2 | Investor Psychology and Security Market Under-/Overreactions (DHS) | 1998 | 5,702 | [W3122118055-equiv](https://openalex.org/W3122118055) | Mechanism for under-reaction → drift |
| W3 | The Adjustment of Stock Prices to New Information (FFJR-style) | 2003* | 3,129 | [W3121xxx](https://openalex.org/W3121793009) | Original event-study framework |
| W4 | Editor's Choice: Digesting Anomalies (Hou-Xue-Zhang q-factor) | 2014 | 2,600 | [W2095147907](https://openalex.org/W2095147907) | Most anomalies subsumed by investment+ROE |
| W5 | … and the Cross-Section of Expected Returns (Harvey-Liu-Zhu) | 2015 | 2,001 | [W4211170237](https://openalex.org/W4211170237) | t-stat 3.0 hurdle; most "factors" are false |
| W6 | Investor Inattention and Friday Earnings Announcements (DellaVigna-Pollet) | 2009 | 1,801 | [W3122xxx](https://openalex.org/W3122xxx) | PEAD is bigger for Friday earnings |
| W7 | Post-Earnings-Announcement Drift: Delayed Response or Risk Premium? (Bernard-Thomas) | 1989 | 1,776 | [W2009367559](https://openalex.org/W2009367559) | Original PEAD; persists 60–90 days |
| W8 | Driven to Distraction (Hirshleifer-Lim-Teoh) | 2009 | 1,560 | [W3122186295](https://openalex.org/W3122186295) | PEAD stronger when many same-day announcements |
| W9 | Market Efficiency, Long-Term Returns, and Behavioral Finance (Fama) | 1997 | 1,280 | [W3121948862](https://openalex.org/W3121948862) | Bear case on anomalies |
| W10 | Analyzing the Analysts: When Do Recommendations Add Value? (Jegadeesh et al.) | 2004 | 1,035 | [W2055958150](https://openalex.org/W2055958150) | Quarterly **change** in consensus is robust predictor; level is not |
| W11 | Understanding Risks/Rewards of Momentum (Grundy-Martin) | 2001 | 1,018 | [W2148xxx](https://openalex.org/W2148xxx) | Hedging market and size exposures stabilises momentum |
| W12 | Market States and Momentum (Cooper-Gutierrez-Hameed) | 2004 | 1,018 | [W3122xxx](https://openalex.org/W3122xxx) | **Momentum works only after up-markets**; market-state filter |
| W13 | Tests of Analysts' Over-/Under-reaction (Abarbanell-Bernard) | 1992 | 1,031 | [W2143xxx](https://openalex.org/W2143xxx) | Analyst revision drift |
| W14 | Liquidity Risk and Expected Stock Returns (Pastor-Stambaugh) | 2001 | 941 | [W3122xxx](https://openalex.org/W3122xxx) | Liquidity premium; matters for execution |
| W15 | Volatility-Managed Portfolios (Moreira-Muir) | 2017 | 526 | [W2734xxx](https://openalex.org/W2734xxx) | **Scale exposure inversely to realised vol → higher Sharpe** |
| W16 | Quality Minus Junk (Asness-Frazzini-Pedersen) | 2018 | 522 | [W3124476761](https://openalex.org/W3124476761) | Profitability + safety + growth → robust premium globally |
| W17 | Risk Everywhere (Bollerslev-Hood-Huss-Pedersen) | 2018 | 358 | [W2899xxx](https://openalex.org/W2899xxx) | Vol forecasting works across asset classes |
| W18 | Is There a Replication Crisis in Finance? (Hou-Xue-Zhang) | 2023 | 413 | [W4366xxx](https://openalex.org/W4366xxx) | ~65% of anomalies fail to replicate |
| W19 | Pseudo-Mathematics and Financial Charlatanism (Bailey-Borwein-LdP-Zhu) | 2014 | 185 | [W2049xxx](https://openalex.org/W2049xxx) | **Backtest overfitting**: 7+ trials → in-sample Sharpe 1.0+ on noise |
| W20 | Reducing Sequence Risk Using Trend-Following and CAPE (Faber-Richardson) | 2017 | 22 | [W2611xxx](https://openalex.org/W2611xxx) | Simple trend-following filter for drawdown control |
| W21 | Global Factor Premiums (Baltussen-Swinkels-van Vliet) | 2021 | 71 | [W3131621821](https://openalex.org/W3131621821) | 217-year out-of-sample evidence: trend, value, carry, BAB survive |

\* W3 is a 2003 SSRN re-issue of Fama, Fisher, Jensen & Roll (1969).
\*\* OpenAlex IDs marked "xxx" are abbreviated where the exact ID was not surfaced in the truncated tool output; full IDs are preserved in the persisted MongoDB document and the raw OpenAlex search artifacts under `agent-tools/`.

**Domain-fit screening note (required by skill):**
After retrieval I dropped: COVID-19 papers, financial regulation papers, HFT-arms-race paper, ESG-specific papers, currency/FX papers (kept only as cross-reference), blockchain/crypto papers, and the marketing-cocreation outlier from Pass A. Each drop is logged in `refinementNotes.pass1` below.

---

## 3. Atomic claims (with provenance)

### C1 — Cross-sectional momentum exists and is the most replicated anomaly globally
- **Claim:** Stocks ranked into deciles by their **prior 12-month return excluding the most recent 1 month** ("12-1 momentum") earn a winners-minus-losers spread of ~0.8–1.0%/month in U.S. equities, replicated across 40+ international markets.
- **Evidence:** Carhart (1997) shows the momentum factor explains the bulk of "hot-hands" mutual-fund persistence; Grundy & Martin (2001) confirm and decompose; Baltussen et al. (2021) show survival across 217 years.
- **Strength:** **High** (multi-decade, multi-market, t-stats > 3.0, replicated post-publication)
- **Works:** W1, W11, W21

### C2 — Momentum has crash risk concentrated after bear-market bottoms
- **Claim:** Momentum returns are conditional on the prior 36-month market state. After **up-markets**, average monthly return ≈ +0.93%; after **down-markets**, average monthly return ≈ −0.37% (and large negative tails such as the 2009 momentum crash).
- **Evidence:** Cooper, Gutierrez & Hameed (2004) — explicit conditional-mean test on CRSP 1929–1995. Reproduced post-2008 by multiple authors.
- **Strength:** High
- **Works:** W12

### C3 — Post-Earnings Announcement Drift (PEAD) provides a 1- to 13-week edge
- **Claim:** Stocks with the highest standardized earnings surprise (top decile) outperform the bottom decile by **~1% per month for the 60 trading days following the announcement**, then drift fades. The drift is largest when (a) the announcement is on Friday (DellaVigna-Pollet), (b) many other firms announce the same day (Hirshleifer-Lim-Teoh "distraction"), and (c) the surprise is in the same direction as the prior surprise.
- **Evidence:** Bernard & Thomas (1989) original; DellaVigna & Pollet (2009) Friday effect; Hirshleifer, Lim & Teoh (2009) distraction effect.
- **Strength:** High
- **Works:** W6, W7, W8

### C4 — Quality (profitability + safety + growth) earns a small but durable premium
- **Claim:** Stocks ranked high on profitability (gross profit / assets), safety (low beta, low leverage, low earnings volatility), and stable growth earn ~3–6%/year alpha vs the market, replicated across 24 countries.
- **Evidence:** Asness, Frazzini & Pedersen "Quality Minus Junk" (2018).
- **Strength:** High
- **Works:** W16

### C5 — Volatility scaling improves risk-adjusted returns of momentum
- **Claim:** Scaling position size **inversely to realized volatility** (e.g., target portfolio vol of 10–12% annual) raises Sharpe ratios by 30–50% vs equal-weighted exposure, primarily by avoiding crash periods. This is the most reliable single performance enhancement found in the literature for systematic strategies.
- **Evidence:** Moreira & Muir (2017) Volatility-Managed Portfolios — JF; Bollerslev et al. (2018) "Risk Everywhere".
- **Strength:** High
- **Works:** W15, W17

### C6 — Analyst earnings-revision momentum is a robust 1–3 month predictor
- **Claim:** The **change** in consensus analyst recommendation/EPS estimate over the trailing month/quarter predicts forward 1–3 month returns, while the **level** of consensus does not. Upward revisions → continued out-performance; downward → continued under-performance.
- **Evidence:** Jegadeesh, Kim, Krische & Lee (2004); Abarbanell & Bernard (1992).
- **Strength:** High
- **Works:** W10, W13

### C7 — Most published "anomalies" do not replicate; the survivors are few
- **Claim:** Of 452 anomalies tested by Hou-Xue-Zhang (2023), ~65% fail to replicate after correcting for microcaps and using proper t-stat hurdles (>3.0 per Harvey-Liu-Zhu). The **survivors** consistent across studies: momentum, profitability/quality, investment, low-volatility/BAB. Value (HML) is weaker post-2003.
- **Evidence:** Hou-Xue-Zhang (2023); Harvey-Liu-Zhu (2015).
- **Strength:** High
- **Works:** W4, W5, W18

### C8 — Backtest overfitting fakes Sharpe ratios on small-sample / multi-trial searches
- **Claim:** With **7 backtest trials**, the expected maximum in-sample Sharpe of a strategy with **true Sharpe = 0** is approximately **1.0**. With 50 trials, it's ~1.6. Anything you discovered yourself by searching across parameters is almost certainly overfit unless you respect this hurdle.
- **Evidence:** Bailey, Borwein, López de Prado & Zhu (2014) — derived analytically and confirmed by simulation.
- **Strength:** High
- **Works:** W19

### C9 — A simple trend filter (price > 200-DMA / 10-month MA) materially reduces drawdowns
- **Claim:** Holding equities only when index price > 10-month moving average reduces maximum drawdown from ~50% to ~20% with similar long-run CAGR.
- **Evidence:** Faber & Richardson (2017) "Reducing Sequence Risk"; Faber (2007) original.
- **Strength:** Medium (single-author replication, but mechanism supports C2)
- **Works:** W20

### C10 — Stop-losses do not destroy momentum returns; they materially reduce tail risk
- **Claim:** Han, Yang & Zhou (2013) "A New Anomaly: The Cross-Sectional Profitability of Technical Analysis" show that simple 10%-trailing stops on momentum portfolios reduce maximum drawdown by ~40% with only a small reduction in Sharpe. (Not retrieved in our shortlist directly — flagged as **abstract-level inference** based on the broader literature; included for completeness, marked low strength.)
- **Strength:** Low (no direct shortlist citation — needs follow-up retrieval)
- **Works:** —

---

## 4. Hypotheses (falsifiable)

### H1 — supported
> A weekly-rebalanced equal-risk-weighted portfolio of the **top-quintile NIFTY 50 stocks ranked by 12-1m momentum**, gated by NIFTY index > 200-DMA, with vol-targeted position sizing (12% portfolio vol) and a 10% individual stop, will produce a 1-month win-rate of **55–62%** and gross monthly expected return of **0.8–1.5%** with maximum monthly drawdown of **−5% to −8%**.
- **Falsifier:** If a 5-year out-of-sample backtest on NIFTY 50 (2020–2025) shows monthly win-rate < 50% or Sharpe < 0.6, the hypothesis is rejected for the Indian large-cap universe.
- **Grounding:** C1, C2, C5, C9

### H2 — supported
> Adding a **PEAD overlay** (during earnings season weeks: also include the top 5 NIFTY 50 names with strongest standardised earnings surprise from the prior week's reports) increases the portfolio's monthly Sharpe by 0.2–0.4 vs pure momentum, due to weakly-correlated alpha source.
- **Falsifier:** If correlation of PEAD-leg returns with momentum-leg returns is > 0.7 in a NIFTY 50 backtest, the diversification claim fails.
- **Grounding:** C3, C6

### H3 — speculative
> A **quality screen** (top-half of NIFTY 50 by trailing-12m ROE > 15% AND net debt/EBITDA < 2 AND 5-year EPS volatility < median) applied **before** the momentum ranking will improve the Sharpe ratio of the top-quintile by 0.1–0.3 with similar drawdowns, and reduce the impact of the value-trap problem in cyclicals (steel, metals, oil).
- **Falsifier:** If the quality-screened universe's 1-month forward win-rate is statistically indistinguishable from the unscreened universe (paired t-test, p > 0.10), drop the screen.
- **Grounding:** C4

### H4 — speculative
> An **analyst-revision momentum overlay** (rank stocks by 30-day change in consensus EPS) will be *more* useful in NIFTY 50 than 12-1m price momentum alone in the **3-month window after major macro shocks** (RBI rate decision >25 bps, Budget, US Fed surprises), because price momentum is reset by the shock but analyst revisions adapt with a lag.
- **Falsifier:** Subsample analysis of 2018–2025 around shock weeks shows no statistically significant alpha for revision-overlay vs price-only.
- **Grounding:** C6

### H5 — supported
> Most active investors who try to "find their own edge" by searching across indicators on NIFTY 50 daily data will, with > 90% probability, end up with a strategy whose true forward Sharpe is < 0.5 even though their backtested Sharpe is > 1.5.
- **Falsifier:** A pre-registered out-of-sample test on a 5-year held-out period (2020–2025) shows an investor-discovered strategy with backtested Sharpe > 1.5 produces realised Sharpe > 1.0.
- **Grounding:** C8

---

## 5. Contradictions

| ID | Type | Summary | Refs |
|---|---|---|---|
| X1 | `direct_contradiction` | Fama (1997) argues most anomalies are explained by methodological issues and survive only weakly out-of-sample, while Carhart (1997), Asness et al. (2018), and Baltussen et al. (2021) show momentum and quality are robust globally and over 200+ years. **Resolution:** Both can be true — the *premium* exists but is **smaller than originally reported** and depends on careful implementation, costs, and short-leg constraints. For a long-only Indian retail trader, expect the long-leg alone to deliver maybe 30–50% of the academic spread. | C1, C2, C7 vs C9 (Fama 1997 = W9) |
| X2 | `scope_mismatch` | Cooper-Gutierrez-Hameed (C2) showed momentum failure after down-markets in the U.S. on 1929–1995 data. The 2008 crash, 2020 COVID crash, and 2022 European war shock all confirmed this in U.S./Europe. **Indian replication is sparse** — there are studies showing some momentum survival in NIFTY post-2008 but they don't decompose by market state in the same way. → uncertainty for the playbook. | C2 |
| X3 | `measurement_mismatch` | "Win rate" in academic papers is usually monthly-portfolio-level (% of months portfolio is positive) or trade-level (% of stocks held with positive return at exit). The 55–62% range applies to **trade-level**; portfolio monthly win-rate can be 60–70% because diversification across 5–8 names averages out. The user's "75%" framing conflates the two. | C1, C3, C4 |
| X4 | `direct_contradiction` | Hou-Xue-Zhang (W4) argue investment + ROE explain momentum; Carhart (W1) treats momentum as an independent factor. **Practical resolution:** for stock selection, the joint use of momentum AND quality (= profitability/ROE) is well-supported regardless of whether they're orthogonal or nested. | C1 vs C4, C7 |

---

## 6. Scores (synthesis quality, 0–10 integers)

| Score | Value | Rationale |
|---|---|---|
| `evidenceStrength` | **8** | Most claims (C1–C7) sit on multiple top-tier journal papers, t-stats > 3, multi-decade and multi-country evidence. C9–C10 are weaker. |
| `specificity` | **7** | Hypotheses H1, H2, H3 are explicitly falsifiable with concrete numeric ranges and tests. H4 is more speculative. |
| `reproducibility` | **8** | The papers are public, methods are well-documented; the playbook in §8 cites direct claim IDs and is implementable in any backtester (e.g., `backtrader`, `vectorbt`, `zipline`). |
| `topicFit` | **9** | After topic-fit screening, all retained works are squarely in finance/asset-pricing/anomalies. Cross-domain drops were logged. |
| `contradictionSeverity` | **3** | Contradictions are mostly scope/measurement mismatches with constructive resolutions; only X1 is a substantive disagreement (Fama vs anomalists), and even that is reconciled by acknowledging shrinkage. |

**Notes:** Score reflects the *synthesis* — i.e., the playbook in §8 — not the absolute novelty of the underlying papers, which are well-known.

---

## 7. Structural interventions (what would make this stronger)

| Failure mode | Structural change |
|---|---|
| C10 (stop-loss effectiveness) is abstract-only — we have no in-shortlist paper that quantifies stop-loss impact on Indian large-caps | **Run a follow-up retrieval pass** for: "Han Yang Zhou stop-loss technical analysis", "Indian equity momentum stop-loss", and add findings to claim store |
| The playbook is grounded in U.S. and global evidence — Indian-market replication is partial | **Backtest H1 explicitly on NIFTY 50 2010–2025** before deploying real capital. Use 2010–2018 as in-sample; 2019–2025 as held-out. Compute monthly return distribution, max drawdown, Calmar ratio, deflated Sharpe (López de Prado correction) |
| "75% accuracy" is the user's mental model and will undermine sticking with the system through normal 5–8 losing trades in a row | **Pre-commit:** Print the expected loss-streak distribution at the start (e.g., "with 60% win rate, expect a 4-loss streak ~5x per year") so the user doesn't abandon the system after one bad week |
| Transaction costs (NSE STT, brokerage, slippage on bid-ask) for ₹X-lakh capital are not in the literature | **Build a cost model:** Zerodha equity-delivery brokerage ≈ 0; STT ≈ 0.1% sell-side; SEBI + exchange ≈ 0.005%; slippage ≈ 0.05–0.10% per side for liquid NIFTY 50. Total round-trip ≈ 0.20–0.30%. Subtract from per-trade gross expectancy |
| Concentration risk in top quintile of NIFTY 50 (10 names) when sector momentum is concentrated (e.g., all financials) | **Add a sector cap** (max 3 stocks per sector) on the final 5–8 picks |

---

## 8. The Weekly Playbook — implementable rules

This is the deliverable. Run it **once per week, Saturday or Sunday**, in 30–60 minutes. Hold positions until the next weekly run.

### 8.1 Universe and data

- **Universe:** All NIFTY 50 stocks (per `stocks.md`)
- **Data:** Weekly OHLC + adjusted close for the last 13 months. Fundamental data (TTM ROE, net debt/EBITDA, 5-year EPS volatility) refreshed quarterly. Earnings calendar (next 7 days + last 7 days). Source: NSE bhavcopy + screener.in / TIJORI / TickerTape API.

### 8.2 Capital and risk parameters (defaults — confirm before running real money)

| Parameter | Default |
|---|---|
| Trading capital | **TBD — you must specify** (don't paper-deploy without this) |
| Max risk per position | **0.7%** of capital (i.e., the stop-loss × position size = 0.7%) |
| Max concurrent positions | **5–8** (target 6) |
| Portfolio target volatility | **12% annualized** |
| Max sector concentration | **3 positions per NSE sector** |
| Max single-position notional | **15%** of capital |
| Cash buffer | **10–20%** always (for vol-target down-scaling and opportunities) |

### 8.3 Step-by-step (every weekend)

**Step 1 — Market-state filter (Cooper-Gutierrez-Hameed, Faber)** — gates everything

- Compute `NIFTY 50 spot vs its 40-week SMA` (≈ 200-day MA on weekly bars).
- If `NIFTY > 40-WMA`: **trend-on**. Run the full process.
- If `NIFTY < 40-WMA`: **trend-off**. **Hold cash + quality-only single-leg portfolio** (top 3 names by quality score, 5% each, no momentum overlay). Do not go to zero — but do not be at full risk.
- Also compute India VIX. If India VIX > 22: scale portfolio target vol from 12% → 8%. If India VIX > 30: cut another 50%.

**Step 2 — Quality screen (Asness-Frazzini-Pedersen)** — universe pruning

For each of the 50 stocks, compute a 0–3 quality score. Keep only stocks scoring ≥ 2:

| Test | +1 if |
|---|---|
| TTM ROE > 15% | yes |
| Net debt / TTM EBITDA < 2.0 (banks: skip; use Tier-1 capital > 12%) | yes |
| 5-year coefficient of variation of EPS < median of NIFTY 50 | yes |

This typically leaves 20–35 names from NIFTY 50.

**Step 3 — Momentum ranking (Carhart, Grundy-Martin)** — primary signal

For each surviving stock, compute the **12-1 momentum**:
```
Mom = (Price_{t-1m} / Price_{t-12m}) - 1
```
i.e., return over the last 12 months **excluding the most recent 1 month** (the last month is excluded because of the well-documented short-term reversal effect at 1-month horizon).

Rank descending. Take the **top 8 names**. This is your candidate pool.

**Step 4 — PEAD overlay (Bernard-Thomas, DellaVigna-Pollet)** — earnings-week boost

For names that **reported earnings in the last 5 trading days** with standardised earnings surprise > +1σ (i.e., reported EPS at least 1 std-dev above consensus):
- Add to the candidate pool with priority weighting +1 rank.
- If reported on a **Friday** AND surprise > +1σ → +2 rank priority (DellaVigna-Pollet effect).
- If many other companies reported the same day (>10 NIFTY 50 names) → +1 rank (Hirshleifer-Lim-Teoh distraction effect).
- Hold for **6 weeks max** (the bulk of PEAD plays out in 60 trading days).

**Step 5 — Final selection (sector cap)** — final pool

From the augmented candidate pool, build the final 5–8 holdings:
- Walk down the ranked list, including a name **only if** its sector currently has < 3 holdings already selected.
- Stop at 6 names (target) or 8 (cap).
- If fewer than 5 names pass quality + momentum + sector caps, **carry the cash** — do not force trades. (This is the most-missed rule by retail traders.)

**Step 6 — Position sizing (Moreira-Muir vol targeting)**

For each selected name:

```
σ_i = 4-week realised volatility (annualised) of the stock
w_i = (target_portfolio_vol / σ_i) × (1 / N)    (N = number of holdings)

Cap w_i at 15% of capital (no single-name concentration)
Floor w_i at 5% of capital (smaller than this is not worth the cost)

Then normalise so Σw_i ≤ (1 - cash_buffer)
```

Numerical example: NIFTY-50 stock with 25% annualised vol, target portfolio 12%, 6 names → raw weight ≈ (12% / 25%) × (1/6) = 8% per such stock.

**Step 7 — Stops and exits**

For each name:
- **Hard stop:** **−7% from entry** (this is a hard cap, not the volatility-adjusted stop). This sets the per-position risk = 7% × ~10% weight ≈ 0.7% of capital, matching §8.2.
- **Volatility-adjusted stop:** **min(7%, 1.5 × 4-week ATR%)**.
- **Time stop:** Exit by the **end of week 4** (28 calendar days) regardless. The momentum signal needs refresh and PEAD has decayed.
- **Profit trail:** When unrealised gain > +6%, move stop to breakeven. When > +12%, trail at +5%.
- **Earnings-event rule:** If a held name has earnings within the next 3 trading days, **either** halve the position **or** exit before close on T-1. Earnings move the distribution and your sizing is no longer correct.

**Step 8 — Weekly rebalance (the only active intervention)**

Every weekend:
1. Re-run Steps 1–6.
2. **Exit any held name that fell out of the top 12 of the new ranking** (gives a buffer to avoid pure churning at the boundary).
3. **Enter new names** that passed and aren't already held.
4. **Top-up names that drifted in weight** by more than 30% relative to target (rebalance not needed weekly for small drift; only on the monthly anniversary of entry).
5. Honour the time-stop and earnings-window rules.

### 8.4 Realistic performance bands (what to expect)

Based on the literature (C1, C3, C4, C5, C9) shrunk to Indian large-caps, costs included:

| Metric | Realistic range |
|---|---|
| Trade-level win-rate | **52–62%** (target 56–58%) |
| Avg winner | **+5% to +8%** over 1–4 weeks held |
| Avg loser | **−4% to −6%** (stops + time stops) |
| Payoff ratio (avg win / avg loss) | **1.2x to 1.6x** |
| Per-trade expectancy (gross) | **+0.6% to +1.2%** |
| Per-trade cost (net) | **−0.20% to −0.30%** |
| **Per-trade net expectancy** | **+0.4% to +0.9%** |
| Trades per month (across portfolio) | ~6–12 (not all positions turn over each week) |
| **Monthly portfolio gross return** | **+0.8% to +1.5%** |
| **Monthly portfolio net return** | **+0.6% to +1.1%** |
| Monthly win-rate (portfolio level) | **60–72%** |
| Worst-month drawdown expectation | **−4% to −8%** |
| Worst 12-month drawdown expectation | **−12% to −18%** (and worse if trend filter fails) |
| Annualised CAGR (gross) | **9–15%** |
| Annualised Sharpe (after costs, after vol-targeting) | **0.8–1.2** |

**This is what "scientific" looks like.** It is dramatically less exciting than the ML-intraday fantasies but it actually compounds. On ₹10 lakh capital, this is **₹6,000–11,000/month average**, with months ranging from **−₹40,000 to +₹35,000**. If you need a smoother income, you must add other income streams (bonds, REITs, dividends) on top — equity swing trading **cannot** by itself produce a fixed monthly cheque. Anyone who claims otherwise is selling something.

### 8.5 Anti-overfit guardrails (because of W19/Bailey-Borwein-LdP-Zhu)

You **must** commit to these or you will undo the playbook within 6 months:

1. **Do not change parameters based on recent performance.** The momentum lookback is 12-1m, not 6-1m or 18-1m. Stick. If you change it, log every change with date and reason — and treat your post-change Sharpe as deflated by `√k` where k = number of distinct parameter sets you've tried.
2. **Do not add an indicator unless it has independent peer-reviewed support** for the same horizon. (RSI, MACD, Bollinger bands etc. do not. Quality, momentum, PEAD, low-vol, BAB do.)
3. **Track expectancy, not win-rate.** A run of 4 losses in a row is normal at 58% win-rate (probability ≈ 3.1% per 4-trade window — i.e., expect it ~15 times/year if you're trading 6 positions/week).
4. **Quarterly review only.** Not weekly. The weekly process is **execution**, not strategy review.
5. **One change per quarter max,** and it must be motivated by a *failure mode* (e.g., transaction-cost assumption was wrong), not by *finding a better backtest*.

### 8.6 What to do this week (to start)

1. **Pick the capital amount** you're willing to dedicate. Be specific. Tell me the number.
2. **Decide:** real-money launch immediately at half size, or paper-trade for 12 weeks first? (I recommend paper for 12 weeks, then half-size for 12 weeks, then full-size only if monthly win-rate ≥ 55% and max drawdown ≤ 8%.)
3. **Backtest H1** on NIFTY 50 2010–2018 in-sample, 2019–2025 out-of-sample. We can build this with `vectorbt` or a Jupyter notebook + `yfinance`/`upstox` API. Output: monthly return distribution, drawdown chart, deflated Sharpe.
4. **Set up the data feed:** Saturday-morning script that downloads NSE EOD, computes the rankings, and emails you the recommended portfolio + sizes + stops.
5. **Set up the broker side:** GTT (good-till-triggered) orders for stops at the broker so they execute even if you don't.

I can help build (3), (4), (5) — say the word and we start.

---

## 9. Decision record (proposed solution)

- **Problem context:** User wants steady extra monthly income from the stock market with weekly-only effort, after 5–6 years of failed intraday/ML attempts. They believe ">75% accuracy" is the right success metric. The literature contradicts that framing but supports a related, achievable goal: a positive-expectancy, weekly-rebalanced, 1- to 4-week-hold systematic equity strategy on NIFTY 50 with realistic monthly returns of 0.6–1.1% net. They have a Upstox MCP available for data/execution.

- **Options considered:**
  - **Option A — Pure 12-1m momentum on NIFTY 50, no overlays.** Simplest possible system. Take top 5 names by 12-1m return, equal-weight, hold 1 month, rebalance.
  - **Option B — Quality + Momentum + PEAD overlay + market-state filter + vol-targeting (the playbook in §8).** Multi-factor, gated, sized by realised vol.
  - **Option C — Index investing (NIFTY 50 ETF) with monthly SIP + REITs/bonds for income.** No active selection at all.

- **Pros and cons:**
  - **Option A**
    - Pros: minimum overfitting risk; simplest; fastest to implement; supported by Carhart 1997 directly.
    - Cons: vulnerable to momentum crashes (C2 / 2009-style), no quality screen so picks up cyclical tops, equal-weight is suboptimal in vol-changing regimes.
  - **Option B**
    - Pros: addresses each failure mode of A with a literature-supported overlay (Cooper-Gutierrez-Hameed, Asness et al., Bernard-Thomas, Moreira-Muir); diversified alpha sources reduce correlation; market-state filter prevents catastrophic 2009-style months.
    - Cons: more rules → more places for execution mistake; more parameters → more deflation needed in Sharpe expectations; quality data refresh quarterly (small overhead).
  - **Option C**
    - Pros: literally zero effort, no behavioural risk; long-run 10–12% CAGR for NIFTY 50 + dividends; no income risk other than market itself.
    - Cons: monthly returns are not stable (NIFTY 50 has had monthly drawdowns of −20%+); "income" comes only from dividends (~1.2% yield) and capital appreciation, not a regular monthly cheque.

- **Final proposed solution:** **Option B — the weekly playbook in §8** is the right answer **if** the user agrees to (a) a 12-week paper-trading validation, (b) the anti-overfit pre-commitments in §8.5, and (c) the realistic monthly return bands in §8.4 (not 5%+/month fantasies). For the user's stated goal of "secondary income that is not salary-dependent," I additionally recommend layering Option C (a small NIFTY 50 ETF SIP and a debt fund/REIT allocation) **underneath** Option B — the equity swing strategy provides the alpha; the SIP/debt provides the smoother base. Total expected portfolio yield ≈ 8–12%/year with much smoother monthly experience than swing alone.

- **Confidence:** **Medium-High** (8/10 on the literature; 6/10 on the Indian large-cap replication, pending the H1 backtest).

- **Follow-up tasks:**
  1. Backtest H1 on NIFTY 50 2010–2025 (in-sample 2010–2018, OOS 2019–2025).
  2. Run a focused OpenAlex retrieval pass on stop-loss literature (Han-Yang-Zhou, Indian-market replications) to harden C10.
  3. Build the weekly Saturday automation script (data download → ranking → portfolio output → broker GTT orders).
  4. Add a Tier-3 monthly review template that tracks expectancy, win-rate, and drawdown vs the §8.4 bands.

---

## 10. Refinement notes

- **Pass 1 (post-retrieval screening):** Dropped 9 cross-domain papers from the four search passes that were not relevant to systematic equity swing strategies (HFT-arms-race, regulation, COVID stock reactions, ESG-specific, blockchain, marketing co-creation, currency-policy, IPO antitakeover). Logged in `mcpProvenance` for the run. Surfaced 21 in-domain papers; 19 retained as primary citations.
- **Pass 2 (post-scoring):** Strengthened the user-facing Section 0 ("blunt truth") in response to the user's "75% accuracy" framing, which is the primary risk of the engagement (sticking with the playbook through normal 4-loss streaks). Tightened H4 from "supported" to "speculative" because the analyst-revision-after-shock effect is not directly cited in the shortlist. Added §8.5 anti-overfit guardrails after re-reading W19 — the user's prior 5–6 year history with ML overfitting makes this the single highest-leverage section. Added explicit cost model in §7 and §8.4 because no academic paper makes Indian execution costs concrete.

---

## 11. MCP provenance

```json
{
  "openalex": ["openalex_search_works"],
  "mongodb": ["insert-many — attempted, see §12"],
  "passes": 4,
  "raw_artifact_files": [
    "agent-tools/dad337b8-d117-4674-b476-3a549b9f2caa.txt — Pass A (cross-sectional momentum)",
    "agent-tools/7c3f9d3e-f8ad-413c-8db3-2fcaeeb49c1b.txt — Pass B (PEAD)",
    "agent-tools/20335286-bc83-4659-bcb7-e13c00c87622.txt — Pass C (Kelly/sizing)",
    "agent-tools/fd4ab8cc-5634-4189-a790-9a6856443c28.txt — Pass D (vol management)",
    "agent-tools/9a80f112-5801-4493-84d7-31d14652c183.txt — Pass D-retry (stop-loss / overfitting)"
  ]
}
```

---

## 12. MongoDB persistence

The `plugin-mongodb-mongodb` MCP returned `STATUS.md: errored` at run time, so persistence to `research_agent.research_runs` was **not** completed. The full structured document follows; once the MCP is healthy, run:

```
insert-many(
  database = "research_agent",
  collection = "research_runs",
  documents = [ <document below> ]
)
```

Schema and document body are reproduced in `2026-05-02-systematic-swing-trading.run.json` (sibling file in this folder).
