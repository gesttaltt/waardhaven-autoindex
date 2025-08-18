# Market Data Providers Documentation

## Overview
Market data providers supply real-time and historical financial data including prices, quotes, and exchange rates. Currently implemented: TwelveData.

## TwelveData Provider

### Location
`app/providers/market_data/twelvedata.py`

### Features
- Historical price data (OHLCV)
- Real-time quotes
- Currency exchange rates
- Technical indicators (planned)
- Batch operations (up to 120 symbols)

### Configuration
```env
TWELVEDATA_API_KEY=your_api_key_here
TWELVEDATA_RATE_LIMIT=8  # Credits per minute (free tier)
ENABLE_MARKET_DATA_CACHE=true
```

### API Documentation
https://twelvedata.com/docs

## Interface Definition

### MarketDataProvider Interface
```python
class MarketDataProvider(BaseProvider):
    @abstractmethod
    def fetch_historical_prices(
        symbols: List[str],
        start_date: date,
        end_date: Optional[date] = None,
        interval: str = "1day"
    ) -> pd.DataFrame
    
    @abstractmethod
    def get_quotes(symbols: List[str]) -> Dict[str, QuoteData]
    
    @abstractmethod
    def get_exchange_rate(
        from_currency: str,
        to_currency: str = "USD"
    ) -> Optional[ExchangeRate]
```

## Data Models

### PriceData
```python
@dataclass
class PriceData:
    symbol: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    adjusted_close: Optional[float] = None
```

### QuoteData
```python
@dataclass
class QuoteData:
    symbol: str
    price: float
    change: float
    percent_change: float
    volume: int
    timestamp: datetime
    open: float
    high: float
    low: float
    previous_close: float
    bid: Optional[float] = None
    ask: Optional[float] = None
```

### ExchangeRate
```python
@dataclass
class ExchangeRate:
    from_currency: str
    to_currency: str
    rate: float
    timestamp: datetime
```

## TwelveData Implementation Details

### Rate Limiting
TwelveData uses a credit-based system:

```python
class TwelveDataRateLimiter:
    def __init__(self, credits_per_minute=8):
        self.credits_per_minute = credits_per_minute
        self.credits_used = []
    
    def wait_if_needed(self, credits_required=1):
        # Distributed rate limiting via Redis
        # Automatic waiting when limit reached
```

**Credit Usage:**
- Single symbol request: 1 credit
- Batch request (2-120 symbols): 1 credit
- Exchange rate: 1 credit
- Technical indicators: 1-2 credits

### Caching Strategy
```yaml
Historical Prices:
  TTL: 3600 seconds (1 hour)
  Key: "twelvedata:prices:{symbol}:{start}:{end}:{interval}"
  Rationale: Historical data doesn't change

Real-time Quotes:
  TTL: 60 seconds (1 minute)
  Key: "twelvedata:quote:{symbol}"
  Rationale: Balance freshness vs API limits

Exchange Rates:
  TTL: 300 seconds (5 minutes)
  Key: "twelvedata:forex:{from}:{to}"
  Rationale: Forex rates change slowly
```

### Batch Operations
Optimize API usage with batch requests:

```python
# Fetch multiple symbols in one request
provider = TwelveDataProvider()

# Good - Single batch request (1 credit)
prices = provider.fetch_historical_prices(
    symbols=["AAPL", "MSFT", "GOOGL", "AMZN"],
    start_date=date(2024, 1, 1)
)

# Bad - Multiple individual requests (4 credits)
for symbol in ["AAPL", "MSFT", "GOOGL", "AMZN"]:
    prices = provider.fetch_historical_prices([symbol], start_date)
```

### Error Handling
```python
try:
    prices = provider.fetch_historical_prices(symbols, start_date)
except TwelveDataError as e:
    # Handle TwelveData-specific errors
    logger.error(f"TwelveData API error: {e}")
    # Use cached data or fallback
except RateLimitError as e:
    # Wait and retry
    time.sleep(e.retry_after)
except APIError as e:
    if e.status_code == 404:
        # Symbol not found
    elif e.status_code >= 500:
        # Server error, will retry automatically
```

## Usage Examples

### Fetching Historical Prices
```python
from app.providers.market_data import TwelveDataProvider
from datetime import date

provider = TwelveDataProvider()

# Fetch daily prices for multiple symbols
prices = provider.fetch_historical_prices(
    symbols=["AAPL", "MSFT"],
    start_date=date(2024, 1, 1),
    end_date=date(2024, 1, 31),
    interval="1day"
)

# Result: MultiIndex DataFrame
# Columns: (AAPL, Open), (AAPL, High), (AAPL, Low), (AAPL, Close), (AAPL, Volume),
#          (MSFT, Open), (MSFT, High), (MSFT, Low), (MSFT, Close), (MSFT, Volume)
# Index: DatetimeIndex
```

### Getting Real-time Quotes
```python
# Fetch current quotes
quotes = provider.get_quotes(["AAPL", "GOOGL", "TSLA"])

for symbol, quote in quotes.items():
    print(f"{symbol}: ${quote.price:.2f} ({quote.percent_change:+.2f}%)")
    print(f"  Volume: {quote.volume:,}")
    print(f"  Day Range: ${quote.low:.2f} - ${quote.high:.2f}")
```

