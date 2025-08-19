# Database Migration & Optimization Tasks

**Priority**: P1 - HIGH  
**Status**: 🟡 Partially Complete  
**Estimated**: 1 day  
**Dependencies**: Backend calculations

## 🎯 Objective

Implement proper database migration system with Alembic and optimize database performance with indexes and query optimization.

## 📋 Current State

### ✅ Completed
- Composite indexes added via SQL scripts
- Auto-migration on startup via `run_migrations.py`
- Basic transaction safety implemented

### 🔴 Missing
- Alembic migration system
- Version control for schema changes
- Rollback capabilities
- Migration testing

## 📋 Task Breakdown

### Phase 1: Alembic Setup (2 hours)

#### Task 1.1: Initialize Alembic
```bash
cd apps/api
pip install alembic
alembic init alembic
```

**Files to create/modify**:
- [ ] `alembic.ini` - Configuration
- [ ] `alembic/env.py` - Environment setup
- [ ] `alembic/script.py.mako` - Migration template

#### Task 1.2: Configure Alembic
**File**: `apps/api/alembic.ini`

```ini
# Key configurations:
- [ ] Set sqlalchemy.url from environment
- [ ] Configure file naming pattern
- [ ] Set compare_type = true
- [ ] Set compare_server_default = true
```

**File**: `apps/api/alembic/env.py`

```python
# Updates needed:
- [ ] Import models from app.models
- [ ] Get DATABASE_URL from environment
- [ ] Configure async support
- [ ] Add custom naming conventions
```

### Phase 2: Create Initial Migration (2 hours)

#### Task 2.1: Generate Base Migration
```bash
# Commands to run:
- [ ] alembic revision --autogenerate -m "Initial schema"
- [ ] Review generated migration
- [ ] Add missing indexes
- [ ] Add constraints
```

#### Task 2.2: Migration Files
**File**: `apps/api/alembic/versions/001_initial_schema.py`

```python
# Migration should include:
- [ ] All current tables
- [ ] Primary keys and foreign keys
- [ ] Unique constraints
- [ ] Check constraints
- [ ] Default values
```

### Phase 3: Performance Indexes (1 hour)

#### Task 3.1: Composite Indexes
**File**: `apps/api/alembic/versions/002_performance_indexes.py`

```python
def upgrade():
    # Indexes to create:
    - [ ] ix_prices_asset_date (asset_id, date)
    - [ ] ix_prices_date (date) for time-series queries
    - [ ] ix_allocations_user_date (user_id, date)
    - [ ] ix_index_values_date_type (date, index_type)
    - [ ] ix_transactions_user_date (user_id, transaction_date)
    
def downgrade():
    # Drop all indexes
```

#### Task 3.2: Partial Indexes
```python
# Conditional indexes for optimization:
- [ ] ix_prices_latest - WHERE is_latest = true
- [ ] ix_allocations_active - WHERE is_active = true
- [ ] ix_users_active - WHERE deleted_at IS NULL
```

### Phase 4: Data Migration Scripts (2 hours)

#### Task 4.1: Data Transformation Migrations
**File**: `apps/api/alembic/versions/003_data_transformations.py`

```python
# Data migrations needed:
- [ ] Normalize existing price data
- [ ] Backfill missing calculations
- [ ] Clean duplicate entries
- [ ] Update denormalized fields
```

#### Task 4.2: Safe Migration Patterns
```python
# Implementation patterns:
- [ ] Batch processing for large tables
- [ ] Progress logging
- [ ] Rollback on error
- [ ] Verification queries
```

### Phase 5: Migration Automation (1 hour)

#### Task 5.1: Startup Migration
**File**: `apps/api/app/core/database_init.py`

```python
async def run_migrations():
    """Run pending migrations on startup"""
    - [ ] Check current version
    - [ ] Run pending migrations
    - [ ] Verify schema
    - [ ] Log migration status
```

#### Task 5.2: CI/CD Integration
**File**: `.github/workflows/deploy.yml`

