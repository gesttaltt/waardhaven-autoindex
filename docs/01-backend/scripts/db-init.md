# Database Initialization Script

## Overview
The `db_init.py` script initializes the database schema and creates default configuration data for the Waardhaven AutoIndex system.

## Location
`apps/api/app/db_init.py`

## Purpose
- Creates all database tables based on SQLAlchemy models
- Establishes default strategy configuration
- Ensures the database is ready for first use

## Functionality

### Table Creation
Uses SQLAlchemy's `Base.metadata.create_all()` to create all tables defined in the models:
- `users` - User accounts
- `assets` - Stock/ETF/commodity information  
- `prices` - Historical price data
- `index_values` - Calculated index values
- `allocations` - Asset allocation weights
- `strategy_configs` - Investment strategy parameters
- `news_articles` - News content and metadata
- `news_sentiment` - Sentiment analysis results
- `news_entities` - Extracted entities from news
- `asset_news` - Links between assets and news

### Default Configuration
Creates a default `StrategyConfig` entry with these parameters:
- `momentum_weight`: 0.4 (40% weight for momentum strategy)
- `market_cap_weight`: 0.3 (30% weight for market cap)
- `risk_parity_weight`: 0.3 (30% weight for risk parity)
- `min_price_threshold`: 1.0 (minimum asset price)
- `max_daily_return`: 0.5 (50% max daily return filter)
- `min_daily_return`: -0.5 (-50% min daily return filter)
- `max_forward_fill_days`: 2 (fill missing data up to 2 days)
- `outlier_std_threshold`: 3.0 (3 standard deviations for outliers)
- `rebalance_frequency`: "weekly"
- `daily_drop_threshold`: -0.01 (-1% daily drop threshold)

## Usage

### Command Line
```bash
cd apps/api
python -m app.db_init
```

### Programmatic
```python
from app.db_init import main
main()
```

### During Deployment
The script is automatically called during container startup via the `startup.sh` script.

## Safety Features
- Only creates tables if they don't exist (safe to run multiple times)
- Only creates default config if none exists
- Uses proper database session management with try/finally
- Logs all operations for visibility

## Dependencies
- SQLAlchemy models must be properly defined
- Database connection must be configured in environment
- PostgreSQL database must be accessible

## Related Files
- `app/core/database.py` - Database connection setup
- `app/models/*.py` - Model definitions
- `scripts/startup.sh` - Startup script that calls this
- `app/migrations/add_news_tables.py` - Additional migration for news tables

## Notes
- This script is idempotent (safe to run multiple times)
- In production, proper migration tools like Alembic should be considered
- The default configuration can be modified via the API after initialization