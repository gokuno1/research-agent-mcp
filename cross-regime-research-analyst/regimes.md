# Historical Regime Catalog — v0.1

Persistent, structured catalog of historical macro regimes used by the analogue layer. Each entry has a fixed schema. The agent computes today's feature vector and scores similarity against every entry here using weighted Euclidean distance.

---

## Feature Vector Specification

Every regime is encoded as a 12-dimensional vector. Today's vector is computed live from WebSearch + base-skill output and compared against each entry's `peak_state` vector below.

| # | Dimension | Definition | Encoding |
|---|---|---|---|
| 1 | `growth` | YoY real GDP growth of the focal economy | percentage points |
| 2 | `headline_inflation` | YoY CPI of focal economy | percentage points |
| 3 | `oil_zscore` | Brent crude vs trailing 5y mean | z-score |
| 4 | `USD_zscore` | DXY vs trailing 5y mean | z-score |
| 5 | `real_10y_yield` | US 10y nominal − 10y inflation breakeven | percentage points |
| 6 | `HY_OAS_zscore` | US HY OAS vs trailing 5y mean | z-score |
| 7 | `equity_drawdown_3m` | Focal equity index 3-month drawdown from peak | percent (negative) |
| 8 | `FX_vol` | Realised vol of focal-currency vs USD, 3m | percent annualised |
| 9 | `geopolitical_flag` | Active major war or sanctions regime affecting trade/energy | 0/1 |
| 10 | `fiscal_stance` | Cyclically-adjusted primary balance change YoY | pct points (− = expansionary) |
| 11 | `monetary_stance` | Real policy rate vs estimated neutral | pct points (+ = restrictive) |
| 12 | `banking_stress_flag` | Senior officer survey shows broad-based tightening | 0/1 |

### Distance Metric

```
distance(today, regime) = sqrt( Σ_i  w_i × (today_i − regime_i)² )
```

Weights `w_i`:

| Dimension | Weight | Rationale |
|---|---|---|
| `headline_inflation` | 1.5 | Biggest regime separator |
| `oil_zscore` | 1.5 | Defines supply-shock regimes |
| `geopolitical_flag` | 1.5 | Cleanly separates war regimes |
| `banking_stress_flag` | 1.5 | Cleanly separates banking-crisis regimes |
| `growth` | 1.2 | |
| `real_10y_yield` | 1.2 | |
| `HY_OAS_zscore` | 1.2 | |
| `monetary_stance` | 1.0 | |
| `USD_zscore` | 1.0 | |
| `equity_drawdown_3m` | 1.0 | |
| `fiscal_stance` | 0.8 | |
| `FX_vol` | 0.8 | |

**Differential diagnosis rule:** when reporting top-2 analogues, identify the dimension where `|today_i − regime_i| × w_i` is largest. That is the *most distinguishing feature* and the one to flag as the "but today is different because…" caveat.

---

## Catalog Entries

### Entry 1 — 2022 Europe Gas Crisis + Global Rate Hikes (FULLY FLESHED)

