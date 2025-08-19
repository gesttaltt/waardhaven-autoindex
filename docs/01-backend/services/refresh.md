# Refresh Service

## Overview
Manages data refresh operations for market data and portfolio calculations.

## Location
`apps/api/app/services/refresh.py`

## Note on Architecture
The refresh service works in conjunction with the provider pattern:
- **Providers** (`apps/api/app/providers/`): Handle external API communication
- **Services** (`apps/api/app/services/`): Implement business logic using providers
- The refresh service uses market data providers for fetching prices

## Actual Implementation

### ensure_assets(db: Session)
Ensures required assets exist in the database.

**Features:**
- Creates initial asset records if missing
- Sets up base assets for the index
- Required before any price fetching
- Idempotent operation

### refresh_all(db: Session, smart_mode: bool = True)
Main refresh function that updates all market data and recalculates portfolio values.

**Parameters:**
- `db`: Database session
- `smart_mode`: Whether to use smart refresh optimizations (default: True)

**Process:**
1. Ensure assets exist in database
2. Fetch latest market data from providers
3. Store updated prices
4. Recalculate portfolio allocations
5. Update index values
6. Calculate performance metrics
7. Invalidate relevant caches

**Features:**
- Handles rate limiting
- Error recovery
- Partial update support
- Transaction management
- Logging throughout

## Data Flow

### Refresh Sequence
1. **Asset Verification**: Check and create required assets
2. **Market Data Fetch**: Get latest prices from TwelveData
3. **Database Update**: Store new price records
4. **Strategy Application**: Apply configured strategy rules
5. **Allocation Calculation**: Determine new portfolio weights
6. **Index Value Update**: Calculate new index values
7. **Metrics Calculation**: Update performance metrics
8. **Cache Invalidation**: Clear outdated cached data

## Smart Mode Features
When `smart_mode=True`:
- Skips unchanged data
- Uses cached results where appropriate
- Optimizes API calls
- Reduces processing time

## Error Handling

### API Failures
- Automatic retry with exponential backoff
- Falls back to cached data if available
- Logs detailed error information
- Continues with partial data when possible

### Data Validation
- Checks for outliers
- Validates price ranges
- Ensures data consistency
- Handles missing data points

## Rate Limiting
- Respects provider rate limits
- Implements request throttling
- Queues requests when at limit
- Uses batch fetching when possible

## Transaction Management
- Uses database transactions for consistency
- Rollback on critical errors
- Partial commits for large updates
- Maintains data integrity

## Performance Optimizations

### Batch Processing
- Groups API calls for efficiency
- Processes multiple assets together
- Minimizes database round trips

### Caching Strategy
- Caches frequently accessed data
- Smart cache invalidation
- Fallback to cache on errors

## Dependencies
- `services/twelvedata.py`: Market data fetching
- `services/strategy.py`: Strategy calculations
- `models/*`: Database models
- `providers/*`: External data providers
- `utils/cache.py`: Cache management

## Usage Examples

### Manual Refresh
```python
from app.services.refresh import refresh_all
from app.core.database import get_db

db = next(get_db())
refresh_all(db, smart_mode=True)
```

### Ensure Assets
```python
from app.services.refresh import ensure_assets

ensure_assets(db)
```

## Related Modules
- `routers/manual_refresh.py`: API endpoints for manual refresh
- `routers/tasks.py`: Admin refresh endpoint
- `tasks/background_tasks.py`: Async refresh tasks
- `providers/market_data/twelvedata.py`: Data provider