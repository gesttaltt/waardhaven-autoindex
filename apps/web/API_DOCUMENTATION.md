# Waardhaven AutoIndex API Documentation

## Overview
This document outlines the API endpoints consumed by the Waardhaven AutoIndex frontend application. The API is organized into logical domains for authentication, portfolio management, market data, and strategy configuration.

## Base Configuration
- **Development**: `http://localhost:8000`
- **Production**: Set via `NEXT_PUBLIC_API_URL` environment variable
- **Authentication**: Bearer token in Authorization header

## API Endpoints

### Authentication (`/api/v1/auth`)

#### POST `/api/v1/auth/register`
Register a new user account.
- **Request Body**: 
  ```json
  {
    "email": "string",
    "password": "string"
  }
  ```
- **Response**: 
  ```json
  {
    "access_token": "string"
  }
  ```
- **Used in**: `register/page.tsx`

#### POST `/api/v1/auth/login`
Authenticate user and receive access token.
- **Request Body**: 
  ```json
  {
    "email": "string",
    "password": "string"
  }
  ```
- **Response**: 
  ```json
  {
    "access_token": "string"
  }
  ```
- **Used in**: `login/page.tsx`

### Index Management (`/api/v1/index`)

#### GET `/api/v1/index/history`
Retrieve historical index values.
- **Response**: 
  ```json
  {
    "series": [
      {
        "date": "string",
        "value": "number"
      }
    ]
  }
  ```
- **Used in**: `dashboard/page.tsx`, `portfolioService`

#### GET `/api/v1/index/current`
Get current index allocations.
- **Response**: 
  ```json
  {
    "date": "string",
    "allocations": [
      {
        "symbol": "string",
        "name": "string",
        "sector": "string",
        "weight": "number"
      }
    ]
  }
  ```
- **Used in**: `dashboard/page.tsx`, `portfolioService`

#### POST `/api/v1/index/simulate`
Run investment simulation.
- **Request Body**: 
  ```json
  {
    "amount": "number",
    "start_date": "string",
    "currency": "string"
  }
  ```
- **Response**: 
  ```json
  {
    "start_date": "string",
    "end_date": "string",
    "start_value": "number",
    "end_value": "number",
    "amount_initial": "number",
    "amount_final": "number",
    "roi_pct": "number",
    "series": [],
    "currency": "string"
  }
  ```
- **Used in**: `dashboard/page.tsx`, `portfolioService`

#### GET `/api/v1/index/currencies`
Get supported currencies for simulation.
- **Response**: Object with currency codes as keys
- **Used in**: `dashboard/page.tsx`, `portfolioService`

#### GET `/api/v1/index/assets/{symbol}/history`
Get historical data for a specific asset.
- **Response**: Same format as `/index/history`
- **Used in**: `dashboard/page.tsx`, `portfolioService`

### Benchmark Data (`/api/v1/benchmark`)

#### GET `/api/v1/benchmark/sp500`
Retrieve S&P 500 benchmark data.
- **Response**: 
  ```json
  {
    "series": [
      {
        "date": "string",
        "value": "number"
      }
    ]
  }
  ```
- **Used in**: `dashboard/page.tsx`, `marketService`

### Strategy Configuration (`/api/v1/strategy`)

#### GET `/api/v1/strategy/config`
Get current strategy configuration.
- **Response**: 
  ```json
  {
    "momentum_weight": "number",
    "market_cap_weight": "number",
    "risk_parity_weight": "number",
    "min_price_threshold": "number",
    "max_daily_return": "number",
    "min_daily_return": "number",
    "max_forward_fill_days": "number",
    "outlier_std_threshold": "number",
    "rebalance_frequency": "string",
    "daily_drop_threshold": "number",
    "ai_adjusted": "boolean",
    "ai_adjustment_reason": "string",
    "ai_confidence_score": "number",
    "last_rebalance": "string",
    "updated_at": "string"
  }
  ```
- **Used in**: `StrategyConfig.tsx`

#### PUT `/api/v1/strategy/config`
Update strategy configuration.
- **Request Body**: Partial strategy config object
- **Query Params**: `recompute=true/false`
- **Used in**: `StrategyConfig.tsx`

#### POST `/api/v1/strategy/config/ai-adjust`
Apply AI-suggested adjustments.
- **Request Body**: 
  ```json
  {
    "adjustments": {},
    "reason": "string",
    "confidence": "number"
  }
  ```
- **Used in**: `utils/api.ts` (strategyApi)