```yaml
name: "2022 Europe gas crisis + global rate hikes"
archetype: supply_shock_with_simultaneous_tightening
date_range:
  start: 2022-02
  end:   2023-06   # crisis acute phase
trigger:
  - "Russia invades Ukraine (Feb 24, 2022)"
  - "EU phases out Russian pipeline gas; Nord Stream 1 sabotaged Sep 2022"
  - "Fed pivots from 0% to 525 bps cumulative hikes in 16 months"
  - "Simultaneous: ECB +450 bps, BoE +500 bps, RBI +250 bps"

pre_state:                              # ~6 months before peak
  growth: 5.5                           # global, 2021 reflation
  headline_inflation: 4.7               # rising fast
  oil_zscore: 0.8
  USD_zscore: 0.5
  real_10y_yield: -0.8                  # negative real rates
  HY_OAS_zscore: -0.4
  equity_drawdown_3m: -3
  FX_vol: 6
  geopolitical_flag: 0
  fiscal_stance: -1.2                   # post-COVID stimulus still flowing
  monetary_stance: -1.5                 # policy below neutral
  banking_stress_flag: 0

peak_state:                             # ~Sep-Oct 2022
  growth: 1.0                           # decelerating sharply
  headline_inflation: 9.8               # US 9.1, Eurozone 10.6
  oil_zscore: 2.2                       # Brent $120
  USD_zscore: 2.5                       # DXY 115
  real_10y_yield: 1.6                   # sharply positive
  HY_OAS_zscore: 1.4
  equity_drawdown_3m: -16               # S&P -25% YTD by Sep
  FX_vol: 14                            # GBP, JPY, EUR all 30y vol highs
  geopolitical_flag: 1
  fiscal_stance: 0.6                    # consolidation begins
  monetary_stance: 1.2                  # restrictive
  banking_stress_flag: 0                # no broad banking event yet

resolution:
  description: |
    Europe rationed gas, accelerated LNG imports (record cargoes from US),
    survived the winter via mild weather + stockpiling. Energy prices
    normalised by mid-2023. US inflation peaked Jun-2022 at 9.1%, fell to
    3% by Jun-2023 as base effects rolled off and supply chains healed.
    Fed paused mid-2023 at 5.25-5.50%. SVB collapse Mar-2023 marked the
    first banking casualty of the rate cycle but was contained. The
    "everything bear market" of 2022 ended.
  duration_acute_months: 16

cross_border_path:
  - "Europe loses ~150 bcm/yr of cheap Russian gas"
  - "Europe outbids Asia for global LNG → Asian power costs rise"
  - "US LNG export capacity becomes the global price-setter for the first time"
  - "European industrial production falls; energy-intensive sectors (chemicals, fertiliser, glass) shut capacity"
  - "USD strength via DXY +20% strangles EM dollar-debt economies; Sri Lanka, Pakistan default; Argentina spirals"
  - "Indian crude bill rises ~$60bn/yr (~2% GDP); INR moves from 75 to 84 to USD"
  - "FII outflows ₹1.4 lakh crore from India in 2022; ECB hikes break Italian/Greek peripheral spreads briefly"

winners:
  - "Energy producers (Exxon, Chevron, Shell, BP all hit record FY profits)"
  - "Defence (Lockheed, RTX, BAE; ramp expected to last decade)"
  - "Refiners (record GRMs as Russian crude diverted to India/China at discount)"
  - "USD itself; US Treasuries late in cycle as terminal-rate clarity emerged"
  - "ONGC, Reliance refining (Russian crude arbitrage)"

losers:
  - "Long-duration tech (Nasdaq -33% peak-to-trough)"
  - "European chemicals, fertiliser, glass (BASF, Yara, Umicore)"
  - "Crypto (TerraLuna, Celsius, FTX implosions)"
  - "Emerging-market deficit countries with USD debt and energy imports"
  - "Sri Lanka, Pakistan (default); Egypt, Turkey (severe stress)"

policy_response:
  - "Fed: 0% → 5.50% in 16 months; balance sheet runoff $95bn/mo from Sep 2022"
  - "ECB: 0% → 4.50%; ended APP and PEPP reinvestments"
  - "Europe: REPowerEU plan; €300bn EU-wide gas-price-cap negotiation"
  - "US: Strategic Petroleum Reserve drawdown of 180mn barrels (largest ever)"
  - "G7 + EU price cap on Russian crude exports ($60/bbl)"

key_indicator_paths:
  brent: "$80 (Jan-22) → $128 (Jun-22) → $76 (Mar-23)"
  TTF_gas: "€80 (Feb-22) → €315 (Aug-22) → €40 (Mar-23)"
  US_CPI:  "7.5% (Jan-22) → 9.1% (Jun-22 peak) → 3.0% (Jun-23)"
  DXY:     "96 (Jan-22) → 115 (Sep-22 peak) → 102 (Jul-23)"
  USDINR:  "75 (Jan-22) → 84 (Oct-22) → 82 (Jul-23)"

analyst_lessons:
  - "Supply shocks layered with simultaneous monetary tightening produce the worst possible portfolio environment: stocks AND bonds fall together (60/40 had its worst year since 1937)."
  - "Energy producers re-rate violently and asymmetrically; missing the rotation cost trillions."
  - "USD strength under simultaneous global tightening was extreme; flight-to-quality + rate differential reinforced each other (rare)."
  - "EM resilience varied by buffers: India (FX reserves >$500bn) navigated; Sri Lanka (reserves <$2bn) defaulted. Same shock, different outcomes."
  - "The first banking casualty (SVB) came from rate-driven duration losses, not credit losses — a lesson that the rate channel cuts before the credit channel."

differential_features:
  vs_1973_OPEC:
    "1973 had no central-bank tightening response (in fact accommodation). 2022 had simultaneous global tightening — that combination is rarer and uglier."
  vs_1979_iran:
    "1979 had a Volcker reaction function that made the recession explicit. 2022 Fed reaction was reactive, not pre-emptive."
  vs_2008:
    "2008 was a banking-credit crisis with deflation; 2022 was a real-economy supply shock with inflation. Opposite signs on inflation and policy direction."

references:
  - "BIS Annual Economic Report 2023, Ch. 1"
  - "IEA Gas Market Report Q1 2023"
  - "Goldman Sachs European Gas Crisis Primer, Sep 2022"
  - "RBI Annual Report 2022-23, External Sector chapter"
```

