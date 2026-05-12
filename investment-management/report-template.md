# Investment Management Report Template

All outputs from this skill MUST be rendered as **self-contained HTML files** with inline CSS styling. Reports are saved as `.html` files — never as `.md`.

---

## Template A: Fund Portfolio Construction Report

Save to `docs/portfolio-construction/YYYY-MM-DD-<fund-name>.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fund Portfolio: [Name] — [Date]</title>
    <style>
        :root {
            --bg: #0f1117;
            --surface: #1a1d27;
            --surface-2: #232733;
            --border: #2d3244;
            --text: #e4e7ef;
            --text-muted: #8b92a8;
            --accent: #6c8cff;
            --green: #4ade80;
            --red: #f87171;
            --yellow: #fbbf24;
            --blue: #60a5fa;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            padding: 2rem;
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 { font-size: 1.8rem; margin-bottom: 0.5rem; color: var(--accent); }
        h2 { font-size: 1.3rem; margin: 2rem 0 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--border); }
        h3 { font-size: 1.1rem; margin: 1.5rem 0 0.75rem; color: var(--blue); }
        .meta { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 2rem; }
        .meta span { margin-right: 1.5rem; }
        .badge {
            display: inline-block; padding: 0.2rem 0.6rem; border-radius: 4px;
            font-size: 0.8rem; font-weight: 600; margin-right: 0.5rem;
        }
        .badge-green { background: rgba(74,222,128,0.15); color: var(--green); }
        .badge-red { background: rgba(248,113,113,0.15); color: var(--red); }
        .badge-yellow { background: rgba(251,191,36,0.15); color: var(--yellow); }
        .badge-blue { background: rgba(96,165,250,0.15); color: var(--blue); }
        .card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        .card-header {
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 1rem;
        }
        .metrics-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem; margin: 1rem 0;
        }
        .metric-card {
            background: var(--surface-2);
            border-radius: 6px;
            padding: 1rem;
            text-align: center;
        }
        .metric-card .value { font-size: 1.5rem; font-weight: 700; }
        .metric-card .label { font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem; }
        table { width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.9rem; }
        th {
            background: var(--surface-2); padding: 0.75rem 1rem;
            text-align: left; font-weight: 600; color: var(--text-muted);
            border-bottom: 2px solid var(--border);
        }
        td { padding: 0.75rem 1rem; border-bottom: 1px solid var(--border); }
        tr:hover td { background: var(--surface-2); }
        .positive { color: var(--green); }
        .negative { color: var(--red); }
        .neutral { color: var(--yellow); }
        .progress-bar {
            height: 6px; background: var(--surface-2); border-radius: 3px; overflow: hidden;
            margin-top: 0.5rem;
        }
        .progress-fill { height: 100%; border-radius: 3px; transition: width 0.3s; }
        .risk-section { border-left: 3px solid var(--red); padding-left: 1rem; margin: 1rem 0; }
        .rebalance-section { border-left: 3px solid var(--yellow); padding-left: 1rem; margin: 1rem 0; }
        .footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--border); color: var(--text-muted); font-size: 0.8rem; }
        @media (max-width: 768px) {
            body { padding: 1rem; }
            .metrics-grid { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
</head>
<body>
    <h1>Fund Portfolio: [Name]</h1>
    <div class="meta">
        <span><strong>Date:</strong> YYYY-MM-DD</span>
        <span><strong>Benchmark:</strong> [Index]</span>
        <span><strong>Regime:</strong> <span class="badge badge-blue">[Label]</span></span>
        <span><strong>Horizon:</strong> [X years]</span>
    </div>

    <!-- INVESTMENT MANDATE -->
    <section class="card">
        <h2>Investment Mandate</h2>
        <table>
            <tr><th>Parameter</th><th>Value</th></tr>
            <tr><td>Benchmark</td><td>[Index]</td></tr>
            <tr><td>Universe</td><td>[Description]</td></tr>
            <tr><td>Time Horizon</td><td>[X years]</td></tr>
            <tr><td>Capital</td><td>[Amount]</td></tr>
            <tr><td>Max Positions</td><td>[N]</td></tr>
            <tr><td>Max Single Position</td><td>[X%]</td></tr>
            <tr><td>Max Sector Weight</td><td>[X%]</td></tr>
            <tr><td>Risk Budget (Volatility)</td><td>[X%]</td></tr>
            <tr><td>Drawdown Tolerance</td><td>[X%]</td></tr>
            <tr><td>Target Alpha</td><td>[X% annualized]</td></tr>
            <tr><td>Factor Tilts</td><td>[Value + Quality + Momentum]</td></tr>
        </table>
    </section>

    <!-- REGIME-ADJUSTED FACTOR WEIGHTS -->
    <section class="card">
        <h2>Regime-Adjusted Factor Weights</h2>
        <p style="color: var(--text-muted); margin-bottom: 1rem;">
            Current regime: <span class="badge badge-blue">[Regime]</span> — [Rationale]
        </p>
        <table>
            <tr><th>Factor</th><th>Base Weight</th><th>Regime Adjustment</th><th>Final Weight</th></tr>
            <tr><td>Value</td><td>X%</td><td>[±X%]</td><td><strong>X%</strong></td></tr>
            <tr><td>Quality</td><td>X%</td><td>[±X%]</td><td><strong>X%</strong></td></tr>
            <tr><td>Momentum</td><td>X%</td><td>[±X%]</td><td><strong>X%</strong></td></tr>
            <tr><td>Low Volatility</td><td>X%</td><td>[±X%]</td><td><strong>X%</strong></td></tr>
        </table>
    </section>

    <!-- PORTFOLIO ALLOCATION TABLE -->
    <section class="card">
        <h2>Portfolio Allocation</h2>
        <table>
            <tr>
                <th>#</th><th>Ticker</th><th>Sector</th><th>Weight</th>
                <th>Conviction</th><th>Factor Score</th><th>Margin of Safety</th>
                <th>Business Quality</th><th>Key Thesis</th>
            </tr>
            <!-- Repeat for each position -->
            <tr>
                <td>1</td><td><strong>[TICKER]</strong></td><td>[Sector]</td>
                <td>X.X%</td><td><span class="badge badge-green">High</span></td>
                <td>X.XX</td><td class="positive">+XX%</td>
                <td>[Compounder]</td><td>[1 sentence]</td>
            </tr>
        </table>
        <p style="margin-top: 1rem; color: var(--text-muted);">
            Total invested: X% | Cash reserve: X%
        </p>
    </section>

    <!-- EXPECTED PORTFOLIO METRICS -->
    <section class="card">
        <h2>Expected Portfolio Metrics</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="value positive">+X.X%</div>
                <div class="label">Expected Return (ann.)</div>
            </div>
            <div class="metric-card">
                <div class="value">X.X%</div>
                <div class="label">Volatility (ann.)</div>
            </div>
            <div class="metric-card">
                <div class="value positive">X.XX</div>
                <div class="label">Sharpe Ratio</div>
            </div>
            <div class="metric-card">
                <div class="value negative">-X.X%</div>
                <div class="label">Max Expected Drawdown</div>
            </div>
            <div class="metric-card">
                <div class="value">X.XX</div>
                <div class="label">Beta</div>
            </div>
            <div class="metric-card">
                <div class="value">X.X%</div>
                <div class="label">Tracking Error</div>
            </div>
            <div class="metric-card">
                <div class="value positive">X.XX</div>
                <div class="label">Information Ratio</div>
            </div>
            <div class="metric-card">
                <div class="value positive">+X.X%</div>
                <div class="label">Alpha vs Benchmark</div>
            </div>
        </div>
        <table>
            <tr><th>Metric</th><th>Portfolio</th><th>Benchmark</th><th>Active Edge</th></tr>
            <tr><td>Expected Return</td><td>X.X%</td><td>X.X%</td><td class="positive">+X.X%</td></tr>
            <tr><td>Volatility</td><td>X.X%</td><td>X.X%</td><td>[comparison]</td></tr>
            <tr><td>Sharpe</td><td>X.XX</td><td>X.XX</td><td class="positive">+X.XX</td></tr>
            <tr><td>Max Drawdown</td><td>X.X%</td><td>X.X%</td><td>[comparison]</td></tr>
        </table>
    </section>

    <!-- FACTOR EXPOSURE -->
    <section class="card">
        <h2>Factor Exposure</h2>
        <table>
            <tr><th>Factor</th><th>Portfolio Z</th><th>Benchmark Z</th><th>Active Tilt</th></tr>
            <tr><td>Value</td><td>X.XX</td><td>0.00</td><td class="positive">+X.XX</td></tr>
            <tr><td>Quality</td><td>X.XX</td><td>0.00</td><td class="positive">+X.XX</td></tr>
            <tr><td>Momentum</td><td>X.XX</td><td>0.00</td><td class="positive">+X.XX</td></tr>
            <tr><td>Low Volatility</td><td>X.XX</td><td>0.00</td><td class="positive">+X.XX</td></tr>
        </table>
    </section>

    <!-- SECTOR ALLOCATION -->
    <section class="card">
        <h2>Sector Allocation</h2>
        <table>
            <tr><th>Sector</th><th>Portfolio</th><th>Benchmark</th><th>Active Bet</th></tr>
            <tr><td>Technology</td><td>X.X%</td><td>X.X%</td><td>[±X.X%]</td></tr>
            <tr><td>Financials</td><td>X.X%</td><td>X.X%</td><td>[±X.X%]</td></tr>
            <!-- more sectors -->
        </table>
    </section>

    <!-- POSITION DETAIL -->
    <section class="card">
        <h2>Position Detail</h2>
        <!-- Repeat for each major position -->
        <div class="card" style="background: var(--surface-2);">
            <h3>[TICKER] — [Sector] (Weight: X.X%)</h3>
            <table>
                <tr><td><strong>Factor Score</strong></td><td>X.XX (V: X.X | Q: X.X | M: X.X | LV: X.X)</td></tr>
                <tr><td><strong>Micro Regime</strong></td><td>[Compounder / Quality Earner / ...]</td></tr>
                <tr><td><strong>Margin of Safety</strong></td><td>XX% (IV: [range] vs CMP: [price])</td></tr>
                <tr><td><strong>Macro Alignment</strong></td><td>[Tailwind / Headwind / Neutral] — [reason]</td></tr>
                <tr><td><strong>Key Risk</strong></td><td>[Single biggest risk]</td></tr>
                <tr><td><strong>Rebalance Trigger</strong></td><td>[What causes trimming/selling]</td></tr>
            </table>
        </div>
    </section>

    <!-- RISK ANALYSIS -->
    <section class="card">
        <h2>Risk Analysis</h2>
        <h3>Concentration</h3>
        <div class="metrics-grid">
            <div class="metric-card"><div class="value">X.X%</div><div class="label">Top 3 Combined</div></div>
            <div class="metric-card"><div class="value">X.X%</div><div class="label">Top 5 Combined</div></div>
            <div class="metric-card"><div class="value">X.X</div><div class="label">Effective N</div></div>
            <div class="metric-card"><div class="value">X.XX</div><div class="label">Max Pairwise Corr</div></div>
        </div>
        <h3>Stress Scenarios</h3>
        <table>
            <tr><th>Scenario</th><th>Portfolio Impact</th><th>Action Plan</th></tr>
            <tr><td>Benchmark -10%</td><td class="negative">-X.X%</td><td>[trigger action]</td></tr>
            <tr><td>Benchmark -20%</td><td class="negative">-X.X%</td><td>[trigger action]</td></tr>
            <tr><td>Rate hike +100bps</td><td class="negative">-X.X%</td><td>[adjustment]</td></tr>
            <tr><td>Recession</td><td class="negative">-X.X%</td><td>[adjustment]</td></tr>
        </table>
        <h3>Tail Risk</h3>
        <div class="risk-section">
            <p><strong>VaR (95%, monthly):</strong> <span class="negative">-X.X%</span></p>
            <p><strong>CVaR (95%, monthly):</strong> <span class="negative">-X.X%</span></p>
        </div>
    </section>

    <!-- REBALANCING SCHEDULE -->
    <section class="card">
        <h2>Rebalancing Schedule</h2>
        <div class="rebalance-section">
            <p><strong>Next monthly review:</strong> [Date]</p>
            <p><strong>Next quarterly deep review:</strong> [Date]</p>
            <p><strong>Active triggers watching:</strong></p>
            <ul style="margin-left: 1.5rem; color: var(--text-muted);">
                <li>[Trigger 1: condition + threshold]</li>
                <li>[Trigger 2: condition + threshold]</li>
            </ul>
            <p><strong>Current drift status:</strong> [On-target / Drifted]</p>
        </div>
    </section>

    <!-- KEY RISKS -->
    <section class="card">
        <h2>Key Risks to Thesis</h2>
        <div class="risk-section">
            <p><strong>1. [Risk 1]:</strong> [Description + probability]</p>
            <p><strong>2. [Risk 2]:</strong> [Description + probability]</p>
            <p><strong>3. [Risk 3]:</strong> [Description + probability]</p>
        </div>
        <h3>What Would Cause Benchmark Underperformance</h3>
        <ul style="margin-left: 1.5rem; color: var(--text-muted);">
            <li>[Scenario 1]</li>
            <li>[Scenario 2]</li>
        </ul>
    </section>

    <div class="footer">
        <p>Generated using investment-management skill. Factor scores use academically replicated premiums.
        Expected returns are estimates, not guarantees. Past factor performance does not guarantee future results.</p>
        <p>Report generated: [DateTime]</p>
    </div>
</body>
</html>
```

