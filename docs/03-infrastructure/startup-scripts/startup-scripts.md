# Startup Scripts Documentation

## Overview
Shell scripts that manage the startup and operation of API services, background workers, and monitoring tools.

## Location
`apps/api/scripts/`

## Scripts Available

### 1. startup.sh
**Purpose**: Unified startup script for the API service with comprehensive health checks and initialization.

**Features**:
- Database connection verification with retries
- Database initialization and migrations
- Optional data refresh on startup
- Health check endpoints
- Environment-based configuration
- Production/development mode detection
- Colored logging output
- Debug mode support

**Environment Variables**:
- `DEBUG_MODE` - Enable debug logging (default: false)
- `SKIP_STARTUP_REFRESH` - Skip data refresh on startup (default: false)
- `MAX_DB_RETRIES` - Maximum database connection retries (default: 60)
- `REFRESH_TIMEOUT` - Timeout for refresh operation in seconds (default: 120)
- `PORT` - API server port (default: 10000)
- `DATABASE_URL` - PostgreSQL connection string (required)
- `RENDER` - Automatically set by Render.com in production
- `PRODUCTION` - Force production mode

**Usage**:
```bash
# Development
./scripts/startup.sh

# Production (on Render)
./scripts/startup.sh  # Automatically detects Render environment

# Debug mode
DEBUG_MODE=true ./scripts/startup.sh

# Skip refresh
SKIP_STARTUP_REFRESH=true ./scripts/startup.sh
```

**Startup Process**:
1. Environment detection (production/development)
2. Database connectivity check (with retries)
3. Database initialization (`python -m app.db_init`)
4. News tables migration check
5. Optional data refresh (if not skipped)
6. Start Uvicorn server

### 2. start_worker.sh
**Purpose**: Start Celery worker for background task processing.

**Features**:
- Processes background tasks from Redis queue
- Handles market data refresh, index calculations
- Configurable concurrency and log levels

**Usage**:
```bash
./scripts/start_worker.sh
```

**Default Command**:
```bash
celery -A app.core.celery_app worker --loglevel=info
```

### 3. start_beat.sh
**Purpose**: Start Celery beat scheduler for periodic tasks.

**Features**:
- Schedules periodic tasks (daily refresh, cleanup)
- Manages task timing and intervals
- Works with Celery workers

**Usage**:
```bash
./scripts/start_beat.sh
```

**Default Command**:
```bash
celery -A app.core.celery_app beat --loglevel=info
```

### 4. start_flower.sh
**Purpose**: Start Flower monitoring dashboard for Celery tasks.

**Features**:
- Web-based monitoring interface
- Real-time task status tracking
- Worker management
- Task history and statistics

**Usage**:
```bash
./scripts/start_flower.sh
```

**Default Command**:
```bash
celery -A app.core.celery_app flower --port=5555
```

**Access**: http://localhost:5555

## Docker Integration

The startup scripts are integrated with Docker containers:

```dockerfile
# Make scripts executable
RUN chmod +x scripts/startup.sh

# Use startup script as entrypoint
CMD ["./scripts/startup.sh"]
```

## Production Deployment

On Render.com, the `startup.sh` script:
1. Detects Render environment via `RENDER` env var
2. Uses production settings
3. Connects to managed PostgreSQL
4. Handles graceful shutdowns
5. Manages health checks

## Health Checks

The startup script enables health endpoints:
- `/health` - Basic health check
- `/api/v1/diagnostics/health` - Detailed health status

## Error Handling

### Database Connection Failures
- Retries up to MAX_DB_RETRIES times
- 1-second delay between retries
- Exits with code 1 on failure

### Migration Failures
- Logs error and continues (non-fatal)
- Manual intervention may be required

### Refresh Failures
- Logs error and continues (non-fatal)
- Service starts without fresh data

## Logging

### Log Levels
- **INFO** (Green): Normal operations
- **ERROR** (Red): Failures and errors
- **WARN** (Yellow): Warnings and non-critical issues
- **DEBUG**: Detailed information (when DEBUG_MODE=true)

### Log Output
- Structured with timestamps
- Color-coded for visibility
- Includes context (DB connection, refresh status, etc.)

## Development vs Production

### Development Mode
- More verbose logging
- Faster startup (can skip refresh)
- Auto-reload enabled
- Debug endpoints active

### Production Mode
- Optimized logging
- Full initialization
- Performance optimizations
- Security hardening

## Troubleshooting

### Script Won't Execute
```bash
# Make executable
chmod +x scripts/*.sh
```

### Database Connection Issues
```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Check environment
echo $DATABASE_URL
```

### Port Already in Use
```bash
# Find process using port
lsof -i :10000

# Kill process
kill -9 <PID>
```

### Celery Not Starting
```bash
# Check Redis connection
redis-cli ping

# Check Celery configuration
celery -A app.core.celery_app inspect stats
```

## Best Practices

1. **Always use startup.sh for API**
   - Ensures proper initialization
   - Handles all edge cases

2. **Monitor logs during startup**
   - Watch for warnings
   - Verify all services start

3. **Use environment variables**
   - Never hardcode credentials
   - Use .env files locally

4. **Test scripts locally**
   - Before deploying
   - With production-like data

5. **Keep scripts idempotent**
   - Safe to run multiple times
   - Handle partial failures

## Related Files
- `apps/api/app/db_init.py` - Database initialization
- `apps/api/app/migrations/` - Database migrations
- `apps/api/app/core/celery_app.py` - Celery configuration
- `apps/api/Dockerfile` - Container configuration
- `render.yaml` - Deployment configuration