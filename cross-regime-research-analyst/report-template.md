# Report Template

Required output structure for the cross-regime-research-analyst skill in **report mode**. Save the populated report to `docs/macro-analysis/YYYY-MM-DD-<topic-slug>.md`.

Every section is mandatory. Sections 3, 4, 7 are what differentiate this skill from the base macro-research-analyst — if any of them is missing, the report is incomplete.

---

```markdown
# <Topic>: Cross-Regime Macro Analysis

**Date:** YYYY-MM-DD
**Source shock:** <country/region/asset where shock originates>
**Destination:** <country/region/asset of impact>
**Shock type:** <one of: supply_shock, demand_shock, monetary_tightening, monetary_easing, currency_crisis, banking_crisis, trade_war, geopolitical_war, liquidity_event, fiscal_expansion, fiscal_contraction>
**Archetype:** <one of the 8 archetypes from archetypes.md>

---

## 1. Executive Summary

3-5 lines. State the source shock, the dominant transmission channel, the top historical analogue with the single most-distinguishing differential, and the headline impact on the destination. Every claim tagged with a framework.

---

## 2. Macro Context

Pulled from base skills' output. Cover the 7 macro dimensions (monetary, fiscal, inflation, labor, growth, credit, geopolitical) at least briefly. Tag every claim:

- Example: "RBI repo at 5.25%, 125 bps cut completed, OMOs ₹2.5L Cr active `[heuristic — RBI policy stance]`"
- Example: "US 10y real yield at 1.8%, vs 0% pre-shock `[real-vs-nominal]`"

---

## 3. Cross-Border Transmission Chain    ← REQUIRED, NEW IN THIS SKILL

Use the elasticity library (`elasticities.md`) and live indicator values. One row per channel:

| Channel | Indicator | Current value | Elasticity used | Lag | Implied impulse on destination | Framework tag |
|---|---|---|---|---|---|---|
| Energy import bill | Brent | $XX | $10 → +0.4% CAD | 1-2 Q | CAD widens X% of GDP | `[CAD identity]` |
| Imported inflation | Brent → CPI | $XX | $10 → +35 bps | 4-6 mo | CPI +X bps | `[USD pass-through]` |
| FX | INR | XX | $10 → 1.25% INR | 0-3 mo | INR moves to XX | `[CAD identity]` |
| Capital flows | FII flows | $X | Fed-conditional | 0-2 mo | $X bn outflow risk | `[Fed-EM transmission]` |
| ... | | | | | | |

**Chain narrative:** prose form of the table, 6-10 lines. Trace the shock from origin to destination via each link. Every numerical claim must reference an elasticity row.

**If any link cannot be quantified, mark it `[heuristic]` and explain the qualitative reasoning.**

---

## 4a. Archetype Classification + Base Rates    ← REQUIRED IN EVERY REPORT

### Archetype: <one of the 8 from archetypes.md>

State the archetype the current regime falls into. May be a *blend* of two if the feature vector spans both (e.g., "supply shock with monetary-tightening overlay" = Archetype 8 + Archetype 5 partial).

**Justifying indicators:** which 3-5 features of today's vector make this archetype the best fit.

### Base-rate context (from archetypes.md)

| Statistic | Value | Source |
|---|---|---|
| Historical incidence | <X occurrences per decade> | archetypes.md |
| Median duration | <N months> | archetypes.md |
| Median equity drawdown | <-X% to -Y%> | archetypes.md |
| Median sector dispersion | <winner-loser spread, e.g., +30% / −20%> | archetypes.md |
| Modal resolution path | <how this archetype typically ends> | archetypes.md |

### What this archetype implies (sector betas)

Apply the sector × archetype beta heuristics from `archetypes.md`. List which sectors typically win/lose in this archetype-class — this seeds the Section 5 mapping (cross-border layer in Section 3 then refines for country-specific exposure).

---

## 4b. Historical Analogue Match    ← OPT-IN ONLY (omit by default)

**Default behavior: this entire section is OMITTED from the report.**

This section appears only if BOTH conditions hold:
1. The user explicitly requested historical context (e.g., "what historical episodes resemble this?", "is this like 2008?", "give me historical comparables")
2. The top similarity score against `regimes.md` catalog is < 0.60 (genuinely strong match)

### If user requested historical context BUT no strong match exists

Output exactly this single block instead:

> *"No historical regime in the catalog is a strong match (best similarity score: X.XX, threshold: 0.60). Today's regime is novel within the `<archetype>` class. Treating it as such avoids forcing a misleading analogue."*

Then proceed directly to Section 5.

### If user requested historical context AND strong match exists

#### Top Analogue: <name from regimes.md>

| Dimension | Today | Analogue (peak) | Distance contribution |
|---|---|---|---|
| growth | X.X% | Y.Y% | small/medium/large |
| headline_inflation | ... | ... | ... |
| ... | | | |

**Similarity score:** XX (lower = more similar; weighted Euclidean per `regimes.md`)

**Most-similar dimensions (top 3):** ...

**Differential diagnosis (most-different dimensions):** ← MANDATORY
- Dimension X: today is Y, analogue was Z. This means: <implication of the difference>
- Dimension Y: ...

**Resolution narrative:** how that historical regime ended; what the equivalent path today would look like — *with explicit notes on the dimensions where today differs from the analogue's pre-resolution conditions* (those are where the analogue's playbook is least applicable).

#### Second Analogue (only if also < 0.60 similarity): <name>

Same structure, briefer.

### Mandatory disclaimer (always end Section 4b with this block)

> *"Historical analogues are reality-checks on framework predictions, not forecasts. The framework-derived chain in Section 3 is the primary basis for any decisions; this section provides historical base-rate context only."*

---

## 5. Stock / Sector Mapping

Inherit the table from base macro skill's output (Phase 5). Two changes:

1. Every "key driver" cell now includes a `[framework tag]`.
2. Add a column "Cross-border channel" linking each stock's exposure to a channel from Section 3.

| Ticker | Sector | Macro verdict | Time horizon | Key driver (with tag) | Cross-border channel |
|---|---|---|---|---|---|
| ONGC | E&P | Strong Bullish | 1 month | Oil realisation +$40/bbl `[heuristic — producer leverage]` | Energy import bill / commodity price |
| INDIGO | Aviation | Strong Bearish | 1 month | ATF +60% YoY = margin destruction `[heuristic — input cost pass-through]` | Energy import bill / imported inflation |
| ... | | | | | |

---

## 6. Trade Implications (only if user requested)

Inherit Tier 1/Tier 2/Tier 3 structure from base skill if applicable. Otherwise omit this section.

---

## 7. Frameworks Used    ← REQUIRED, NEW IN THIS SKILL

For every `[framework-tag]` that appears anywhere in this report, list it here with a 2-3 line definition pulled from `frameworks.md`. This is a learning aid — the user should be able to read this section standalone and understand every framework that informed the analysis.

| Tag | What it states (2-3 lines) |
|---|---|
| `[CAD identity]` | A country's current account balance equals (savings − investment) and equivalently (trade + net income + transfers). It is an accounting identity, not a behavioural model — every cross-border flow analysis starts here. |
| `[Fed-EM transmission]` | US monetary tightening propagates to EM via three reinforcing channels: USD strength, dollar-debt servicing burden, and risk-asset repricing. Median elasticity: DXY +10% → EM equities −10-15% over 3 months. |
| ... | |

If a tag was used that is not yet in `frameworks.md`, it must be added there in this same run, before saving the report.

---

## 8. Risks & Invalidation

Every report ends with explicit invalidation triggers. For each major call:

| Call | What would invalidate it | Probability |
|---|---|---|
| <call 1> | <specific event/data> | <low/moderate/high> |
| ... | | |

Plus a "regime-shift watch list" — the 3-5 indicators whose movement would force re-classifying the archetype.

---

## Appendix: Data Provenance

List the WebSearch queries and dates of data freshness for each live indicator used in Sections 3 and 4. This is for reproducibility and to flag any indicator where data was stale or unavailable.

```

---

## Slug Convention

Filename: `docs/macro-analysis/YYYY-MM-DD-<source>-<destination>-<shock>.md`

Examples:
- `2026-04-30-europe-us-gas-spillover.md`
- `2026-04-30-fed-india-tightening-spillover.md`
- `2026-04-30-india-macro-iran-shock.md`

If the report is regime-classification-focused (no specific cross-border), use:
- `2026-04-30-<destination>-regime-<archetype>.md`
