# TwelveData Service

## Overview
Integration service for fetching market data from TwelveData API.

## Location
`apps/api/app/services/twelvedata.py`
`apps/api/app/services/twelvedata_optimized.py`

## Purpose
Provides real-time and historical market data for portfolio assets.

## Core Functions

### fetch_price(symbol)
- Get current price for asset
- Handle API rate limits
- Error handling
- Cache results

### fetch_historical(symbol, interval, outputsize)
- Historical price data
- Multiple timeframes
- Data validation
- Missing data handling

### fetch_batch_prices(symbols)
- Batch price fetching
- Optimized API calls
- Parallel processing
- Rate limit management

### fetch_market_cap(symbol)
- Market capitalization data
- Company statistics
- Fundamental data

## API Integration

### Authentication
- API key from environment
- Request headers
- Rate limit tracking

### Endpoints Used
- `/price` - Current prices
- `/time_series` - Historical data
- `/statistics` - Market cap
- `/quote` - Real-time quotes

### Rate Limiting
- API credit management
- Request throttling
- Retry logic
- Error handling

## Data Processing

### Price Validation
- Minimum price threshold ($1.00)
- Outlier detection
- Data quality checks
- Missing data handling

### Data Transformation
- JSON to DataFrame
- Type conversion
- Timestamp parsing
- Currency conversion

## Optimization Features

### Caching
- In-memory cache
- TTL configuration
- Cache invalidation

### Batch Operations
- Group API calls
- Parallel requests
- Efficient querying

### Error Recovery
- Retry mechanisms
- Fallback strategies
- Graceful degradation

## Configuration

### API Settings
- Base URL
- Timeout values
- Retry attempts
- Rate limits

### Data Settings
- Default intervals
- Output sizes
- Time zones
- Market hours

## Error Handling

### API Errors
- Rate limit exceeded
- Invalid symbol
- Service unavailable
- Timeout errors

### Data Errors
- Missing data
- Invalid values
- Format issues
- Parsing failures

## Performance Metrics

### Response Times
- Single symbol: <1s
- Batch (10 symbols): <3s
- Historical data: <5s

### Rate Limits
- Free tier: 800 requests/day
- Batch endpoints save credits
- Optimize call frequency

## Testing
- test_twelvedata.py
- test_rate_limits.py
- Mock responses
- Integration tests

## Dependencies
- twelvedata: Official client
- requests: HTTP library
- pandas: Data processing

## Related Modules
- refresh.py: Uses price data
- strategy.py: Market cap data
- currency.py: FX rates