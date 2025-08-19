# Seed Assets Script

## Overview
Script to populate the database with initial asset data (stocks, ETFs, commodities).

## Location
`apps/api/app/seed_assets.py`

## Purpose
- Initialize asset database with default symbols
- Ensure required assets exist
- Set up initial portfolio components
- Prepare database for first use

## Functionality

### Main Process
1. Creates database session
2. Calls `ensure_assets()` from refresh service
3. Populates assets table with default symbols
4. Prints completion message

### Default Assets Created
The `ensure_assets()` function creates:
- **Tech Stocks**: AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA
- **ETFs**: SPY, QQQ, IWM, DIA, VTI
- **Commodities**: GLD (Gold), SLV (Silver), USO (Oil)
- **Index Tracking**: ^GSPC (S&P 500), ^DJI (Dow Jones), ^IXIC (NASDAQ)

## Usage

### Command Line
```bash
cd apps/api
python -m app.seed_assets
```

### During Setup
```bash
# After database initialization
python -m app.db_init
python -m app.seed_assets
```

### Programmatic
```python
from app.seed_assets import main
main()
```

## Output
```
Assets ensured.
```

## Database Changes

### Assets Table
Creates entries with:
- `symbol`: Ticker symbol
- `name`: Company/ETF name (fetched from API)
- `asset_type`: STOCK, ETF, or COMMODITY
- `is_active`: true (default)
- `created_at`: Current timestamp

## Idempotency
- Safe to run multiple times
- Only creates assets that don't exist
- Updates inactive assets to active
- Preserves existing asset data

## Error Handling
- Continues on API failures
- Logs warnings for failed symbols
- Creates asset with symbol only if name fetch fails
- Database rollback on critical errors

## Performance
- Batches API requests
- Respects rate limits
- Caches successful fetches
- Typical runtime: 10-30 seconds

## Dependencies
- Database must be initialized
- API key must be configured
- Network connection required
- TwelveData API availability

## Related Scripts
- `app/db_init.py` - Database initialization
- `app/tasks_refresh.py` - Refresh all data
- `app/services/refresh.py` - Core refresh logic

## When to Run
1. **Initial Setup**: After database creation
2. **Adding Assets**: When new symbols needed
3. **Recovery**: After database restore
4. **Testing**: Setting up test environment

## Configuration
Assets list defined in:
- `app/services/refresh.py` - `DEFAULT_ASSETS` constant
- Can be overridden via environment variables
- Customizable per deployment

## Troubleshooting

### No Assets Created
- Check database connection
- Verify API key configuration
- Check network connectivity
- Review logs for errors

### Partial Creation
- API rate limits hit
- Some symbols invalid
- Network interruption
- Re-run to complete

### Performance Issues
- Too many assets at once
- API rate limiting
- Database locks
- Consider batching

## Best Practices
1. Run after `db_init.py`
2. Verify API key before running
3. Check logs for warnings
4. Test in development first
5. Monitor API usage

## Future Enhancements
- Custom asset lists via config
- Asset metadata enrichment
- Historical data backfill
- Asset categorization
- Market cap fetching

## Notes
- Essential for first-time setup
- Not needed for normal operations
- Assets can be managed via API after seeding
- Consider running during off-hours for better API rates