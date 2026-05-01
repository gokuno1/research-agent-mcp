# Regime Archetypes — v0.3

Eight regime archetypes spanning the macro state space. Each archetype is a *type* — multiple historical regimes share an archetype.

Used by:
1. **Phase 4a (always-on archetype classification)** in report mode — the report names the archetype and cites this file's base-rate context
2. **Drill mode** — scenarios are picked across archetypes to ensure full state-space exposure
3. **Executive summary** — every report names the archetype in the header

For each archetype, this file defines:
- Macro signature (what the 12 features look like)
- **Base-rate statistics** (incidence, duration, drawdown, dispersion, modal resolution path) — cited in Section 4a of every report
- Sector winners/losers with rough beta to growth and beta to inflation
- Common analyst errors
- Canonical historical examples (used as input to `regimes.md` catalog, NOT cited in Section 4a)

**Base-rate caveats:**
- All statistics are *approximate medians* drawn from observed instances since ~1970 (developed markets) or ~1990 (broad EM coverage)
- Tails are wide — these are central tendencies, not point predictions
- Sample sizes are small (most archetypes have 3-8 instances in modern data); treat base rates as *priors* to update, not as forecasts
- Equity drawdowns are stated in *real* terms (inflation-adjusted) where available, *nominal* otherwise — flagged per archetype

---

## Archetype 1 — Goldilocks

**Signature:** Moderate growth (2-3.5%), falling/stable inflation (<3%), accommodative-but-not-easy policy, low credit spreads, low FX vol, strong risk appetite.

**Base-rate statistics (modern era, US-anchored):**

| Stat | Value | Notes |
|---|---|---|
| Incidence | ~2-3 occurrences per decade | Most-common regime in modern data |
| Median duration | 24-48 months | Tail can extend to 5+ years (1995-2000) |
| Median equity return (annualised) | +12-18% nominal, +9-15% real | Strong risk-asset regime |
| Sector dispersion | Low (winner-loser spread ~10-20%) | Broad-based participation |
| Modal resolution path | (a) inflation surprises upward → policy tightens → regime ends; (b) growth scare from external shock; (c) asset bubble forms → bursts |
| Sample size | ~6-8 modern instances | 1995-99, 2003-06, 2017, 2024-early |

**Winners:** High-multiple growth (tech, software), consumer discretionary, banks (curve steepening), cyclicals.

**Losers:** Defensive staples (laggards), gold (no fear bid), volatility products.

**Common analyst errors:**
- Extrapolating the regime indefinitely (1990s, 2017, 2024)
- Assuming any rise in inflation is transient
- Underweighting tail-risk hedges because vol is cheap

**Canonical examples:** US 1995-1999, US 2017, US 2024 (early).

---

## Archetype 2 — Reflation

**Signature:** Accelerating growth, rising-but-moderate inflation, fiscal/monetary stimulus active, curve steepening, weakening USD, EM tailwind.

**Base-rate statistics:**

| Stat | Value | Notes |
|---|---|---|
| Incidence | ~2-3 per decade | Often follows recession or growth scare |
| Median duration | 12-24 months | Shorter than Goldilocks; transitions to either continued expansion or stagflation |
| Median equity return (annualised) | +15-25% nominal | Cyclicals lead; small-caps outperform |
| Sector dispersion | High (winner-loser spread ~30-40%) | Cyclical leadership very pronounced |
| Modal resolution path | (a) capacity tightens → wage pressure → regime morphs into stagflation; (b) Fed leans against → growth slows; (c) external shock disrupts |
| Sample size | ~5-7 modern instances | 1983-84, 2003-06, 2009-10, 2020Q4-21Q2 |

**Winners:** Cyclicals (industrials, materials, energy), EM equities, commodities, banks (NIM expansion + low credit losses), small caps.

**Losers:** Long-duration bonds, defensives, USD assets in USD terms.

**Common analyst errors:**
- Mistaking reflation for stagflation when first-derivative inflation looks scary
- Selling cyclicals too early on "valuation" before the earnings cycle has played out

**Canonical examples:** US 2003-2006, US 2020-Q4 to 2021-Q2, post-2009 early recovery.

