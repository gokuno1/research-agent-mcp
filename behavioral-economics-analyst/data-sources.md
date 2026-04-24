# Behavioral Economics Data Sources

Complete access guide for all behavioral indicators referenced in the skill. Organized by dimension with access tier (Free / Freemium / Paid).

---

## Macro Behavioral Data

### Sentiment & Narrative

| Indicator | Source | Access | Frequency | URL / Access Method |
|-----------|--------|--------|-----------|---------------------|
| AAII Investor Sentiment | AAII | Free (summary) | Weekly (Thursday) | aaii.com/sentimentsurvey |
| CNN Fear & Greed Index | CNN Business | Free | Daily | money.cnn.com/data/fear-and-greed |
| Put/Call Ratio (equity + index) | CBOE | Free | Daily | cboe.com/market-data |
| Michigan Consumer Sentiment | University of Michigan | Free (preliminary/final) | Monthly | sca.isr.umich.edu |
| Conference Board Consumer Confidence | Conference Board | Freemium (summary free) | Monthly | conference-board.org |
| Google Trends (financial narratives) | Google | Free | Real-time | trends.google.com |
| Media sentiment analysis | Manual / WebSearch | Free | As needed | Search major financial outlet headlines |

### Herding & Crowding

| Indicator | Source | Access | Frequency | URL / Access Method |
|-----------|--------|--------|-----------|---------------------|
| CFTC Commitments of Traders (COT) | CFTC | Free | Weekly (Friday) | cftc.gov/dea/futures/financial.htm |
| ICI Fund Flows | Investment Company Institute | Free | Weekly | ici.org/research/stats |
| NAAIM Exposure Index | NAAIM | Free | Weekly (Wednesday) | naaim.org/programs/naaim-exposure-index |
| Analyst recommendation distribution | Koyfin / Tikr / Bloomberg | Freemium / Paid | Ongoing | koyfin.com, tikr.com |
| Short interest data | Exchange data / FINRA | Free (delayed) | Bi-monthly | finra.org/finra-data/browse-catalog/short-interest |
| 13-F institutional holdings | SEC EDGAR | Free | Quarterly | sec.gov/cgi-bin/browse-edgar (13-F search) |
| ETF flow concentration | etf.com / VettaFi | Free | Daily | etf.com/etf-flow-tool |

### Risk Appetite & Complacency

| Indicator | Source | Access | Frequency | URL / Access Method |
|-----------|--------|--------|-----------|---------------------|
| VIX Index | CBOE | Free | Real-time | cboe.com or any charting platform |
| VIX Futures Term Structure | CBOE / vixcentral.com | Free | Daily | vixcentral.com |
| MOVE Index (bond volatility) | ICE/BofA via TradingView | Freemium | Daily | TradingView: MOVE |
| HY Credit Spreads (OAS) | FRED | Free | Daily | FRED: BAMLH0A0HYM2 |
| IG Credit Spreads | FRED | Free | Daily | FRED: BAMLC0A0CM |
| Chicago Fed NFCI | Federal Reserve | Free | Weekly | chicagofed.org/research/data/nfci |
| Goldman Sachs FCI | Bloomberg | Paid | Daily | Bloomberg terminal only |
| Covenant-lite loan % | LCD / PitchBook | Paid | Quarterly | pitchbook.com/lcd |
| SLOOS (lending standards) | Federal Reserve | Free | Quarterly | federalreserve.gov/data/sloos |

### Expectations Formation

| Indicator | Source | Access | Frequency | URL / Access Method |
|-----------|--------|--------|-----------|---------------------|
| Fed Funds Futures (implied path) | CME FedWatch | Free | Real-time | cmegroup.com/trading/interest-rates/countdown-to-fomc.html |
| Survey of Professional Forecasters | Philadelphia Fed | Free | Quarterly | philadelphiafed.org/surveys-and-data/real-time-data-research/survey-of-professional-forecasters |
| NY Fed Survey of Consumer Expectations | NY Fed | Free | Monthly | newyorkfed.org/microeconomics/sce |
| TIPS Breakeven Inflation (5yr, 10yr) | FRED | Free | Daily | FRED: T5YIE, T10YIE |
| Michigan Inflation Expectations | U of Michigan | Free | Monthly | Included in Michigan Consumer Sentiment |
| Earnings Revision Breadth | Koyfin / Bloomberg | Freemium / Paid | Weekly | koyfin.com |
| Atlanta Fed GDPNow vs. Consensus | Atlanta Fed | Free | Updated frequently | atlantafed.org/cqer/research/gdpnow |

### Animal Spirits & Speculative Excess

