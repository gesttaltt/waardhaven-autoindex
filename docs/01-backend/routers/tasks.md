# Tasks Router

## Overview
Background task management and scheduling for asynchronous operations.

## Location
`apps/api/app/routers/tasks.py`

## Purpose
Manages background tasks, scheduled jobs, and asynchronous processing.

## Endpoints

### GET /api/v1/tasks
- List all tasks
- Filter by status
- Pagination support
- Sort by date

### POST /api/v1/tasks
- Create new task
- Schedule execution
- Set priority
- Define retry policy

### GET /api/v1/tasks/{task_id}
- Get task details
- Execution status
- Result data
- Error information

### DELETE /api/v1/tasks/{task_id}
- Cancel pending task
- Stop running task
- Clean up resources
- Remove from queue

### GET /api/v1/tasks/{task_id}/logs
- Task execution logs
- Debug information
- Performance metrics
- Error traces

## Task Types

### Data Refresh Tasks
- `refresh_all_prices` - Update all asset prices
- `refresh_portfolio` - Update portfolio values
- `refresh_benchmark` - Update benchmark data
- `calculate_metrics` - Compute risk metrics

### Maintenance Tasks
- `cleanup_old_data` - Remove outdated records
- `optimize_database` - Database maintenance
- `backup_data` - Create backups
- `generate_reports` - Create reports

### Notification Tasks
- `send_email` - Email notifications
- `send_alert` - Push notifications
- `webhook_callback` - External webhooks
- `generate_digest` - Daily summaries

## Task Management

### Task States
- **pending**: Waiting in queue
- **running**: Currently executing
- **completed**: Successfully finished
- **failed**: Execution error
- **cancelled**: Manually stopped
- **retrying**: Retry attempt

### Priority Levels
1. **critical**: Immediate execution
2. **high**: Next in queue
3. **normal**: Standard priority
4. **low**: Background processing

## Scheduling

### Cron Schedules
```python
SCHEDULES = {
    "daily_refresh": "0 9 * * *",      # 9 AM daily
    "hourly_update": "0 * * * *",      # Every hour
    "weekly_report": "0 10 * * MON",   # Monday 10 AM
    "monthly_cleanup": "0 2 1 * *"     # 1st of month, 2 AM
}
```

### Task Queue
- Redis-based queue
- Priority ordering
- FIFO within priority
- Concurrent execution
- Worker pool management

## Task Configuration

### Retry Policy
```json
{
  "max_retries": 3,
  "retry_delay": 60,
  "exponential_backoff": true,
  "max_retry_delay": 3600
}
```

### Timeout Settings
- Default: 300 seconds
- Data refresh: 600 seconds
- Reports: 1800 seconds
- Cleanup: 3600 seconds

## Task Response

### Task Creation Response
```json
{
  "task_id": "task_abc123",
  "status": "pending",
  "created_at": "2024-01-01T00:00:00Z",
  "scheduled_for": "2024-01-01T01:00:00Z",
  "priority": "normal",
  "estimated_duration": 120
}
```

### Task Status Response
```json
{
  "task_id": "task_abc123",
  "status": "running",
  "progress": 0.65,
  "started_at": "2024-01-01T01:00:00Z",
  "current_step": "Processing data",
  "messages": ["Fetched 100 records", "Processing..."]
}
```

## Worker Management

### Worker Pool
- Configurable size
- Auto-scaling
- Health monitoring
- Graceful shutdown
- Resource limits

### Concurrency Control
- Max concurrent tasks
- Task type limits
- Resource allocation
- Queue management
- Deadlock prevention

## Error Handling

### Failure Modes
- Task timeout
- Worker crash
- Resource exhaustion
- External service failure
- Data corruption

### Recovery Strategies
- Automatic retry
- Exponential backoff
- Dead letter queue
- Manual intervention
- Rollback capability

## Monitoring

### Metrics
- Task throughput
- Success rate
- Average duration
- Queue length
- Worker utilization

### Alerts
- Task failures
- Queue backup
- Worker issues
- Long-running tasks
- Resource limits

## Task Results

### Storage
- Database for metadata
- Object storage for large results
- Cache for frequent access
- TTL for cleanup

### Retrieval
- Direct API access
- Webhook delivery
- Email attachment
- Download link

## Security

### Authorization
- Task creation permissions
- View permissions
- Cancel permissions
- Admin override

### Data Security
- Encrypted task data
- Secure parameters
- Audit logging
- Access control

## Integration

### Event Triggers
- API callbacks
- Database triggers
- File uploads
- Schedule events
- External webhooks

### Notification Channels
- Email
- SMS
- Push notifications
- Slack
- Webhooks

## Best Practices

### Task Design
- Idempotent operations
- Clear success criteria
- Proper error handling
- Resource cleanup
- Progress reporting

### Performance
- Batch operations
- Efficient queries
- Memory management
- Connection pooling
- Cache utilization

## Dependencies
- Task queue (Celery/Redis)
- Database models
- Service layer
- Notification service
- Monitoring tools