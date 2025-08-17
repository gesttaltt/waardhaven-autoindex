# Celery Task Queue Configuration

## Overview
The Celery module (`app/core/celery_app.py`) configures and manages the distributed task queue for asynchronous processing.

## Location
`apps/api/app/core/celery_app.py`

## Core Configuration

### Celery Application
```python
celery_app = Celery(
    "waardhaven_tasks",
    broker=settings.REDIS_URL or "redis://localhost:6379/1",
    backend=settings.REDIS_URL or "redis://localhost:6379/1",
    include=["app.tasks.background_tasks"]
)
```

### Task Settings
```python
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,  # 1 hour
    task_track_started=True,
    task_time_limit=1800,  # 30 minutes hard limit
    task_soft_time_limit=1500,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50
)
```

## Task Routing

### Queue Configuration
```python
task_routes = {
    "refresh_market_data": {"queue": "high_priority"},
    "compute_index": {"queue": "high_priority"},
    "generate_report": {"queue": "low_priority"},
    "cleanup_old_data": {"queue": "low_priority"},
}
```

### Queue Priorities
| Queue | Purpose | Tasks |
|-------|---------|-------|
| high_priority | Time-sensitive operations | Market refresh, Index computation |
| low_priority | Background maintenance | Reports, Cleanup |
| default | General tasks | Everything else |

## Beat Schedule (Periodic Tasks)

### Configured Schedule
```python
beat_schedule = {
    "daily-refresh": {
        "task": "refresh_market_data",
        "schedule": 86400.0,  # Daily
        "options": {"queue": "high_priority"}
    },
    "hourly-index": {
        "task": "compute_index",
        "schedule": 3600.0,  # Hourly
        "options": {"queue": "high_priority"}
    },
    "weekly-cleanup": {
        "task": "cleanup_old_data",
        "schedule": 604800.0,  # Weekly
        "options": {"queue": "low_priority"}
    }
}
```

### Schedule Types
| Interval | Seconds | Use Case |
|----------|---------|----------|
| Minutely | 60 | High-frequency updates |
| Hourly | 3600 | Regular computations |
| Daily | 86400 | Market data refresh |
| Weekly | 604800 | Maintenance tasks |

## Worker Configuration

### Performance Settings
- **prefetch_multiplier**: 1 (disable prefetching for long tasks)
- **max_tasks_per_child**: 50 (restart after 50 tasks)
- **time_limit**: 1800 seconds (30 minutes hard limit)
- **soft_time_limit**: 1500 seconds (25 minutes warning)

### Concurrency
```bash
# Start worker with concurrency
celery -A app.core.celery_app worker --concurrency=4
```

## Task Serialization

### JSON Serialization
- **Advantages**: Human-readable, debuggable
- **Limitations**: No complex Python objects
- **Use Case**: API data, configurations

### Supported Content Types
```python
accept_content = ["json"]  # Only JSON for security
```

## Result Backend

### Redis Backend
- Stores task results for 1 hour
- Enables result retrieval by task ID
- Supports task state tracking

### Result States
| State | Description |
|-------|-------------|
| PENDING | Task waiting to execute |
| STARTED | Task has begun |
| PROGRESS | Custom progress updates |
| SUCCESS | Task completed successfully |
| FAILURE | Task failed with error |
| RETRY | Task will be retried |
| REVOKED | Task was cancelled |

## Starting Workers

### Basic Worker
```bash
celery -A app.core.celery_app worker --loglevel=info
```

### With Specific Queues
```bash
celery -A app.core.celery_app worker \
  --queues=high_priority,low_priority \
  --loglevel=info
```

### Beat Scheduler
```bash
celery -A app.core.celery_app beat \
  --loglevel=info \
  --scheduler=celery.beat:PersistentScheduler
```

### Flower Monitoring
```bash
celery -A app.core.celery_app flower \
  --port=5555 \
  --basic_auth=admin:password
```

