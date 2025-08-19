# API Service Layer

## Overview
Frontend API client services for backend communication.

## Location
`apps/web/app/services/api/`

## Service Files

### base.ts
Core API client configuration:
- Axios instance setup
- Base URL configuration
- Token management (localStorage)
- Request/response interceptors
- Error handling

### client.ts
Main API client export and configuration.

### portfolio.ts
Portfolio-related API calls:
- Get portfolio data
- Update allocations
- Calculate performance

### market.ts  
Market data API calls:
- Fetch price data
- Get market trends
- Currency rates

### strategy.ts
Strategy configuration API:
- Get current strategy
- Update strategy weights
- Rebalance portfolio

### benchmark.ts
Benchmark comparison API:
- Fetch S&P 500 data
- Compare performance
- Get benchmark metrics

### news.ts
News and sentiment API:
- Search news articles
- Get sentiment analysis
- Fetch trending topics

### background.ts
Background task management:
- Trigger refresh tasks
- Check task status
- Get active tasks

### diagnostics.ts
System diagnostics API:
- Database status
- Cache metrics
- System health

### manual.ts
Manual operations API:
- Trigger manual refresh
- Smart refresh options
- Debug operations

### types.ts
TypeScript type definitions for API responses and requests.

## Authentication
- JWT tokens stored in localStorage
- Automatic token attachment to requests
- 401 response triggers re-authentication

## Error Handling
- Network error catching
- API error response parsing
- User-friendly error messages
- Automatic retry logic for certain errors

## Base Configuration
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

## Common Patterns

### GET Request
```typescript
const response = await apiClient.get('/endpoint');
return response.data;
```

### POST with Data
```typescript
const response = await apiClient.post('/endpoint', data);
return response.data;
```

### Error Handling
```typescript
try {
  const data = await apiCall();
} catch (error) {
  console.error('API Error:', error);
  // Handle error appropriately
}
```

## Available Endpoints

### Authentication
- `/api/v1/auth/login`
- `/api/v1/auth/register`
- `/api/v1/auth/google`

### Portfolio Management
- `/api/v1/index/`
- `/api/v1/index/performance`

### Strategy
- `/api/v1/strategy/config`
- `/api/v1/strategy/config/ai-adjust`
- `/api/v1/strategy/risk-metrics`
- `/api/v1/strategy/rebalance`

### Market Data
- `/api/v1/benchmark/sp500`
- `/api/v1/benchmark/compare`

### News
- `/api/v1/news/search`
- `/api/v1/news/article/{id}`
- `/api/v1/news/sentiment/{symbol}`
- `/api/v1/news/trending`

### Background Tasks
- `/api/v1/background/refresh`
- `/api/v1/background/status/{task_id}`
- `/api/v1/background/active`

### System
- `/api/v1/diagnostics/database-status`
- `/api/v1/diagnostics/cache-status`
- `/api/v1/manual/trigger-refresh`
- `/api/v1/manual/smart-refresh`

## Note on Implementation
The actual implementation uses a modular approach with separate service files for each API domain, rather than a single monolithic API file.