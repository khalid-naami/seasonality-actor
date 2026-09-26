"""
Comprehensive Financial Seasonality Analytics Engine.
Calculates Multi-Period Cumulative Curves, Day-of-Week Win Rates, Monthly Matrices,
Quarterly Probabilities, and AI-Ready Market Biases.
"""

import numpy as np
import pandas as pd
from datetime import datetime
from src.constants import MONTH_NAMES, DAYS_OF_WEEK, QUARTERS


def compute_seasonality_analysis(
    df: pd.DataFrame,
    symbol: str,
    asset_name: str,
    asset_type: str,
    source_used: str,
    ticker_used: str,
    years_back: int | None = None,
    periods: list[int] = [5, 10, 15, 20],
    include_monthly_matrix: bool = True,
    include_probabilities: bool = True,
    include_daily_curves: bool = True,
) -> dict | None:
    """
    Core mathematical engine for seasonality calculations.
    """
    if df is None or df.empty or len(df) < 50:
        return None

    # Calculate returns
    clean_df = df.copy()
    clean_df['return'] = clean_df['Close'].pct_change().fillna(0)

    # Filter full years
    years_with_jan = clean_df[clean_df.index.month == 1].index.year.unique()
    years_with_dec = clean_df[clean_df.index.month == 12].index.year.unique()
    valid_years = sorted(list(set(years_with_jan) & set(years_with_dec)))

    if not valid_years:
        # Fallback if less than 1 full year or incomplete
        valid_years = sorted(list(clean_df.index.year.unique()))
        if len(valid_years) < 2:
            return None

    if years_back and years_back > 0 and len(valid_years) > years_back:
        valid_years = valid_years[-years_back:]

    start_year = valid_years[0]
    end_year = valid_years[-1]
    filtered_df = clean_df[(clean_df.index.year >= start_year) & (clean_df.index.year <= end_year)].copy()

    if filtered_df.empty:
        return None

    is_crypto = "crypto" in str(asset_type).lower() or "btc" in symbol.lower() or "eth" in symbol.lower()
    days_in_cycle = 365 if is_crypto else 252

    # 1. Calculate Monthly Return Matrix (Year x Month)
    monthly_data = {}
    for y in valid_years:
        ydf = filtered_df[filtered_df.index.year == y]
        m_returns = ydf.groupby(ydf.index.month)['return'].apply(lambda x: ((1 + x).prod() - 1) * 100)
        monthly_data[int(y)] = {MONTH_NAMES[m - 1]: round(float(m_returns.get(m, 0.0)), 2) for m in range(1, 13)}

    # 2. Monthly Statistical Summary (Jan - Dec)
    monthly_stats = []
    month_avg_list = []
    for m_idx in range(1, 13):
        m_name = MONTH_NAMES[m_idx - 1]
        m_vals = [monthly_data[y][m_name] for y in valid_years if m_name in monthly_data[y]]
        
        if m_vals:
            pos = sum(1 for v in m_vals if v > 0)
            neg = sum(1 for v in m_vals if v < 0)
            total = len(m_vals)
            win_rate = round((pos / total) * 100, 1) if total > 0 else 0.0
            avg_ret = round(float(np.mean(m_vals)), 2)
            med_ret = round(float(np.median(m_vals)), 2)
            max_ret = round(float(np.max(m_vals)), 2)
            min_ret = round(float(np.min(m_vals)), 2)
            vol_ret = round(float(np.std(m_vals)), 2)

            month_avg_list.append((m_name, avg_ret, win_rate))
            monthly_stats.append({
                "month": m_name,
                "monthNumber": m_idx,
                "winRatePct": win_rate,
                "averageReturnPct": avg_ret,
                "medianReturnPct": med_ret,
                "maxReturnPct": max_ret,
                "minReturnPct": min_ret,
                "volatilityPct": vol_ret,
                "positiveYears": pos,
                "negativeYears": neg,
                "totalYears": total
            })

    # 3. Day of Week Probabilities (Mon - Fri)
    day_of_week_stats = []
    if include_probabilities:
        filtered_df['dow'] = filtered_df.index.dayofweek
        for d_idx in range(5):
            d_name = DAYS_OF_WEEK[d_idx]
            d_df = filtered_df[filtered_df['dow'] == d_idx]
            if not d_df.empty:
                pos = sum(1 for r in d_df['return'] if r > 0)
                tot = len(d_df)
                win_rate = round((pos / tot) * 100, 1) if tot > 0 else 0.0
                avg_ret = round(float(d_df['return'].mean() * 100), 3)
                day_of_week_stats.append({
                    "day": d_name,
                    "winRatePct": win_rate,
                    "averageReturnPct": avg_ret,
                    "totalDaysAnalyzed": tot
                })

    # 4. Quarterly Analysis (Q1 - Q4)
    quarterly_stats = []
    if include_probabilities:
        filtered_df['quarter'] = filtered_df.index.quarter
        for q_idx in range(1, 5):
            q_name = QUARTERS[q_idx - 1]
            q_returns = []
            for y in valid_years:
                ydf = filtered_df[(filtered_df.index.year == y) & (filtered_df['quarter'] == q_idx)]
                if not ydf.empty:
                    q_ret = ((1 + ydf['return']).prod() - 1) * 100
                    q_returns.append(q_ret)
            
            if q_returns:
                pos = sum(1 for v in q_returns if v > 0)
                tot = len(q_returns)
                quarterly_stats.append({
                    "quarter": q_name,
                    "winRatePct": round((pos / tot) * 100, 1) if tot > 0 else 0.0,
                    "averageReturnPct": round(float(np.mean(q_returns)), 2),
                    "medianReturnPct": round(float(np.median(q_returns)), 2),
                    "positiveYears": pos,
                    "negativeYears": tot - pos,
                    "totalYears": tot
                })

    # 5. Multi-Period Seasonal Cumulative Trajectories (Curves)
    seasonal_curves = {}
    if include_daily_curves:
        # Build matrix of day_in_year returns
        yearly_day_returns = {}
        for y in valid_years:
            ydf = filtered_df[filtered_df.index.year == y]
            yearly_day_returns[y] = ydf['return'].reset_index(drop=True)
        
        curves_df = pd.DataFrame(yearly_day_returns)
        
        # Calculate cumulative returns per year, then average across periods
        cum_years = curves_df.cumsum() * 100

        # All-time curve
        all_time_mean = cum_years.mean(axis=1).dropna().tolist()
        seasonal_curves["allTime"] = [round(float(v), 2) for v in all_time_mean[:days_in_cycle]]

        # Custom periods (e.g. 5Y, 10Y, 20Y)
        for p in periods:
            if len(valid_years) >= p:
                selected_cols = valid_years[-p:]
                p_curve = cum_years[selected_cols].mean(axis=1).dropna().tolist()
                seasonal_curves[f"{p}Y"] = [round(float(v), 2) for v in p_curve[:days_in_cycle]]

    # 6. Actionable AI Summary & Market Bias
    best_month = max(month_avg_list, key=lambda x: x[1]) if month_avg_list else ("N/A", 0, 0)
    worst_month = min(month_avg_list, key=lambda x: x[1]) if month_avg_list else ("N/A", 0, 0)
    highest_winrate_month = max(month_avg_list, key=lambda x: x[2]) if month_avg_list else ("N/A", 0, 0)
    
    current_month_name = MONTH_NAMES[datetime.now().month - 1]
    current_m_stat = next((m for m in monthly_stats if m["month"] == current_month_name), None)

    overall_bias = "BULLISH" if np.mean([m[1] for m in month_avg_list]) > 0 else "BEARISH"

    ai_insights = {
        "overallBias": overall_bias,
        "bestMonthHistorical": {"month": best_month[0], "avgReturnPct": best_month[1], "winRatePct": best_month[2]},
        "worstMonthHistorical": {"month": worst_month[0], "avgReturnPct": worst_month[1], "winRatePct": worst_month[2]},
        "highestWinRateMonth": {"month": highest_winrate_month[0], "winRatePct": highest_winrate_month[2], "avgReturnPct": highest_winrate_month[1]},
        "currentMonthOutlook": {
            "month": current_month_name,
            "historicalWinRatePct": current_m_stat["winRatePct"] if current_m_stat else None,
            "historicalAvgReturnPct": current_m_stat["averageReturnPct"] if current_m_stat else None,
            "bias": "BULLISH" if current_m_stat and current_m_stat["averageReturnPct"] > 0 else "BEARISH"
        },
        "executiveSummary": (
            f"{symbol} ({asset_name}) historical seasonality spans {len(valid_years)} years ({start_year}-{end_year}). "
            f"Strongest calendar month is {best_month[0]} (+{best_month[1]}% avg, {best_month[2]}% win rate). "
            f"Weakest calendar month is {worst_month[0]} ({worst_month[1]}% avg, {worst_month[2]}% win rate). "
            f"For current month ({current_month_name}), historical win rate is {current_m_stat['winRatePct'] if current_m_stat else 'N/A'}% "
            f"with an average return of {current_m_stat['averageReturnPct'] if current_m_stat else 'N/A'}%."
        )
    }

    result = {
        "symbol": symbol.upper(),
        "name": asset_name,
        "assetType": asset_type,
        "dataProvider": source_used,
        "tickerUsed": ticker_used,
        "yearsAnalyzed": len(valid_years),
        "historyRange": f"{start_year} - {end_year}",
        "latestPrice": round(float(filtered_df['Close'].iloc[-1]), 4),
        "lastUpdated": filtered_df.index[-1].strftime('%Y-%m-%d'),
        "aiInsights": ai_insights,
        "monthlyStatistics": monthly_stats,
        "dayOfWeekProbabilities": day_of_week_stats if include_probabilities else None,
        "quarterlyStatistics": quarterly_stats if include_probabilities else None,
        "seasonalTrajectories": seasonal_curves if include_daily_curves else None,
        "monthlyMatrix": monthly_data if include_monthly_matrix else None,
    }

    return result
