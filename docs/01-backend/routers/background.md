# Background Tasks Router

## ⚠️ Implementation Status: PARTIAL
- ✅ Basic endpoints implemented
- ⚠️ Celery integration may not be fully configured
- ⚠️ Some task implementations may be stubs

## Overview
Manages asynchronous background tasks using Celery for long-running operations like data refresh, report generation, and cleanup.

## Location
`apps/api/app/routers/background.py`

## Endpoints

### POST /api/v1/background/refresh
Trigger background market data refresh task.

**Request Body:**
```json
{
  "mode": "smart",  // "smart" or "full"
  "symbols": ["AAPL", "MSFT"],  // Optional, defaults to all
  "force": false  // Skip cache if true
}
```

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Refresh task queued"
}
```

### POST /api/v1/background/compute-index
Trigger index value computation in background.

**Request Body:**
```json
{
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "strategy": "momentum"  // Optional strategy override
}
```

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "pending",
  "message": "Index computation task queued"
}
```

### POST /api/v1/background/generate-report
Generate portfolio performance report.

**Request Body:**
```json
{
  "report_type": "monthly",  // "daily", "weekly", "monthly", "quarterly"
  "format": "pdf",  // "pdf", "excel", "json"
  "email": "user@example.com"  // Optional email delivery
}
```

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440002",
  "status": "pending",
  "message": "Report generation task queued"
}
```

### POST /api/v1/background/cleanup
Clean up old data based on retention policy.

**Request Body:**
```json
{
  "older_than_days": 365,
  "types": ["prices", "news", "logs"],
  "dry_run": true  // Preview without deleting
}
```

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440003",
  "status": "pending",
  "message": "Cleanup task queued"
}
```

### GET /api/v1/background/status/{task_id}
Get status of a background task.

**Note:** Endpoint path is `/status/{task_id}`, not `/task/{task_id}`

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "success",  // "pending", "started", "success", "failure", "retry"
  "result": {
    "symbols_processed": 10,
    "records_updated": 2500,
    "duration_seconds": 45
  },
  "error": null,
  "started_at": "2024-01-01T10:00:00Z",
  "completed_at": "2024-01-01T10:00:45Z"
}
```

### GET /api/v1/background/active
Get list of active tasks (replaces /tasks endpoint).

**Response:**
```json
{
  "active": {},
  "scheduled": {},
  "reserved": {},
  "stats": {
    "total_active": 0,
    "total_scheduled": 0,
    "total_reserved": 0
  }
}
```

**Note:** Returns error message if Celery worker is not running.

### ❌ DELETE /api/v1/background/task/{task_id}
**NOT IMPLEMENTED** - Task cancellation is not available in current implementation.

## Task Types

### Market Data Refresh
- Fetches latest prices from TwelveData
- Updates database with new records
- Invalidates relevant caches
- Triggers index recalculation

### Index Computation
- Calculates portfolio values
- Updates allocations
- Computes performance metrics
- Stores historical data

### Report Generation
- Aggregates performance data
- Creates visualizations
- Formats output (PDF/Excel)
- Optionally emails results

### Data Cleanup
- Removes old price records
- Archives historical data
- Cleans up temporary files
- Optimizes database

## Celery Configuration

### Queue Structure
- `high_priority`: Critical tasks (refresh)
- `default`: Normal tasks (computation)
- `low_priority`: Cleanup and maintenance

### Worker Configuration
```python
# Start worker
celery -A app.core.celery_app worker --loglevel=info

# Start beat scheduler for periodic tasks
celery -A app.core.celery_app beat --loglevel=info

# Monitor with Flower
celery -A app.core.celery_app flower --port=5555
```

### Periodic Tasks
- Hourly: Smart refresh of active symbols
- Daily: Full market data update
- Weekly: Performance report generation
- Monthly: Data cleanup and optimization

## Task Monitoring

### Flower Dashboard
Access at `http://localhost:5555` when running:
- View active workers
- Monitor task queue
- Inspect task details
- View task history

### Task States
- **PENDING**: Task waiting in queue
- **STARTED**: Task being executed
- **SUCCESS**: Task completed successfully
- **FAILURE**: Task failed with error
- **RETRY**: Task scheduled for retry
- **REVOKED**: Task cancelled

## Error Handling

### Retry Policy
```python
retry_kwargs = {
    'max_retries': 3,
    'countdown': 60,  # Wait 60 seconds between retries
    'retry_jitter': True
}
```

### Failure Notifications
- Critical failures logged to error tracking
- Email notifications for report failures
- Slack integration for monitoring

## Performance Considerations

### Task Optimization
- Batch processing for bulk operations
- Chunking large datasets
- Parallel execution where possible
- Result caching

### Resource Limits
- Memory limit: 512MB per task
- Time limit: 5 minutes for refresh
- Soft time limit with graceful shutdown

## Security

- Authentication required for all endpoints
- Task results expire after 24 hours
- Input validation and sanitization
- Rate limiting per user

## Redis Backend

### Configuration
```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
```

### Key Patterns
- `celery-task-meta-{task_id}`: Task results
- `celery-task-tombstone-{task_id}`: Completed tasks
- `celery-queue-{queue_name}`: Task queues

## Related Modules
- `tasks/background_tasks.py`: Task implementations
- `core/celery_app.py`: Celery configuration
- `services/refresh.py`: Refresh logic
- `utils/cache.py`: Cache invalidation