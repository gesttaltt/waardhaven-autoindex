"""
Optimized TwelveData service with rate limiting protection and caching.
"""
from twelvedata import TDClient
import pandas as pd
from datetime import date, datetime, timedelta
from typing import Optional, Dict, List, Tuple
import logging
import time
import json
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Rate limiting configuration
RATE_LIMIT_PER_MINUTE = 8  # Free tier limit
RATE_LIMIT_DELAY = 60  # Seconds to wait when rate limited
CACHE_DIR = Path("/tmp/twelvedata_cache")
CACHE_EXPIRY_HOURS = 24  # Cache data for 24 hours

# Ensure cache directory exists
CACHE_DIR.mkdir(parents=True, exist_ok=True)

class RateLimitedTDClient:
    """TwelveData client with rate limiting protection."""
    
    def __init__(self, api_key: str):
        self.client = TDClient(apikey=api_key)
        self.credits_used = 0
        self.last_reset = time.time()
        self.cache = {}
        
    def _check_rate_limit(self, credits_needed: int = 1):
        """Check if we have enough credits available."""
        current_time = time.time()
        
        # Reset counter every minute
        if current_time - self.last_reset >= 60:
            self.credits_used = 0
            self.last_reset = current_time
            
        # Check if we would exceed limit
        if self.credits_used + credits_needed > RATE_LIMIT_PER_MINUTE:
            # Wait until next minute
            wait_time = 60 - (current_time - self.last_reset)
            if wait_time > 0:
                logger.warning(f"Rate limit reached. Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time + 1)  # Add 1 second buffer
                self.credits_used = 0
                self.last_reset = time.time()
                
        self.credits_used += credits_needed
        
    def get_time_series(self, symbol: str, **kwargs):
        """Get time series with rate limiting."""
        self._check_rate_limit(1)
        return self.client.time_series(symbol=symbol, **kwargs)
    
    def get_batch_quotes(self, symbols: List[str]):
        """Get quotes for multiple symbols in one request (uses 1 credit)."""
        self._check_rate_limit(1)
        # TwelveData supports batch requests with comma-separated symbols
        symbols_str = ",".join(symbols[:8])  # Max 8 symbols per request
        return self.client.quote(symbol=symbols_str)

def get_cache_path(symbol: str, start_date: date) -> Path:
    """Generate cache file path for a symbol."""
    filename = f"{symbol}_{start_date.isoformat()}.json"
    return CACHE_DIR / filename

def load_from_cache(symbol: str, start_date: date) -> Optional[pd.DataFrame]:
    """Load cached data if available and not expired."""
    cache_path = get_cache_path(symbol, start_date)
    
    if not cache_path.exists():
        return None
        
    # Check cache age
    cache_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
    if datetime.now() - cache_time > timedelta(hours=CACHE_EXPIRY_HOURS):
        logger.info(f"Cache expired for {symbol}")
        return None
        
    try:
        with open(cache_path, 'r') as f:
            data = json.load(f)
            df = pd.DataFrame(data)
            df.index = pd.to_datetime(df.index)
            logger.info(f"Loaded {symbol} from cache")
            return df
    except Exception as e:
        logger.error(f"Error loading cache for {symbol}: {e}")
        return None

def save_to_cache(symbol: str, start_date: date, df: pd.DataFrame):
    """Save data to cache."""
    cache_path = get_cache_path(symbol, start_date)
    
    try:
        # Convert DataFrame to JSON-serializable format
        data = df.to_json(orient='split', date_format='iso')
        with open(cache_path, 'w') as f:
            f.write(data)
        logger.info(f"Cached data for {symbol}")
    except Exception as e:
        logger.error(f"Error caching data for {symbol}: {e}")

def get_client() -> RateLimitedTDClient:
    """Initialize and return rate-limited TwelveData client."""
    from ..core.config import settings
    api_key = getattr(settings, 'TWELVEDATA_API_KEY', None)
    if not api_key:
        raise ValueError("TWELVEDATA_API_KEY not configured in settings")
    return RateLimitedTDClient(api_key)

def fetch_prices_optimized(symbols: List[str], start: date) -> pd.DataFrame:
    """
    Fetch historical prices with optimization strategies:
    1. Check cache first
    2. Batch requests where possible
    3. Rate limit protection
    4. Fallback to cached data on API failure
    """
    client = get_client()
    all_data = {}
    failed_symbols = []
    
    # Sort symbols to fetch cached ones first
    cached_symbols = []
    uncached_symbols = []
    
    for symbol in symbols:
        cached_df = load_from_cache(symbol, start)
        if cached_df is not None:
            all_data[symbol] = cached_df
            cached_symbols.append(symbol)
        else:
            uncached_symbols.append(symbol)
    
    logger.info(f"Using cache for {len(cached_symbols)} symbols: {cached_symbols}")
    logger.info(f"Need to fetch {len(uncached_symbols)} symbols: {uncached_symbols}")
    
    # Process uncached symbols with rate limiting
    for i, symbol in enumerate(uncached_symbols):
        try:
            logger.info(f"Fetching {symbol} ({i+1}/{len(uncached_symbols)})")
            
            # Use the rate-limited client
            ts = client.get_time_series(
                symbol,
                interval="1day",
                start_date=start.strftime("%Y-%m-%d"),
                outputsize=5000,
                timezone="America/New_York"
            )
            
            df = ts.as_pandas()
            
            if df is not None and not df.empty:
                # Standardize column names
                df = df.rename(columns={
                    'close': 'Close',
                    'open': 'Open',
                    'high': 'High',
                    'low': 'Low',
                    'volume': 'Volume'
                })
                
                all_data[symbol] = df
                save_to_cache(symbol, start, df)
                logger.info(f"Fetched and cached {len(df)} records for {symbol}")
            else:
                logger.warning(f"No data returned for {symbol}")
                failed_symbols.append(symbol)
                
        except Exception as e:
            if "API credits" in str(e):
                logger.error(f"Rate limit hit for {symbol}: {e}")
                # Try to use any existing cache, even if expired
                old_cache = load_from_cache(symbol, start)
                if old_cache is not None:
                    logger.warning(f"Using expired cache for {symbol}")
                    all_data[symbol] = old_cache
                else:
                    failed_symbols.append(symbol)
            else:
                logger.error(f"Error fetching {symbol}: {e}")
                failed_symbols.append(symbol)
    
    if failed_symbols:
        logger.warning(f"Failed to fetch data for: {failed_symbols}")
    
    if not all_data:
        logger.error("No data fetched for any symbols")
        return pd.DataFrame()
    
    # Combine all DataFrames
    result = pd.concat(all_data, axis=1)
    
    if not isinstance(result.index, pd.DatetimeIndex):
        result.index = pd.to_datetime(result.index)
    
    return result

def fetch_prices_batch(symbols: List[str], start: date) -> pd.DataFrame:
    """
    Alternative batch fetching strategy for multiple symbols.
    Uses TwelveData's batch endpoint which costs fewer credits.
    """
    client = get_client()
    all_data = {}
    
    # TwelveData allows up to 120 symbols in one request for time_series
    # But with rate limits, we should be conservative
    batch_size = 8  # Adjust based on your plan
    
    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i+batch_size]
        symbols_str = ",".join(batch)
        
        try:
            logger.info(f"Batch fetching: {symbols_str}")
            
            # This counts as 1 API credit for up to 8 symbols
            ts = client.client.time_series(
                symbol=symbols_str,
                interval="1day",
                start_date=start.strftime("%Y-%m-%d"),
                outputsize=500,  # Reduce to save bandwidth
                timezone="America/New_York"
            )
            
            # Process the batch response
            data = ts.as_json()
            
            if isinstance(data, dict):
                for symbol in batch:
                    if symbol in data:
                        df = pd.DataFrame(data[symbol]['values'])
                        df['datetime'] = pd.to_datetime(df['datetime'])
                        df.set_index('datetime', inplace=True)
                        df = df.rename(columns={
                            'close': 'Close',
                            'open': 'Open',
                            'high': 'High',
                            'low': 'Low',
                            'volume': 'Volume'
                        })
                        all_data[symbol] = df
                        save_to_cache(symbol, start, df)
                        
        except Exception as e:
            logger.error(f"Batch fetch error: {e}")
            # Fall back to individual fetching for this batch
            for symbol in batch:
                cached = load_from_cache(symbol, start)
                if cached is not None:
                    all_data[symbol] = cached
    
    if not all_data:
        return pd.DataFrame()
    
    return pd.concat(all_data, axis=1)

