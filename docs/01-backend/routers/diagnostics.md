# Diagnostics Router

## Overview
System diagnostics and health monitoring endpoints for operational visibility.

## Location
`apps/api/app/routers/diagnostics.py`

## Purpose
Provides system health checks, database status, cache metrics, and debugging tools.

## Actual Implementation

### GET /api/v1/diagnostics/database-status
Check database connectivity and data status.

**Response includes:**
- Database connection status
- Table row counts (users, assets, prices, index values, etc.)
- Data freshness information
- Connection pool statistics

**Response example:**
```json
{
  "status": "connected",
  "tables": {
    "users": 5,
    "assets": 500,
    "prices": 125000,
    "index_values": 365,
    "strategy_configs": 1,
    "allocations": 5000,
    "news_articles": 1000
  },
  "latest_data": {
    "latest_price_date": "2024-01-15",
    "latest_index_date": "2024-01-15"
  },
  "pool_status": {
    "size": 5,
    "checked_in": 4,
    "overflow": 0,
    "total": 5
  }
}
```

### GET /api/v1/diagnostics/refresh-status
Get status of recent data refresh operations.

**Response includes:**
- Last refresh timestamp
- Assets refreshed count
- Price records added
- Success/failure status
- Error messages if any

### GET /api/v1/diagnostics/cache-status
Check Redis cache connectivity and statistics.

**Response includes:**
- Redis connection status
- Memory usage
- Key count
- Cache hit/miss statistics
- TTL information

**Response example:**
```json
{
  "redis_available": true,
  "stats": {
    "used_memory": "1.5MB",
    "connected_clients": 2,
    "total_keys": 150,
    "expired_keys": 10
  },
  "cache_info": {
    "market_data_keys": 50,
    "news_keys": 30,
    "strategy_keys": 5
  }
}
```

### POST /api/v1/diagnostics/cache-invalidate
Invalidate cache entries by pattern.

**Request Body:**
```json
{
  "pattern": "market_data:*",
  "confirm": true
}
```

**Response:**
```json
{
  "status": "success",
  "keys_deleted": 50,
  "pattern": "market_data:*"
}
```

### POST /api/v1/diagnostics/test-refresh
Test data refresh with a small subset of data.

**Features:**
- Fetches data for 3 test symbols
- Limited date range (7 days)
- Verbose logging
- Returns detailed results

**Response includes:**
- Fetch status
- Records processed
- Errors encountered
- Performance metrics

### POST /api/v1/diagnostics/recalculate-index
Force recalculation of index values.

**Query Parameters:**
- `start_date`: Beginning date for recalculation
- `end_date`: End date for recalculation

**Features:**
- Recalculates portfolio values
- Updates allocations
- Refreshes performance metrics
- Returns calculation summary

### GET /api/v1/diagnostics/twelvedata-status
Check TwelveData API connectivity and quota.

**Response includes:**
- API connectivity status
- Rate limit information
- Credits used/remaining
- Current plan details
- Recent API call statistics

**Response example:**
```json
{
  "status": "connected",
  "api_key_configured": true,
  "plan": "free",
  "rate_limit": {
    "limit": 8,
    "remaining": 5,
    "reset_at": "2024-01-15T10:30:00Z"
  },
  "test_response": {
    "symbol": "AAPL",
    "price": 195.89,
    "timestamp": "2024-01-15T10:00:00Z"
  }
}
```

### POST /api/v1/diagnostics/clear-market-cache
Clear all market data from cache.

**Features:**
- Removes all market data cache entries
- Forces fresh data on next request
- Returns count of cleared entries

**Response:**
```json
{
  "status": "success",
  "cleared_entries": 150,
  "cache_type": "market_data"
}
```

## Authentication
All endpoints require user authentication via JWT token.

## Error Handling
- Returns detailed error messages for debugging
- Includes stack traces in debug mode
- Graceful handling of service unavailability

## Use Cases
1. **Health Monitoring**: Check system components are operational
2. **Debugging**: Investigate data issues or refresh problems
3. **Performance Tuning**: Monitor cache effectiveness
4. **Maintenance**: Clear caches, force recalculations

## Security Considerations
- Exposes internal system state
- Should have restricted access in production
- Consider rate limiting to prevent abuse

## Dependencies
- Database models and session
- Redis client
- TwelveData service
- User authentication