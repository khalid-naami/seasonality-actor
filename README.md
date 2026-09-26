# Financial Seasonality & Multi-Asset Probability Analytics Actor 📈

Analyze **historical seasonal trajectories**, **calendar win rates**, **day-of-week probabilities**, and **quarterly performance metrics** across Stocks, ETFs, Forex pairs, Cryptocurrencies, Commodities, and Federal Reserve (FRED) macroeconomic series.

Built for **algorithmic traders**, **quantitative researchers**, **portfolio managers**, and **AI Agents (MCP & LLMs)** seeking pre-calculated market biases.

---

## 🌟 Key Features

- **Multi-Asset Coverage**: Analyzes US Equities (`AAPL`, `NVDA`), ETFs (`SPY`, `QQQ`), Commodities (`GC=F` Gold, `CL=F` Crude Oil, `SI=F` Silver), Forex (`EURUSD`, `GBPUSD`, `USDJPY`), Crypto (`BTC-USD`, `ETH-USD`), and Macro (`CPI`, `FEDFUNDS`, `US10Y`).
- **Triple Data Source Engine**:
  - **Yahoo Finance**: Real-time global market data.
  - **Stooq**: Direct CSV scraper with up to **100+ years of historical data** (e.g. S&P 500, Gold, Dow Jones) without requiring any API keys.
  - **FRED (Federal Reserve)**: Direct scraper for central bank interest rates, inflation, and macro indicators without API keys.
- **Multi-Period Seasonal Trajectories**: Pre-calculated day-by-day cumulative curves for **5-Year**, **10-Year**, **15-Year**, **20-Year**, and **All-Time** historical benchmarks.
- **Calendar & Probability Matrix**:
  - **Monthly Analysis**: Month-by-month win rate (%), mean return, median, max/min, volatility, and positive/negative year counts.
  - **Day-of-Week Probabilities**: Monday through Friday closing probability and average returns.
  - **Quarterly Breakdown**: Q1, Q2, Q3, and Q4 performance distributions.
  - **Full Monthly Matrix**: Complete historical Year x Month returns table.
- **AI Agent & MCP Ready**: Generates an executive market summary with bias classifications (`BULLISH` / `BEARISH`) and current month historical outlooks ready for LLMs, Claude, ChatGPT, and LangChain.

---

## 📥 Input Configuration

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `symbols` | `Array<string>` | `["SPY", "GC=F", "BTC-USD", "EURUSD=X"]` | List of tickers or symbols to analyze. |
| `dataProvider` | `String` | `"auto"` | Choose `"auto"` (longest history wins), `"yahoo"`, `"stooq"`, or `"fred"`. |
| `yearsBack` | `Integer` | `0` | Number of years to analyze (`0` for all available history). |
| `seasonalPeriods` | `Array<number>` | `[5, 10, 15, 20]` | Lookback periods for cumulative seasonal curves. |
| `includeMonthlyMatrix`| `Boolean` | `true` | Include the full Year x Month return matrix. |
| `includeProbabilities` | `Boolean` | `true` | Include Day-of-Week and Quarterly win rates. |
| `includeDailyCurves` | `Boolean` | `true` | Include daily normalized cumulative seasonal trajectories. |

### Example Input (`input.json`):
```json
{
  "symbols": ["SPY", "GC=F", "BTC-USD", "EURUSD=X", "CPI"],
  "dataProvider": "auto",
  "yearsBack": 0,
  "seasonalPeriods": [5, 10, 20],
  "includeMonthlyMatrix": true,
  "includeProbabilities": true,
  "includeDailyCurves": true
}
```

---

## 📤 Output Dataset Format

Each dataset record contains comprehensive statistics and AI insights:

