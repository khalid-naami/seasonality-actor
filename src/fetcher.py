"""
Unified Multi-Source Data Fetcher for Financial Seasonality.
Supports Yahoo Finance, Stooq (100+ yrs history), and FRED (Free Direct CSV without API key).
"""

import io
import os
import subprocess
import logging
import requests
import pandas as pd
import yfinance as yf
from src.constants import TICKER_MAPPINGS

logger = logging.getLogger(__name__)

def map_symbol(symbol: str, source: str) -> str:
    """Normalize and map generic user symbol to source-specific ticker."""
    s = symbol.upper().strip()
    if s in TICKER_MAPPINGS:
        mapped = TICKER_MAPPINGS[s].get(source.lower())
        if mapped:
            return mapped

    # Heuristic rules
    source_lower = source.lower()
    if source_lower == "stooq":
        if s == "^GSPC": return "^SPX"
        if s == "^IXIC" or s == "^NDX": return "^NDQ"
        if s.endswith("=X"): return s.replace("=X", "")
        if len(s) <= 5 and "." not in s and s.isalpha():
            return f"{s}.US"
    elif source_lower == "yahoo":
        if s == "XAUUSD": return "GC=F"
        if s == "XAGUSD": return "SI=F"
        if len(s) == 6 and s.isalpha() and not s.endswith("=X"):
            return f"{s}=X"
    elif source_lower == "fred":
        if s in ["CPI", "INFLATION"]: return "CPIAUCSL"
        if s in ["FEDRATE", "FEDFUNDS"]: return "FEDFUNDS"
        if s in ["GOLD", "XAUUSD"]: return "GOLDAMGBD228NLBM"
        if s in ["OIL", "CRUDE"]: return "DCOILWTICO"
        if s == "EURUSD": return "DEXUSEU"
        if s == "GBPUSD": return "DEXUSUK"
        if s == "USDJPY": return "DEXJPUS"
        if s in ["10Y", "US10Y"]: return "DGS10"
        
    return s


def fetch_stooq_direct(ticker: str) -> pd.DataFrame | None:
    """Fetch raw daily CSV from Stooq without API key."""
    url = f"https://stooq.com/q/d/l/?s={ticker.lower()}&i=d"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    # Try requests first
    try:
        resp = requests.get(url, headers=headers, timeout=12)
        if resp.status_code == 200 and "Date" in resp.text:
            df = pd.read_csv(io.StringIO(resp.text))
            return _process_stooq_df(df)
    except Exception as e:
        logger.debug(f"Requests failed for Stooq {ticker}: {e}")

    # Fallback to curl with http1.1
    try:
        cmd = ["curl.exe" if os.name == "nt" else "curl", "-s", "--http1.1", url]
        out = subprocess.check_output(cmd, timeout=12)
        if b"Date" in out:
            df = pd.read_csv(io.BytesIO(out))
            return _process_stooq_df(df)
    except Exception as e:
        logger.debug(f"Curl failed for Stooq {ticker}: {e}")

    return None


def _process_stooq_df(df: pd.DataFrame) -> pd.DataFrame | None:
    if df.empty or 'Date' not in df.columns:
        return None
    col = 'Close' if 'Close' in df.columns else ('Value' if 'Value' in df.columns else None)
    if not col:
        return None
    
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    df.set_index('Date', inplace=True)
    df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df[[col]].dropna().sort_index()
    df.columns = ['Close']
    return df if not df.empty else None


def fetch_fred_direct(series_id: str) -> pd.DataFrame | None:
    """Fetch historical economic series from FRED directly without API key."""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    
    # Try curl with --http1.1 first (highest reliability for FRED)
    try:
        cmd = ["curl.exe" if os.name == "nt" else "curl", "-s", "--http1.1", url]
        out = subprocess.check_output(cmd, timeout=15)
        if b"observation_date" in out or b"DATE" in out:
            df = pd.read_csv(io.BytesIO(out))
            return _process_fred_df(df)
    except Exception as e:
        logger.debug(f"Curl failed for FRED {series_id}: {e}")

    # Fallback to requests
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200 and ("observation_date" in resp.text or "DATE" in resp.text):
            df = pd.read_csv(io.StringIO(resp.text))
            return _process_fred_df(df)
    except Exception as e:
        logger.debug(f"Requests failed for FRED {series_id}: {e}")

    return None