### Currency Conversion
```python
# Get exchange rate
rate = provider.get_exchange_rate("EUR", "USD")

if rate:
    print(f"1 EUR = {rate.rate:.4f} USD")
    print(f"Updated: {rate.timestamp}")
    
    # Convert amount
    eur_amount = 1000
    usd_amount = eur_amount * rate.rate
    print(f"€{eur_amount} = ${usd_amount:.2f}")
```

### Symbol Validation
```python
# Check if symbols are available
symbols_to_check = ["AAPL", "INVALID", "MSFT"]
validation = provider.validate_symbols(symbols_to_check)

for symbol, is_valid in validation.items():
    status = "✓" if is_valid else "✗"
    print(f"{status} {symbol}")
```

## Data Quality

### Validation Rules
1. **Price Validation**
   - Close price must be positive
   - Remove rows with null close prices
   - Flag extreme movements (>50% daily change)

2. **Volume Validation**
   - Volume must be non-negative
   - Convert to integer type

3. **Date Validation**
   - Ensure chronological order
   - Handle market holidays
   - Convert to UTC timezone

### Data Cleaning
```python
def _process_price_data(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
    # Standardize column names
    df = df.rename(columns={
        'close': 'Close',
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'volume': 'Volume'
    })
    
    # Ensure numeric types
    for col in ['Close', 'Open', 'High', 'Low', 'Volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Remove invalid prices
    df = df[df['Close'].notna() & (df['Close'] > 0)]
    
    # Check for extreme movements
    returns = df['Close'].pct_change()
    extreme = returns[(returns > 0.5) | (returns < -0.5)]
    if len(extreme) > 0:
        logger.warning(f"{symbol}: {len(extreme)} extreme movements")
    
    return df
```

## Performance Optimization

### 1. Use Caching
```python
# Enable caching in configuration
ENABLE_MARKET_DATA_CACHE=true

# Cache is automatically used
prices = provider.fetch_historical_prices(symbols, start_date)
# First call: Fetches from API
# Subsequent calls within TTL: Returns from cache
```

### 2. Batch Requests
```python
# Optimize API credits
symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA"]

# Process in optimal batch size
batch_size = min(120, len(symbols))  # TwelveData max is 120
prices = provider.fetch_historical_prices(symbols[:batch_size], start_date)
```

### 3. Parallel Processing
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def fetch_all_data(symbols: List[str]):
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Fetch prices, quotes, and rates in parallel
        prices_future = executor.submit(
            provider.fetch_historical_prices, symbols, start_date
        )
        quotes_future = executor.submit(
            provider.get_quotes, symbols
        )
        
        prices = prices_future.result()
        quotes = quotes_future.result()
        
    return prices, quotes
```

## Monitoring & Debugging

### Health Check
```python
status = provider.health_check()
if status == ProviderStatus.HEALTHY:
    print("TwelveData API is operational")
elif status == ProviderStatus.DEGRADED:
    print("TwelveData API has issues, using cache")
else:
    print("TwelveData API is down")
```

### API Usage Statistics
```python
usage = provider.get_api_usage()
if usage:
    print(f"API Credits Used: {usage.get('current_usage')}")
    print(f"Credits Remaining: {usage.get('plan_limit') - usage.get('current_usage')}")
```

### Debug Logging
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('app.providers.market_data')

# Will log:
# - API requests and responses
# - Cache hits and misses
# - Rate limit warnings
# - Data quality issues
```

## Troubleshooting

### Common Issues

#### 1. Rate Limit Exceeded
```
Error: Rate limit exceeded
Solution: 
- Reduce request frequency
- Enable caching
- Use batch operations
- Upgrade API plan
```

#### 2. Symbol Not Found
```
Error: Invalid symbol
Solution:
- Validate symbols before requesting
- Use provider.validate_symbols()
- Check symbol format (e.g., "AAPL" not "AAPL.US")
```

#### 3. Empty Data Response
```
Error: No data returned
Solution:
- Check date range (market holidays)
- Verify symbol availability for date range
- Check API key permissions
```

#### 4. Connection Timeout
```
Error: Request timeout
Solution:
- Check network connectivity
- Increase timeout setting
- Use cached data as fallback
```

## Migration Guide

### From Old Service to Provider
```python
# Old way (deprecated)
from app.services.twelvedata import fetch_prices
prices = fetch_prices(symbols, start=start_date)

# New way (recommended)
from app.providers.market_data import TwelveDataProvider
provider = TwelveDataProvider()
prices = provider.fetch_historical_prices(symbols, start_date=start_date)
```

### Benefits of Migration
- Circuit breaker protection
- Automatic retry logic
- Better error handling
- Consistent interface
- Statistics tracking

## Future Enhancements

### Planned Features
1. **Technical Indicators**
   - Moving averages (SMA, EMA)
   - RSI, MACD, Bollinger Bands
   - Custom indicators

2. **WebSocket Streaming**
   - Real-time price updates
   - Live order book data
   - Market depth

3. **Options Data**
   - Option chains
   - Greeks calculation
   - Implied volatility

4. **Fundamental Data**
   - Earnings reports
   - Financial statements
   - Company metrics