```yaml
# Add migration step:
- [ ] Run migrations before deployment
- [ ] Backup database first
- [ ] Rollback on failure
- [ ] Notify on completion
```

### Phase 6: Query Optimization (2 hours)

#### Task 6.1: Slow Query Analysis
```sql
-- Queries to optimize:
- [ ] Portfolio value calculation
- [ ] Historical price fetching
- [ ] Allocation rebalancing
- [ ] Performance metrics
```

#### Task 6.2: Query Optimization
**File**: `apps/api/app/services/database_optimization.py`

```python
# Optimizations:
- [ ] Use bulk operations
- [ ] Implement query caching
- [ ] Add query hints
- [ ] Use materialized views
```

## 📊 Migration Examples

### Complete Alembic Setup

```python
# apps/api/alembic/env.py

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent.parent))

from app.models import Base
from app.core.config import settings

config = context.config

# Get database URL from environment
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Performance Index Migration

```python
# apps/api/alembic/versions/002_performance_indexes.py

from alembic import op
import sqlalchemy as sa

revision = '002'
down_revision = '001'

def upgrade():
    # Composite indexes for common queries
    op.create_index(
        'ix_prices_asset_date',
        'prices',
        ['asset_id', 'date'],
        unique=True
    )
    
    # Partial index for latest prices
    op.execute("""
        CREATE INDEX ix_prices_latest 
        ON prices(asset_id, date) 
        WHERE is_latest = true
    """)
    
    # Index for time-series queries
    op.create_index(
        'ix_prices_date_desc',
        'prices',
        [sa.text('date DESC')]
    )
    
    # User portfolio queries
    op.create_index(
        'ix_allocations_user_date',
        'allocations',
        ['user_id', 'date', 'asset_id']
    )
    
    # Performance tracking
    op.create_index(
        'ix_index_values_date',
        'index_values',
        ['date', 'index_type']
    )

def downgrade():
    op.drop_index('ix_prices_asset_date')
    op.drop_index('ix_prices_latest')
    op.drop_index('ix_prices_date_desc')
    op.drop_index('ix_allocations_user_date')
    op.drop_index('ix_index_values_date')
```

## 🧪 Testing Checklist

### Migration Tests
- [ ] Test upgrade path
- [ ] Test downgrade path
- [ ] Test with empty database
- [ ] Test with existing data
- [ ] Test rollback scenarios

### Performance Tests
- [ ] Measure query time before/after indexes
- [ ] Test with large datasets (1M+ rows)
- [ ] Test concurrent access
- [ ] Monitor index usage
- [ ] Check query plans

## 📈 Success Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Migration system | Manual SQL | Alembic | 🔴 |
| Query performance | >500ms | <50ms | 🔴 |
| Index coverage | Partial | Complete | 🟡 |
| Migration testing | None | Automated | 🔴 |
| Rollback capability | None | Full | 🔴 |

## 🚀 Implementation Commands

```bash
# Initial setup
cd apps/api
pip install alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Description"

# Review migration
cat alembic/versions/xxx_description.py

# Run migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1

# Check current version
alembic current

# Show history
alembic history
```

## ⚠️ Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Data loss during migration | Critical | Backup before migration |
| Long migration time | High | Run during maintenance window |
| Index bloat | Medium | Monitor index usage |
| Failed rollback | High | Test rollback path |

## 📝 Monitoring Queries

```sql
-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan;

-- Find slow queries
SELECT query, calls, mean_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC;

-- Check table sizes
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC;
```

## 🔄 Dependencies

### Python Packages
```txt
alembic>=1.12.0
psycopg2-binary>=2.9.0
```

### Environment Variables
```env
# Add to .env
ALEMBIC_CONFIG=alembic.ini
AUTO_MIGRATE_ON_START=true
MIGRATION_TIMEOUT=300
```

---

**Next**: Continue with [03-api-integrations.md](./03-api-integrations.md)