| Indicator | Source | Access | Frequency | URL / Access Method |
|-----------|--------|--------|-----------|---------------------|
| IPO issuance volume + returns | Renaissance Capital | Free (summary) | Monthly | renaissancecapital.com |
| FINRA Margin Debt | FINRA | Free | Monthly | finra.org/investors/learn-to-invest/advanced-investing/margin-statistics |
| Options volume (especially 0DTE) | CBOE / OCC | Free | Daily | theocc.com/market-data/market-data-layout |
| Retail trading flow proxies | Vanda Research / Bloomberg | Paid | Daily | vandatrack.com |
| Crypto market cap / altcoin index | CoinGecko / CoinMarketCap | Free | Real-time | coingecko.com |
| NFIB Small Business Optimism | NFIB | Free | Monthly | nfib.com/surveys/small-business-economic-trends |
| Conference Board CEO Confidence | Conference Board | Freemium | Quarterly | conference-board.org |
| VC funding pace | Crunchbase / PitchBook | Freemium / Paid | Quarterly | crunchbase.com |

---

## Micro Behavioral Data

### Management Behavioral Indicators

| Indicator | Source | Access | Frequency | URL / Access Method |
|-----------|--------|--------|-----------|---------------------|
| Earnings call transcripts | Seeking Alpha / Company IR | Free / Freemium | Quarterly | seekingalpha.com (limited free), tikr.com |
| Management guidance vs. actual | Tikr / Koyfin / Bloomberg | Freemium / Paid | Quarterly | Compare guidance to actuals over 8+ quarters |
| M&A history + goodwill writedowns | Company annual reports / SEC | Free | Annual | sec.gov (10-K search) |
| Share buyback timing | Company 10-Q/10-K filings | Free | Quarterly | Cross-reference buyback $ with stock price chart |
| Insider transactions (Form 4) | SEC EDGAR / OpenInsider | Free | As filed | sec.gov/cgi-bin/browse-edgar, openinsider.com |
| CEO compensation structure | Proxy statements (DEF 14A) | Free | Annual | sec.gov (proxy search) |

### Customer & Demand Behavioral Indicators

| Indicator | Source | Access | Frequency | URL / Access Method |
|-----------|--------|--------|-----------|---------------------|
| Brand vs. category search volume | Google Trends | Free | Real-time | trends.google.com (compare brand vs. category) |
| NPS scores | Company disclosures / third-party | Mixed | Varies | Company reports, customer.guru, satmetrix |
| Social media mention velocity | StockTwits / Reddit / Twitter | Free | Real-time | stocktwits.com, reddit.com/r/wallstreetbets |
| App download / active user trends | Sensor Tower / data.ai | Freemium / Paid | Monthly | sensortower.com |
| Subscription churn rates | Company filings (SaaS/subscription) | Free | Quarterly | Earnings calls, investor presentations |

### Market Pricing Behavioral Indicators

| Indicator | Source | Access | Frequency | URL / Access Method |
|-----------|--------|--------|-----------|---------------------|
| Analyst target price clustering | Bloomberg / Koyfin / Tikr | Freemium / Paid | Ongoing | Check dispersion of analyst targets |
| 52-week high/low proximity | Any charting platform | Free | Real-time | TradingView, Yahoo Finance |
| Options implied volatility skew | CBOE / broker platforms | Free / Freemium | Real-time | Broker options chain tools |
| Retail vs. institutional ownership | SEC 13-F / exchange data | Free | Quarterly | WhaleWisdom, sec.gov |
| Post-earnings drift patterns | Any charting platform | Free | Post-earnings | Observe price action 1-30 days post-announcement |
| Short interest + days to cover | FINRA / exchange data | Free (delayed) | Bi-monthly | finra.org, shortsqueeze.com |

### Governance Behavioral Indicators

| Indicator | Source | Access | Frequency | URL / Access Method |
|-----------|--------|--------|-----------|---------------------|
| Board composition / tenure | Proxy statements | Free | Annual | sec.gov (DEF 14A) |
| Related-party transactions | Annual report notes | Free | Annual | Company 10-K, related-party disclosures |
| Auditor changes / qualifications | Company filings | Free | Annual | 10-K auditor's report section |
| Promoter pledge % (India) | BSE/NSE disclosures | Free | Quarterly | bseindia.com, nseindia.com |
| Whistleblower / regulatory actions | SEC / SEBI / news | Free | As occurred | WebSearch for company + "SEC action" / "SEBI order" |

---

## India-Specific Sources (if analyzing Indian markets)

| Indicator | Source | Access |
|-----------|--------|--------|
| FII/DII daily flows | NSDL / moneycontrol | Free |
| RBI Consumer Confidence Survey | RBI | Free (quarterly) |
| India VIX | NSE | Free |
| Promoter holding + pledge data | BSE/NSE | Free |
| Mutual fund flow data | AMFI | Free (monthly) |
| Insider trading disclosures | BSE/NSE | Free |

---

## Data Freshness Guidelines

| Indicator Type | Maximum Acceptable Staleness |
|----------------|------------------------------|
| Sentiment surveys (AAII, Michigan) | 2 weeks |
| Positioning data (COT, fund flows) | 1 week |
| Volatility indicators (VIX, MOVE) | Real-time / same day |
| Management behavioral data (transcripts) | Most recent quarter |
| Governance data (proxy, board) | Most recent annual filing |
| Social sentiment (Google Trends, Reddit) | 1 week |

Flag any data point older than its maximum staleness threshold explicitly in the analysis.
