# Manual Refresh Router

## Overview
Provides manual data refresh capabilities for administrators and users.

## Location
`apps/api/app/routers/manual_refresh.py`

## Purpose
Allows manual triggering of data updates outside of scheduled refresh cycles.

## Endpoints

### POST /api/v1/manual/refresh/all
- Refresh all market data
- Update all portfolios
- Recalculate metrics
- Full system refresh

### POST /api/v1/manual/refresh/prices
- Update asset prices only
- Fetch latest market data
- Skip calculations
- Quick price update

### POST /api/v1/manual/refresh/portfolio/{user_id}
- Refresh specific user portfolio
- Recalculate allocations
- Update performance metrics
- User-specific refresh

### POST /api/v1/manual/refresh/strategy
- Rerun strategy calculations
- Update allocations
- Generate new signals
- Apply rebalancing

### POST /api/v1/manual/refresh/benchmark
- Update benchmark data
- Refresh S&P 500 prices
- Recalculate comparisons
- Update correlations

## Refresh Types

### Full Refresh
- Complete data update
- All assets and portfolios
- Historical data backfill
- Cache invalidation
- Duration: 30-60 seconds

### Incremental Refresh
- Latest prices only
- Changed data update
- Partial calculations
- Cache update
- Duration: 5-10 seconds

### Smart Refresh
- Intelligent detection
- Priority-based updates
- Resource optimization
- Minimal API calls
- Duration: Variable

## Authorization

### Access Levels
- **Admin**: All refresh operations
- **User**: Own portfolio only
- **System**: Automated triggers
- **Support**: Limited refresh

### Rate Limiting
- Admin: 100 requests/hour
- User: 10 requests/hour
- Cooldown: 1 minute
- Burst protection

## Refresh Process

### Execution Flow
1. Validate request
2. Check permissions
3. Acquire lock
4. Fetch data
5. Update database
6. Recalculate metrics
7. Invalidate cache
8. Return status

### Error Handling
- API failures: Retry with backoff
- Partial failures: Continue with available data
- Lock conflicts: Queue request
- Timeout: Cancel and notify

## Response Format

### Success Response
```json
{
  "status": "success",
  "refresh_id": "ref_123456",
  "timestamp": "2024-01-01T00:00:00Z",
  "duration_ms": 5234,
  "items_updated": {
    "prices": 12,
    "portfolios": 1,
    "metrics": 24
  }
}
```

### Progress Response
```json
{
  "status": "in_progress",
  "refresh_id": "ref_123456",
  "progress": 0.75,
  "current_step": "Calculating metrics",
  "estimated_completion": "2024-01-01T00:00:30Z"
}
```

## Scheduling

### Manual vs Automated
- Manual overrides schedule
- Prevents duplicate runs
- Respects rate limits
- Logged separately

### Priority Queue
- Admin requests: High
- User requests: Medium
- System requests: Low
- Emergency: Immediate

## Performance Optimization

### Caching Strategy
- Selective invalidation
- Incremental updates
- Pre-warming
- TTL management

### Resource Management
- Connection pooling
- Parallel processing
- Batch operations
- Memory limits

## Monitoring

### Metrics Tracked
- Refresh frequency
- Success rate
- Duration
- API calls used
- Cache impact

### Logging
- Request details
- Execution time
- Data changes
- Error details
- User actions

## Webhook Integration

### Refresh Triggers
- External webhooks
- Market events
- Schedule overrides
- Alert conditions

### Notifications
- Refresh complete
- Errors occurred
- Data anomalies
- Rate limit warnings

## Testing

### Test Scenarios
- Concurrent refreshes
- API failures
- Large datasets
- Permission checks
- Rate limiting

### Mock Mode
- Simulated refresh
- No API calls
- Test data updates
- Performance testing

## Best Practices

### Usage Guidelines
- Avoid peak hours
- Batch similar requests
- Monitor rate limits
- Check status before retry

### Performance Tips
- Use incremental when possible
- Schedule during off-hours
- Monitor resource usage
- Cache effectively

## Dependencies
- Refresh service
- TwelveData service
- Database models
- Cache service
- Task queue