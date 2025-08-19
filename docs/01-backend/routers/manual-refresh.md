# Manual Refresh Router

## Overview
Provides manual data refresh capabilities for debugging and testing purposes.

## Location
`apps/api/app/routers/manual_refresh.py`

## Purpose
Allows manual triggering of data updates outside of scheduled refresh cycles, primarily for debugging.

## Actual Implementation

### POST /api/v1/manual/trigger-refresh
Trigger a manual refresh without requiring admin token (for debugging).

**Note:** This endpoint should be removed or secured in production.

**Features:**
- Checks current database state (index values, prices)
- Runs refresh in background
- Returns current state information

**Response:**
```json
{
  "status": "REFRESH_STARTED",
  "message": "Refresh has been triggered in the background",
  "current_state": {
    "index_values": 100,
    "prices": 5000
  },
  "note": "Check /api/v1/diagnostics/database-status in 30-60 seconds to see results"
}
```

### POST /api/v1/manual/smart-refresh
Trigger smart refresh with rate limiting protection.

**Query Parameters:**
- `mode`: Refresh mode ("auto", "full", "minimal", "cached")

**Features:**
- Rate limit protection
- Caching support
- Fallback to cached data
- API tier optimization

**Response:**
```json
{
  "status": "SMART_REFRESH_STARTED",
  "message": "Smart refresh has been triggered in auto mode",
  "mode": "auto",
  "features": [
    "Rate limit protection",
    "Caching support",
    "Fallback to cached data",
    "API tier optimization"
  ],
  "note": "This refresh is optimized for your API plan and will avoid rate limits"
}
```

### POST /api/v1/manual/minimal-refresh
Perform a minimal refresh with just a few days of data for testing.

**Features:**
- Fetches only 7 days of data
- Limited to 3 symbols (AAPL, MSFT, GOOGL)
- Creates simple index values
- Good for quick testing

**Response:**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "steps": [
    {
      "step": "assets",
      "count": 3,
      "symbols": ["AAPL", "MSFT", "GOOGL"]
    },
    {
      "step": "prices",
      "fetched": 21,
      "stored": 21
    },
    {
      "step": "index_values",
      "created": 7
    }
  ],
  "status": "SUCCESS",
  "message": "Minimal data refresh completed"
}
```

## Helper Functions

### run_refresh_with_logging(db: Session)
Internal function that:
- Logs refresh progress
- Calls `refresh_all()` from services
- Verifies results
- Handles errors with detailed logging

### run_smart_refresh_with_logging(db: Session, mode: str)
Internal function that:
- Attempts to use `smart_refresh()` if available
- Falls back to standard refresh if not
- Logs all operations
- Verifies results

## Security Considerations

⚠️ **WARNING**: These endpoints are intended for debugging and testing only.
- No authentication required (security risk)
- Should be disabled or secured in production
- Exposes internal system state

## Error Handling
- Database errors return traceback (debug info)
- Failed refreshes log detailed error information
- Graceful fallback for missing smart refresh module

## Dependencies
- services/refresh: Core refresh logic
- services/refresh_optimized: Smart refresh (optional)
- Database session
- Background tasks