---

### Entry 2 — 2008 Global Financial Crisis (SKELETON)

```yaml
name: "2008 Global Financial Crisis"
archetype: banking_leverage_deflation
date_range:
  start: 2007-08    # quants blow-up + BNP Paribas freezes funds
  end:   2009-06    # NBER trough
trigger:
  - "US subprime mortgage delinquencies exceed loss assumptions"
  - "Lehman Brothers files Chapter 11 (Sep 15, 2008)"
  - "AIG, Fannie/Freddie, Bear Stearns, WaMu fail in cascade"

# TODO: fill peak_state vector once first analogue match against this regime is required
# TODO: fill resolution narrative
# TODO: fill cross_border_path: US subprime → European banks (Northern Rock, RBS, HBOS) → trade collapse → EM commodity exporters

archetype_anchors:
  - growth: deeply negative (-3 to -5% peak deceleration)
  - headline_inflation: deflationary (US PCE -1% briefly)
  - HY_OAS_zscore: extreme (3+)
  - banking_stress_flag: 1
  - real_10y_yield: collapsing
  - oil_zscore: collapsing late ($147 → $35 in 6 months)

# To be fleshed when first user query implies a 2008-like analogue match.
```

---

### Entry 3 — 1997 Asian Financial Crisis (SKELETON)

```yaml
name: "1997 Asian Financial Crisis"
archetype: em_currency_crisis
date_range:
  start: 1997-07    # Thai baht float
  end:   1998-12    # IMF programs stabilise

trigger:
  - "Thailand abandons baht peg under speculative attack"
  - "Contagion to Indonesia, Korea, Philippines, Malaysia"
  - "LTCM blow-up + Russian default Aug-1998 extends crisis"

archetype_anchors:
  - USD_zscore: high
  - FX_vol: extreme in EM Asia
  - HY_OAS_zscore: high
  - banking_stress_flag: 1 (Asian banks)
  - real_10y_yield: positive
  - geopolitical_flag: 0

key_lessons_to_record:
  - "Pegged currencies + USD-denominated short-term external debt = self-fulfilling crisis"
  - "IMF programs initially deepened the crisis (high rates + fiscal contraction); approach reformed afterwards"
  - "Korea and Thailand both 'V'-recovered by 2000; Indonesia took longer (political crisis layered on)"

# To be fleshed when first user query implies a 1997-like analogue.
```