```json
{
  "symbol": "SPY",
  "name": "SPDR S&P 500 ETF",
  "assetType": "ETF",
  "dataProvider": "Stooq",
  "tickerUsed": "SPY.US",
  "yearsAnalyzed": 31,
  "historyRange": "1994 - 2025",
  "latestPrice": 580.45,
  "lastUpdated": "2026-09-26",
  "aiInsights": {
    "overallBias": "BULLISH",
    "bestMonthHistorical": {
      "month": "Nov",
      "avgReturnPct": 2.45,
      "winRatePct": 80.6
    },
    "worstMonthHistorical": {
      "month": "Sep",
      "avgReturnPct": -0.85,
      "winRatePct": 45.2
    },
    "currentMonthOutlook": {
      "month": "Sep",
      "historicalWinRatePct": 45.2,
      "historicalAvgReturnPct": -0.85,
      "bias": "BEARISH"
    },
    "executiveSummary": "SPY (SPDR S&P 500 ETF) historical seasonality spans 31 years (1994-2025). Strongest calendar month is Nov (+2.45% avg, 80.6% win rate)..."
  },
  "monthlyStatistics": [
    {
      "month": "Jan",
      "monthNumber": 1,
      "winRatePct": 61.3,
      "averageReturnPct": 1.12,
      "medianReturnPct": 1.45,
      "maxReturnPct": 8.05,
      "minReturnPct": -8.57,
      "volatilityPct": 4.12,
      "positiveYears": 19,
      "negativeYears": 12,
      "totalYears": 31
    }
  ],
  "dayOfWeekProbabilities": [
    { "day": "Monday", "winRatePct": 54.2, "averageReturnPct": 0.045 },
    { "day": "Tuesday", "winRatePct": 55.1, "averageReturnPct": 0.062 },
    { "day": "Wednesday", "winRatePct": 56.4, "averageReturnPct": 0.078 },
    { "day": "Thursday", "winRatePct": 53.8, "averageReturnPct": 0.039 },
    { "day": "Friday", "winRatePct": 52.1, "averageReturnPct": 0.028 }
  ],
  "quarterlyStatistics": [
    { "quarter": "Q1", "winRatePct": 67.7, "averageReturnPct": 2.85 },
    { "quarter": "Q2", "winRatePct": 71.0, "averageReturnPct": 3.42 },
    { "quarter": "Q3", "winRatePct": 58.1, "averageReturnPct": 0.95 },
    { "quarter": "Q4", "winRatePct": 80.6, "averageReturnPct": 4.65 }
  ],
  "seasonalTrajectories": {
    "5Y": [0.0, 0.12, 0.35, 0.48],
    "10Y": [0.0, 0.08, 0.22, 0.41],
    "20Y": [0.0, 0.05, 0.18, 0.36],
    "allTime": [0.0, 0.06, 0.19, 0.38]
  }
}
```

---

## 🤖 AI Agent & MCP Integration

Because this Actor outputs clean, pre-calculated probabilities and executive summaries, it is 100% plug-and-play with **Apify Model Context Protocol (MCP)** servers, OpenAI GPTs, Claude Tools, and LangChain/CrewAI agents.

### Apify Python Client Example:
```python
from apify_client import ApifyClient

client = ApifyClient("<YOUR_API_TOKEN>")

run_input = {
    "symbols": ["SPY", "GC=F", "EURUSD=X", "BTC-USD"],
    "dataProvider": "auto"
}

run = client.actor("khnaami/financial-seasonality-actor").call(run_input=run_input)

for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(f"Symbol: {item['symbol']} | Best Month: {item['aiInsights']['bestMonthHistorical']['month']}")
```

### Apify JavaScript / TypeScript Client Example:
```typescript
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({
    token: '<YOUR_API_TOKEN>',
});

const run = await client.actor('khnaami/financial-seasonality-actor').call({
    symbols: ['SPY', 'GC=F', 'EURUSD=X'],
    dataProvider: 'auto',
});

const { items } = await client.dataset(run.defaultDatasetId).listItems();
console.log(items);
```

---

## ⚖️ Disclaimer

*This Actor provides statistical and historical seasonality metrics for educational and analytical purposes only. It is not financial or investment advice.*