---

## Archetype 3 — Stagflation

**Signature:** Slowing growth, persistent/accelerating inflation, policy dilemma, real yields rising, USD strong, equity multiples compressing, gold strong.

**Base-rate statistics:**

| Stat | Value | Notes |
|---|---|---|
| Incidence | ~1 per 2 decades (developed); rare modern | 1970s defined the archetype; 2022 was a partial revival |
| Median duration | 18-36 months acute; long tails | 1970s lasted ~10 years cumulative across multiple shocks |
| Median equity return | −15% to −30% real | Nominal returns can be flat-to-positive (1970s S&P nominal flat, real −65%) — `[real-vs-nominal]` |
| Sector dispersion | Extreme (winner-loser spread can exceed 60%) | Energy/gold +30-50%; long-duration −30-40% |
| Modal resolution path | (a) policy capitulation (Volcker-style brutal tightening induces recession to break inflation); (b) supply normalization (commodity prices fall); (c) productivity shock (rare) |
| Sample size | ~3-4 modern instances | 1973-75, 1978-82, briefly 2022 |

**Winners:** Energy producers, gold/precious metals, defence, value stocks with pricing power, real assets.

**Losers:** Long-duration tech, consumer discretionary, fixed-rate bonds, leveraged growth.

**Common analyst errors:**
- Buying the dip on long-duration tech (multiples keep compressing)
- Treating commodity producer rallies as "late cycle" when they're early in a regime
- Underestimating how long inflation can stay sticky
- Looking at *nominal* equity returns and concluding stagflation isn't that bad — the damage shows up only in real terms `[real-vs-nominal]`

**Canonical examples:** 1973-1975, 1979-1982 (transitioning), 2022 (acute phase).

---

## Archetype 4 — Disinflationary Boom

**Signature:** Strong growth, falling inflation (productivity-driven, not demand-destroyed), real yields stable-to-falling, equity multiples expanding.

**Base-rate statistics:**

| Stat | Value | Notes |
|---|---|---|
| Incidence | ~1 per 2-3 decades | Rarest of the bullish regimes |
| Median duration | 36-60 months | Long when it occurs (1990s lasted nearly a decade) |
| Median equity return (annualised) | +18-25% nominal | Multiple expansion adds to earnings growth |
| Sector dispersion | Low-medium | Most sectors participate; productivity beneficiaries lead |
| Modal resolution path | (a) productivity shock fades → reverts to Goldilocks; (b) asset bubble forms → bursts; (c) inflation re-accelerates from external shock |
| Sample size | ~2 clean modern instances | US late 1990s; arguably US 2010-2019 (slow version); post-2023 debated |

**Winners:** Productivity-leveraged sectors (tech, software, capital-light services), banks (good credit + steepening), cyclicals.

**Losers:** Few absolute losers; relative laggards are inflation-hedge plays.