---

### Entry 4 — 2020 COVID Shock (SKELETON)

```yaml
name: "2020 COVID Shock"
archetype: real_economy_plus_liquidity_shock
date_range:
  start: 2020-02
  end:   2020-04    # acute phase only; second-order effects extend through 2022

trigger:
  - "Global pandemic forces synchronized lockdowns"
  - "Demand collapses across services; oil futures briefly negative"
  - "Massive fiscal+monetary response (Fed balance sheet $4.2T → $7.1T in 6 months; US deficit ~15% GDP)"

archetype_anchors:
  - growth: extreme negative briefly
  - headline_inflation: brief disinflation, then accelerated reflation 2021+
  - oil_zscore: extreme negative briefly
  - HY_OAS_zscore: extreme spike then collapse
  - banking_stress_flag: 0 (banks were not the epicentre)
  - fiscal_stance: extreme expansion
  - monetary_stance: extreme accommodation

key_lessons_to_record:
  - "When the shock hits the real economy directly (not via banking), policy can offset within weeks if politically feasible"
  - "QE-on-steroids + fiscal transfers prevented the 'Great Depression 2' scenario but seeded the 2022 inflation"
  - "Sectoral rotation was extreme and fast: tech/at-home stocks soared, travel/leisure cratered, then reversed"

# To be fleshed when first user query implies a 2020-like analogue.
```

---

### Entry 5 — 1991 India Balance-of-Payments Crisis (SKELETON)

```yaml
name: "1991 India BoP Crisis"
archetype: em_external_collapse
date_range:
  start: 1990-08    # Iraq invasion of Kuwait spikes oil
  end:   1991-07    # IMF program + reform package

trigger:
  - "Gulf War spikes oil price; India imports ~70% of crude"
  - "Remittances from Gulf workers collapse"
  - "FX reserves fall to <2 weeks of imports ($1.2bn)"
  - "Credit ratings downgrade; international borrowing dries up"

archetype_anchors:
  - oil_zscore: extreme positive (briefly)
  - USD_zscore: high
  - FX_vol: extreme (USDINR devalued 18% in two steps)
  - growth: decelerating to 1.1% (FY92)
  - banking_stress_flag: 0 in modern sense (Indian banks were nationalised; stress was on sovereign external balance)
  - geopolitical_flag: 1

key_lessons_to_record:
  - "FX reserves are the single most important EM resilience metric; <3 months of imports is danger zone"
  - "1991 reforms (currency convertibility, trade liberalisation, industrial delicensing) followed the crisis — structural shocks force structural reform"
  - "The shock hit India hardest because of: (a) high oil import dependency, (b) heavy reliance on Gulf remittances, (c) fixed exchange rate. Today's India has buffers on (a) via SPR + diversified suppliers, (c) via flexible regime — but (b) and (a) still apply."

# To be fleshed when first user query implies a 1991-like analogue.
```

---

## Pending entries (to add as needed)

The following are referenced in differential-diagnosis sections but not yet entered. Add full entries when first cited:

- **1973 OPEC oil embargo** (`1973_OPEC`) — pure supply shock without monetary tightening
- **1979 Iranian oil shock + Volcker disinflation** (`1979_volcker`) — supply shock followed by ruthless tightening
- **2013 Taper Tantrum** (`2013_taper`) — Fed→EM canonical case (the single most teachable Fed→EM episode)
- **2018 Turkey/Argentina EM-FX crisis** (`2018_emfx`) — USD strength channel under benign Fed
- **2013 India fragile-five episode** — INR collapse during taper tantrum, India-specific lens

When using any of these in differential diagnosis, add the full entry (using the same schema as 2022 above) before completing the report.
