# API Endpoints Documentation

## Base URL
- **Production**: `https://waardhaven-api.onrender.com`
- **Local Development**: `http://localhost:8000`

## Authentication
All protected endpoints require JWT token in Authorization header:
```
Authorization: Bearer <token>
```

## Endpoints

### Health & Status

#### GET /
**Description**: Root endpoint with API information  
**Authentication**: None  
**Response**:
```json
{
  "message": "Waardhaven AutoIndex API",
  "version": "0.1.0",
  "docs": "/docs"
}
```

#### GET /health
**Description**: Health check endpoint  
**Authentication**: None  
**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-19T12:00:00Z"
}
```

### Authentication (`/api/v1/auth`)

#### POST /api/v1/auth/register
**Description**: Register new user  
**Authentication**: None  
**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```
**Response**:
```json
{
  "message": "User created successfully",
  "user_id": 1
}
```

#### POST /api/v1/auth/login
**Description**: User login  
**Authentication**: None  
**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```
**Response**:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### POST /api/v1/auth/google
**Description**: Google OAuth authentication  
**Authentication**: None  
**Request Body**:
```json
{
  "credential": "google-id-token"
}
```
**Response**: Same as login

#### GET /api/v1/auth/me
**Description**: Get current user information  
**Authentication**: Required  
**Response**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "is_google_user": false,
  "created_at": "2025-01-19T12:00:00Z"
}
```

#### POST /api/v1/auth/refresh
**Description**: Refresh access token  
**Authentication**: None  
**Request Body**:
```json
{
  "refresh_token": "eyJ..."
}
```
**Response**:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

#### POST /api/v1/auth/logout
**Description**: Logout user  
**Authentication**: Required  
**Response**:
```json
{
  "message": "Successfully logged out"
}
```

### Portfolio Index (`/api/v1/index`)

#### GET /api/v1/index/values
**Description**: Get index values with optional date range  
**Authentication**: Required  
**Query Parameters**:
- `start_date` (optional): ISO date string
- `end_date` (optional): ISO date string
- `limit` (optional): Number of records

**Response**:
```json
{
  "values": [
    {
      "date": "2025-01-19",
      "value": 1050.25,
      "daily_return": 0.0125,
      "total_return": 0.0502
    }
  ],
  "metadata": {
    "count": 100,
    "start_date": "2024-01-01",
    "end_date": "2025-01-19"
  }
}
```

#### POST /api/v1/index/compute
**Description**: Compute index values for date range  
**Authentication**: Required  
**Request Body**:
```json
{
  "start_date": "2024-01-01",
  "end_date": "2025-01-19",
  "initial_value": 1000
}
```
**Response**:
```json
{
  "message": "Index computation completed",
  "records_created": 250,
  "date_range": {
    "start": "2024-01-01",
    "end": "2025-01-19"
  }
}
```

#### GET /api/v1/index/performance
**Description**: Get performance metrics  
**Authentication**: Required  
**Query Parameters**:
- `period` (optional): "1M", "3M", "6M", "1Y", "YTD", "ALL"

**Response**:
```json
{
  "returns": {
    "daily": 0.0012,
    "weekly": 0.0085,
    "monthly": 0.0342,
    "yearly": 0.1523
  },
  "risk_metrics": {
    "volatility": 0.1823,
    "sharpe_ratio": 1.45,
    "sortino_ratio": 1.82,
    "max_drawdown": -0.0823,
    "var_95": -0.0234
  },
  "statistics": {
    "best_day": 0.0453,
    "worst_day": -0.0367,
    "positive_days": 145,
    "negative_days": 105
  }
}
```

#### GET /api/v1/index/allocations
**Description**: Get current portfolio allocations  
**Authentication**: Required  
**Response**:
```json
{
  "allocations": [
    {
      "asset_id": 1,
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "weight": 0.15,
      "value": 15000,
      "shares": 100
    }
  ],
  "total_value": 100000,
  "asset_count": 10
}
```

### Benchmark (`/api/v1/benchmark`)

#### GET /api/v1/benchmark/sp500
**Description**: Get S&P 500 benchmark data  
**Authentication**: Required  
**Query Parameters**:
- `start_date` (optional): ISO date string
- `end_date` (optional): ISO date string

