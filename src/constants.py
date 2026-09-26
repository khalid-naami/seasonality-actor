"""
Constants, mappings, and tickers definitions for Financial Seasonality Actor.
"""

MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
QUARTERS = ['Q1', 'Q2', 'Q3', 'Q4']

# Predefined asset mappings across data providers
TICKER_MAPPINGS = {
    # US Major Indices & ETFs
    "SPX": {"yahoo": "^GSPC", "stooq": "^SPX", "fred": None, "name": "S&P 500 Index", "type": "INDEX"},
    "SPY": {"yahoo": "SPY", "stooq": "SPY.US", "fred": None, "name": "SPDR S&P 500 ETF", "type": "ETF"},
    "QQQ": {"yahoo": "QQQ", "stooq": "QQQ.US", "fred": None, "name": "Invesco QQQ Trust (Nasdaq 100)", "type": "ETF"},
    "NDX": {"yahoo": "^NDX", "stooq": "^NDQ", "fred": None, "name": "Nasdaq 100 Index", "type": "INDEX"},
    "DJI": {"yahoo": "^DJI", "stooq": "^DJI", "fred": None, "name": "Dow Jones Industrial Average", "type": "INDEX"},
    "DIA": {"yahoo": "DIA", "stooq": "DIA.US", "fred": None, "name": "SPDR Dow Jones Industrial ETF", "type": "ETF"},
    "RUT": {"yahoo": "^RUT", "stooq": "^RUT", "fred": None, "name": "Russell 2000 Index", "type": "INDEX"},
    "IWM": {"yahoo": "IWM", "stooq": "IWM.US", "fred": None, "name": "iShares Russell 2000 ETF", "type": "ETF"},
    
    # Commodities & Precious Metals
    "GOLD": {"yahoo": "GC=F", "stooq": "XAUUSD", "fred": "GOLDAMGBD228NLBM", "name": "Gold (London / Futures)", "type": "COMMODITY"},
    "XAUUSD": {"yahoo": "GC=F", "stooq": "XAUUSD", "fred": "GOLDAMGBD228NLBM", "name": "Gold Spot", "type": "COMMODITY"},
    "GLD": {"yahoo": "GLD", "stooq": "GLD.US", "fred": None, "name": "SPDR Gold Shares ETF", "type": "ETF"},
    "SILVER": {"yahoo": "SI=F", "stooq": "XAGUSD", "fred": None, "name": "Silver Futures", "type": "COMMODITY"},
    "XAGUSD": {"yahoo": "SI=F", "stooq": "XAGUSD", "fred": None, "name": "Silver Spot", "type": "COMMODITY"},
    "SLV": {"yahoo": "SLV", "stooq": "SLV.US", "fred": None, "name": "iShares Silver Trust", "type": "ETF"},
    "OIL": {"yahoo": "CL=F", "stooq": "CL.F", "fred": "DCOILWTICO", "name": "Crude Oil (WTI)", "type": "COMMODITY"},
    "CL": {"yahoo": "CL=F", "stooq": "CL.F", "fred": "DCOILWTICO", "name": "Crude Oil Futures", "type": "COMMODITY"},
    "USO": {"yahoo": "USO", "stooq": "USO.US", "fred": None, "name": "United States Oil Fund", "type": "ETF"},
    "NATGAS": {"yahoo": "NG=F", "stooq": "NG.F", "fred": "DHHNGSP", "name": "Natural Gas (Henry Hub)", "type": "COMMODITY"},
    "COPPER": {"yahoo": "HG=F", "stooq": "HG.F", "fred": "PCOPPUSDM", "name": "Copper Futures", "type": "COMMODITY"},

    # Forex Pairs
    "EURUSD": {"yahoo": "EURUSD=X", "stooq": "EURUSD", "fred": "DEXUSEU", "name": "Euro / US Dollar", "type": "CURRENCY"},
    "GBPUSD": {"yahoo": "GBPUSD=X", "stooq": "GBPUSD", "fred": "DEXUSUK", "name": "British Pound / US Dollar", "type": "CURRENCY"},
    "USDJPY": {"yahoo": "USDJPY=X", "stooq": "USDJPY", "fred": "DEXJPUS", "name": "US Dollar / Japanese Yen", "type": "CURRENCY"},
    "AUDUSD": {"yahoo": "AUDUSD=X", "stooq": "AUDUSD", "fred": "DEXUSAL", "name": "Australian Dollar / US Dollar", "type": "CURRENCY"},
    "USDCAD": {"yahoo": "USDCAD=X", "stooq": "USDCAD", "fred": "DEXCAUS", "name": "US Dollar / Canadian Dollar", "type": "CURRENCY"},
    "USDCHF": {"yahoo": "USDCHF=X", "stooq": "USDCHF", "fred": "DEXSZUS", "name": "US Dollar / Swiss Franc", "type": "CURRENCY"},
    "NZDUSD": {"yahoo": "NZDUSD=X", "stooq": "NZDUSD", "fred": "DEXUSNZ", "name": "New Zealand Dollar / US Dollar", "type": "CURRENCY"},
    "DXY": {"yahoo": "DX-Y.NYB", "stooq": "USD_I", "fred": "DTWEXBGS", "name": "US Dollar Index", "type": "CURRENCY"},

    # Crypto
    "BTC": {"yahoo": "BTC-USD", "stooq": "XBTUSD", "fred": "CBBTCUSD", "name": "Bitcoin", "type": "CRYPTO"},
    "BTC-USD": {"yahoo": "BTC-USD", "stooq": "XBTUSD", "fred": "CBBTCUSD", "name": "Bitcoin", "type": "CRYPTO"},
    "ETH": {"yahoo": "ETH-USD", "stooq": "ETHUSD", "fred": None, "name": "Ethereum", "type": "CRYPTO"},
    "ETH-USD": {"yahoo": "ETH-USD", "stooq": "ETHUSD", "fred": None, "name": "Ethereum", "type": "CRYPTO"},
    "SOL-USD": {"yahoo": "SOL-USD", "stooq": "SOLUSD", "fred": None, "name": "Solana", "type": "CRYPTO"},

    # Macro & Interest Rates (FRED Free Series)
    "CPI": {"yahoo": None, "stooq": None, "fred": "CPIAUCSL", "name": "Consumer Price Index (Inflation)", "type": "MACRO"},
    "FEDFUNDS": {"yahoo": None, "stooq": None, "fred": "FEDFUNDS", "name": "Federal Funds Effective Rate", "type": "MACRO"},
    "US10Y": {"yahoo": "^TNX", "stooq": "10YUS.B", "fred": "DGS10", "name": "10-Year Treasury Yield", "type": "MACRO"},
    "US2Y": {"yahoo": None, "stooq": "2YUS.B", "fred": "DGS2", "name": "2-Year Treasury Yield", "type": "MACRO"},
    "VIX": {"yahoo": "^VIX", "stooq": "^VIX", "fred": "VIXCLS", "name": "CBOE Volatility Index", "type": "INDEX"}
}
