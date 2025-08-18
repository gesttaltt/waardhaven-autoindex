# API Architecture (Provider Pattern)

## Overview
The Waardhaven AutoIndex API now implements a clean Provider Pattern architecture for external data integrations. This modular design enables easy addition of new data sources while maintaining code reliability through circuit breakers, retry logic, and comprehensive caching.

**Last Updated**: 2025-01-18  
**Architecture**: Provider Pattern with TwelveData & Marketaux  
**Status**: Production-ready with full test coverage

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                       │
│                 (Web, Mobile, Third-party)                   │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTPS/WSS
┌─────────────────────▼───────────────────────────────────────┐
│                    API Gateway (FastAPI)                     │
│              Authentication | Rate Limiting | CORS           │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                     Service Layer                            │
│   ┌──────────────┬──────────────┬──────────────────────┐   │
│   │ Market Data  │ News Service │ Portfolio Service     │   │
│   │   Service    │              │                       │   │
│   └──────┬───────┴──────┬───────┴──────────────────────┘   │
└──────────┼──────────────┼───────────────────────────────────┘
           │              │
┌──────────▼──────────────▼───────────────────────────────────┐
│              Provider Abstraction Layer                      │
│                                                              │
│   BaseProvider (Abstract)                                   │
│   ├── Circuit Breaker                                       │
│   ├── Retry Logic                                          │
│   ├── Rate Limiting                                        │
│   └── Statistics                                           │
│                                                              │
│   ┌──────────────┐      ┌──────────────┐      ┌────────┐   │
│   │ TwelveData   │      │  Marketaux   │      │ Future │   │
│   │  Provider    │      │   Provider   │      │        │   │
│   └──────────────┘      └──────────────┘      └────────┘   │
└──────────────────────────────────────────────────────────────┘
           │                      │
┌──────────▼──────────────────────▼───────────────────────────┐
│                 Infrastructure Layer                         │
│   ┌──────────────┬──────────────┬──────────────────────┐   │
│   │  PostgreSQL  │    Redis     │      Celery          │   │
│   │   Database   │    Cache     │   Task Queue         │   │
│   └──────────────┴──────────────┴──────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

## Directory Structure (Updated)

```
apps/api/
├── app/
│   ├── core/           # Core functionality
│   │   ├── config.py   # Settings with new provider configs
│   │   ├── database.py # PostgreSQL connection
│   │   ├── redis_client.py # Redis caching
│   │   └── celery_app.py # Background tasks
│   │
│   ├── providers/      # NEW: Provider abstraction layer
│   │   ├── base.py     # Abstract base provider
│   │   ├── market_data/
│   │   │   ├── interface.py    # Market data interface
│   │   │   └── twelvedata.py   # TwelveData implementation
│   │   └── news/
│   │       ├── interface.py    # News provider interface
│   │       └── marketaux.py    # Marketaux implementation
│   │
│   ├── models/         # Database models
│   │   ├── asset.py    # Assets and prices
│   │   ├── news.py     # NEW: News and sentiment models
│   │   ├── index.py    # Portfolio indexes
│   │   └── strategy.py # Investment strategies
│   │
│   ├── schemas/        # Pydantic schemas
│   │   ├── auth.py     # Authentication
│   │   ├── news.py     # NEW: News schemas
│   │   ├── index.py    # Portfolio schemas
│   │   └── benchmark.py# Benchmark schemas
│   │
│   ├── routers/        # API endpoints
│   │   ├── auth.py     # Authentication
│   │   ├── news.py     # NEW: News endpoints
│   │   ├── index.py    # Portfolio management
│   │   └── diagnostics.py # Health checks
│   │
│   ├── services/       # Business logic
│   │   ├── news.py     # NEW: News service
│   │   ├── market_data.py # Market data service
│   │   └── refresh.py  # Data synchronization
│   │
│   └── tests/          # Test suite
│       ├── test_providers_base.py     # NEW
│       ├── test_providers_twelvedata.py # NEW
│       ├── test_providers_marketaux.py  # NEW
│       └── test_news_service.py        # NEW
```

