# Transmission Elasticity Library — v0.1

Quantified rules linking shocks to destination-economy impacts. Each entry is structured so the cross-border layer can apply it mechanically: shock → channel → number → lag → framework.

**Rules of use:**
1. Every elasticity must be cited (academic paper, central-bank research, or institutional analysis).
2. Every elasticity has a stated *confidence interval* — these are medians, not laws.
3. Every elasticity has a stated *lag* — when the effect lands.
4. Every elasticity is tagged with the framework that justifies it.
5. When using an elasticity, also state the *current value* of the shock and the *implied* destination impact.

---

## Elasticity 1 — Brent Crude → India Macro (FULLY FLESHED)

**Source shock:** Change in Brent crude oil price (USD/bbl)
**Destination:** India macro indicators
**Channel:** Energy import bill → Current account → FX → Imported inflation → Policy
**Framework tags:** `[CAD identity] + [USD pass-through] + [Fed-EM transmission]`

### Rule Set

| # | Source movement | Destination effect | Lag | Confidence | Citation |
|---|---|---|---|---|---|
| 1.1 | Brent +$10/bbl | India CAD widens by ~0.4% of GDP | 1-2 quarters | High | RBI Annual Report; CEA estimates |
| 1.2 | Brent +$10/bbl | India headline CPI +30-40 bps | 2-3 months direct, 4-6 months full pass-through | Moderate-high | RBI Bulletin Sep-2018, ICRIER 2019 |
| 1.3 | Brent +$10/bbl | INR depreciates 1-1.5% (other things equal) | 0-3 months | Moderate | NIPFP working papers |
| 1.4 | Brent +$10/bbl | FII equity outflows ~$2-3bn | 0-2 months | Low-moderate (highly conditional on Fed stance) | Empirical from 2018, 2022 episodes |
| 1.5 | Brent above $100 sustained 3 months | RBI rate-cut cycle paused or reversed | 1-2 quarters | High | RBI MPC minutes 2008, 2018, 2022 |
| 1.6 | Brent +$10/bbl | India fiscal subsidy bill (LPG + fertiliser) +₹15-20k crore/yr | 2-3 quarters | High | Union Budget elasticities |

### Worked Example — Apr 2026 (matches your existing report)

Given Brent at $120 vs $80 baseline (delta = +$40/bbl):

- **CAD widening:** +1.6% of GDP → CAD goes from ~−1% to ~−2.6% of GDP → ratings-watch territory `[CAD identity]`
- **CPI impulse:** +120-160 bps to headline, fully landing within 4-6 months → from CPI 3.4% to 4.6-5.0% `[USD pass-through]`
- **INR pressure:** ~4-6% depreciation channel → INR moves from 88 to 92-94 to USD `[CAD identity + USD pass-through]`
- **FII outflows:** $8-12bn implied (subject to Fed stance) `[Fed-EM transmission]`
- **RBI implication:** rate-cut cycle dead; pause is base case, hike if CPI breaches 5% `[heuristic — RBI reaction function]`

This is exactly the chain the existing 17-Apr-2026 report stated qualitatively. The library makes it numerically explicit.

### Asymmetries and Caveats

- The pass-through is **not symmetric**: oil falls don't translate fully to lower CPI because: (a) administered fuel prices are sticky downward, (b) downstream margins absorb the gain, (c) excise duties get raised on the way down (cushioning fiscal but blocking CPI relief).
- Pass-through is **less than 1:1 in nominal terms**: India taxes fuel heavily, so a $10 wholesale rise becomes a smaller retail rise. This dampens the pure mathematical elasticity.
- Buffer stocks matter: India's strategic petroleum reserve is small (~10 days import cover). It cannot cushion a multi-month shock.
- The FII channel is conditional on Fed stance: in a Fed-easing window, FII outflows are smaller; in a Fed-tightening window, the oil + USD shock compounds.

---

## Elasticity 2 — DXY → EM (BRIEF; expand on first use)

**Source shock:** DXY (broad dollar index) movement
**Destination:** EM equities, EM credit spreads, EM growth
**Channel:** Dollar debt servicing + financial conditions
**Framework tags:** `[Fed-EM transmission]`

| # | Source | Destination | Lag | Confidence |
|---|---|---|---|---|
| 2.1 | DXY +10% | MSCI EM equities −10 to −15% (USD terms) | 0-3 months | High |
| 2.2 | DXY +10% | EMBI sovereign spreads +50-80 bps | 1-3 months | High |
| 2.3 | DXY +10% | EM real GDP −0.3 to −0.5% over 1 year | 6-12 months | Moderate |
| 2.4 | DXY +10% | LatAm > Asia EM impact (LatAm has more USD debt) | concurrent | Moderate |

**Citations:** BIS Working Paper 615 (Avdjiev et al), IMF GFSR 2018 ch. 1, IIF Capital Flows Tracker.

To expand into a full worked example when first cross-border query involves USD-as-source.

---

## Elasticity 3 — Fed Funds → US 10y → Mortgage → Consumption (BRIEF; expand on first use)

**Framework tag:** `[Fed transmission mechanism]`

Approximate links:
- Fed funds +100 bps → 2y yield +60-80 bps within 3 months
- 2y +100 bps → 30y mortgage +50-70 bps
- Mortgage +100 bps → housing starts −10 to −15% (lag 6-9 months)
- Housing starts −10% → personal consumption −0.3 to −0.5% (lag 6-12 months)

To expand on first cross-border query involving Fed → US-domestic chain.

---

## Elasticity 4 — China Stimulus → Industrial Metals → Producer Equities (BRIEF; expand on first use)

**Framework tag:** `[heuristic — commodity demand channel]`

Approximate links:
- China credit impulse +1 std dev → Bloomberg Industrial Metals +15-25% over 6-12 months
- Iron ore +10% → BHP / Vale / Rio FCF +5-8% (next quarter)
- Copper +10% → Freeport / Antofagasta earnings +12-18% (next year)

To expand on first cross-border query involving China-as-source.

---

## Pending elasticities (to add as needed)

- **EU gas (TTF) → US LNG → US natgas** (the literal Europe→US chain from your example)
- **Tariff X% on Y product → US CPI category Z** (trade-war channel)
- **Yield-curve inversion → US recession (lag, base rate)**
- **Wage growth → core services CPI** (Phillips curve in low-slack regime)
- **VIX → SPX 1m return** (intraday/short-horizon)
- **Treasury supply duration → term premium**
- **JPY carry unwind → global risk-asset drawdown** (Aug-2024 archetype)

When using any of these channels, add the full entry above (with citations and lags) before completing the report.

---

## Format When Citing in a Report

Inline:

> "$10 Brent rise widens India CAD by ~0.4% of GDP within 1-2 quarters `[CAD identity]` (elasticity 1.1, source: RBI Annual Report)."

In the cross-border section table:

| Channel | Indicator | Current value | Elasticity used | Lag | Implied impulse | Framework |
|---|---|---|---|---|---|---|
| Energy import bill | Brent | $120 (+$40 vs base) | 1.1: $10 → +0.4% CAD | 1-2 Q | CAD +1.6% GDP | `[CAD identity]` |
| Imported inflation | Brent → CPI | $120 | 1.2: $10 → +35 bps | 4-6 mo | CPI +140 bps | `[USD pass-through]` |
| FX | INR | 88 | 1.3: $10 → 1.25% INR | 0-3 mo | INR to 92-93 | `[CAD identity]` |
| Capital flows | FII flows | $1.8L cr YTD outflow | 1.4 (Fed-conditional) | 0-2 mo | further $8-12bn outflow risk | `[Fed-EM transmission]` |