**Common analyst errors:**
- Calling it stagflation when growth is decelerating from 5% to 3% (still strong)
- Assuming productivity will persist (it usually doesn't)
- Confusing this with bubble (the regime is genuine; the bubble forms within it but isn't the regime itself)

**Canonical examples:** US late 1990s, post-2023 US (debated).

---

## Archetype 5 — Recession / Contraction

**Signature:** Negative or near-zero growth, rising unemployment, widening credit spreads, equity drawdown, falling real yields late, falling inflation, USD safe-haven bid.

**Base-rate statistics:**

| Stat | Value | Notes |
|---|---|---|
| Incidence | ~1.5 per decade (US, NBER-dated) | Single most-common "stress" regime |
| Median duration | 11 months (NBER median) | Tails: 2 months (2020) to 18 months (2007-09) |
| Median equity drawdown | −25% to −40% peak-to-trough | 1929-32 was −85% (outlier); 2020 was −34% in 5 weeks |
| Sector dispersion | High (winner-loser spread ~50%+) | Defensives + Treasuries up 10-20%; cyclicals down 40-60% |
| Modal resolution path | (a) policy fully responds (Fed cuts to floor + fiscal impulse) → credit thaws → V-recovery; (b) policy responds slowly → L-shaped recovery (1937, Eurozone 2012); (c) policy fails → depression (1929-39) |
| Sample size | ~12 modern instances | 1973-75, 1980, 1981-82, 1990-91, 2001, 2007-09, 2020, plus several non-US recessions |

**Winners:** Long-duration Treasuries, gold (real-rate driven), high-quality defensives (staples, utilities, healthcare), cash.

**Losers:** Cyclicals, banks (credit losses), high-yield credit, EM, leveraged anything.

**Common analyst errors:**
- Calling the bottom too early ("forward earnings look fine")
- Assuming recessions are short — historical median is 11 months but tails can be 2+ years
- Over-relying on one indicator (yield curve inversion has 12+ month lag)
- Assuming central bank response speed is constant — it has accelerated dramatically post-2008

**Canonical examples:** 2008-2009, 2020 Q1-Q2, 1981-1982, 1973-1975.

---

## Archetype 6 — EM Currency / BoP Crisis

**Signature:** Specific country: collapsing currency, rising sovereign spreads, FX reserves draining, capital flight, inflation spiking via imported channel, banking stress.

**Base-rate statistics:**

| Stat | Value | Notes |
|---|---|---|
| Incidence | ~1 country per 5-7 years globally | Country-specific, not global; clusters in DXY-strength windows |
| Median duration | 6-18 months acute | Followed by multi-year structural reform period |
| Median equity drawdown (local terms) | −30% to −60% in USD | Local currency drawdown can be 50-80% |
| Sector dispersion | Extreme | USD-revenue exporters can be UP in USD terms while domestic sectors collapse |
| Modal resolution path | (a) IMF program + currency adjustment + structural reforms → 12-24 month recovery; (b) default + debt restructuring (longer recovery); (c) hyperinflation spiral (rare; Argentina, Venezuela) |
| Sample size | ~12 modern instances | 1991 India, 1994 Mexico, 1997 Asia (Thailand/Korea/Indonesia), 1998 Russia, 2001 Argentina, 2014 Russia, 2018 Turkey/Argentina, 2022-23 Sri Lanka/Pakistan |

**Winners (within crisis country):** USD assets, exporters with USD revenues, gold.

**Winners (globally):** USD itself, US Treasuries, defensive globals.

**Losers (within crisis country):** Importers, dollar debtors, domestic financials, leveraged corporates.

**Common analyst errors:**
- Treating the currency move as overdone too early — they overshoot fundamentals dramatically
- Assuming contagion will spread to all EMs — usually country-specific buffers separate winners from losers
- Buying "cheap" sovereign bonds before the IMF program is announced
- Underweighting the structural-reform upside that follows successful resolution (1991 India IT sector emerged from this)

**Canonical examples:** 1991 India, 1994 Mexico, 1997 Asia, 1998 Russia, 2018 Turkey/Argentina, 2022-23 Sri Lanka/Pakistan.

---

## Archetype 7 — Banking / Credit Crisis

**Signature:** Banking sector stress, credit spreads exploding, deflation pressure, central bank scrambling for liquidity, equity drawdown >30%, USD funding stress globally.

**Base-rate statistics:**

| Stat | Value | Notes |
|---|---|---|
| Incidence | ~1 systemic per 2 decades | Plus 2-3 contained ones per decade (Mar-2023, 1998 LTCM) |
| Median duration | 18-36 months acute; 5-10 years to fully reset banking sector | 2008-09 was 18 months acute; recovery to pre-crisis output trend took 8+ years |
| Median equity drawdown | −35% to −55% peak-to-trough | Banks specifically: −60% to −80% |
| Sector dispersion | Extreme; financials worst, defensives best | Treasuries +15-25%, banks −60-80%; spread ~80-100% |
| Modal resolution path | (a) central-bank LoLR + asset purchases + government recapitalisation → 18-24 months acute, then long workout; (b) policy-failure → depression (1929-39, Japan 1990-2020) |
| Sample size | ~3 modern systemic | 2008 GFC, 2010-12 Eurozone, Japan 1990s. Plus contained: 1990 S&L, 1998 LTCM, Mar-2023 SVB/CS |

**Winners:** Long Treasuries, gold (eventually), cash, USD funding.

**Losers:** Banks, financials, leveraged anything, real estate, high-yield.

**Common analyst errors:**
- Assuming the first failure is the last (cascade dynamics)
- Buying "cheap" banks before the asset side is marked to market
- Not distinguishing solvency from liquidity crises (different policy responses, different recoveries)
- Underestimating the speed of modern policy response — post-2008 institutional changes (resolution authorities, swap lines, SLR exemptions) shorten the cycle dramatically (Mar-2023 was contained in ~10 days)

**Canonical examples:** 2008 GFC, 2010-12 Eurozone, 1990 S&L, 1997 Asia (banking layer), Mar-2023 SVB/CS (contained).

---

## Archetype 8 — Geopolitical War / Supply Shock

**Signature:** Specific commodity or trade-route disruption, energy/food prices spike, defence spending re-rates, USD strength, FX vol elevated, sometimes layered on other archetypes (2022 = this + monetary tightening).

**Base-rate statistics:**

| Stat | Value | Notes |
|---|---|---|
| Incidence | ~1 major per 1-2 decades; smaller shocks more frequent | Wars / embargoes / corridor closures specifically |
| Median duration | 12-24 months acute commodity dislocation | Sector re-ratings (defence) can persist a decade |
| Median equity drawdown (importer countries) | −10% to −20% nominal | Massive sector dispersion within the drawdown |
| Sector dispersion | Extreme | Energy producers +30-60%, importers −15-25%, defence +30-50% (multi-year), aviation/chemicals −25-40% |
| Modal resolution path | (a) supply restoration (war ends, route reopens) → fast price normalisation; (b) demand destruction (importers cut consumption) → slower normalisation; (c) substitution (alternative supply ramps, e.g., US LNG replacing Russian gas) → permanent restructuring |
| Sample size | ~5 modern major | 1973 OPEC, 1979 Iran, 1990 Gulf War, 2022 Ukraine + Europe gas, 2025-26 Iran (current) |

**Winners:** Energy producers, defence, refiners (if access to discounted feedstock), agriculture, gold.

**Losers:** Energy importers, energy-intensive industrials (chemicals, fertiliser, glass, metals smelting), airlines, anything with thin margins on commodity inputs.

**Common analyst errors:**
- Assuming the shock is short — many last 1-2 years
- Underweighting defence — re-ratings persist for a decade post-trigger
- Treating "ceasefire hopes" as base case repeatedly (path dependency: each ceasefire failure compounds)
- Confusing this archetype with stagflation when the *commodity* is the only inflation driver — pure supply shocks resolve faster than entrenched stagflation if the underlying demand is healthy

**Canonical examples:** 1973 OPEC, 1979 Iran, 1990 Gulf War, 2022 Ukraine + Europe gas, 2025-26 Iran (your current regime).

---

## Sector × Archetype Beta Heuristics (rough)

These are **heuristic priors**, not historical regressions. Treat as starting points; refine empirically.

| Sector | Goldilocks | Reflation | Stagflation | Recession | EM crisis (within) | Banking crisis | War/supply shock |
|---|---|---|---|---|---|---|---|
| Tech (long-duration) | ++ | + | −− | − | − | − | − |
| Banks | + | ++ | 0 | −− | −− | −−− | + (rate-cycle) |
| Energy producers | 0 | ++ | +++ | − | + (USD revenues) | − | +++ |
| Refiners | + | + | + | − | − | − | ++ (if feedstock arb) |
| Defensives (staples, utilities) | − | 0 | + | ++ | + | ++ | + |
| Healthcare | + | + | + | + | 0 | + | + |
| Industrials (capex) | + | ++ | − | −− | − | − | mixed |
| Materials/metals | + | ++ | + | − | − | − | + |
| Discretionary | ++ | + | −− | −− | −− | −− | − |
| Defence | 0 | 0 | + | 0 | 0 | 0 | +++ |
| Gold/precious | − | − | ++ | + | ++ | ++ | ++ |
| Long Treasuries | 0 | − | −− | +++ | 0 | +++ | mixed |

Use these only to seed a hypothesis; verify with the live data the base macro skill produces.
