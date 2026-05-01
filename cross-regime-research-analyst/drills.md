# Drill Scenarios — v0.3 (Synthetic / Parameter-Driven)

Graded practice scenarios for multi-regime exposure. **All drill prompts are synthetic and parameter-driven** — no country names, no dates, no real-world anchors. This forces first-principles reasoning from frameworks and elasticities, not pattern-matching to a remembered story.

After the user answers and is graded, an **optional Historical Comparable** section reveals which real-world episode most closely resembles the synthetic scenario and identifies the dimensions where the actual outcome diverged from the pure-framework prediction. This is exposure to history *as reality-check*, not as anchor.

---

## Authoring Principles

1. **Parameters over stories.** Every drill specifies the regime via numerical/structural parameters: import dependency %, FX reserves cover, currency regime (fixed/managed/float), debt composition, sectoral mix. No "country X has been through Y crisis" framing in the prompt.
2. **Counterfactual-friendly.** The same parameters can be re-rolled to test edge cases that never happened in real history (e.g., "what if 1991 India had floating exchange rate?"). This stress-tests the user's mechanism understanding.
3. **Graded on reasoning, not prediction.** The user is right or wrong about *the chain* (frameworks applied correctly, elasticities used appropriately), not about the eventual price target. Synthetic scenarios don't have ground-truth outcomes — they have ground-truth *reasoning paths*.
4. **History as appendix, not prompt.** Real historical episodes appear *after* grading, as a comparison set. The user sees both their framework-derived answer and how reality diverged — and that divergence is itself a lesson (it shows the limits of pure first-principles thinking).

---

## Grading Rubric (5 dimensions × 1-5 points = 25 max)

Same rubric across all drills. Score each dimension 1-5 with one-line justification.

| Dimension | What to look for | 1 (poor) | 3 (adequate) | 5 (strong) |
|---|---|---|---|---|
| **D1. Transmission-chain completeness** | All major channels (trade, FX, banking, commodity, sentiment, policy) identified given the parameters | One channel only | 2-3 channels | All relevant channels with second-order links |
| **D2. Quantified elasticities** | Each link includes a number and a lag, derived from `elasticities.md` or first principles | No numbers | Some numbers, vague lags | Every link has a number + lag with explicit confidence |
| **D3. Framework citations** | User names the frameworks they applied | None | 1-2 named | 3+ named with correct application |
| **D4. Counter-signals / contradictions** | What could invalidate the chain? Which parameter would flip the outcome? | None | One contradiction noted | 2+ contradictions with specific invalidation triggers |
| **D5. Time-horizon clarity** | Distinguishes near-term (0-3m), medium-term (3-12m), structural (1-3y) | One horizon | 2 horizons | All three horizons with what plays out in each |

**Scoring guide:** 22-25 expert, 17-21 solid, 12-16 directionally correct, 7-11 significant gaps, ≤6 re-do. After grading, identify the user's lowest-scoring dimension and recommend a drill targeting it.

---

## Drill 1 — Closed-Corridor Energy Supply Shock

**Archetype:** Geopolitical war / supply shock with cross-border spillover
**Difficulty:** Medium
**Tests:** CAD identity, USD pass-through, energy substitution, fiscal pass-through, multi-channel transmission

### Prompt

