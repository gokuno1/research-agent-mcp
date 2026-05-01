# Framework Glossary — v0.1

Persistent reference of named frameworks the agent must cite via `[framework-name]` tags in every analytical claim. Each entry has a fixed schema:

- **What it states** — the framework in one paragraph
- **Variables** — symbols and what each means
- **Why it must hold / why it works** — derivation or empirical basis
- **Worked example** — short numerical application
- **Common misuse** — how analysts get it wrong
- **Tag form** — exact string used inline (e.g., `[CAD identity]`)

When the agent uses a framework not yet in this file, it must add the entry in the same run.

---

## 1. CAD Identity (Current Account Decomposition)

**Tag form:** `[CAD identity]`

**What it states:** A country's current account balance is identically equal to the gap between its national saving and its national investment, and equivalently to the trade balance plus net income from abroad plus net transfers. Every cross-border flow analysis starts here because this identity must hold by construction — it is not a behavioural claim.

**Variables:**
- `CA` — current account balance (% of GDP)
- `S` — national saving (private + public) (% of GDP)
- `I` — gross domestic investment (% of GDP)
- `NX` — net exports (X − M) (% of GDP)
- `NI` — net income from abroad (% of GDP)
- `NT` — net transfers (% of GDP)

**Two equivalent forms:**

```
CA ≡ S − I                         (saving-investment form)
CA ≡ NX + NI + NT                  (trade-flow form)
```

**Why it must hold:** Both follow from the national income accounting identity `Y = C + I + G + NX` and the saving definition `S = Y − C − G`. There is no model assumption.

**Worked example (India, oil shock):**
- India imports ~85% of crude. Brent at $120/bbl vs $80 baseline implies an extra ~$50bn/yr import bill (~1.4% of GDP).
- That widens `M`, narrows `NX`, and (assuming `S − I` is sticky in the short run) the CAD must widen by approximately the same magnitude — driving the FX adjustment that follows.
- This is why "$10 Brent → ~0.4% CAD widening" is an *arithmetic* rule, not a forecast.

**Common misuse:**
- Treating CAD widening as the *cause* of FX depreciation, when both are joint outcomes of the same shock.
- Forgetting the saving-investment side: if private saving rises (oil shock dampens consumption), the CAD widens *less* than the trade-flow channel implies.
- Mixing flow (CA) with stock (NIIP, net international investment position).

---

## 2. Fed → EM Transmission Mechanism

**Tag form:** `[Fed-EM transmission]`

**What it states:** Tightening US monetary policy propagates to emerging markets through three reinforcing channels — USD strength, dollar-debt servicing burden, and risk-asset repricing — with quantifiable elasticities and predictable lags. The chain is `Fed funds ↑ → real US yields ↑ → DXY ↑ → EM FX ↓ + EM dollar-debt cost ↑ → EM credit spreads ↑ → EM growth ↓`.

**Variables:**
- `r*` — US real 10y yield (TIPS)
- `DXY` — broad dollar index
- `EMBI_OAS` — JPMorgan EMBI spread over Treasuries
- `EM_FX` — emerging-market currency index (e.g., MSCI EM FX)
- `dollar_debt_em` — EM external USD-denominated debt outstanding (% of EM GDP)

**Approximate empirical elasticities (from BIS, IMF, IIF research; medians, with wide confidence intervals):**

| Link | Elasticity | Lag |
|---|---|---|
| US 2y yield ↑ 100 bps | DXY +5-7% | 1-3 months |
| DXY ↑ 10% | EM equities −10-15% (USD terms) | 0-3 months |
| DXY ↑ 10% | EMBI spreads +50-80 bps | 1-3 months |
| EMBI spreads +100 bps | EM real GDP −0.5% over 1 year | 6-12 months |

**Worked example (2013 Taper Tantrum):**
- May 2013: Bernanke signals tapering. US 10y rises ~120 bps in 3 months.
- DXY rises ~5%, EM FX (esp. fragile-five: India, Indonesia, Brazil, South Africa, Turkey) falls 10-20%.
- India 10y rises ~150 bps; INR moves from 54 to 68 to USD.
- Lag: peak EM credit spread widening hits in Aug-Sep 2013, ~3 months after the verbal trigger.

**Common misuse:**
- Assuming the mechanism is symmetric — easing transmits more weakly than tightening (financial accelerator asymmetry).
- Ignoring EM-specific buffers: countries with high reserves (% of short-term external debt) absorb the shock; fragile balance sheets amplify it. Same DXY move ≠ same EM impact.
- Treating the channel as instantaneous — the slowest link (spread → growth) lags by a full year.

---

## 3. Sectoral Balances (Godley-Wynne)

**Tag form:** `[sectoral balances]`

**What it states:** In any closed accounting system, the financial balances of the three sectors — private (households + firms), public (government), and external (rest of world) — must sum to zero. This means a government deficit is mathematically *somebody else's* surplus. It is the most-violated "obvious" identity in macro commentary.

**Variables:**

```
(S − I) + (T − G) − CA ≡ 0
private surplus + public surplus − current account ≡ 0
```

Equivalently:
```
private surplus  =  public deficit  +  current account surplus
```

**Why it must hold:** Sum of all sectors' net financial assets in a closed system is zero. This is just double-entry accounting at the macro level.

**Worked example (US 2009-2014):**
- Public deficit averaged ~7% of GDP; current account averaged ~−3% of GDP.
- Therefore private surplus had to average ~+4% of GDP.
- Households were "deleveraging" — paying down debt — *because* the government was running large deficits and the current account was in deficit. Not despite it.
- Implication: had the government tried to "balance the budget" while the CA stayed in deficit, the private sector would have been *forced* into deficit (re-leveraging) — producing the deflationary trap that 1937 and 2010 austerity Europe demonstrate.

