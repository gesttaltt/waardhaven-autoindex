"""
TwelveData provider implementation.
Implements MarketDataProvider interface with TwelveData API.
"""

import time
import json
import logging
from datetime import date, datetime
from typing import Dict, List, Optional, Any
import pandas as pd
from twelvedata import TDClient
from twelvedata.exceptions import TwelveDataError

from .interface import MarketDataProvider, QuoteData, ExchangeRate
from ..base import ProviderStatus, APIError, retry_with_backoff
from ...core.config import settings
from ...core.redis_client import get_redis_client

logger = logging.getLogger(__name__)


class TwelveDataRateLimiter:
    """
    Rate limiter specific to TwelveData API.
    Handles distributed rate limiting via Redis.
    """
    
    def __init__(self, credits_per_minute: int = 8):
        self.credits_per_minute = credits_per_minute
        self.credits_used = []
        self.redis_client = get_redis_client()
        self.redis_key = "twelvedata:rate_limit"
    
    def wait_if_needed(self, credits_required: int = 1):
        """Wait if rate limit would be exceeded."""
        now = time.time()
        
        # Try Redis for distributed rate limiting
        if self.redis_client.is_connected:
            try:
                usage_data = self.redis_client.get(self.redis_key)
                if usage_data:
                    self.credits_used = json.loads(usage_data)
            except Exception as e:
                logger.debug(f"Redis rate limit fetch failed: {e}")
        
        # Clean old credits
        self.credits_used = [t for t in self.credits_used if now - t < 60]
        
        # Check if we need to wait
        if len(self.credits_used) + credits_required > self.credits_per_minute:
            oldest_credit = min(self.credits_used)
            wait_time = 60 - (now - oldest_credit) + 1
            logger.info(f"Rate limit: waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
            now = time.time()
            self.credits_used = [t for t in self.credits_used if now - t < 60]
        
        # Record usage
        for _ in range(credits_required):
            self.credits_used.append(now)
        
        # Update Redis
        if self.redis_client.is_connected:
            try:
                self.redis_client.set(
                    self.redis_key,
                    json.dumps(self.credits_used),
                    expire=120
                )
            except Exception as e:
                logger.debug(f"Redis rate limit update failed: {e}")


class TwelveDataProvider(MarketDataProvider):
    """
    TwelveData API provider implementation.
    Provides market data, quotes, and technical indicators.
    """
    
    def __init__(self, api_key: Optional[str] = None, cache_enabled: bool = True):
        super().__init__(api_key or settings.TWELVEDATA_API_KEY, cache_enabled)
        
        if not self.api_key:
            raise ValueError("TwelveData API key not configured")
        
        self.client = TDClient(apikey=self.api_key)
        self.rate_limiter = TwelveDataRateLimiter(settings.TWELVEDATA_RATE_LIMIT)
        self.redis_client = get_redis_client()
        
        # Cache TTL settings
        self.price_cache_ttl = 3600  # 1 hour
        self.quote_cache_ttl = 60    # 1 minute
        self.forex_cache_ttl = 300   # 5 minutes
    
    def get_provider_name(self) -> str:
        return "TwelveData"
    
    def validate_config(self) -> bool:
        """Validate API key and configuration."""
        return bool(self.api_key)
    
    def health_check(self) -> ProviderStatus:
        """Check TwelveData API health."""
        try:
            # Try a simple API call
            self.rate_limiter.wait_if_needed(1)
            usage = self.client.api_usage().as_json()
            
            if usage:
                return ProviderStatus.HEALTHY
            else:
                return ProviderStatus.DEGRADED
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return ProviderStatus.UNHEALTHY
    
    def _get_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key."""
        parts = [f"twelvedata:{prefix}"]
        for k, v in sorted(kwargs.items()):
            if v is not None:
                parts.append(f"{k}:{v}")
        return ":".join(parts)
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get data from cache."""
        if not self.cache_enabled or not self.redis_client.is_connected:
            return None
        
        try:
            cached = self.redis_client.get(cache_key)
            if cached:
                logger.debug(f"Cache hit: {cache_key}")
                return json.loads(cached) if isinstance(cached, str) else cached
        except Exception as e:
            logger.debug(f"Cache get failed: {e}")
        
        return None
    
    def _set_cache(self, cache_key: str, data: Any, ttl: int):
        """Store data in cache."""
        if not self.cache_enabled or not self.redis_client.is_connected:
            return
        
        try:
            json_data = json.dumps(data) if not isinstance(data, str) else data
            self.redis_client.set(cache_key, json_data, expire=ttl)
            logger.debug(f"Cached: {cache_key}, TTL: {ttl}s")
        except Exception as e:
            logger.debug(f"Cache set failed: {e}")
    
    def _execute_request(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Execute TwelveData API request."""
        # This is called by base class with retry logic
        # Endpoint here is just for logging, actual API calls use client methods
        return params.get('func')(*params.get('args', []), **params.get('kwargs', {}))
    
    @retry_with_backoff(max_retries=3)
    def fetch_historical_prices(
        self,
        symbols: List[str],
        start_date: date,
        end_date: Optional[date] = None,
        interval: str = "1day"
    ) -> pd.DataFrame:
        """Fetch historical prices with caching and batching."""
        if not symbols:
            return pd.DataFrame()
        
        end_date = end_date or date.today()
        all_data = {}
        
        # Process in batches
        batch_size = min(8, settings.TWELVEDATA_RATE_LIMIT)
        
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i + batch_size]
            
            # Check cache for each symbol
            uncached_symbols = []
            for symbol in batch:
                cache_key = self._get_cache_key(
                    "prices",
                    symbol=symbol,
                    start=start_date.isoformat(),
                    end=end_date.isoformat(),
                    interval=interval
                )
                
                cached_data = self._get_from_cache(cache_key)
                if cached_data:
                    df = pd.DataFrame(cached_data)
                    if not df.empty:
                        df.index = pd.to_datetime(df.index)
                        all_data[symbol] = df
                else:
                    uncached_symbols.append(symbol)
            
            if not uncached_symbols:
                continue
            
            # Rate limit
            self.rate_limiter.wait_if_needed(len(uncached_symbols))
            
            try:
                # Fetch data
                if len(uncached_symbols) == 1:
                    symbol = uncached_symbols[0]
                    logger.info(f"Fetching prices for {symbol}")
                    
                    ts = self.client.time_series(
                        symbol=symbol,
                        interval=interval,
                        start_date=start_date.strftime("%Y-%m-%d"),
                        end_date=end_date.strftime("%Y-%m-%d"),
                        outputsize=5000,
                        timezone="America/New_York",
                        order="asc",
                        dp=4
                    )
                    
                    df = ts.as_pandas()
                    if df is not None and not df.empty:
                        df = self._process_price_data(df, symbol)
                        if not df.empty:
                            all_data[symbol] = df
                            # Cache it
                            cache_key = self._get_cache_key(
                                "prices",
                                symbol=symbol,
                                start=start_date.isoformat(),
                                end=end_date.isoformat(),
                                interval=interval
                            )
                            self._set_cache(cache_key, df.to_json(), self.price_cache_ttl)
                else:
                    # Batch request
                    logger.info(f"Fetching batch: {','.join(uncached_symbols)}")
                    
                    ts = self.client.time_series(
                        symbol=uncached_symbols,
                        interval=interval,
                        start_date=start_date.strftime("%Y-%m-%d"),
                        end_date=end_date.strftime("%Y-%m-%d"),
                        outputsize=5000,
                        timezone="America/New_York",
                        order="asc",
                        dp=4
                    )
                    
                    batch_data = ts.as_json()
                    
                    if batch_data:
                        for symbol in uncached_symbols:
                            if symbol in batch_data and 'values' in batch_data[symbol]:
                                df = pd.DataFrame(batch_data[symbol]['values'])
                                df['datetime'] = pd.to_datetime(df['datetime'])
                                df.set_index('datetime', inplace=True)
                                
                                df = self._process_price_data(df, symbol)
                                if not df.empty:
                                    all_data[symbol] = df
                                    
                                    # Cache it
                                    cache_key = self._get_cache_key(
                                        "prices",
                                        symbol=symbol,
                                        start=start_date.isoformat(),
                                        end=end_date.isoformat(),
                                        interval=interval
                                    )
                                    self._set_cache(cache_key, df.to_json(), self.price_cache_ttl)
                    
            except TwelveDataError as e:
                logger.error(f"TwelveData error: {e}")
                raise APIError(f"TwelveData API error: {e}")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise
        
        if not all_data:
            return pd.DataFrame()
        
        # Combine into MultiIndex DataFrame
        result = pd.concat(all_data, axis=1)
        
        if not isinstance(result.index, pd.DatetimeIndex):
            result.index = pd.to_datetime(result.index)
        
        return result
    
    def _process_price_data(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Process and validate price data."""
        # Standardize columns
        df = df.rename(columns={
            'close': 'Close',
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'volume': 'Volume'
        })
        
        # Ensure numeric
        for col in ['Close', 'Open', 'High', 'Low', 'Volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Validate
        initial_len = len(df)
        df = df[df['Close'].notna() & (df['Close'] > 0)]
        
        if len(df) < initial_len:
            logger.debug(f"{symbol}: Removed {initial_len - len(df)} invalid rows")
        
        # Check for extreme movements
        if len(df) > 1:
            returns = df['Close'].pct_change()
            extreme = returns[(returns > 0.5) | (returns < -0.5)]
            if len(extreme) > 0:
                logger.warning(f"{symbol}: {len(extreme)} extreme movements (>50%)")
        
        return df
    
    def get_quotes(self, symbols: List[str]) -> Dict[str, QuoteData]:
        """Get real-time quotes."""
        if not symbols:
            return {}
        
        quotes = {}
        
        # Check cache
        uncached = []
        for symbol in symbols:
            cache_key = self._get_cache_key("quote", symbol=symbol)
            cached = self._get_from_cache(cache_key)
            if cached:
                quotes[symbol] = QuoteData(**cached)
            else:
                uncached.append(symbol)
        
        if not uncached:
            return quotes
        
        # Rate limit
        self.rate_limiter.wait_if_needed(1)
        
        try:
            logger.info(f"Fetching quotes: {','.join(uncached)}")
            
            if len(uncached) == 1:
                quote_data = self.client.quote(symbol=uncached[0]).as_json()
                if quote_data:
                    quote = self._process_quote(quote_data)
                    quotes[uncached[0]] = quote
                    # Cache
                    cache_key = self._get_cache_key("quote", symbol=uncached[0])
                    self._set_cache(cache_key, quote.to_dict(), self.quote_cache_ttl)
            else:
                quote_data = self.client.quote(symbol=uncached).as_json()
                if quote_data:
                    for symbol in uncached:
                        if symbol in quote_data:
                            quote = self._process_quote(quote_data[symbol])
                            quotes[symbol] = quote
                            # Cache
                            cache_key = self._get_cache_key("quote", symbol=symbol)
                            self._set_cache(cache_key, quote.to_dict(), self.quote_cache_ttl)
                    
        except TwelveDataError as e:
            logger.error(f"Quote fetch error: {e}")
            raise APIError(f"Failed to fetch quotes: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
        
        return quotes
    
    def _process_quote(self, data: Dict) -> QuoteData:
        """Process quote data into QuoteData object."""
        return QuoteData(
            symbol=data.get('symbol', ''),
            price=float(data.get('close', 0)),
            change=float(data.get('change', 0)),
            percent_change=float(data.get('percent_change', 0)),
            volume=int(data.get('volume', 0)),
            timestamp=datetime.fromtimestamp(data.get('timestamp', 0)),
            open=float(data.get('open', 0)),
            high=float(data.get('high', 0)),
            low=float(data.get('low', 0)),
            previous_close=float(data.get('previous_close', 0))
        )
    
    def get_exchange_rate(
        self,
        from_currency: str,
        to_currency: str = "USD"
    ) -> Optional[ExchangeRate]:
        """Get exchange rate."""
        if from_currency == to_currency:
            return ExchangeRate(
                from_currency=from_currency,
                to_currency=to_currency,
                rate=1.0,
                timestamp=datetime.now()
            )
        
        # Check cache
        cache_key = self._get_cache_key("forex", from_curr=from_currency, to_curr=to_currency)
        cached = self._get_from_cache(cache_key)
        if cached:
            return ExchangeRate(**cached)
        
        # Rate limit
        self.rate_limiter.wait_if_needed(1)
        
        try:
            symbol = f"{from_currency}/{to_currency}"
            logger.info(f"Fetching exchange rate: {symbol}")
            
            rate_data = self.client.exchange_rate(symbol=symbol).as_json()
            if rate_data and 'rate' in rate_data:
                exchange_rate = ExchangeRate(
                    from_currency=from_currency,
                    to_currency=to_currency,
                    rate=float(rate_data['rate']),
                    timestamp=datetime.fromtimestamp(rate_data.get('timestamp', time.time()))
                )
                
                # Cache
                self._set_cache(
                    cache_key,
                    {
                        'from_currency': exchange_rate.from_currency,
                        'to_currency': exchange_rate.to_currency,
                        'rate': exchange_rate.rate,
                        'timestamp': exchange_rate.timestamp.isoformat()
                    },
                    self.forex_cache_ttl
                )
                
                return exchange_rate
                
        except Exception as e:
            logger.error(f"Exchange rate error: {e}")
        
        return None
    
    def validate_symbols(self, symbols: List[str]) -> Dict[str, bool]:
        """Validate symbol availability."""
        results = {}
        batch_size = min(8, settings.TWELVEDATA_RATE_LIMIT)
        
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i + batch_size]
            self.rate_limiter.wait_if_needed(len(batch))
            
            for symbol in batch:
                try:
                    ts = self.client.time_series(
                        symbol=symbol,
                        interval="1day",
                        outputsize=1
                    )
                    data = ts.as_json()
                    results[symbol] = data is not None and 'values' in data
                except Exception:
                    results[symbol] = False
        
        return results
    
    def get_technical_indicators(
        self,
        symbol: str,
        indicators: List[str],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **params
    ) -> Dict[str, pd.Series]:
        """Get technical indicators (not fully implemented yet)."""
        # TODO: Implement technical indicators using TwelveData
        logger.warning("Technical indicators not yet implemented")
        return {}
    
    def get_api_usage(self) -> Optional[Dict[str, Any]]:
        """Get API usage statistics."""
        try:
            self.rate_limiter.wait_if_needed(1)
            usage = self.client.api_usage().as_json()
            return usage
        except Exception as e:
            logger.error(f"Failed to get API usage: {e}")
            return None