---

## Template B: Personal Portfolio Analysis Report

Save to `docs/portfolio-analysis/YYYY-MM-DD-<analysis-type>.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portfolio Health Report — [Date]</title>
    <style>
        :root {
            --bg: #0f1117;
            --surface: #1a1d27;
            --surface-2: #232733;
            --border: #2d3244;
            --text: #e4e7ef;
            --text-muted: #8b92a8;
            --accent: #6c8cff;
            --green: #4ade80;
            --red: #f87171;
            --yellow: #fbbf24;
            --blue: #60a5fa;
            --purple: #a78bfa;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            padding: 2rem;
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 { font-size: 1.8rem; margin-bottom: 0.5rem; color: var(--accent); }
        h2 { font-size: 1.3rem; margin: 2rem 0 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--border); }
        h3 { font-size: 1.1rem; margin: 1.5rem 0 0.75rem; color: var(--blue); }
        .meta { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 2rem; }
        .meta span { margin-right: 1.5rem; }
        .badge {
            display: inline-block; padding: 0.2rem 0.6rem; border-radius: 4px;
            font-size: 0.8rem; font-weight: 600; margin-right: 0.5rem;
        }
        .badge-green { background: rgba(74,222,128,0.15); color: var(--green); }
        .badge-red { background: rgba(248,113,113,0.15); color: var(--red); }
        .badge-yellow { background: rgba(251,191,36,0.15); color: var(--yellow); }
        .badge-blue { background: rgba(96,165,250,0.15); color: var(--blue); }
        .card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        .health-score {
            text-align: center;
            padding: 2rem;
            background: var(--surface);
            border-radius: 12px;
            border: 2px solid var(--accent);
            margin-bottom: 2rem;
        }
        .health-score .score {
            font-size: 3.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, var(--accent), var(--purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .health-score .subtitle { color: var(--text-muted); font-size: 1rem; }
        .dimension-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem; margin: 1.5rem 0;
        }
        .dimension-card {
            background: var(--surface-2);
            border-radius: 8px;
            padding: 1.2rem;
            border-left: 4px solid var(--border);
        }
        .dimension-card.good { border-left-color: var(--green); }
        .dimension-card.warning { border-left-color: var(--yellow); }
        .dimension-card.danger { border-left-color: var(--red); }
        .dimension-card .dim-title { font-weight: 600; margin-bottom: 0.25rem; }
        .dimension-card .dim-score { font-size: 1.3rem; font-weight: 700; }
        .dimension-card .dim-detail { font-size: 0.85rem; color: var(--text-muted); margin-top: 0.25rem; }
        .metrics-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem; margin: 1rem 0;
        }
        .metric-card {
            background: var(--surface-2);
            border-radius: 6px;
            padding: 1rem;
            text-align: center;
        }
        .metric-card .value { font-size: 1.4rem; font-weight: 700; }
        .metric-card .label { font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem; }
        table { width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.9rem; }
        th {
            background: var(--surface-2); padding: 0.75rem 1rem;
            text-align: left; font-weight: 600; color: var(--text-muted);
            border-bottom: 2px solid var(--border);
        }
        td { padding: 0.75rem 1rem; border-bottom: 1px solid var(--border); }
        tr:hover td { background: var(--surface-2); }
        .positive { color: var(--green); }
        .negative { color: var(--red); }
        .neutral { color: var(--yellow); }
        .progress-bar {
            height: 8px; background: var(--surface-2); border-radius: 4px;
            overflow: hidden; margin-top: 0.5rem; width: 100%;
        }
        .progress-fill { height: 100%; border-radius: 4px; }
        .progress-fill.green { background: var(--green); }
        .progress-fill.yellow { background: var(--yellow); }
        .progress-fill.red { background: var(--red); }
        .recommendation {
            background: var(--surface-2);
            border-radius: 8px;
            padding: 1.2rem;
            margin-bottom: 1rem;
            border-left: 4px solid var(--accent);
        }
        .recommendation.urgent { border-left-color: var(--red); }
        .recommendation.moderate { border-left-color: var(--yellow); }
        .recommendation.low { border-left-color: var(--green); }
        .recommendation .rec-title { font-weight: 600; margin-bottom: 0.5rem; }
        .recommendation .rec-detail { font-size: 0.9rem; color: var(--text-muted); }
        .behavioral-flag {
            display: flex; align-items: center; gap: 0.75rem;
            padding: 0.75rem 1rem; border-radius: 6px;
            margin-bottom: 0.5rem; font-size: 0.9rem;
        }
        .behavioral-flag.detected { background: rgba(248,113,113,0.1); }
        .behavioral-flag.clear { background: rgba(74,222,128,0.05); }
        .footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--border); color: var(--text-muted); font-size: 0.8rem; }
        @media (max-width: 768px) {
            body { padding: 1rem; }
            .metrics-grid { grid-template-columns: repeat(2, 1fr); }
            .dimension-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <h1>Portfolio Health Report</h1>
    <div class="meta">
        <span><strong>Date:</strong> YYYY-MM-DD</span>
        <span><strong>Value:</strong> [Amount]</span>
        <span><strong>Benchmark:</strong> [Index]</span>
        <span><strong>Period:</strong> [Start] to [End]</span>
    </div>

    <!-- HEALTH SCORE -->
    <div class="health-score">
        <div class="score">[X] / 100</div>
        <div class="subtitle">Portfolio Health Score</div>
    </div>

    <!-- DIMENSION BREAKDOWN -->
    <div class="dimension-grid">
        <div class="dimension-card [good/warning/danger]">
            <div class="dim-title">Returns</div>
            <div class="dim-score">[X] / 20</div>
            <div class="dim-detail">[Key finding]</div>
        </div>
        <div class="dimension-card [good/warning/danger]">
            <div class="dim-title">Risk-Adjusted Performance</div>
            <div class="dim-score">[X] / 20</div>
            <div class="dim-detail">[Key finding]</div>
        </div>
        <div class="dimension-card [good/warning/danger]">
            <div class="dim-title">Diversification</div>
            <div class="dim-score">[X] / 20</div>
            <div class="dim-detail">[Key finding]</div>
        </div>
        <div class="dimension-card [good/warning/danger]">
            <div class="dim-title">Factor Alignment</div>
            <div class="dim-score">[X] / 20</div>
            <div class="dim-detail">[Key finding]</div>
        </div>
        <div class="dimension-card [good/warning/danger]">
            <div class="dim-title">Behavioral Health</div>
            <div class="dim-score">[X] / 20</div>
            <div class="dim-detail">[Key finding]</div>
        </div>
    </div>

    <!-- RETURN ANALYSIS -->
    <section class="card">
        <h2>Return Analysis</h2>
        <h3>Position-Level Returns</h3>
        <table>
            <tr>
                <th>Ticker</th><th>Sector</th><th>Weight</th><th>Entry</th>
                <th>Current</th><th>Return</th><th>Ann. Return</th><th>Contribution</th>
            </tr>
            <tr>
                <td><strong>[TICKER]</strong></td><td>[Sector]</td><td>X.X%</td>
                <td>[Price]</td><td>[Price]</td>
                <td class="positive">+X.X%</td><td class="positive">+X.X%</td>
                <td class="positive">+X.X%</td>
            </tr>
            <!-- Repeat for each position -->
        </table>
        <h3>Benchmark Comparison</h3>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="value positive">+X.X%</div>
                <div class="label">Portfolio Return</div>
            </div>
            <div class="metric-card">
                <div class="value">+X.X%</div>
                <div class="label">Benchmark Return</div>
            </div>
            <div class="metric-card">
                <div class="value positive">+X.X%</div>
                <div class="label">Alpha</div>
            </div>
            <div class="metric-card">
                <div class="value">X.X%</div>
                <div class="label">Win Rate</div>
            </div>
        </div>
    </section>

    <!-- RISK METRICS -->
    <section class="card">
        <h2>Risk Metrics</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="value">X.X%</div>
                <div class="label">Annualized Vol</div>
            </div>
            <div class="metric-card">
                <div class="value">X.XX</div>
                <div class="label">Beta</div>
            </div>
            <div class="metric-card">
                <div class="value negative">-X.X%</div>
                <div class="label">Max Drawdown</div>
            </div>
            <div class="metric-card">
                <div class="value positive">X.XX</div>
                <div class="label">Sharpe</div>
            </div>
            <div class="metric-card">
                <div class="value positive">X.XX</div>
                <div class="label">Sortino</div>
            </div>
            <div class="metric-card">
                <div class="value">X.XX</div>
                <div class="label">Calmar</div>
            </div>
        </div>
        <table>
            <tr><th>Metric</th><th>Portfolio</th><th>Benchmark</th><th>Assessment</th></tr>
            <tr><td>Volatility</td><td>X.X%</td><td>X.X%</td><td>[Assessment]</td></tr>
            <tr><td>Max Drawdown</td><td>X.X%</td><td>X.X%</td><td>[Assessment]</td></tr>
            <tr><td>Sharpe</td><td>X.XX</td><td>X.XX</td><td>[Assessment]</td></tr>
            <tr><td>Sortino</td><td>X.XX</td><td>X.XX</td><td>[Assessment]</td></tr>
            <tr><td>Info Ratio</td><td>X.XX</td><td>—</td><td>[Assessment]</td></tr>
        </table>
        <h3>Tail Risk</h3>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="value negative">-X.X%</div>
                <div class="label">VaR (95%, monthly)</div>
            </div>
            <div class="metric-card">
                <div class="value negative">-X.X%</div>
                <div class="label">CVaR (95%)</div>
            </div>
        </div>
    </section>

    <!-- FACTOR EXPOSURE -->
    <section class="card">
        <h2>Factor Exposure</h2>
        <table>
            <tr><th>Factor</th><th>Portfolio</th><th>Ideal (for regime)</th><th>Gap</th><th>Action</th></tr>
            <tr><td>Value</td><td>X.XX σ</td><td>X.XX σ</td><td>[±X.XX]</td><td>[Over/Under/Aligned]</td></tr>
            <tr><td>Quality</td><td>X.XX σ</td><td>X.XX σ</td><td>[±X.XX]</td><td>[Over/Under/Aligned]</td></tr>
            <tr><td>Momentum</td><td>X.XX σ</td><td>X.XX σ</td><td>[±X.XX]</td><td>[Over/Under/Aligned]</td></tr>
            <tr><td>Low Vol</td><td>X.XX σ</td><td>X.XX σ</td><td>[±X.XX]</td><td>[Over/Under/Aligned]</td></tr>
        </table>
        <h3>Regime Alignment</h3>
        <p>Current macro regime: <span class="badge badge-blue">[Label]</span></p>
        <p style="color: var(--text-muted);">Your factor mix is: [Aligned / Misaligned] — [reason]</p>
    </section>

    <!-- CONCENTRATION & CORRELATION -->
    <section class="card">
        <h2>Concentration & Correlation</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="value">X.X%</div>
                <div class="label">Top 3 Weight</div>
            </div>
            <div class="metric-card">
                <div class="value">X.X%</div>
                <div class="label">Top 5 Weight</div>
            </div>
            <div class="metric-card">
                <div class="value">X.X</div>
                <div class="label">Effective N</div>
            </div>
            <div class="metric-card">
                <div class="value">X.XX</div>
                <div class="label">Avg Pairwise Corr</div>
            </div>
        </div>
        <h3>Sector Concentration</h3>
        <table>
            <tr><th>Sector</th><th>Portfolio</th><th>Benchmark</th><th>Active Bet</th></tr>
            <!-- Repeat per sector -->
        </table>
        <h3>Correlation Flags</h3>
        <p style="color: var(--text-muted);">
            Highest correlated pair: <strong>[A] ↔ [B]</strong> = X.XX
            <span class="badge badge-red" style="margin-left: 0.5rem;">⚠ > 0.7</span>
        </p>
        <p style="color: var(--text-muted);">
            True independent risk clusters: <strong>X</strong>
            (you have N positions but only X clusters of independent risk)
        </p>
    </section>

    <!-- BEHAVIORAL AUDIT -->
    <section class="card">
        <h2>Behavioral Audit</h2>
        <div class="behavioral-flag detected">
            <span class="badge badge-red">DETECTED</span>
            <strong>[Pattern Name]</strong> — [Evidence + specific positions]
        </div>
        <div class="behavioral-flag clear">
            <span class="badge badge-green">CLEAR</span>
            <strong>[Pattern Name]</strong> — No evidence found
        </div>
        <!-- Repeat for each pattern checked -->
    </section>

    <!-- RECOMMENDATIONS -->
    <section class="card">
        <h2>Recommendations (Prioritized)</h2>

        <h3>Priority 1: Immediate Action</h3>
        <div class="recommendation urgent">
            <div class="rec-title">1. [Action] — [Ticker]</div>
            <div class="rec-detail">[Detail + rationale + expected impact]</div>
        </div>

        <h3>Priority 2: Next Rebalance</h3>
        <div class="recommendation moderate">
            <div class="rec-title">1. [Action] — [Ticker]</div>
            <div class="rec-detail">[Detail + rationale + expected impact]</div>
        </div>

        <h3>Priority 3: Structural Improvements</h3>
        <div class="recommendation low">
            <div class="rec-title">1. [Action]</div>
            <div class="rec-detail">[Detail + expected improvement]</div>
        </div>
    </section>

    <!-- NEXT STEPS -->
    <section class="card">
        <h2>What to Do Next</h2>
        <table>
            <tr><th>Timeframe</th><th>Action</th></tr>
            <tr><td><strong>This week</strong></td><td>[Most urgent action]</td></tr>
            <tr><td><strong>This month</strong></td><td>[Scheduled rebalancing]</td></tr>
            <tr><td><strong>This quarter</strong></td><td>[Strategic improvement]</td></tr>
            <tr><td><strong>Monitor</strong></td><td>[Key metrics/events to watch]</td></tr>
        </table>
    </section>

    <div class="footer">
        <p>Generated using investment-management skill (Mode B: Portfolio Analysis).
        All metrics computed from available price data. Risk estimates are probabilistic —
        actual outcomes may exceed these bounds in extreme scenarios.</p>
        <p>Report generated: [DateTime]</p>
    </div>
</body>
</html>
```

---

## Output Format Rules

1. **ALL reports MUST be self-contained HTML** — inline CSS, no external dependencies
2. **Save with `.html` extension** — never `.md`
3. **Dark theme by default** — the CSS variables above provide a professional dark palette
4. **Responsive** — works on desktop and mobile viewport
5. **Interactive-ready** — the template structure supports adding JavaScript for sorting tables, toggling sections, or rendering charts if needed
6. **Print-friendly consideration** — when printing, the dark background can be overridden with `@media print` rules if needed
7. **Tables must use proper `<th>` and `<td>`** — never raw text alignment
8. **Color coding** — use `.positive` (green), `.negative` (red), `.neutral` (yellow) classes for returns/metrics
9. **Badges** — use for regime labels, status indicators, and categorical data
10. **Metric cards** — use the grid layout for key KPIs that deserve visual prominence
