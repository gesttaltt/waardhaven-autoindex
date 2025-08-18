# API Endpoints Reference

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.waardhaven.com` (configured in Render)

## Authentication Required

All endpoints except `/auth/register` and `/auth/login` require a valid JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

## Endpoints by Category

### Authentication (`/api/v1/auth`)

#### POST `/api/v1/auth/register`
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe" // optional
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Error Responses:**
- `400` - Invalid input data
- `409` - Email already exists

---

#### POST `/api/v1/auth/login`
Login with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Error Responses:**
- `401` - Invalid credentials
- `400` - Missing required fields

---

#### POST `/api/v1/auth/refresh`
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

#### GET `/api/v1/auth/me`
Get current user information.

**Headers Required:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": "user_123",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

#### POST `/api/v1/auth/logout`
Logout and invalidate tokens.

**Headers Required:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

---

### Portfolio Index (`/api/v1/index`)

#### GET `/api/v1/index/current`
Get current portfolio allocations.

**Response (200):**
```json
{
  "date": "2024-01-18",
  "allocations": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "weight": 0.05,
      "sector": "Technology",
      "value": 5000.00
    },
    {
      "symbol": "GOOGL",
      "name": "Alphabet Inc.",
      "weight": 0.05,
      "sector": "Technology",
      "value": 5000.00
    }
  ]
}
```

---

#### GET `/api/v1/index/history`
Get historical index values.

**Query Parameters:**
- `start_date` (optional) - Start date in YYYY-MM-DD format
- `end_date` (optional) - End date in YYYY-MM-DD format
- `frequency` (optional) - Data frequency: `daily`, `weekly`, `monthly`

**Response (200):**
```json
{
  "series": [
    {
      "date": "2024-01-01",
      "value": 100.00
    },
    {
      "date": "2024-01-02",
      "value": 101.50
    }
  ]
}
```

---

#### POST `/api/v1/index/simulate`
Run portfolio simulation.

**Request Body:**
```json
{
  "amount": 10000,
  "start_date": "2020-01-01",
  "currency": "USD"
}
```

**Response (200):**
```json
{
  "amount_initial": 10000,
  "amount_final": 15234.56,
  "roi_pct": 52.35,
  "currency": "USD",
  "start_date": "2020-01-01",
  "end_date": "2024-01-18",
  "series": [
    {
      "date": "2020-01-01",
      "value": 10000
    },
    {
      "date": "2020-01-02",
      "value": 10150
    }
  ]
}
```

---

#### GET `/api/v1/index/currencies`
Get available currencies.

**Response (200):**
```json
{
  "USD": "US Dollar",
  "EUR": "Euro",
  "GBP": "British Pound",
  "JPY": "Japanese Yen"
}
```

---

#### GET `/api/v1/index/assets/{symbol}/history`
Get historical data for specific asset.

**Path Parameters:**
- `symbol` - Asset symbol (e.g., AAPL)

**Response (200):**
```json
{
  "series": [
    {
      "date": "2024-01-01",
      "value": 150.00
    },
    {
      "date": "2024-01-02",
      "value": 152.00
    }
  ]
}
```

---

### Benchmark (`/api/v1/benchmark`)

#### GET `/api/v1/benchmark/sp500`
Get S&P 500 benchmark data.

**Query Parameters:**
- `start_date` (optional) - Start date in YYYY-MM-DD format
- `end_date` (optional) - End date in YYYY-MM-DD format

**Response (200):**
```json
{
  "series": [
    {
      "date": "2024-01-01",
      "value": 4700.00
    },
    {
      "date": "2024-01-02",
      "value": 4725.00
    }
  ],
  "performance": {
    "total_return": 15.5,
    "annualized_return": 12.3,
    "volatility": 18.5
  }
}
```

---

### Strategy (`/api/v1/strategy`)

#### GET `/api/v1/strategy/config`
Get current strategy configuration.

**Response (200):**
```json
{
  "momentum_weight": 0.3,
  "market_cap_weight": 0.4,
  "risk_parity_weight": 0.3,
  "min_price_threshold": 5.0,
  "max_daily_return": 0.1,
  "min_daily_return": -0.1,
  "max_forward_fill_days": 5,
  "outlier_std_threshold": 3.0,
  "rebalance_frequency": "daily",
  "daily_drop_threshold": -0.05,
  "ai_adjusted": false,
  "last_rebalance": "2024-01-18T00:00:00Z",
  "updated_at": "2024-01-18T00:00:00Z"
}
```

---

#### PUT `/api/v1/strategy/config`
Update strategy configuration.

**Query Parameters:**
- `recompute` (optional, default: true) - Whether to recompute index after update

**Request Body:**
```json
{
  "momentum_weight": 0.4,
  "market_cap_weight": 0.3,
  "risk_parity_weight": 0.3,
  "rebalance_frequency": "weekly"
}
```

**Response (200):** Updated configuration object

---

#### POST `/api/v1/strategy/config/ai-adjust`
Apply AI-suggested adjustments.

**Request Body:**
```json
{
  "adjustments": {
    "momentum_weight": 0.35,
    "risk_parity_weight": 0.35
  },
  "reason": "Market volatility increased",
  "confidence": 0.85
}
```

**Response (200):** Updated configuration with AI adjustments applied

---

#### GET `/api/v1/strategy/risk-metrics`
Get risk metrics.

**Query Parameters:**
- `limit` (optional, default: 30) - Number of data points

**Response (200):**
```json
{
  "metrics": [
    {
      "date": "2024-01-18",
      "total_return": 52.3,
      "annualized_return": 18.5,
      "sharpe_ratio": 1.2,
      "sortino_ratio": 1.5,
      "max_drawdown": -15.2,
      "current_drawdown": -3.5,
      "volatility": 18.5,
      "var_95": -2.5,
      "var_99": -3.8,
      "beta_sp500": 0.85,
      "correlation_sp500": 0.75
    }
  ]
}
```

---

#### POST `/api/v1/strategy/rebalance`
Trigger portfolio rebalancing.

**Query Parameters:**
- `force` (optional, default: false) - Force rebalancing even if not due

**Response (200):**
```json
{
  "message": "Rebalancing completed",
  "allocations_changed": 15,
  "new_allocations": [...],
  "timestamp": "2024-01-18T12:00:00Z"
}
```

---

### News & Sentiment (`/api/v1/news`)

#### GET `/api/v1/news/search`
Search news articles.

**Query Parameters:**
- `symbols` - Comma-separated stock symbols
- `keywords` - Search keywords
- `sentiment_min` - Minimum sentiment score (-1 to 1)
- `sentiment_max` - Maximum sentiment score (-1 to 1)
- `published_after` - ISO timestamp
- `published_before` - ISO timestamp
- `limit` (default: 50) - Maximum results
- `offset` (default: 0) - Pagination offset

**Response (200):**
```json
[
  {
    "id": "article_123",
    "title": "Apple Reports Strong Q4 Earnings",
    "description": "Apple Inc. exceeded expectations...",
    "url": "https://example.com/article",
    "published_at": "2024-01-18T10:00:00Z",
    "source": "Financial Times",
    "symbols": ["AAPL"],
    "sentiment_score": 0.75,
    "relevance_score": 0.9
  }
]
```

---

#### GET `/api/v1/news/sentiment/{symbol}`
Get sentiment analysis for specific symbol.

**Path Parameters:**
- `symbol` - Stock symbol

**Response (200):**
```json
{
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "sentiment_score": 0.65,
  "mention_count": 234,
  "articles": [...]
}
```

---

#### GET `/api/v1/news/trending`
Get trending entities.

**Response (200):**
```json
[
  {
    "symbol": "NVDA",
    "name": "NVIDIA Corporation",
    "mention_count": 456,
    "sentiment_score": 0.8,
    "trend": "up"
  }
]
```

---

### Background Tasks (`/api/v1/background`)

#### POST `/api/v1/background/refresh`
Trigger data refresh task.

**Request Body:**
```json
{
  "mode": "smart",  // "full", "smart", "minimal"
  "symbols": ["AAPL", "GOOGL"]  // optional
}
```

**Response (200):**
```json
{
  "task_id": "task_abc123",
  "status": "pending",
  "created_at": "2024-01-18T12:00:00Z"
}
```

---

#### GET `/api/v1/background/status/{task_id}`
Get task status.

**Path Parameters:**
- `task_id` - Task identifier

**Response (200):**
```json
{
  "task_id": "task_abc123",
  "status": "completed",  // "pending", "processing", "completed", "failed"
  "result": {
    "records_updated": 1500,
    "duration_seconds": 45
  },
  "error": null,
  "created_at": "2024-01-18T12:00:00Z",
  "completed_at": "2024-01-18T12:00:45Z"
}
```

---

#### GET `/api/v1/background/active`
Get all active tasks.

**Response (200):**
```json
{
  "tasks": [
    {
      "task_id": "task_abc123",
      "type": "refresh",
      "status": "processing",
      "progress": 65,
      "created_at": "2024-01-18T12:00:00Z"
    }
  ]
}
```

---

### Diagnostics (`/api/v1/diagnostics`)

#### GET `/api/v1/diagnostics/database-status`
Get database status and statistics.

**Response (200):**
```json
{
  "timestamp": "2024-01-18T12:00:00Z",
  "tables": {
    "users": {
      "count": 1234,
      "status": "OK",
      "earliest_date": "2020-01-01",
      "latest_date": "2024-01-18"
    },
    "prices": {
      "count": 500000,
      "status": "OK",
      "earliest_date": "2020-01-01",
      "latest_date": "2024-01-18"
    }
  },
  "simulation_ready": true,
  "message": "Database healthy"
}
```

---

#### GET `/api/v1/diagnostics/refresh-status`
Check if data refresh is needed.

**Response (200):**
```json
{
  "assets": {
    "count": 100,
    "symbols": ["AAPL", "GOOGL", ...],
    "has_benchmark": true
  },
  "prices": {
    "latest_date": "2024-01-17",
    "days_old": 1,
    "needs_update": true
  },
  "recommendation": "Refresh recommended - data is 1 day old"
}
```

---

#### GET `/api/v1/diagnostics/cache-status`
Get cache statistics.

**Response (200):**
```json
{
  "enabled": true,
  "type": "redis",
  "stats": {
    "keys": 250,
    "memory_used": "12.5MB",
    "hit_rate": 0.85,
    "miss_rate": 0.15
  }
}
```

---

#### POST `/api/v1/diagnostics/cache-invalidate`
Invalidate cache entries.

**Request Body:**
```json
{
  "pattern": "portfolio:*"  // optional, invalidates all if not provided
}
```

**Response (200):**
```json
{
  "message": "Cache invalidated",
  "keys_cleared": 45
}
```

---

#### POST `/api/v1/diagnostics/test-refresh`
Test refresh process without saving.

**Response (200):**
```json
{
  "status": "success",
  "duration_seconds": 3.5,
  "records_processed": 100,
  "errors": []
}
```

---

#### POST `/api/v1/diagnostics/recalculate-index`
Recalculate index values.

**Response (200):**
```json
{
  "message": "Index recalculated successfully",
  "records_updated": 365,
  "duration_seconds": 12.3
}
```

---

### Manual Operations (`/api/v1/manual`)

#### POST `/api/v1/manual/trigger-refresh`
Manually trigger data refresh.

**Response (200):**
```json
{
  "status": "success",
  "message": "Refresh triggered",
  "records_updated": 1500
}
```

---

#### POST `/api/v1/manual/smart-refresh`
Smart refresh with optimization.

**Query Parameters:**
- `mode` - Refresh mode: `auto`, `full`, `minimal`, `cached`

**Response (200):**
```json
{
  "status": "success",
  "message": "Smart refresh completed",
  "mode": "auto",
  "features": ["rate_limiting", "caching", "optimization"],
  "note": "Using cached data where possible"
}
```

---

#### POST `/api/v1/manual/minimal-refresh`
Minimal refresh for testing.

**Response (200):**
```json
{
  "status": "success",
  "message": "Minimal refresh completed",
  "records_updated": 10
}
```

---

## Error Response Format

All endpoints return errors in a consistent format:

```json
{
  "detail": "Detailed error message",
  "status": 400,
  "type": "validation_error",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

## Common Status Codes

- `200` - Success
- `201` - Created
- `204` - No Content
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `422` - Unprocessable Entity
- `429` - Too Many Requests
- `500` - Internal Server Error
- `503` - Service Unavailable

## Rate Limiting

API implements rate limiting:
- **Anonymous**: 100 requests per hour
- **Authenticated**: 1000 requests per hour
- **Premium**: 10000 requests per hour

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1705590000
```

## Pagination

List endpoints support pagination:
```
GET /api/v1/news/search?limit=20&offset=40
```

Response includes pagination info:
```json
{
  "data": [...],
  "pagination": {
    "total": 100,
    "limit": 20,
    "offset": 40,
    "has_next": true,
    "has_prev": true
  }
}
```

## Webhooks

Configure webhooks for real-time events:
- `portfolio.rebalanced`
- `strategy.updated`
- `alert.triggered`
- `task.completed`

## API Versioning

API version is included in the URL path:
- Current: `/api/v1/`
- Legacy: `/api/v0/` (deprecated)

## Authentication Methods

1. **Bearer Token** (Primary)
   ```
   Authorization: Bearer <jwt_token>
   ```

2. **API Key** (Service-to-service)
   ```
   X-API-Key: <api_key>
   ```

3. **Session Cookie** (Web only)
   ```
   Cookie: session=<session_id>
   ```

## CORS Configuration

Allowed origins:
- Development: `http://localhost:3000`
- Production: `https://waardhaven.com`

Allowed methods: `GET, POST, PUT, DELETE, OPTIONS`

Allowed headers: `Content-Type, Authorization, X-API-Key, X-Request-ID`

## Next Steps

- Review [Security Best Practices](./12-security-best-practices.md)
- Learn about [Error Handling](./08-error-handling.md)
- Understand [Testing Guide](./09-testing-guide.md)