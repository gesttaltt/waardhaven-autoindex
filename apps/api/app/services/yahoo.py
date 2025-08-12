import yfinance as yf
import pandas as pd
from datetime import date

def fetch_prices(symbols: list[str], start: date) -> pd.DataFrame:
    # yfinance will align date index and return a column MultiIndex: [symbol][Close, ...]
    data = yf.download(symbols, start=start, auto_adjust=True, progress=False, group_by='ticker')
    # Ensure DataFrame format is consistent for single symbol
    if isinstance(data.columns, pd.Index):
        # Single symbol case
        sym = symbols[0] if symbols else ""
        data = pd.concat({sym: data}, axis=1)
    return data