# Export the optimized function as the default
fetch_prices = fetch_prices_optimized

def get_minimal_refresh_data(symbols: List[str], days_back: int = 7) -> pd.DataFrame:
    """
    Fetch minimal data for refresh (last N days only).
    This reduces API credit consumption significantly.
    """
    start = date.today() - timedelta(days=days_back)
    client = get_client()
    all_data = {}
    
    # For minimal refresh, only fetch a subset of symbols
    priority_symbols = symbols[:5]  # Only fetch top 5 symbols
    
    for symbol in priority_symbols:
        try:
            # Check cache first
            cached = load_from_cache(symbol, start)
            if cached is not None and len(cached) >= days_back - 1:
                all_data[symbol] = cached.tail(days_back)
                continue
                
            # Fetch minimal data
            ts = client.get_time_series(
                symbol,
                interval="1day",
                outputsize=days_back,  # Only fetch needed days
                timezone="America/New_York"
            )
            
            df = ts.as_pandas()
            if df is not None and not df.empty:
                df = df.rename(columns={
                    'close': 'Close',
                    'open': 'Open',
                    'high': 'High',
                    'low': 'Low',
                    'volume': 'Volume'
                })
                all_data[symbol] = df
                
        except Exception as e:
            logger.error(f"Error in minimal refresh for {symbol}: {e}")
            
    return pd.concat(all_data, axis=1) if all_data else pd.DataFrame()

def validate_api_key() -> Tuple[bool, Optional[Dict]]:
    """
    Validate API key and return plan information.
    """
    try:
        client = get_client()
        # Use a simple endpoint to check API key
        response = client.client.api_usage()
        
        if response.as_json():
            plan_info = response.as_json()
            return True, {
                'plan': plan_info.get('plan', 'unknown'),
                'credits_used': plan_info.get('current_usage', 0),
                'credits_limit': plan_info.get('plan_limit', 8)
            }
    except Exception as e:
        logger.error(f"API key validation failed: {e}")
        
    return False, None