> **Country A** has the following parameters:
> - GDP $4 trillion, growing 6.5%
> - Imports 75% of crude oil
> - Of that, 60% transits through a single shipping corridor (call it Corridor X)
> - Strategic petroleum reserve covers 10 days of imports
> - Currency: floats freely; current account deficit running 1% of GDP
> - FX reserves: 9 months of imports (~$650bn)
> - Banking sector: well-capitalized, asset quality at multi-year highs
> - Central bank: at neutral monetary stance, repo rate at 5%, 3% inflation
> - Fiscal: capex 4% of GDP, mildly expansionary
> - Reserve-currency country (call it Country B) is the dominant pricing currency for crude
>
> **Shock event (T=0):** Corridor X is closed by military action. The closure is expected to last "indefinitely." Crude oil price (in B's currency) spikes 50% from $80 to $120/bbl within 30 days. Country B's central bank holds policy rate steady at 4% (restrictive given B's 3% inflation), with hawkish dissent on the committee.
>
> **Your task:** Build the full transmission chain showing what happens to Country A over the next 12 months. Address all 5 grading dimensions. Identify which sectors of A's economy benefit, which are hurt, and over what time horizon. Identify the 2-3 parameters that, if different, would most change your answer.

### Canonical Answer (DO NOT show until user has attempted)

**Channel set (all should appear in user's answer):**

1. **Energy import bill → CAD widening** `[CAD identity]`
   - $40/bbl × A's crude consumption × 75% imported = ~$50bn additional annual import bill
   - That's ~1.25% of A's GDP → CAD widens from −1% to ~−2.25% of GDP
   - Lag: 1-2 quarters as bills settle

2. **CAD widening → currency depreciation** `[CAD identity]`
   - Approximate elasticity: 1% additional CAD ≈ 3-5% currency depreciation in flexible-FX regime
   - Implied A's currency depreciates 4-6% vs B's currency on the oil channel alone
   - Lag: concurrent (FX adjusts within weeks)

3. **Currency depreciation → imported inflation** `[USD pass-through]`
   - 5% depreciation adds ~35 bps to A's CPI when layered on energy shock
   - Direct fuel pass-through: $40 Brent → 30-40 bps headline CPI per $10 = +120-160 bps
   - Combined: A's CPI rises from 3% to ~4.5-5% over 4-6 months
   - Lag: 2-3 months direct fuel; 4-6 months full

4. **Reserve-currency hawkish hold → capital outflow amplification** `[Fed-EM transmission]`
   - With B's central bank holding restrictive, capital flows toward B's assets, away from A
   - Pure-oil channel implies depreciation 4-6%; observed depreciation likely 7-10% as Fed-EM channel amplifies
   - Lag: 0-3 months; reflexive (more outflow → more depreciation → more outflow until something breaks the loop)

5. **Inflation rising → central bank reaction** `[heuristic — central bank reaction function]`
   - A's central bank pauses any easing; if CPI breaches 4.5%, hike risk emerges
   - Rate-sensitive sectors compress; banking NIMs cap (cannot expand into rising-rate environment if loan growth stalls)
   - Lag: 1-2 quarters

6. **Crude → fiscal subsidy load** `[heuristic — fiscal pass-through]`
   - Most countries subsidize transport fuel and cooking gas to some degree
   - $40 Brent → ~₹15-20k Cr (or local equivalent) per $10 → +₹60-80k Cr fiscal pressure (~0.2% GDP)
   - Either subsidies absorb the shock (deficit widens) or are passed through to consumers (CPI rises faster)
   - Lag: 2-3 quarters

**Sector winners (A):**
- Domestic crude producers (if any) — pure realization windfall, no oil-import exposure
- Refiners with complex configurations — refining margin (crack spread) typically widens during oil supply shocks
- Defence/security — geopolitical re-rating
- Domestic capex/infrastructure — government spending counter-cyclical, immune to oil shock
- Pharma exporters / IT exporters — currency weakness boosts USD revenue translation
- Energy-security plays — coal, nuclear, renewables (substitution demand)

**Sector losers (A):**
- Aviation — jet fuel is largest variable cost; fare-elasticity prevents pass-through
- Energy-intensive manufacturers (paints, chemicals, fertiliser) — input cost compression
- Consumer discretionary — real income squeeze from CPI
- Importers of crude derivatives (TiO2, plastics, lubricants) — input cost amplified by FX

**Frameworks invoked:**
- `[CAD identity]` — CAD widening from oil shock
- `[USD pass-through]` — imported inflation channel
- `[Fed-EM transmission]` — capital flow amplification
- `[real-vs-nominal]` — distinguishing nominal CPI rise from real-income compression
- `[sectoral balances]` — government deficit funds private sector amid external drain
- `[heuristic — central bank reaction function]`
- `[heuristic — fiscal pass-through]`

**Counter-signals (which parameters would flip the answer):**
- If A had **fixed** exchange rate instead of float → no FX shock-absorber → currency crisis becomes the binding constraint, FX reserves drain rapidly
- If A's **FX reserves were 2 months instead of 9** → BoP crisis materializes; no buffer to absorb sustained outflows
- If A's **banking sector was stressed** → credit channel transmits the shock, multiplier effect 2-3×
- If B's central bank were **dovish** instead of hawkish → no Fed-EM amplification → currency channel less severe by half
- If corridor closure proves **short (< 30 days)** → no full pass-through; oil reverts before CPI absorbs

**Time horizons:**
- **Near-term (0-3 months):** FX collapse, equity volatility, headline news cycle dominates. CPI hasn't yet shown the pass-through.
- **Medium-term (3-12 months):** CPI rises, central-bank reaction crystallizes, fiscal subsidy bills visible, sector dispersion widens. Sector winners outperform losers by 30-50%.
- **Structural (1-3 years):** Energy-security policy responses (SPR expansion, supplier diversification, alternative-energy investment), permanent shift in sourcing patterns. Defence spending re-rates structurally.

### Optional Historical Comparable (show only after grading)

This synthetic scenario most closely resembles **two real episodes**, with different outcomes — the comparison itself teaches the limits of single-analogue reasoning:

| Real episode | Match dimensions | Differential vs synthetic | Outcome divergence from framework prediction |
|---|---|---|---|
| **2022 Europe gas crisis** | Geopolitical-war shock to a single-corridor energy supply | Europe's currency was the *reserve* currency (so no Fed-EM amplification on it); inflation was already running hot pre-shock | The framework's "+120-160 bps CPI" *underestimated* — Europe got +700 bps because pre-shock momentum compounded |
| **2026 Iran war / Hormuz blockade (India)** | Same shock structure, India as Country A | India's banking system genuinely is at multi-year asset-quality highs; FX reserves at 9-10 months cover | Framework prediction of +120-160 bps CPI within 6 months *to be tested* on May 12 print; INR depreciation has run *ahead* of pure-oil channel due to Fed amplification (matches framework prediction) |

**Lesson on framework limits:** the synthetic chain is correct on the *direction* and *channels* but the magnitude depends critically on the pre-shock starting point (which the parameters specify) and the path-dependent dynamics (which they don't capture). First-principles reasoning gets you 70% of the way; the missing 30% is the path-dependency that only historical observation reveals.

---

## Drill 2 — Reserve-Currency Tightening into a Vulnerable EM

**Archetype:** Monetary tightening with cross-border (reserve-currency → EM) spillover
**Difficulty:** Medium-hard
**Tests:** Fed-EM transmission, dollar-debt channel, currency-regime sensitivity, EM resilience indicators

### Prompt

> **Country B** is the issuer of the world's dominant reserve currency. Its central bank shifts from QE to QT, raises policy rate by 250 bps over 18 months, and signals further hikes if inflation doesn't return to its 2% target. The currency index (DXY equivalent) rises from baseline 95 to 110 (a 15.8% appreciation) over the same period.
>
> **Country A** is an emerging market with these parameters:
> - GDP $1.2 trillion, growing 5.5%
> - Currency: managed float (central bank intervenes occasionally)
> - Current account deficit: 4% of GDP (large, financed by FII flows)
> - FX reserves: 7 months of imports
> - External debt: 22% of GDP, of which 60% is USD-denominated; 40% short-term (matures within 12 months)
> - Banking sector: 14% NPLs in corporate loan book; capital adequacy meeting minimum
> - Inflation: 7% headline, 5% core
> - Central bank policy rate: 8% (was on easing trajectory before B's tightening began)
>
> **Your task:** Build the full transmission chain showing what happens to Country A over 12 months. Specifically: (1) what happens to A's currency, (2) what happens to A's sovereign credit spread, (3) what happens to A's banking system, (4) what happens to A's growth, (5) which sectors win/lose. Identify which 2-3 of A's parameters most determine whether this becomes a manageable adjustment or a crisis.

### Canonical Answer

*To be drafted on first user attempt. Skeleton: Fed-EM transmission three-channel attack — DXY ↑ → A's FX ↓ → USD debt servicing burden ↑ → corporate stress → banking stress (already vulnerable) → credit contraction → growth collapse → either IMF program or crisis. The 14% NPL parameter and 60% USD debt parameter are the binding fragility constraints. Differential outcomes: a country with 4-5% reserves and 30% USD debt absorbs (Mexico 2018); a country with 2-3 month reserves and 70% USD debt defaults (Argentina 2018). The currency-regime parameter — if A had floating instead of managed — adjusts faster, less deep but more volatile.*

### Optional Historical Comparable (after grading)

| Real episode | Match dimensions | Differential | Outcome divergence |
|---|---|---|---|
| **2013 Taper Tantrum (India)** | Reserve-currency tightening trigger, EM CAD widening | India's NPL situation in 2013 was *worse* than in synthetic (corporate balance sheet repair was just beginning) | Framework predicts ~50-80 bps EM spread widening; actual India 10y rose 150 bps before stabilising. Rajan-as-Governor confidence boost was a *non-framework* (institutional) factor that capped the damage. |
| **2018 Turkey** | Reserve-currency tightening + same vulnerability profile | Turkey had political central-bank-independence concerns layered on | Framework's "manageable adjustment" became "deep crisis" because of the institutional overlay — first-principles framework cannot capture this. |
| **2018 Argentina** | Same plus IMF history | Same | Even worse outcome — illustrates that small-buffer EMs in tightening cycles default more often than the framework's median elasticity predicts |

---

## Drill 3 — Industrial-Demand Collapse from Largest Buyer

**Archetype:** Demand shock with cross-border (commodity demand → producer economies) spillover
**Difficulty:** Medium
**Tests:** commodity demand elasticities, terms-of-trade channel, currency response in commodity exporters, sector concentration risk

### Prompt

> **Commodity X** has the following structure:
> - Single largest buyer (Country C) accounts for 65% of global demand
> - Top three producers (Countries D, E, F) collectively supply 60% of global production
> - Producer countries are highly concentrated in a single industry (commodity X is 12-18% of their GDP, 30-50% of their export receipts)
> - Spot price baseline: $130 per unit
>
> **Shock event:** Country C's domestic property and construction sector enters multi-year deleveraging. Construction starts fall 50% YoY for 18 months. C's credit impulse moves from +5% to −2%. C does not reverse with stimulus (assume political/structural reasons prevent it).
>
> **Your task:** Over 12-24 months, what happens to:
> 1. Commodity X's price
> 2. The mining-equity earnings of producer countries D, E, F
> 3. The currencies of D, E, F
> 4. The terms of trade and fiscal balance of countries D, E, F
> 5. Second-order: what happens to other commodities and other emerging markets
>
> Identify which parameter (concentration, % of GDP, fiscal dependence, alternative buyers) most determines whether each producer country adapts smoothly or has a domestic crisis.

### Canonical Answer

*To be drafted on first user attempt. Skeleton: commodity X price down 30-40% (demand elasticity), producer earnings down 40-60% (operating leverage), producer currencies down 15-25% (terms-of-trade channel), fiscal balance deteriorates by 1-3% of GDP per producer (royalty/tax base shrinks), second-order = correlated commodities (other industrial metals) down 15-25%; commodity-importing EMs benefit asymmetrically. Differential parameter that matters most: % of GDP exposure — a 5% exposure economy adapts; a 30% exposure economy faces structural recession.*

### Optional Historical Comparable

*To populate. Match: 2014-16 China property slowdown impact on iron ore (Australia/Brazil), copper (Chile/Peru). Differential: Australia diversified faster than Brazil; Chile had fiscal cushion; difference was state strength, not commodity exposure.*

---

## Drill 4 — Pattern-Recognition from Indicator Dashboard

**Archetype:** Variable — user must identify
**Difficulty:** Hard
**Tests:** archetype recognition, parameter sensitivity, framework selection

### Prompt

> You're given the following indicator dashboard for **Country A** (no name, no date disclosed):
>
> - GDP growth: 5.6% (last full year), 1.1% projected current year
> - Inflation: 13% and rising
> - Oil import dependency: ~70%; oil price has risen 80% in past 6 months
> - FX reserves: covers <2 weeks of imports
> - Currency: officially fixed; black-market discount widening to 15-20%
> - Sovereign credit: just downgraded to junk; international borrowing access closed
> - Workers' remittances from a key source region: collapsed 60% due to a regional war
> - Banking system: state-owned, low transparency, no overt stress yet
> - Manufacturing PMI: 41 (deep contraction)
> - Stock market: −35% from peak in local currency
>
> **Tasks:**
> 1. **Classify the archetype** (which of the 8 in `archetypes.md`). Justify with at least 3 indicators.
> 2. **Predict the policy response** in the next 6 months. What does A's government do? What does A's central bank do? What external help does A seek?
> 3. **Build the transmission chain** explaining how A's economy gets here from the listed parameters.
> 4. **Predict the structural-reform package** that follows the crisis (if any).
> 5. **Predict the post-crisis sector winners** over a 1-3 year horizon.
> 6. **Identify which 2-3 indicators most distinguish this from a "normal recession"** vs a "balance-of-payments crisis."

### Canonical Answer

*Archetype: EM external collapse / BoP crisis (Archetype 6). Policy response: forced devaluation, IMF/multilateral program, capital controls, structural-reform commitments, fiscal consolidation conditional on aid. Structural reforms typically follow: trade liberalization, currency convertibility, financial-sector reform, industrial delicensing, tax reform. Post-crisis winners: export-oriented sectors (IT, pharma, textiles), private banks (filling state-bank capacity), beneficiaries of liberalization (telecom, aviation, retail). Distinguishing indicators vs normal recession: FX reserves cover (the binding constraint), fixed-exchange-rate regime (which prevents shock absorption), external-borrowing access (which determines whether default is on the table).*

### Optional Historical Comparable

| Real episode | Match | Differential | Lesson |
|---|---|---|---|
| **1991 India BoP** | All parameters match closely | India's banking system was state-owned but Government of India backed; sovereign was always going to be supported by structural reform | Framework prediction of "structural reform follows" played out almost exactly — 1991 reforms (currency convertibility, trade liberalization, industrial delicensing, IT liberalization) created the next 30 years of Indian growth |
| **1994 Mexico (Tequila Crisis)** | Similar BoP profile, USD-pegged peso | Different trigger (political assassination + capital flight); larger US backstop | Framework predicts "manageable adjustment with IMF help"; actual outcome much worse short-term but recovery faster than India's |
| **2018 Argentina** | Similar BoP profile | Pre-existing institutional fragility, prior IMF history | Framework's "structural reform → growth" outcome did NOT materialize; institutional context overrode parameter prediction |

**Meta-lesson:** the same parameter-set can resolve into very different outcomes depending on factors the parameters don't capture (political institutions, central-bank independence, prior crisis history, geopolitical backing). This is the limit of pure first-principles framework reasoning.

---

## Drill 5 — Banking Deleveraging Cascade

**Archetype:** Banking / credit crisis
**Difficulty:** Hard
**Tests:** financial-accelerator, contagion mechanics, central-bank lender-of-last-resort response, second-order effects across asset classes

### Prompt

> The five largest banks in **Country A** (a developed economy with reserve-currency status) jointly announce that their commercial real estate and leveraged-loan portfolios contain undisclosed losses equal to **8% of their loan books**. The interbank lending market freezes within 48 hours.
>
> Country A's parameters:
> - Banking sector total assets: 130% of GDP
> - Banking sector market capitalization at announcement: $2.5 trillion (S&P Banks-equivalent)
> - Central bank policy rate: 4%; balance sheet was in QT mode
> - Government debt: 105% of GDP, fiscal deficit 6% of GDP (limited fiscal headroom)
> - Yield curve: 3m4y 50 bps (positive but flattening)
> - Inflation: 2.5% headline, on target
> - Stock market just hit ATH 4 weeks before announcement
>
> **Tasks:** Build the chain of effects over the next 6 months across:
> 1. Banking equity prices (within sector)
> 2. Sovereign yields (10y, 2y)
> 3. Investment-grade and high-yield credit spreads
> 4. Currency vs other reserve currencies
> 5. Other asset classes: gold, oil, EM equities, USD-denominated EM debt
> 6. Real economy: credit growth, employment, GDP
> 7. Central-bank policy response (sequencing matters)
>
> Identify which 2-3 parameters would change the outcome from "contained" to "systemic." Identify counter-signals to the bear thesis.

### Canonical Answer

*To be drafted on first user attempt. Skeleton: banking equity −40-60% within weeks, 2y yields collapse 150-200 bps in flight to safety, IG spreads widen 50-100 bps, HY spreads widen 300-500 bps, currency initially weakens then strengthens as flight-to-safety bid emerges, gold rallies 10-15%, oil falls 20-30% on demand-destruction fears, EM equities -15-25% in USD terms. Real economy: credit growth turns negative, employment lags 6-9 months, GDP enters recession within 2-3 quarters unless central bank acts decisively. Central bank response sequence: (1) emergency liquidity facilities within 72 hours, (2) policy rate cuts within 2-4 weeks, (3) restart QE within 1-3 months, (4) coordinated international response if FX channels open up. Differential parameters: if banking sector were 200% of GDP (Eurozone), contained becomes systemic; if government debt were 60% of GDP (room for bailout), contained outcome more likely; if reserve-currency status held (USD), recovery faster than non-reserve. Counter-signals: deposit-insurance limits depositor panic, OW resolution authorities exist post-2008, central banks have explicit lender-of-last-resort tools.*

### Optional Historical Comparable

*To populate. Match: 2008 GFC (US), 2010-12 Eurozone (Italy/Spain), Mar-2023 SVB/CS (contained). Differential: 2008 was largest, Eurozone was slowest-resolved, 2023 was fastest-contained. Lesson: speed of policy response is the single biggest determinant of outcome severity, and that variable is institutional, not parametric.*

---

## Drill 6 — Trade-War Escalation

**Archetype:** Trade war
**Difficulty:** Medium
**Tests:** tariff incidence, supply-chain reorganization, retaliation game theory, third-country spillovers

### Prompt

> **Country A** (the world's largest economy by GDP) imposes a **30% tariff** on manufactured goods imported from **Country B** (the world's second-largest economy and largest manufacturer). The targeted goods represent **18% of A's total imports** and span consumer electronics, machinery, and textiles.
>
> Country B retaliates with **25% tariffs** on agricultural exports from A (12% of B's imports). Negotiations break down. Both sides escalate to broader product coverage over 6 months.
>
> **Your task:** Over 12-24 months, what happens to:
> 1. Goods prices in A and B
> 2. CPI in A and B
> 3. Currency exchange rates (A vs B, A vs third-country currencies)
> 4. Sector winners and losers within A
> 5. Sector winners and losers within B
> 6. Third-country effects: which beneficiary EMs absorb redirected supply chains? Which lose?
> 7. Long-run effects on global trade architecture
>
> Identify which parameter most determines whether this stays a bilateral spat or becomes a global trade-system breakdown.

### Canonical Answer

*To be drafted on first user attempt. Skeleton: A's CPI rises 30-80 bps (import substitution and pass-through), B's CPI relatively unaffected initially (excess capacity absorbs domestic demand). Currency: B's currency depreciates 5-10% (offsetting half the tariff effectively), A's currency strengthens (capital flow channel) then weakens (growth concerns). A's sector winners: domestic manufacturers in tariff-protected categories, alternative suppliers from third countries. A's sector losers: importers, retailers (margin compression), tech firms with B-based supply chains. B's sector losers: export-dependent manufacturers; winners: import-substituting domestic firms. Third-country beneficiaries: Vietnam, Mexico, India absorbing redirected supply chains for low-cost manufacturing; Brazil, Argentina absorbing redirected agricultural demand. Determining parameter: WTO/multilateral institutional credibility — if the WTO mediates and dispute resolution holds, contained; if dispute resolution mechanism is bypassed, system breakdown.*

### Optional Historical Comparable

*To populate. Match: 2018-19 US-China trade war. Differential: 2018-19 retaliation was symmetric early, then asymmetric; trade war eventually settled into "managed decoupling" not full breakdown. Lesson: the framework predicts equilibrium effects but trade wars are political processes, and political resolution is path-dependent and not predictable from parameters alone.*

---

## Pending Drills (to add as needed)

The agent should add fully-fleshed canonical answers for Drills 2, 3, 5, 6 the first time a user attempts them, before grading. New drills should target archetypes the user has practised least.

Suggested future drills:
- **Yield-curve inversion → recession** (synthetic version of US 2007 / 2019)
- **Hyperinflation in commodity exporter** (synthetic version of Argentina, Venezuela, Zimbabwe)
- **Sovereign debt restructuring** (synthetic version of Greece 2012, Argentina 2001/2020)
- **Asset-bubble collapse with no banking transmission** (synthetic version of dot-com 2000)
- **Fast carry-trade unwind** (synthetic version of JPY August 2024)
- **Stagflation in a developed economy** (synthetic version of US 1970s — testing whether the user can reason about this archetype without modern Fed reaction-function assumptions)

Each new drill should follow the same structure: parameter-driven prompt (no anchor), canonical answer derived from frameworks + elasticities, optional historical comparable appendix that surfaces the divergence between framework prediction and actual outcome.

---

## Why this format works for *learning*

1. **Prompt has no story-shortcut.** You cannot answer "well in 2022 they did X" because the prompt doesn't tell you it's 2022.
2. **Forces parameter sensitivity.** Each parameter has a role — testing whether the user understands what would change if it changed.
3. **Counterfactuals are first-class.** "What if A had floating exchange rate?" is a legitimate variation, not a trick question.
4. **Historical exposure as reality-check.** After your answer is graded, you see how reality played out — and where your framework-pure prediction was right or wrong. The divergence is itself the lesson (it shows the limits of pure first-principles thinking).
5. **Compounds with frameworks.md.** Every drill exercise drives the user back to the framework glossary — those are the tools, the drill is the workshop.
