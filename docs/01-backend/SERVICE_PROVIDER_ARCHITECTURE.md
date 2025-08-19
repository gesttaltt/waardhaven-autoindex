# Service and Provider Architecture

## Overview
The backend uses a dual-layer architecture separating external integrations (providers) from business logic (services).

## Architecture Layers

### 1. Provider Layer (`apps/api/app/providers/`)
Handles all external API integrations and data sources.

```
providers/
├── base.py                 # Abstract base provider with retry logic
├── market_data/
│   ├── interface.py       # Market data provider interface
│   └── twelvedata.py      # TwelveData API implementation
└── news/
    ├── interface.py       # News provider interface
    └── marketaux.py       # MarketAux API implementation
```

#### Provider Responsibilities:
- External API communication
- Rate limiting and retry logic
- Data format transformation
- Error handling for external services
- Response caching at API level

#### Base Provider Features:
- Automatic retry with exponential backoff
- Request/response logging
- Error standardization
- Health check capabilities

### 2. Service Layer (`apps/api/app/services/`)
Implements business logic using providers and database models.

```
services/
├── refresh.py             # Data refresh orchestration
├── strategy.py            # Portfolio strategy implementation
├── performance.py         # Performance calculations
├── currency.py            # Currency conversion
├── news.py               # News aggregation and analysis
└── twelvedata.py         # TwelveData-specific business logic
```

#### Service Responsibilities:
- Business logic implementation
- Data validation and processing
- Database operations
- Cache management
- Provider orchestration

## Data Flow

```
API Request
    ↓
Router Layer
    ↓
Service Layer (Business Logic)
    ↓
Provider Layer (External APIs) ←→ Database Layer
    ↓
Service Layer (Processing)
    ↓
Response
```

## Key Services

### Refresh Service (`refresh.py`)
Orchestrates data updates across the system.

**Key Functions:**
- `refresh_all(db, smart_mode=True)`: Full system refresh
- `ensure_assets(db)`: Ensures default assets exist
- Creates database backups before modifications
- Uses TwelveDataProvider for market data

**Smart Mode Features:**
- Rate limit protection
- Incremental updates
- Fallback to shorter periods on failure

### Strategy Service (`strategy.py`)
Implements portfolio allocation strategies.

**Key Functions:**
- `compute_index_and_allocations(db, config)`: Calculate portfolio weights
- `apply_strategy_weights(prices_df, config)`: Apply strategy logic
- Supports momentum, market cap, and risk parity strategies

### Performance Service (`performance.py`)
Calculates portfolio performance metrics.

**Key Functions:**
- `calculate_performance_metrics(returns)`: Comprehensive metrics
- `calculate_sharpe_ratio(returns, risk_free_rate)`: Risk-adjusted returns
- `calculate_max_drawdown(returns)`: Maximum drawdown calculation
- `calculate_var(returns, confidence_level)`: Value at Risk

**Metrics Calculated:**
- Total return, annualized return
- Volatility, Sharpe ratio, Sortino ratio
- Maximum drawdown, current drawdown
- VaR (95% and 99%)
- Beta and correlation vs S&P 500

### Currency Service (`currency.py`)
Handles multi-currency support.

**Key Functions:**
- `get_exchange_rates()`: Fetch current rates
- `convert_amount(amount, from_currency, to_currency)`: Currency conversion
- Caches exchange rates for performance

### News Service (`news.py`)
Aggregates and processes financial news.

**Current Implementation:**
- Basic news fetching via MarketAux provider
- Article storage and retrieval
- Symbol-based news filtering

**Note**: Advanced features like sentiment analysis and entity extraction are documented but not fully implemented.

### TwelveData Service (`twelvedata.py`)
TwelveData-specific business logic.

**Key Functions:**
- `fetch_price_data(symbols, start_date, end_date)`: Batch price fetching
- `fetch_real_time_price(symbol)`: Real-time quotes
- `fetch_market_state()`: Market open/close status

## Provider Implementations

### TwelveDataProvider (`providers/market_data/twelvedata.py`)
**Features:**
- Rate limiting (8 requests/minute for free tier)
- Automatic retry on failure
- Batch request optimization
- Response caching

**Methods:**
- `fetch_time_series(symbols, start_date, end_date)`
- `fetch_quote(symbols)`
- `get_market_state()`

### MarketAuxProvider (`providers/news/marketaux.py`)
**Features:**
- Rate limiting (500 requests/day)
- Sentiment score integration
- Entity extraction
- Multi-symbol search

**Methods:**
- `search_news(symbols, keywords, date_range)`
- `get_article(article_id)`
- `get_trending_entities()`

## Error Handling Strategy

### Provider Level
- Retry with exponential backoff
- Circuit breaker pattern (planned, not fully implemented)
- Graceful degradation on API failure

### Service Level
- Transaction rollback on database errors
- Backup creation before destructive operations
- Comprehensive logging
- User-friendly error messages

## Caching Strategy

### Redis Cache Layers:
1. **Provider Cache**: Raw API responses (5-15 minutes)
2. **Service Cache**: Processed business data (15-60 minutes)
3. **Result Cache**: Computed results (1-24 hours)

### Cache Invalidation:
- Automatic on data updates
- Manual refresh endpoints
- Time-based expiration

## Testing Approach

### Provider Tests
- Mock external API responses
- Test retry logic
- Verify rate limiting
- Error handling scenarios

### Service Tests
- Unit tests with mocked providers
- Integration tests with test database
- Performance benchmarks
- Data validation tests

## Future Enhancements

### Planned Provider Features:
- Circuit breaker implementation
- Health check monitoring
- Provider failover
- Request batching optimization

### Planned Service Features:
- Advanced sentiment analysis
- Real-time WebSocket updates
- Machine learning predictions
- Automated rebalancing

## Configuration

### Environment Variables:
```env
# Provider API Keys
TWELVEDATA_API_KEY=your_key
MARKETAUX_API_KEY=your_key

# Provider Settings
PROVIDER_RETRY_MAX=3
PROVIDER_RETRY_DELAY=1
PROVIDER_TIMEOUT=30

# Cache Settings
REDIS_URL=redis://localhost:6379
CACHE_TTL_PROVIDER=300
CACHE_TTL_SERVICE=900
```

## Best Practices

1. **Always use providers for external APIs** - Don't make direct API calls from services
2. **Implement caching at appropriate levels** - Provider for raw data, service for processed
3. **Handle errors gracefully** - Use fallbacks and provide meaningful error messages
4. **Log important operations** - Especially external API calls and data modifications
5. **Write tests for both layers** - Mock providers in service tests
6. **Document API limits** - Track rate limits and quotas for each provider

## Dependencies

### Provider Dependencies:
- `httpx`: Async HTTP client
- `tenacity`: Retry logic
- `pydantic`: Data validation

### Service Dependencies:
- `pandas`: Data manipulation
- `numpy`: Numerical calculations
- `sqlalchemy`: Database ORM
- `redis`: Caching layer