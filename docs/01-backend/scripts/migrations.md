# Database Migrations

## Overview
Database migration scripts for schema updates and data transformations in the Waardhaven AutoIndex system.

## Current Migrations

### add_news_tables.py
Location: `apps/api/app/migrations/add_news_tables.py`

Creates news and sentiment analysis tables for the news integration feature.

#### Tables Created
1. **news_sources**
   - Stores information about news providers
   - Fields: id, name, domain, country, language, credibility_score, is_active
   - Indexes on name and domain

2. **news_articles**
   - Main news content storage
   - Fields: id, external_id, title, description, content, url, image_url, source_id, published_at, categories, keywords
   - Indexes on published_at, source_id, external_id, url
   - Unique constraints on external_id and url

3. **news_sentiment**
   - Sentiment analysis results
   - Fields: id, article_id, sentiment_score, sentiment_label, confidence, positive/negative/neutral scores
   - One-to-one relationship with news_articles
   - Indexes on article_id, sentiment_score, sentiment_label

4. **news_entities**
   - Extracted entities (companies, stocks) from articles
   - Fields: id, article_id, symbol, name, type, exchange, sentiment_score, mention_count
   - Many-to-one relationship with news_articles
   - Indexes on article_id, symbol, type, name

5. **asset_news**
   - Association table linking assets to news articles
   - Fields: asset_id (INTEGER), article_id (UUID), relevance_score, sentiment_score
   - Composite primary key (asset_id, article_id)
   - **Note**: Contains a type mismatch bug - asset_id should be UUID

6. **entity_sentiment_history**
   - Historical sentiment tracking by symbol
   - Fields: id, symbol, date, sentiment_score, article counts, mention counts
   - Unique constraint on (symbol, date)
   - Index on (symbol, date) for time-series queries

## Running Migrations

### Manual Execution
```bash
cd apps/api
python -m app.migrations.add_news_tables
```

### Automatic Execution
Migrations are checked and run automatically during startup via the startup script.

### Check Migration Status
```python
from app.migrations.add_news_tables import create_news_tables
create_news_tables()  # Safe to run multiple times
```

## Migration Safety Features
- Checks if tables exist before creation
- Uses `IF NOT EXISTS` clauses
- Idempotent operations (safe to run multiple times)
- Logs all operations
- Runs in transactions

## Known Issues

### Type Mismatch Bug
The `asset_news` association table has a critical bug:
- `asset_id` is defined as INTEGER
- But `assets.id` (reference table) uses UUID
- This causes foreign key constraint failures

**Fix Required**:
```sql
ALTER TABLE asset_news 
ALTER COLUMN asset_id TYPE UUID USING asset_id::text::uuid;
```

## Best Practices
1. Always backup database before running migrations
2. Test migrations in development first
3. Review migration logs after execution
4. Verify data integrity post-migration
5. Document any manual steps required

## Future Improvements
- Implement Alembic for version-controlled migrations
- Add rollback capabilities
- Create migration validation tests
- Add data migration scripts
- Implement zero-downtime migrations

## Related Files
- `app/db_init.py` - Initial database setup
- `app/core/database.py` - Database configuration
- `app/models/*.py` - Model definitions
- `scripts/startup.sh` - Runs migrations on startup

## Migration History
| Date | Migration | Description |
|------|-----------|-------------|
| 2025-01-19 | add_news_tables | Added news and sentiment analysis tables |

## Creating New Migrations
1. Create new file in `app/migrations/`
2. Follow naming convention: `{action}_{description}.py`
3. Include existence checks
4. Add to startup sequence if needed
5. Document in this file

## Troubleshooting
- **Foreign key errors**: Check type compatibility
- **Duplicate key errors**: Migration may have partially run
- **Permission errors**: Check database user privileges
- **Connection errors**: Verify DATABASE_URL configuration