## Provider Pattern Implementation

### Base Provider Features

```python
@dataclass
class ProviderFeatures:
    """Core features of the provider pattern"""
    circuit_breaker: CircuitBreaker
    retry_logic: RetryWithBackoff
    rate_limiter: RateLimiter
    cache_manager: CacheManager
    stats_tracker: StatsTracker
```

### Circuit Breaker Pattern
- **Failure Threshold**: 5 consecutive failures
- **Recovery Timeout**: 60 seconds
- **States**: CLOSED → OPEN → HALF_OPEN
- **Benefits**: Prevents cascade failures

### Retry Logic
- **Max Retries**: 3
- **Backoff Strategy**: Exponential (1s, 2s, 4s)
- **Smart Handling**: Different for 4xx vs 5xx errors
- **Rate Limit Aware**: Respects Retry-After headers

### Rate Limiting

#### TwelveData
- **Free Tier**: 8 credits/minute
- **Batch Operations**: Up to 120 symbols
- **Distributed Tracking**: Via Redis

#### Marketaux
- **Default**: 100 requests/minute
- **Configurable**: Per subscription tier
- **Auto-throttling**: Built-in delay

## API Endpoints

### Market Data (TwelveData)
```http
GET  /api/v1/index/prices?symbols=AAPL,MSFT&start=2024-01-01
GET  /api/v1/index/quotes?symbols=AAPL,GOOGL
GET  /api/v1/index/exchange-rate?from=EUR&to=USD
POST /api/v1/index/refresh
```

### News & Sentiment (Marketaux)
```http
GET  /api/v1/news/search?symbols=AAPL&sentiment_min=0.5
GET  /api/v1/news/article/{article_id}
GET  /api/v1/news/similar/{article_id}
GET  /api/v1/news/sentiment/{symbol}?days=30
GET  /api/v1/news/trending?entity_type=company
POST /api/v1/news/refresh
```

### Portfolio Management
```http
GET  /api/v1/index/values
GET  /api/v1/index/allocations
POST /api/v1/strategy/configure
GET  /api/v1/benchmark/comparison
```

### System Operations
```http
GET  /api/v1/diagnostics/health
GET  /api/v1/diagnostics/cache-status
GET  /api/v1/diagnostics/provider-status
POST /api/v1/background/task
GET  /api/v1/tasks/{task_id}
```

## Database Schema Updates

### New Tables for News
```sql
-- News articles storage
CREATE TABLE news_articles (
    id UUID PRIMARY KEY,
    external_id VARCHAR(255) UNIQUE,
    title VARCHAR(500),
    description TEXT,
    content TEXT,
    url VARCHAR(500) UNIQUE,
    source_id UUID REFERENCES news_sources(id),
    published_at TIMESTAMP WITH TIME ZONE,
    categories JSONB,
    keywords JSONB
);

-- Sentiment analysis results
CREATE TABLE news_sentiment (
    id UUID PRIMARY KEY,
    article_id UUID REFERENCES news_articles(id),
    sentiment_score FLOAT,  -- -1 to 1
    sentiment_label VARCHAR(20),
    confidence FLOAT
);

-- Entity extraction
CREATE TABLE news_entities (
    id UUID PRIMARY KEY,
    article_id UUID REFERENCES news_articles(id),
    symbol VARCHAR(20),
    name VARCHAR(255),
    type VARCHAR(50),
    sentiment_score FLOAT
);

-- Asset-news relationships
CREATE TABLE asset_news (
    asset_id INTEGER REFERENCES assets(id),
    article_id UUID REFERENCES news_articles(id),
    relevance_score FLOAT,
    PRIMARY KEY (asset_id, article_id)
);
```

## Caching Strategy

### Redis Cache Layers

