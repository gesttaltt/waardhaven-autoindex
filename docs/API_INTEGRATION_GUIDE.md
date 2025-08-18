# API Integration Guide

## Overview
Waardhaven AutoIndex now integrates with two primary data providers:
- **TwelveData**: Technical analysis and market data
- **Marketaux**: Financial news and sentiment analysis

## Architecture

### Provider Pattern
The API uses a clean provider pattern with abstract base classes:

```
providers/
├── base.py              # Abstract base provider with common functionality
├── market_data/
│   ├── interface.py     # Market data provider interface
│   └── twelvedata.py    # TwelveData implementation
└── news/
    ├── interface.py     # News provider interface
    └── marketaux.py     # Marketaux implementation
```

### Key Features
- **Modular Design**: Easy to add new providers
- **Circuit Breaker**: Prevents cascading failures
- **Rate Limiting**: Respects API limits
- **Caching**: Redis-based caching for performance
- **Retry Logic**: Exponential backoff for transient failures

## Configuration

### Environment Variables

#### TwelveData Configuration
```env
TWELVEDATA_API_KEY=your_api_key_here
TWELVEDATA_RATE_LIMIT=8        # Credits per minute (free tier)
ENABLE_MARKET_DATA_CACHE=true
```

#### Marketaux Configuration
```env
MARKETAUX_API_KEY=your_api_key_here
MARKETAUX_RATE_LIMIT=100       # Requests per minute
ENABLE_NEWS_CACHE=true
NEWS_REFRESH_INTERVAL=900       # 15 minutes
```

#### Redis Configuration (Optional but Recommended)
```env
REDIS_URL=redis://localhost:6379/0
CACHE_TTL_SECONDS=300           # 5 minutes
CACHE_TTL_LONG_SECONDS=3600     # 1 hour
```

## API Endpoints

### Market Data Endpoints (TwelveData)

#### Get Historical Prices
```http
GET /api/v1/index/prices?symbols=AAPL,MSFT&start=2024-01-01
```

#### Get Real-time Quotes
```http
GET /api/v1/index/quotes?symbols=AAPL,GOOGL,TSLA
```

#### Get Exchange Rates
```http
GET /api/v1/index/exchange-rate?from=EUR&to=USD
```

### News & Sentiment Endpoints (Marketaux)

#### Search News
```http
GET /api/v1/news/search?symbols=AAPL&sentiment_min=0.5&limit=20
```

Parameters:
- `symbols`: Comma-separated stock symbols
- `keywords`: Search keywords
- `sentiment_min/max`: Filter by sentiment (-1 to 1)
- `published_after/before`: Date filters
- `limit`: Results per page (max 100)
- `offset`: Pagination offset

#### Get Article Details
```http
GET /api/v1/news/article/{article_id}
```

#### Get Similar Articles
```http
GET /api/v1/news/similar/{article_id}?limit=10
```

#### Get Entity Sentiment Over Time
```http
GET /api/v1/news/sentiment/{symbol}?days=30
```

Response includes:
- Current sentiment score
- Average sentiment over period
- Sentiment trend data points
- Top news sources

#### Get Trending Entities
```http
GET /api/v1/news/trending?entity_type=company&limit=20
```

#### Refresh News Data
```http
POST /api/v1/news/refresh
{
  "symbols": ["AAPL", "MSFT", "GOOGL"]
}
```

## Database Schema

### News-Related Tables

#### news_articles
- Stores article metadata
- Links to sources and entities
- Supports full-text search

#### news_sentiment
- Sentiment scores and labels
- Confidence levels
- Provider information

#### news_entities
- Entities mentioned in articles
- Entity-specific sentiment
- Match scores

#### asset_news
- Many-to-many relationship
- Links assets to relevant news
- Relevance scores

#### entity_sentiment_history
- Historical sentiment tracking
- Daily aggregations
- Trend analysis

## Usage Examples

### Python Client Example

```python
import requests

# Base configuration
BASE_URL = "http://localhost:8000/api/v1"
headers = {"Authorization": "Bearer your_token_here"}

# Search for positive news about Apple
response = requests.get(
    f"{BASE_URL}/news/search",
    params={
        "symbols": "AAPL",
        "sentiment_min": 0.5,
        "limit": 10
    },
    headers=headers
)
articles = response.json()

# Get sentiment trend for Microsoft
response = requests.get(
    f"{BASE_URL}/news/sentiment/MSFT",
    params={"days": 30},
    headers=headers
)
sentiment_data = response.json()

# Get trending tech companies
response = requests.get(
    f"{BASE_URL}/news/trending",
    params={
        "entity_type": "company",
        "limit": 20
    },
    headers=headers
)
trending = response.json()
```

### JavaScript/TypeScript Example

```typescript
// services/api/news.ts
interface NewsSearchParams {
  symbols?: string[];
  keywords?: string;
  sentimentMin?: number;
  sentimentMax?: number;
  limit?: number;
}

async function searchNews(params: NewsSearchParams) {
  const queryParams = new URLSearchParams({
    symbols: params.symbols?.join(',') || '',
    keywords: params.keywords || '',
    sentiment_min: params.sentimentMin?.toString() || '',
    limit: params.limit?.toString() || '20'
  });

  const response = await fetch(
    `/api/v1/news/search?${queryParams}`,
    {
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`
      }
    }
  );

  return response.json();
}