**Response**:
```json
{
  "data": [
    {
      "date": "2025-01-19",
      "close": 4823.15,
      "return": 0.0023
    }
  ],
  "performance": {
    "total_return": 0.1234,
    "volatility": 0.1456
  }
}
```

#### GET /api/v1/benchmark/comparison
**Description**: Compare portfolio vs benchmark  
**Authentication**: Required  
**Response**:
```json
{
  "portfolio": {
    "return": 0.1523,
    "volatility": 0.1823,
    "sharpe": 1.45
  },
  "benchmark": {
    "return": 0.1234,
    "volatility": 0.1456,
    "sharpe": 1.23
  },
  "relative": {
    "excess_return": 0.0289,
    "tracking_error": 0.0456,
    "information_ratio": 0.63
  }
}
```

### Strategy (`/api/v1/strategy`)

#### GET /api/v1/strategy/config
**Description**: Get current strategy configuration  
**Authentication**: Required  
**Response**:
```json
{
  "id": 1,
  "name": "Balanced Growth",
  "rebalance_frequency": "MONTHLY",
  "min_weight": 0.01,
  "max_weight": 0.20,
  "target_assets": 20,
  "risk_level": "MODERATE",
  "optimization_method": "MEAN_VARIANCE"
}
```

#### POST /api/v1/strategy/update
**Description**: Update strategy configuration  
**Authentication**: Required  
**Request Body**:
```json
{
  "rebalance_frequency": "QUARTERLY",
  "max_weight": 0.15,
  "risk_level": "AGGRESSIVE"
}
```
**Response**:
```json
{
  "message": "Strategy updated successfully",
  "config": { /* updated config */ }
}
```

#### POST /api/v1/strategy/backtest
**Description**: Run strategy backtest  
**Authentication**: Required  
**Request Body**:
```json
{
  "start_date": "2023-01-01",
  "end_date": "2024-12-31",
  "initial_capital": 100000,
  "config": { /* strategy config */ }
}
```
**Response**:
```json
{
  "results": {
    "total_return": 0.2345,
    "annual_return": 0.1156,
    "max_drawdown": -0.1234,
    "sharpe_ratio": 1.56,
    "trades": 48
  },
  "equity_curve": [ /* time series data */ ]
}
```

### News (`/api/v1/news`)

#### GET /api/v1/news/articles
**Description**: Get news articles  
**Authentication**: Required  
**Query Parameters**:
- `symbols` (optional): Comma-separated stock symbols
- `limit` (optional): Number of articles (default: 10)
- `published_after` (optional): ISO datetime

**Response**:
```json
{
  "articles": [
    {
      "id": 1,
      "title": "Market Update",
      "description": "...",
      "url": "https://...",
      "published_at": "2025-01-19T12:00:00Z",
      "source": "Reuters",
      "symbols": ["AAPL", "MSFT"],
      "sentiment": 0.65
    }
  ],
  "count": 10
}
```

#### GET /api/v1/news/sentiment
**Description**: Get sentiment analysis  
**Authentication**: Required  
**Query Parameters**:
- `symbol` (optional): Stock symbol
- `period` (optional): Time period

**Response**:
```json
{
  "overall_sentiment": 0.45,
  "sentiment_distribution": {
    "positive": 45,
    "neutral": 35,
    "negative": 20
  },
  "trending_topics": [
    {
      "topic": "earnings",
      "count": 23,
      "sentiment": 0.67
    }
  ]
}
```

### Background Tasks (`/api/v1/background`)

#### POST /api/v1/background/refresh-market-data
**Description**: Trigger market data refresh  
**Authentication**: Required  
**Request Body**:
```json
{
  "symbols": ["AAPL", "MSFT"],
  "start_date": "2024-01-01"
}
```
**Response**:
```json
{
  "task_id": "abc-123-def",
  "status": "queued",
  "message": "Market data refresh initiated"
}
```

#### POST /api/v1/background/compute-index
**Description**: Trigger index computation  
**Authentication**: Required  
**Response**:
```json
{
  "task_id": "xyz-456-ghi",
  "status": "processing"
}
```