def _process_fred_df(df: pd.DataFrame) -> pd.DataFrame | None:
    if df.empty:
        return None
    date_col = 'observation_date' if 'observation_date' in df.columns else ('DATE' if 'DATE' in df.columns else df.columns[0])
    val_col = df.columns[1] if len(df.columns) > 1 else None
    if not val_col:
        return None
    
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=[date_col])
    df.set_index(date_col, inplace=True)
    df[val_col] = pd.to_numeric(df[val_col], errors='coerce')
    df = df[[val_col]].dropna().sort_index()
    df.columns = ['Close']
    return df if not df.empty else None


def fetch_yahoo_direct(ticker: str) -> tuple[pd.DataFrame | None, str, str]:
    """Fetch daily adjusted close from Yahoo Finance."""
    try:
        data = yf.download(ticker, start='1900-01-01', auto_adjust=True, progress=False)
        if data is not None and not data.empty:
            if isinstance(data.columns, pd.MultiIndex):
                try:
                    if ticker in data.columns.get_level_values(1):
                        close_data = data.loc[:, ('Close', ticker)]
                    else:
                        close_data = data['Close']
                except Exception:
                    close_data = data['Close']
            else:
                close_data = data['Close']

            if isinstance(close_data, pd.DataFrame):
                close_data = close_data.iloc[:, 0]

            df = pd.DataFrame({'Close': pd.to_numeric(close_data, errors='coerce')}).dropna().sort_index()
            
            # Fetch metadata
            short_name, quote_type = ticker, "EQUITY"
            try:
                info = yf.Ticker(ticker).info
                short_name = info.get('shortName', ticker)
                quote_type = info.get('quoteType', 'EQUITY')
            except Exception:
                pass
            return df, short_name, quote_type
    except Exception as e:
        logger.debug(f"Yahoo fetch error for {ticker}: {e}")

    return None, ticker, "EQUITY"


def get_market_data(symbol: str, preferred_source: str = "auto") -> dict | None:
    """
    Fetch market data using user preference or auto-selecting the source with the longest history.
    """
    symbol_clean = symbol.upper().strip()
    meta = TICKER_MAPPINGS.get(symbol_clean, {})
    asset_name = meta.get("name", symbol_clean)
    asset_type = meta.get("type", "EQUITY")

    candidates = []

    # 1. Stooq
    if preferred_source in ["auto", "stooq"]:
        st_ticker = map_symbol(symbol_clean, "stooq")
        if st_ticker:
            st_df = fetch_stooq_direct(st_ticker)
            if st_df is not None and len(st_df) > 30:
                candidates.append({
                    "df": st_df,
                    "source": "Stooq",
                    "ticker": st_ticker,
                    "name": asset_name,
                    "type": asset_type,
                    "len": len(st_df)
                })

    # 2. Yahoo Finance
    if preferred_source in ["auto", "yahoo"]:
        yf_ticker = map_symbol(symbol_clean, "yahoo")
        if yf_ticker:
            yf_df, yf_name, yf_type = fetch_yahoo_direct(yf_ticker)
            if yf_df is not None and len(yf_df) > 30:
                candidates.append({
                    "df": yf_df,
                    "source": "Yahoo Finance",
                    "ticker": yf_ticker,
                    "name": yf_name if yf_name else asset_name,
                    "type": yf_type if yf_type else asset_type,
                    "len": len(yf_df)
                })

    # 3. FRED
    if preferred_source in ["auto", "fred"]:
        fr_series = map_symbol(symbol_clean, "fred")
        if fr_series:
            fr_df = fetch_fred_direct(fr_series)
            if fr_df is not None and len(fr_df) > 30:
                candidates.append({
                    "df": fr_df,
                    "source": "FRED",
                    "ticker": fr_series,
                    "name": asset_name,
                    "type": "MACRO" if asset_type == "EQUITY" else asset_type,
                    "len": len(fr_df)
                })

    if not candidates:
        return None

    # If preferred_source is specific and matched, pick it. Otherwise pick longest history.
    if preferred_source != "auto":
        for c in candidates:
            if c["source"].lower().startswith(preferred_source.lower()):
                return c

    # Longest history wins
    best = sorted(candidates, key=lambda x: x["len"], reverse=True)[0]
    return best