// Usage
const articles = await searchNews({
  symbols: ['AAPL', 'MSFT'],
  sentimentMin: 0.3,
  limit: 50
});
```

## Provider Features

### TwelveData Provider

#### Features
- Historical price data
- Real-time quotes
- Exchange rates
- Technical indicators (coming soon)
- Batch operations (up to 120 symbols)

#### Rate Limiting
- Free tier: 8 credits/minute
- Automatic rate limit handling
- Distributed rate limiting via Redis

#### Caching
- Historical prices: 1 hour
- Real-time quotes: 1 minute
- Exchange rates: 5 minutes

### Marketaux Provider

#### Features
- Financial news search
- Sentiment analysis
- Entity extraction
- Similar articles
- Trending entities
- 5,000+ news sources
- 30+ languages
- 80+ markets coverage

#### Rate Limiting
- Configurable per plan
- Automatic retry on 429 errors
- Respects Retry-After headers

#### Caching
- News articles: 15 minutes
- Sentiment data: 1 hour
- Entity data: 30 minutes

## Error Handling

### Provider Errors
```python
class ProviderError(Exception):
    """Base exception for provider errors"""

class RateLimitError(ProviderError):
    """Rate limit exceeded"""
    retry_after: int  # Seconds to wait

class APIError(ProviderError):
    """API returned an error"""
    status_code: int

class CircuitBreakerError(ProviderError):
    """Circuit breaker is open"""
```

### Response Status Codes
- `200`: Success
- `400`: Bad request (invalid parameters)
- `401`: Unauthorized (invalid token)
- `404`: Resource not found
- `429`: Rate limit exceeded
- `500`: Internal server error
- `503`: Service unavailable (circuit breaker open)

## Best Practices

### 1. Use Caching
Enable Redis caching to reduce API calls and improve performance:
```env
REDIS_URL=redis://localhost:6379/0
ENABLE_MARKET_DATA_CACHE=true
ENABLE_NEWS_CACHE=true
```

### 2. Batch Operations
When fetching data for multiple symbols, use batch operations:
```python
# Good - Single batch request
quotes = get_quotes(["AAPL", "MSFT", "GOOGL", "AMZN"])

# Bad - Multiple individual requests
for symbol in symbols:
    quote = get_quote(symbol)
```

### 3. Handle Rate Limits
Implement retry logic with exponential backoff:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def fetch_data():
    return provider.get_data()
```

### 4. Monitor Health
Check provider health before critical operations:
```python
health = provider.health_check()
if health == ProviderStatus.UNHEALTHY:
    # Use fallback or cached data
    pass
```

### 5. Use Appropriate Intervals
- Real-time data: Poll every 1-5 minutes
- Historical data: Update daily
- News: Refresh every 15-30 minutes

## Migration Guide

### Running Migrations
The new tables are created automatically on startup, or manually:
```bash
cd apps/api
python -m app.migrations.add_news_tables
```

### Backward Compatibility
The old `twelvedata.py` service maintains backward compatibility:
```python
# Old way (still works)
from app.services.twelvedata import fetch_prices

# New way (recommended)
from app.providers.market_data import TwelveDataProvider
provider = TwelveDataProvider()
prices = provider.fetch_historical_prices(symbols, start_date)
```

## Monitoring

### Health Check Endpoint
```http
GET /api/v1/diagnostics/health
```

Returns provider status:
```json
{
  "providers": {
    "twelvedata": "healthy",
    "marketaux": "healthy"
  },
  "cache": "connected",
  "database": "connected"
}
```

### Usage Statistics
```http
GET /api/v1/diagnostics/stats
```

### Cache Status
```http
GET /api/v1/diagnostics/cache-status
```

## Troubleshooting

### Common Issues

#### 1. Rate Limit Errors
- Check your API plan limits
- Increase `TWELVEDATA_RATE_LIMIT` or `MARKETAUX_RATE_LIMIT`
- Enable caching to reduce API calls

#### 2. Circuit Breaker Open
- Provider is temporarily unavailable
- Check provider health status
- Wait for recovery timeout (60 seconds default)

#### 3. Cache Connection Failed
- Verify Redis is running
- Check `REDIS_URL` configuration
- System falls back to direct API calls

#### 4. Missing Data
- Verify API keys are configured
- Check symbol validity
- Review date ranges

## Future Enhancements

### Planned Features
1. **Technical Indicators**: RSI, MACD, Moving Averages
2. **WebSocket Support**: Real-time data streaming
3. **More News Providers**: Bloomberg, Reuters integration
4. **AI Sentiment Analysis**: Custom ML models
5. **GraphQL API**: Alternative to REST
6. **Webhooks**: Push notifications for events

### Performance Improvements
1. **Connection Pooling**: Reuse HTTP connections
2. **Async Operations**: Full async/await support
3. **Data Compression**: Reduce bandwidth usage
4. **Edge Caching**: CDN integration

## Support

For issues or questions:
1. Check the logs: `docker logs waardhaven-api`
2. Review configuration: Ensure all API keys are set
3. Test provider health: Use diagnostic endpoints
4. Contact support with error details and timestamps