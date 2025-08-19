# Tasks Refresh Script

## Overview
The `tasks_refresh.py` script provides a simple command-line interface to manually refresh all market data and calculations.

## Location
`apps/api/app/tasks_refresh.py`

## Purpose
- Manual data refresh trigger
- Debugging and testing
- Scheduled job execution
- Initial data population

## Functionality

### Main Process
1. Creates database session
2. Calls `refresh_all()` from the refresh service
3. Prints completion message
4. Closes database session

### What Gets Refreshed
The `refresh_all()` function performs:
- Fetches latest market prices for all assets
- Updates index calculations
- Recalculates allocations
- Updates performance metrics
- Refreshes benchmark data (S&P 500)

## Usage

### Command Line
```bash
cd apps/api
python -m app.tasks_refresh
```

### Cron Job
```bash
# Add to crontab for daily refresh at 6 PM EST
0 18 * * * cd /app && python -m app.tasks_refresh
```

### Docker Container
```bash
docker exec -it waardhaven-api python -m app.tasks_refresh
```

## Output
Simple console output:
```
Refresh complete.
```

For detailed logging, check the application logs which will show:
- Number of assets updated
- Price fetch details
- Calculation results
- Any errors encountered

## Error Handling
- Basic error handling via the refresh service
- Database rollback on failures
- Errors logged to application logs

## Performance Considerations
- Can take several minutes for large asset lists
- API rate limits may cause delays
- Database locks during updates

## Related Files
- `app/services/refresh.py` - Core refresh logic
- `app/routers/tasks.py` - API endpoint for refresh
- `app/routers/manual.py` - Manual refresh endpoints
- `app/routers/background.py` - Background task version

## Notes
- This is a synchronous operation (blocks until complete)
- For production, use the background task API endpoints
- Consider using Celery workers for async processing
- Check API rate limits before running frequently

## Alternatives
- `/api/v1/manual/refresh` - HTTP endpoint
- `/api/v1/background/refresh` - Async version
- `/api/v1/tasks/refresh` - Task-based endpoint
- Celery beat scheduler for periodic execution