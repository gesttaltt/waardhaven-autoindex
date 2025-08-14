from twelvedata import TDClient
import pandas as pd
from datetime import date, datetime
from typing import Optional, Dict, List
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)

def get_client() -> TDClient:
    """Initialize and return TwelveData client."""
    api_key = getattr(settings, 'TWELVEDATA_API_KEY', None)
    if not api_key:
        raise ValueError("TWELVEDATA_API_KEY not configured in settings")
    return TDClient(apikey=api_key)

def fetch_prices(symbols: List[str], start: date) -> pd.DataFrame:
    """
    Fetch historical prices for multiple symbols from TwelveData.
    Returns a DataFrame with MultiIndex columns [symbol][Close, ...] to match Yahoo format.
    """
    client = get_client()
    all_data = {}
    
    for symbol in symbols:
        try:
            logger.info(f"Fetching data for {symbol}")
            
            # Fetch time series data with proper parameters
            ts = client.time_series(
                symbol=symbol,
                interval="1day",
                start_date=start.strftime("%Y-%m-%d"),
                outputsize=5000,  # Max historical data
                timezone="America/New_York",
                order="asc",  # Ensure chronological order
                adjust="splits",  # Adjust for stock splits
                dp=4  # 4 decimal places for precision
            )
            
            # Convert to pandas DataFrame
            df = ts.as_pandas()
            
            if df is not None and not df.empty:
                # TwelveData returns data with datetime index and columns like 'close', 'open', etc.
                # We need to standardize column names to match Yahoo format
                df = df.rename(columns={
                    'close': 'Close',
                    'open': 'Open',
                    'high': 'High',
                    'low': 'Low',
                    'volume': 'Volume'
                })
                
                # Ensure data quality
                # 1. Remove any rows where Close price is null or <= 0
                initial_len = len(df)
                df = df[df['Close'].notna() & (df['Close'] > 0)]
                
                if len(df) < initial_len:
                    logger.warning(f"{symbol}: Removed {initial_len - len(df)} invalid price rows")
                
                # 2. Sort by date to ensure chronological order (even though we request asc)
                df = df.sort_index()
                
                # 3. Log any large price jumps that might indicate data issues
                if len(df) > 1:
                    returns = df['Close'].pct_change()
                    extreme_returns = returns[(returns > 0.5) | (returns < -0.5)]
                    if len(extreme_returns) > 0:
                        logger.warning(f"{symbol}: {len(extreme_returns)} extreme price movements detected (>50%)")
                        for date, ret in extreme_returns.items():
                            logger.debug(f"  {date}: {ret:.2%} change")
                
                # Store in dictionary with symbol as key
                all_data[symbol] = df
                logger.info(f"Fetched {len(df)} valid records for {symbol}")
            else:
                logger.warning(f"No data returned for {symbol}")
                
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            continue
    
    if not all_data:
        logger.error("No data fetched for any symbols")
        return pd.DataFrame()
    
    # Combine all DataFrames into MultiIndex format matching Yahoo
    result = pd.concat(all_data, axis=1)
    
    # Ensure datetime index
    if not isinstance(result.index, pd.DatetimeIndex):
        result.index = pd.to_datetime(result.index)
    
    return result

def get_exchange_rate(from_currency: str, to_currency: str = "USD") -> Optional[float]:
    """
    Get current exchange rate between two currencies using TwelveData.
    Returns the rate to convert from_currency to to_currency.
    """
    if from_currency == to_currency:
        return 1.0
    
    try:
        client = get_client()
        
        # TwelveData uses format like "EUR/USD" for forex pairs
        if from_currency == "USD":
            # Need reciprocal rate
            symbol = f"{to_currency}/USD"
            rate_data = client.exchange_rate(symbol=symbol).as_json()
            if rate_data and 'rate' in rate_data:
                return 1.0 / float(rate_data['rate'])
        else:
            # Direct rate or cross rate
            symbol = f"{from_currency}/{to_currency}"
            rate_data = client.exchange_rate(symbol=symbol).as_json()
            if rate_data and 'rate' in rate_data:
                return float(rate_data['rate'])
        
        # If direct pair not available, try cross rate through USD
        if to_currency != "USD" and from_currency != "USD":
            rate_to_usd = get_exchange_rate(from_currency, "USD")
            rate_from_usd = get_exchange_rate("USD", to_currency)
            if rate_to_usd and rate_from_usd:
                return rate_to_usd * rate_from_usd
                
    except Exception as e:
        logger.error(f"Error fetching exchange rate {from_currency} to {to_currency}: {e}")
    
    return None

def get_quote(symbol: str) -> Optional[Dict]:
    """
    Get real-time quote for a symbol.
    Returns dict with price, change, percent_change, etc.
    """
    try:
        client = get_client()
        quote = client.quote(symbol=symbol).as_json()
        
        if quote:
            return {
                'symbol': quote.get('symbol'),
                'price': float(quote.get('close', 0)),
                'change': float(quote.get('change', 0)),
                'percent_change': float(quote.get('percent_change', 0)),
                'volume': int(quote.get('volume', 0)),
                'timestamp': quote.get('timestamp')
            }
    except Exception as e:
        logger.error(f"Error fetching quote for {symbol}: {e}")
    
    return None

def validate_symbols(symbols: List[str]) -> Dict[str, bool]:
    """
    Validate if symbols are available in TwelveData.
    Returns dict mapping symbol to availability status.
    """
    client = get_client()
    results = {}
    
    for symbol in symbols:
        try:
            # Try to fetch a single data point to validate
            ts = client.time_series(
                symbol=symbol,
                interval="1day",
                outputsize=1
            )
            data = ts.as_json()
            results[symbol] = data is not None and 'values' in data
        except Exception:
            results[symbol] = False
    
    return results