**Common misuse:**
- Treating "fiscal consolidation" as universally virtuous without checking which other sector is forced into deficit.
- Confusing stocks (debt levels) with flows (deficit per period). The identity is on flows.
- Forgetting the external sector — analysts who model only public + private inevitably get sign errors when CA is large.

**Why it matters for cross-border analysis:** A country with persistent current account surplus (Germany, China, Korea) is forcing either its government or its private sector to run a surplus too — externalising savings. When that surplus is recycled into a deficit country's bonds (Treasury, BTP, Gilt), capital-flow shocks land hardest on the deficit country when the recycling stops.

---

## 4. Real-vs-Nominal Distinction

**Tag form:** `[real-vs-nominal]`

**What it states:** Economic decisions and welfare depend on real (inflation-adjusted) variables, but most reported data, contracts, and headlines are in nominal terms. Confusing the two is the single most common error in macro/markets reasoning. A 5% nominal yield with 8% inflation is a *negative* real yield even though "rates went up."

**Variables:**
- `i` — nominal interest rate
- `π` — realised inflation (or `π_e` for expected)
- `r` — real interest rate
- Fisher: `i ≈ r + π_e` (exact: `(1 + i) = (1 + r)(1 + π_e)`)
- Real return on asset: `R_real ≈ R_nominal − π`
- Real GDP growth ≠ nominal GDP growth; nominal includes the inflation deflator

**Why it matters:**
- Investment decisions: real returns determine capital allocation; a 12% nominal yield in Argentina with 50% inflation is destroying capital in real terms.
- Wage bargaining: if nominal wages rise 4% with 7% CPI, workers lost 3% of real purchasing power even though their pay "went up."
- Asset prices: a long-duration equity priced off nominal earnings looks cheaper than it is when those earnings are inflating but real cash flow is flat ("nominal earnings illusion").
- Cross-country comparison: comparing nominal yields across countries with different inflation rates is meaningless; compare real yields.

**Worked example (1970s US equities):**
- Nominal S&P 500 essentially flat from 1968 to 1982 (~14 years).
- CPI rose ~180% over the same period.
- *Real* S&P drawdown was ~−65%, comparable to 1929-1932.
- The "nominal flat" hid a generational equity bear market — visible only when reframed in real terms.

**Common misuse:**
- "Rates are high" — without specifying real or nominal, this is ambiguous.
- "The market is at all-time highs" — usually meant nominal, often false in real terms.
- "Wages are rising" — meaningful only against contemporaneous inflation.
- Comparing 1970s S&P returns to 2020s S&P returns without deflating both.

---

## 5. DuPont Decomposition

**Tag form:** `[DuPont]`

**What it states:** Return on equity is the product of three operational levers — net profit margin, asset turnover, and financial leverage. Decomposing ROE this way reveals *where* a firm's profitability comes from and which lever is fragile to macro shocks. It is the bridge between micro fundamentals and macro impact analysis.

**Variables:**

```
ROE = (Net Income / Sales) × (Sales / Assets) × (Assets / Equity)
ROE =      NPM           ×       ATO         ×    Leverage
```

- `NPM` — net profit margin (operating efficiency, pricing power)
- `ATO` — asset turnover (capital efficiency)
- `Leverage` — assets-to-equity multiple

**Why it works:** Algebraic identity — sales cancel between first and second terms, assets cancel between second and third. Every firm's ROE *must* decompose this way; the question is which lever does the work.

**Worked example (oil shock, India auto sector):**
- Maruti Suzuki: NPM dominant (~7%), ATO moderate (~1.4x), Leverage low (~1.5x). NPM is squeezed by raw-material costs (steel, aluminium, plastics), so an oil shock that lifts commodity prices compresses NPM and the whole ROE.
- HDFC Bank: NPM very high (~25%), ATO low (~0.1x), Leverage very high (~7x). The leverage lever does the work; an oil shock matters only if it triggers credit losses (raising NPM-via-provisions).
- Reliance: blended (refining + retail + telecom). Refining segment's NPM *expands* in an oil shock as crack spreads widen; retail/telecom NPM compresses. Net effect depends on segment mix — the framework forces the analyst to disaggregate.

**Common misuse:**
- Comparing ROEs across sectors without decomposing — a 20% bank ROE and a 20% software ROE come from completely different levers and have completely different macro fragility.
- Treating high leverage as automatically risky without checking what `NPM × ATO` (return on assets, ROA) is. A 1% ROA × 20x leverage (a typical bank) is fine; a 1% ROA × 5x leverage (a stretched industrial) is not.
- Static analysis — DuPont evolves over the cycle. Track it in three time slices (last cycle peak, last cycle trough, current) before concluding anything.

**Why it matters for this skill:** When the cross-border layer hands a macro shock to the micro layer, DuPont is the channel through which "macro pressure" becomes "stock-specific impact." The shock hits one of the three levers; identifying which lever distinguishes winners from losers within the same sector.

---

## Pending entries (to add as needed)

The following are commonly-cited but not yet in v0.1. Add full entries when first used:

- Minsky financial-instability hypothesis (`[Minsky]`)
- Reflexivity (Soros) (`[reflexivity]`)
- Capital cycle (Marathon) (`[capital cycle]`)
- Porter's five forces (`[Porter-5F]`)
- Fed transmission mechanism — domestic version (`[Fed transmission mechanism]`)
- USD pass-through to imported inflation (`[USD pass-through]`)
- Financial accelerator (Bernanke-Gertler) (`[financial accelerator]`)
- Anchoring bias (`[anchoring]`)
- Herding / informational cascade (`[herding]`)
- Order-book imbalance (`[OBI]`)
- VPIN flow toxicity (`[VPIN]`)

When using any of these tags, add the full entry above before saving the report.