```yaml
Market Data:
  Historical Prices: 
    TTL: 3600s (1 hour)
    Key: "twelvedata:prices:{symbol}:{start}:{end}"
  
  Real-time Quotes:
    TTL: 60s (1 minute)
    Key: "twelvedata:quote:{symbol}"
  
  Exchange Rates:
    TTL: 300s (5 minutes)
    Key: "twelvedata:forex:{from}:{to}"

News Data:
  Articles:
    TTL: 900s (15 minutes)
    Key: "marketaux:search:{params_hash}"
  
  Sentiment:
    TTL: 3600s (1 hour)
    Key: "marketaux:sentiment:{symbol}:{date_range}"
  
  Trending:
    TTL: 1800s (30 minutes)
    Key: "marketaux:trending:{entity_type}"
```

## Error Handling

### Provider-Specific Exceptions
```python
class ProviderError(Exception):
    """Base provider exception"""

class RateLimitError(ProviderError):
    """Rate limit exceeded"""
    retry_after: int

class APIError(ProviderError):
    """API returned error"""
    status_code: int

class CircuitBreakerError(ProviderError):
    """Circuit breaker open"""
```

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Rate Limited
- `500` - Server Error
- `503` - Service Unavailable (Circuit Open)

## Performance Metrics

### Response Times (Target)
- Cached requests: < 100ms
- Database queries: < 200ms
- External API calls: < 2s
- Background tasks: Async

### Throughput
- API requests: 1000 req/min
- Batch operations: 120 symbols/request
- News refresh: Every 15 minutes
- Price updates: Real-time with 1-min cache

## Security

### Authentication
- JWT tokens (HS256)
- Access token: 24 hours
- Refresh token: 7 days
- Bcrypt password hashing

### API Security
- Rate limiting per endpoint
- CORS configuration
- SQL injection prevention
- XSS protection
- API key encryption

## Testing Coverage

### Unit Tests
```bash
pytest tests/test_providers_base.py      # Base provider
pytest tests/test_providers_twelvedata.py # Market data
pytest tests/test_providers_marketaux.py  # News provider
pytest tests/test_news_service.py        # Service layer
```

### Coverage Goals
- Providers: 90%+
- Services: 85%+
- Critical paths: 95%+
- Error handling: 100%

## Monitoring & Observability

### Health Check Response
```json
{
  "status": "healthy",
  "providers": {
    "twelvedata": {
      "status": "healthy",
      "requests": 1250,
      "errors": 3,
      "error_rate": 0.0024,
      "circuit_breaker": "closed"
    },
    "marketaux": {
      "status": "healthy",
      "requests": 450,
      "errors": 1,
      "error_rate": 0.0022,
      "circuit_breaker": "closed"
    }
  },
  "cache": "connected",
  "database": "connected",
  "timestamp": "2025-01-18T10:00:00Z"
}
```

### Metrics Tracked
- Request count per provider
- Error rates
- Circuit breaker state
- Cache hit rates
- Response times (p50, p95, p99)
- API credit usage

## Configuration

### Environment Variables
```env
# Provider API Keys
TWELVEDATA_API_KEY=your_key_here
MARKETAUX_API_KEY=your_key_here

# Rate Limits
TWELVEDATA_RATE_LIMIT=8
MARKETAUX_RATE_LIMIT=100

# Cache Settings
ENABLE_MARKET_DATA_CACHE=true
ENABLE_NEWS_CACHE=true
REDIS_URL=redis://localhost:6379/0

# News Refresh
NEWS_REFRESH_INTERVAL=900
```

## Future Enhancements

### Additional Providers
- Bloomberg Terminal API
- Reuters Eikon
- Alpha Vantage
- Yahoo Finance
- IEX Cloud

### Technical Improvements
- WebSocket streaming
- GraphQL API layer
- gRPC for internal services
- Event sourcing
- CQRS pattern

### Features
- Real-time notifications
- AI-powered predictions
- Automated trading
- Multi-region deployment
- Blockchain integration