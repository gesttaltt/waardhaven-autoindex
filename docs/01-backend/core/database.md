# Database Connection Management

## Overview
The database module (`app/core/database.py`) manages SQLAlchemy database connections with optimized pooling strategies for different environments.

## Location
`apps/api/app/core/database.py`

## Core Components

### Engine Configuration
```python
# Adaptive configuration based on environment
if is_sqlite:  # Testing
    pool_config = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool
    }
elif os.getenv("RENDER"):  # Production
    pool_config = {
        "poolclass": QueuePool,
        "pool_size": 20,
        "max_overflow": 40,
        "pool_timeout": 30,
        "pool_recycle": 3600,
        "pool_pre_ping": True
    }
else:  # Development
    pool_config = {
        "pool_size": 5,
        "max_overflow": 10,
        "pool_pre_ping": True
    }
```

### Connection Pooling Strategy

| Environment | Pool Size | Max Overflow | Special Config |
|-------------|-----------|--------------|----------------|
| SQLite/Test | N/A | N/A | StaticPool, single connection |
| Production | 20 | 40 | 1hr recycle, pre-ping |
| Development | 5 | 10 | Pre-ping enabled |

### Pool Parameters Explained
- `pool_size`: Number of persistent connections
- `max_overflow`: Additional connections when pool exhausted
- `pool_timeout`: Seconds to wait for connection
- `pool_recycle`: Recycle connections after X seconds
- `pool_pre_ping`: Test connections before use

## Session Management

### SessionLocal Factory
```python
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
```

### Dependency Injection
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Base Model Class

### Declarative Base
```python
Base = declarative_base()

# Common columns for all models
class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
```

## Usage Patterns

### Basic Usage in Routes
```python
from app.core.database import get_db
from sqlalchemy.orm import Session

@router.get("/items")
def get_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

### Transaction Management
```python
def create_with_transaction(db: Session):
    try:
        db.begin_nested()  # Savepoint
        # Operations
        db.commit()
    except Exception:
        db.rollback()
        raise
```

### Bulk Operations
```python
# Efficient bulk insert
db.bulk_insert_mappings(Model, data_list)
db.commit()

# Bulk update with ON CONFLICT
stmt = insert(Model).values(data)
stmt = stmt.on_conflict_do_update(
    index_elements=['id'],
    set_={'field': stmt.excluded.field}
)
db.execute(stmt)
```

## Database Schema

### Core Tables
| Table | Purpose | Key Fields |
|-------|---------|------------|
| users | User accounts | id, email, password_hash |
| assets | Trading assets | id, symbol, name, sector |
| prices | Historical prices | asset_id, date, close, volume |
| index_values | Portfolio values | date, value |
| allocations | Asset weights | date, asset_id, weight |
| strategy_config | Strategy settings | Various weight parameters |
| risk_metrics | Risk analytics | sharpe_ratio, volatility, etc |

### Relationships
```
users (1) ─── (∞) strategy_config
assets (1) ─── (∞) prices
assets (1) ─── (∞) allocations
```

## SQLAlchemy 2.0 Features

### Future Mode
```python
engine = create_engine(
    DATABASE_URL,
    future=True  # SQLAlchemy 2.0 style
)
```

### Benefits
- Better type hints
- Improved performance
- Modern query syntax
- Better async support preparation

## Performance Optimizations

### Indexes Created
```sql
-- Composite indexes for common queries
CREATE INDEX idx_price_asset_date ON prices(asset_id, date);
CREATE INDEX idx_allocation_date ON allocations(date);
CREATE INDEX idx_index_value_date ON index_values(date);
```

### Query Optimization Tips
1. Use eager loading: `query.options(joinedload(Model.relationship))`
2. Batch operations when possible
3. Use raw SQL for complex aggregations
4. Implement query result caching

### Connection Pool Monitoring
```python
# Check pool status
pool = engine.pool
print(f"Size: {pool.size()}")
print(f"Checked out: {pool.checkedout()}")
print(f"Overflow: {pool.overflow()}")
```

## Testing Configuration

### SQLite for Tests
```python
# In-memory database
TEST_DATABASE_URL = "sqlite:///:memory:"

# Test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
```

### Test Fixtures
```python
@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=test_engine)
```

## Error Handling

### Common Database Errors
| Error | Cause | Solution |
|-------|-------|----------|
| OperationalError | Connection lost | Retry with backoff |
| IntegrityError | Constraint violation | Validate before insert |
| DataError | Invalid data type | Check field types |
| ProgrammingError | SQL syntax | Review query syntax |

### Retry Logic
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def execute_with_retry(db, query):
    return db.execute(query)
```

## Migrations

### Using Alembic
```bash
# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Manual Migration Support
The app includes automatic index creation on startup via `run_migrations.py`

## Connection Management

### Health Checks
```python
def check_database_health():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
    finally:
        db.close()
```

### Graceful Shutdown
```python
def shutdown():
    engine.dispose()  # Close all connections
```

## Best Practices

### Do's
1. ✅ Always use connection pooling
2. ✅ Close sessions in finally blocks
3. ✅ Use transactions for multi-step operations
4. ✅ Index foreign keys and filtered columns
5. ✅ Monitor pool metrics in production
6. ✅ Use batch operations for bulk data

### Don'ts
1. ❌ Share sessions between threads
2. ❌ Keep sessions open unnecessarily
3. ❌ Use raw SQL without parameterization
4. ❌ Ignore connection pool warnings
5. ❌ Commit after every operation in loops

## Monitoring

### Key Metrics to Track
- Active connections count
- Pool overflow usage
- Average query time
- Slow query log
- Connection wait time
- Transaction duration

### Logging Configuration
```python
# Enable SQL logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Log pool events
logging.getLogger('sqlalchemy.pool').setLevel(logging.DEBUG)
```

## Dependencies
- `SQLAlchemy==2.0.32`: ORM framework
- `psycopg2-binary==2.9.9`: PostgreSQL adapter
- `alembic`: Database migrations (optional)

## Related Modules
- All models inherit from Base
- All routers use get_db dependency
- `run_migrations.py`: Automatic index creation
- Tests use separate test configuration