## Task Implementation

### Base Task Class
```python
class DatabaseTask(Task):
    """Base task with database session management."""
    
    def __call__(self, *args, **kwargs):
        db = SessionLocal()
        try:
            kwargs['db'] = db
            result = self.run(*args, **kwargs)
            db.commit()
            return result
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
```

### Task Example
```python
@celery_app.task(bind=True, base=DatabaseTask)
def refresh_market_data(self, mode="smart", db=None):
    self.update_state(state="PROGRESS", meta={"status": "Starting..."})
    # Task implementation
    return {"status": "success"}
```

## Progress Tracking

### Update State
```python
self.update_state(
    state="PROGRESS",
    meta={
        "current": 50,
        "total": 100,
        "status": "Processing..."
    }
)
```

### Retrieve Progress
```python
from celery.result import AsyncResult

result = AsyncResult(task_id)
if result.state == "PROGRESS":
    current = result.info.get("current", 0)
    total = result.info.get("total", 100)
    percent = (current / total) * 100
```

## Error Handling

### Retry Logic
```python
@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def task_with_retry(self):
    try:
        # Task logic
        pass
    except Exception as exc:
        raise self.retry(exc=exc)
```

### Exponential Backoff
```python
raise self.retry(
    exc=exc,
    countdown=2 ** self.request.retries
)
```

## Task Monitoring

### Inspect Active Tasks
```python
from app.core.celery_app import celery_app

inspect = celery_app.control.inspect()
active = inspect.active()  # Currently executing
scheduled = inspect.scheduled()  # Scheduled tasks
reserved = inspect.reserved()  # Tasks reserved by workers
```

### Revoke Tasks
```python
celery_app.control.revoke(task_id, terminate=True)
```

## Performance Optimization

### Task Chunking
```python
from celery import group

# Split large task into chunks
job = group(
    process_chunk.s(chunk)
    for chunk in chunks
)
result = job.apply_async()
```

### Rate Limiting
```python
@celery_app.task(rate_limit="10/m")  # 10 per minute
def rate_limited_task():
    pass
```

## Deployment Considerations

### Production Settings
```python
# Recommended production configuration
CELERY_SETTINGS = {
    "broker_connection_retry_on_startup": True,
    "broker_pool_limit": 10,
    "result_backend_pool_limit": 10,
    "task_acks_late": True,
    "task_reject_on_worker_lost": True,
    "worker_disable_rate_limits": False,
}
```

### Scaling Workers
```bash
# Scale horizontally
celery -A app.core.celery_app worker --autoscale=10,3
# Min 3 workers, max 10 based on load
```

## Security

### Task Signing
```python
celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    task_always_eager=False,
    task_ignore_result=False,
)
```

### Access Control
- Use Redis AUTH
- Implement task-level permissions
- Validate task inputs

## Troubleshooting

### Common Issues
| Issue | Cause | Solution |
|-------|-------|----------|
| Tasks not executing | Worker not running | Start worker process |
| Tasks stuck | Long-running without timeout | Set time limits |
| Memory leaks | Worker not restarting | Set max_tasks_per_child |
| Lost tasks | Worker crash | Enable task_acks_late |

### Debug Mode
```python
# Enable debug logging
celery_app.conf.update(
    task_always_eager=True,  # Execute synchronously
    task_eager_propagates=True,  # Propagate exceptions
)
```

## Integration Points

### Background Tasks Module
All task implementations in `app/tasks/background_tasks.py`

### API Routes
Task triggers in `app/routers/background.py`

### Redis Client
Shares Redis connection for broker/backend

## Dependencies
- `celery==5.3.4`: Task queue framework
- `redis==5.0.7`: Broker and backend
- `flower==2.0.1`: Monitoring dashboard

## Related Modules
- `background_tasks.py`: Task implementations
- `background.py`: API endpoints for tasks
- `redis_client.py`: Redis connection management