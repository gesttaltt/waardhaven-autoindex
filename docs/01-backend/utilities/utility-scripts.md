# Utility Scripts Documentation

## Overview
Collection of utility scripts and helper functions for various backend operations including caching, database management, and validation.

## Location
`apps/api/app/utils/`

## Scripts and Utilities

### 1. cache.py & cache_utils.py
**Purpose**: Redis cache management and utility functions

**Key Functions**:
- Cache key generation
- Data serialization/deserialization  
- TTL management
- Cache invalidation patterns
- Distributed locking

**Usage**:
```python
from app.utils.cache import cache_key, invalidate_pattern
from app.utils.cache_utils import get_cached_or_compute

# Generate cache key
key = cache_key("prices", symbol="AAPL", date="2024-01-01")

# Cache with computation fallback
data = await get_cached_or_compute(
    key, 
    compute_func=fetch_prices,
    ttl=3600
)
```

### 2. create_indexes.py
**Purpose**: Database index creation and optimization

**Functionality**:
- Creates composite indexes for performance
- Handles index existence checks
- Adds indexes for common query patterns

**Indexes Created**:
- `(asset_id, date)` on prices table
- `(symbol)` on assets table
- `(user_id, created_at)` on various tables
- Query-specific indexes for joins

**Usage**:
```python
from app.utils.create_indexes import create_all_indexes

# Run during initialization
create_all_indexes(engine)
```

### 3. password_validator.py
**Purpose**: Password strength validation and security checks

**Validation Rules**:
- Minimum length (8 characters)
- Contains uppercase letter
- Contains lowercase letter
- Contains number
- Contains special character
- No common passwords
- No user info in password

**Usage**:
```python
from app.utils.password_validator import validate_password

is_valid, errors = validate_password(
    password="MyP@ssw0rd",
    username="john_doe"
)
if not is_valid:
    raise ValueError(f"Password validation failed: {', '.join(errors)}")
```

### 4. run_migrations.py
**Purpose**: Database migration runner for schema updates

**Features**:
- Checks for pending migrations
- Runs migrations in order
- Tracks migration history
- Rollback capability
- Migration validation

**Usage**:
```python
from app.utils.run_migrations import run_pending_migrations

# Run all pending migrations
results = run_pending_migrations()
for migration, status in results.items():
    print(f"{migration}: {status}")
```

### 5. token_dep.py
**Purpose**: JWT token dependency for FastAPI authentication

**Functionality**:
- Token extraction from headers
- Token validation
- User authentication
- Permission checking
- Token refresh logic

**Usage**:
```python
from app.utils.token_dep import get_current_user, require_admin

@router.get("/protected")
async def protected_route(user = Depends(get_current_user)):
    return {"user": user.username}

@router.post("/admin")
async def admin_route(admin = Depends(require_admin)):
    return {"admin": admin.username}
```

## Common Patterns

### Caching Pattern
```python
# Check cache first, compute if miss
cache_key = f"data:{identifier}"
cached = redis_client.get(cache_key)
if cached:
    return json.loads(cached)

result = expensive_computation()
redis_client.setex(cache_key, 3600, json.dumps(result))
return result
```

### Database Index Pattern
```python
# Create index if not exists
with engine.begin() as conn:
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_table_columns 
        ON table_name(column1, column2)
    """))
```

### Password Validation Pattern
```python
# Validate before saving
if not validate_password(password, username):
    raise HTTPException(
        status_code=400,
        detail="Password does not meet requirements"
    )
hashed = hash_password(password)
```

## Error Handling

### Cache Errors
- Fallback to database on cache miss
- Log cache failures but don't fail request
- Automatic retry with exponential backoff

### Migration Errors
- Rollback on failure
- Log detailed error information
- Prevent partial migrations

### Validation Errors
- Return descriptive error messages
- Log security-related failures
- Rate limit validation attempts

## Performance Considerations

### Caching
- Use appropriate TTLs
- Implement cache warming
- Monitor cache hit rates
- Clear cache on data updates

### Indexing
- Create indexes during low traffic
- Monitor index usage
- Remove unused indexes
- Balance read vs write performance

### Migrations
- Run during maintenance windows
- Test in staging first
- Have rollback plan ready
- Monitor migration duration

## Security Considerations

### Password Validation
- Never log passwords
- Use constant-time comparison
- Implement rate limiting
- Check against breach databases

### Token Management
- Short token lifetimes
- Secure token storage
- Refresh token rotation
- Blacklist compromised tokens

### Cache Security
- Don't cache sensitive data
- Encrypt cached data if needed
- Set appropriate TTLs
- Implement cache key namespacing

## Testing

### Unit Tests
```python
def test_password_validator():
    assert validate_password("Strong@Pass1")[0] == True
    assert validate_password("weak")[0] == False

def test_cache_key_generation():
    key = cache_key("test", id=1)
    assert key == "test:id:1"
```

### Integration Tests
- Test cache with Redis running
- Test migrations on test database
- Test index creation
- Test token validation

## Dependencies
- Redis for caching
- SQLAlchemy for database operations
- Passlib for password hashing
- PyJWT for token management
- PostgreSQL for database

## Related Files
- `app/core/redis_client.py` - Redis connection
- `app/core/database.py` - Database configuration
- `app/core/security.py` - Security utilities
- `app/migrations/` - Migration scripts

## Notes
- All utilities are designed to be reusable
- Error handling is built-in
- Performance optimized for production
- Security best practices followed
- Comprehensive logging included