#### GET `/api/v1/strategy/risk-metrics`
Get risk metrics for the strategy.
- **Response**: 
  ```json
  {
    "metrics": [
      {
        "date": "string",
        "total_return": "number",
        "annualized_return": "number",
        "sharpe_ratio": "number",
        "sortino_ratio": "number",
        "max_drawdown": "number",
        "current_drawdown": "number",
        "volatility": "number",
        "var_95": "number",
        "var_99": "number",
        "beta_sp500": "number",
        "correlation_sp500": "number"
      }
    ]
  }
  ```
- **Used in**: `StrategyConfig.tsx`, `dashboard/page.tsx`

#### POST `/api/v1/strategy/rebalance`
Trigger portfolio rebalancing.
- **Query Params**: `force=true/false`
- **Used in**: `StrategyConfig.tsx`

### Diagnostics (`/api/v1/diagnostics`)

#### GET `/api/v1/diagnostics/database-status`
Check database status and table counts.
- **Response**: 
  ```json
  {
    "timestamp": "string",
    "tables": {
      "table_name": {
        "count": "number",
        "status": "OK|EMPTY|ERROR",
        "earliest_date": "string",
        "latest_date": "string"
      }
    },
    "simulation_ready": "boolean",
    "message": "string"
  }
  ```
- **Used in**: `admin/page.tsx`, `SmartRefresh.tsx`

#### GET `/api/v1/diagnostics/refresh-status`
Check what needs to be refreshed.
- **Response**: 
  ```json
  {
    "assets": {
      "count": "number",
      "symbols": [],
      "has_benchmark": "boolean"
    },
    "prices": {
      "latest_date": "string",
      "days_old": "number",
      "needs_update": "boolean"
    },
    "recommendation": "string"
  }
  ```
- **Used in**: `utils/api.ts` (marketDataApi)

#### POST `/api/v1/diagnostics/test-refresh`
Test the refresh process with detailed reporting.
- **Used in**: `utils/api.ts` (marketDataApi)

#### POST `/api/v1/diagnostics/recalculate-index`
Recalculate the AutoIndex.
- **Used in**: `utils/api.ts` (marketDataApi)

### Manual Refresh (`/api/v1/manual`)

#### POST `/api/v1/manual/trigger-refresh`
Trigger a manual data refresh.
- **Used in**: `utils/api.ts` (marketDataApi), `marketService`

#### POST `/api/v1/manual/smart-refresh`
Trigger smart refresh with rate limiting protection.
- **Query Params**: `mode=auto|full|minimal|cached`
- **Used in**: `utils/api.ts` (marketDataApi), `SmartRefresh.tsx`

#### POST `/api/v1/manual/minimal-refresh`
Perform minimal refresh for testing.
- **Used in**: `utils/api.ts` (marketDataApi)

### System Health

#### GET `/health`
Basic health check endpoint.
- **Response**: `{ "status": "ok" }`
- **Note**: Currently not used by frontend

### Protected Endpoints

#### POST `/api/v1/tasks/refresh`
Requires `X-Admin-Token` header. Not directly accessible from frontend.

## API Client Services

The frontend uses three main service classes to interact with the API:

### 1. `portfolioService` (portfolio.ts)
- `getIndexHistory()`
- `getCurrentAllocations()`
- `getAssetHistory(symbol)`
- `runSimulation(request)`
- `getCurrencies()`
- `getRiskMetrics()`
- `refreshPortfolio()`

### 2. `marketService` (market.ts)
- `getSP500History()`
- `refreshMarketData()`
- `getDiagnostics()`

### 3. `strategyApi` (utils/api.ts)
- `getConfig()`
- `updateConfig(config, recompute)`
- `aiAdjust(adjustments, reason, confidence)`
- `getRiskMetrics(limit)`
- `triggerRebalance(force)`

### 4. `marketDataApi` (utils/api.ts)
- `getDatabaseStatus()`
- `triggerRefresh()`
- `triggerSmartRefresh(mode)`
- `triggerMinimalRefresh()`
- `testRefresh()`
- `getRefreshStatus()`
- `recalculateIndex()`

## Authentication Flow

1. User registers or logs in via `/auth/register` or `/auth/login`
2. Access token is stored in localStorage
3. Token is automatically included in all API requests via axios interceptor
4. On 401 responses, user is redirected to login page

## Error Handling

- All API errors are caught and handled gracefully
- 401 errors trigger automatic logout and redirect
- Network errors display user-friendly messages
- Form validation errors are shown inline

## Rate Limiting

The API implements rate limiting:
- 100 requests per minute per IP address
- Health check endpoint is excluded from rate limiting
- 429 status code returned when limit exceeded

## CORS Configuration

- Development: Allows `localhost:3000` and `127.0.0.1:3000`
- Production: Configured for Render deployment URLs
- Credentials are allowed for authenticated requests

## Security Headers

The API sets the following security headers:
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: strict-origin-when-cross-origin
- Strict-Transport-Security (production only)