# Saturday Runner

A weekend-only Python script that produces the upcoming week's NIFTY 50 swing-trading portfolio per the evidence-based playbook in:

> `docs/research-runs/2026-05-02-systematic-swing-trading-evidence-based-playbook.md`

It implements the eight steps in §8.3 of that playbook, using `yfinance` for free NSE EOD data and outputting a markdown report + GTT-stop CSV ready to upload to your broker.

**Capital default:** ₹1,00,000.

---

## Why this exists

The playbook says to do a 30–60 minute weekly analysis. This script automates the mechanical 25 minutes of that (data fetch, ranking, sizing, stops, formatting), so your active time goes to the 5 things a script should not do:

1. Updating `fundamentals.json` quarterly from screener.in.
2. Updating `earnings_recent.json` weekly from `nseindia.com/companies-listing/corporate-filings-financial-results`.
3. Eyeballing the recommendation against any unusual news (corporate action, regulatory event).
4. Placing the buy orders Monday 09:30.
5. Uploading the GTT CSV to your broker.

The script does **not** auto-trade. By design.

---

## Install

```bash
cd automation/saturday-runner
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Tested with Python 3.11+.

---

## Run

```bash
# Standard weekly run
python run.py

# Override capital from CLI
python run.py --capital 100000

# Dry run (console only, no files)
python run.py --dry-run
```

Outputs land under `runs/<YYYY-MM-DD>/`:

- `portfolio.md` — the human-readable report (also emailed if SMTP configured)
- `gtt_orders.csv` — broker-agnostic GTT stop-loss orders, ready to upload

---

## Saturday workflow (≈30 min total)

1. **(5 min) Update `earnings_recent.json`** with the past 5 trading days' NIFTY 50 earnings releases. Source: NSE corporate-filings page. Compute `surprise_sigma = (actual_eps − consensus_eps) / |consensus_eps|`. Mark next 3 trading days' upcoming earnings.
2. **(5 min, only if quarter-end month)** Update `fundamentals.json` with new TTM ROE / NetDebtEBITDA / Tier-1 / EPS-CV from screener.in.
3. **(2 min)** `python run.py`
4. **(5 min)** Skim `runs/<today>/portfolio.md`. Compare to last week's holdings — keep what's still in top-12, exit what fell out.
5. **(5 min Monday 09:30)** Place the buy orders. Use the limit price = entry + 0.30% (covers slippage).
6. **(3 min Monday 09:35)** Upload `gtt_orders.csv` to your broker (Upstox: GTT module → bulk upload). These are your stop-loss safety nets.
7. **(2 min Monday 09:40)** Set calendar reminders for the `Exit by` time-stop dates printed in the report.
8. **(3 min)** Done.

---

## Files

| File | What it is | Refresh cadence |
|---|---|---|
| `config.yaml` | All thresholds & params | **Quarterly review only**, per playbook §8.5 |
| `universe.csv` | NIFTY 50 with NSE symbols + ISINs | Update on NSE semi-annual review (March/Sep) |
| `fundamentals.json` | TTM ROE, NetDebt/EBITDA, Tier-1, EPS-CV-5y | **Quarterly** (after Q-results season) |
| `earnings_recent.json` | Last 5 days' earnings + next 3 days' upcoming | **Weekly**, manually |
| `run.py` | Orchestrator | – |
| `lib/playbook.py` | The 8 steps as functions | – |
| `lib/data.py` | yfinance wrapper | – |
| `lib/report.py` | Markdown + GTT CSV + email | – |
| `runs/` | Dated outputs | Auto-created |

---

## What you'll see

```
==============================================================================
  SATURDAY RUNNER — 2026-05-02 17:30 IST
  Capital: ₹100,000    Universe: NIFTY 50
==============================================================================

STEP 1 — Market state
  NIFTY close:          24,850.30
  NIFTY 40-WMA:         23,210.45    → TREND-ON
  India VIX:            14.20
  Vol scaling:          ×1.00  (effective target = 12.0%)

STEPS 2–4 — Quality-passing top-12 momentum candidates
  Rank  Symbol        Sector                  Mom12-1  Vol(ann)   ATR%   Q  PEAD
     1  TRENT         ConsumerServices          +85.2%     31.4%  2.41%   3  -
     2  BAJFINANCE    Financials-NBFC           +52.1%     27.8%  1.98%   3  -
     3  RELIANCE      Energy                    +38.5%     22.1%  1.55%   2  PEAD +1σ surprise…
     ...

STEPS 5–7 — Final portfolio (5 of 5 target)
  Symbol        Sector                    Sh      Entry       Stop  Stop%   Notional   Wt%    Risk
  TRENT         ConsumerServices           1   8,420.00   7,830.60   7.00%   ₹8,420   8.4%    ₹589
  BAJFINANCE    Financials-NBFC            1   9,140.00   8,500.20   7.00%   ₹9,140   9.1%    ₹640
  ...
  TOTAL                                                                       ₹52,300  52.3%  ₹3,672
  Cash buffer: ₹47,700 (47.7%)   Total at-risk: 3.67% of capital
```

---

## Troubleshooting

- **`yfinance` returns NaN for an Indian ticker:** transient — re-run. If persistent, check `universe.csv` symbol mapping.
- **A NIFTY 50 stock is missing from `fundamentals.json`:** add an entry; the script falls back to `quality_score=0` (skip) if missing.
- **All quality scores are 0:** likely your `eps_cv_5y` field is missing for all stocks → median can't be computed → eps_cv_pass defaults to false, and most stocks score ≤ 2. Fill in `fundamentals.json`.
- **TREND-OFF defensive mode:** the script switches to top-3 quality at 5% each. This is intentional — see playbook §8.3 Step 1.
- **Email not sending:** verify env vars `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `EMAIL_TO` are set; for Gmail, use an app-password.

---

## Promoting to live execution

When you're ready to move beyond manual GTT upload, plug a broker SDK into `lib/report.py:write_gtt_csv` and replace the CSV output with REST calls. The CSV columns map cleanly:

- **Upstox:** `POST /v3/order/place-gtt` with `instrument_token` (lookup by ISIN) → trigger_price → limit_price.
- **Zerodha Kite:** `kite.place_gtt(...)` with `tradingsymbol`, `transaction_type=SELL`, `trigger_values=[trigger_price]`.

**Do this only after the 12-week paper trial in playbook §8.6 step 2.** Real money before validation = the same mistake from the last 5 years.

---

## What this script will NOT do

Per playbook §8.5 anti-overfit rules:

- It will not change parameters based on recent performance.
- It will not add an indicator that has no peer-reviewed support for the same horizon.
- It will not skip the cash buffer to "deploy more on a strong week".
- It will not lift the sector cap because "Financials look great".
- It will not extend the time stop because "this name is about to break out".

If you want to override any rule, do it in a quarterly review with a written reason. Once-per-quarter, max one rule. Otherwise the deflated Sharpe estimate from §8.5 ruins the whole design.
