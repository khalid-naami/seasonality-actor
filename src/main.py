"""
Main Apify Actor Entry Point for Financial Seasonality & Market Probabilities.
"""

import asyncio
import logging
from apify import Actor
from src.fetcher import get_market_data
from src.analytics import compute_seasonality_analysis

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def main():
    async with Actor:
        actor_input = await Actor.get_input() or {}
        
        # Parse inputs
        raw_symbols = actor_input.get("symbols", ["SPY", "GC=F", "BTC-USD", "EURUSD=X"])
        if isinstance(raw_symbols, str):
            symbols = [s.strip() for s in raw_symbols.replace(",", "\n").splitlines() if s.strip()]
        elif isinstance(raw_symbols, list):
            symbols = [str(s).strip() for s in raw_symbols if str(s).strip()]
        else:
            symbols = ["SPY", "GC=F", "BTC-USD", "EURUSD=X"]

        data_provider = actor_input.get("dataProvider", "auto")
        years_back = actor_input.get("yearsBack", 0)
        years_back_val = int(years_back) if years_back and int(years_back) > 0 else None
        
        seasonal_periods = actor_input.get("seasonalPeriods", [5, 10, 15, 20])
        include_matrix = actor_input.get("includeMonthlyMatrix", True)
        include_probabilities = actor_input.get("includeProbabilities", True)
        include_daily_curves = actor_input.get("includeDailyCurves", True)

        Actor.log.info(f"Starting Financial Seasonality analysis for {len(symbols)} symbol(s)...")
        Actor.log.info(f"Configuration: Provider='{data_provider}', YearsBack={years_back_val or 'All'}, Periods={seasonal_periods}")

        dataset_items = []
        summary_records = []

        for symbol in symbols:
            Actor.log.info(f"Processing symbol: {symbol} ...")
            try:
                # 1. Fetch raw data
                market_res = get_market_data(symbol, preferred_source=data_provider)
                if not market_res or market_res["df"] is None or market_res["df"].empty:
                    Actor.log.warning(f"Could not fetch historical data for symbol '{symbol}'. Skipping.")
                    continue

                # 2. Compute Seasonality Analytics
                analysis = compute_seasonality_analysis(
                    df=market_res["df"],
                    symbol=symbol,
                    asset_name=market_res["name"],
                    asset_type=market_res["type"],
                    source_used=market_res["source"],
                    ticker_used=market_res["ticker"],
                    years_back=years_back_val,
                    periods=seasonal_periods,
                    include_monthly_matrix=include_matrix,
                    include_probabilities=include_probabilities,
                    include_daily_curves=include_daily_curves
                )

                if not analysis:
                    Actor.log.warning(f"Insufficient history or calculation error for symbol '{symbol}'. Skipping.")
                    continue

                # 3. Push to Apify Dataset
                await Actor.push_data(analysis)
                dataset_items.append(analysis)

                summary_records.append({
                    "symbol": analysis["symbol"],
                    "name": analysis["name"],
                    "provider": analysis["dataProvider"],
                    "history": analysis["historyRange"],
                    "years": analysis["yearsAnalyzed"],
                    "currentMonth": analysis["aiInsights"]["currentMonthOutlook"]["month"],
                    "currentMonthWinRate": f"{analysis['aiInsights']['currentMonthOutlook']['historicalWinRatePct']}%",
                    "currentMonthAvgReturn": f"{analysis['aiInsights']['currentMonthOutlook']['historicalAvgReturnPct']}%",
                    "overallBias": analysis["aiInsights"]["overallBias"]
                })

                Actor.log.info(f"Successfully processed {symbol} ({analysis['dataProvider']}: {analysis['yearsAnalyzed']} years)")

            except Exception as e:
                Actor.log.error(f"Error analyzing {symbol}: {str(e)}")

        # 4. Save High-Level Summary to Key-Value Store for AI / MCP consumption
        if dataset_items:
            output_summary = {
                "totalSymbolsAnalyzed": len(dataset_items),
                "analyzedSymbols": [item["symbol"] for item in dataset_items],
                "marketSummaries": summary_records,
                "aiContextReady": True,
                "message": f"Successfully calculated multi-asset seasonality analytics for {len(dataset_items)} symbol(s)."
            }
            await Actor.set_value("OUTPUT", output_summary)
            Actor.log.info(f"Saved summary report to Key-Value store 'OUTPUT'. Total items: {len(dataset_items)}")
        else:
            Actor.log.warning("No valid seasonality records were produced.")


if __name__ == "__main__":
    asyncio.run(main())