#### GET /api/v1/background/task/{task_id}
**Description**: Get task status  
**Authentication**: Required  
**Response**:
```json
{
  "task_id": "abc-123-def",
  "status": "completed",
  "result": { /* task result */ },
  "created_at": "2025-01-19T12:00:00Z",
  "completed_at": "2025-01-19T12:05:00Z"
}
```

### Tasks (`/api/v1/tasks`)

#### GET /api/v1/tasks/active
**Description**: Get active tasks  
**Authentication**: Required  
**Response**:
```json
{
  "tasks": [
    {
      "id": "task-123",
      "name": "market_data_refresh",
      "status": "running",
      "progress": 0.45,
      "started_at": "2025-01-19T12:00:00Z"
    }
  ],
  "count": 2
}
```

#### GET /api/v1/tasks/scheduled
**Description**: Get scheduled tasks  
**Authentication**: Required  
**Response**:
```json
{
  "tasks": [
    {
      "name": "daily_refresh",
      "schedule": "0 9 * * *",
      "next_run": "2025-01-20T09:00:00Z",
      "enabled": true
    }
  ]
}
```

### Diagnostics (`/api/v1/diagnostics`)

#### GET /api/v1/diagnostics/system-health
**Description**: Get system health status  
**Authentication**: Required  
**Response**:
```json
{
  "status": "healthy",
  "components": {
    "database": "connected",
    "redis": "connected",
    "celery": "running",
    "external_apis": {
      "twelvedata": "operational",
      "marketaux": "operational"
    }
  },
  "metrics": {
    "cpu_usage": 45.2,
    "memory_usage": 62.8,
    "disk_usage": 35.4,
    "response_time_ms": 125
  }
}
```

#### GET /api/v1/diagnostics/data-quality
**Description**: Check data quality  
**Authentication**: Required  
**Response**:
```json
{
  "quality_score": 0.95,
  "issues": [
    {
      "type": "missing_data",
      "severity": "low",
      "description": "Missing prices for 2 assets on 2025-01-15",
      "affected_assets": ["SYMBOL1", "SYMBOL2"]
    }
  ],
  "last_refresh": "2025-01-19T09:00:00Z",
  "data_coverage": {
    "assets": 95,
    "dates": 250,
    "completeness": 0.98
  }
}
```

#### GET /api/v1/diagnostics/cache-status
**Description**: Get cache statistics  
**Authentication**: Required  
**Response**:
```json
{
  "enabled": true,
  "provider": "redis",
  "statistics": {
    "hits": 1523,
    "misses": 234,
    "hit_rate": 0.867,
    "memory_used_mb": 45.2,
    "keys_count": 156
  }
}
```

### Manual Operations (`/api/v1/manual`)

#### POST /api/v1/manual/refresh-all
**Description**: Manually refresh all data  
**Authentication**: Required (Admin)  
**Headers**:
```
X-Admin-Token: <admin-token>
```
**Response**:
```json
{
  "message": "Full refresh initiated",
  "components": {
    "market_data": "processing",
    "index_values": "queued",
    "news": "queued"
  }
}
```

#### POST /api/v1/manual/clear-cache
**Description**: Clear all caches  
**Authentication**: Required (Admin)  
**Response**:
```json
{
  "message": "Cache cleared successfully",
  "keys_removed": 156
}
```

#### POST /api/v1/manual/run-migrations
**Description**: Run database migrations  
**Authentication**: Required (Admin)  
**Response**:
```json
{
  "message": "Migrations completed",
  "migrations_run": [
    "add_composite_indexes",
    "add_performance_indexes"
  ]
}
```

## Error Responses

### Standard Error Format
```json
{
  "detail": "Error message",
  "status_code": 400,
  "error_code": "INVALID_REQUEST"
}
```

### Common Error Codes
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Rate Limiting
- Default: 100 requests per minute per IP
- Authenticated users: 200 requests per minute
- Admin endpoints: 50 requests per minute

## Pagination
For endpoints returning lists:
- `limit`: Number of items (default: 50, max: 100)
- `offset`: Skip items (default: 0)
- `sort`: Sort field (e.g., "date", "-value")

## WebSocket (Planned)
```javascript
// Future implementation
ws://waardhaven-api.onrender.com/ws
```

## API Versioning
- Current version: v1
- Version in URL: `/api/v1/`
- Deprecation notice: 6 months
- Sunset period: 12 months