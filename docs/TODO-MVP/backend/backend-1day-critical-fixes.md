# Backend Critical Fixes - 1 Day Roadmap

**Date**: 2025-08-17  
**Objective**: Fix critical issues and implement essential safety measures in 1 day

## 🚨 CRITICAL FIXES ONLY - 8 Hour Sprint

### Hour 1-2: Data Loss Prevention (MUST DO)
- [ ] **Fix refresh.py data deletion** - Replace dangerous delete with incremental update
- [ ] **Add database transaction safety** - Wrap operations in try/catch with rollback
- [ ] **Create backup before refresh** - Export existing data before any modification
- [ ] **Add operation logging** - Log all data modifications for audit trail

### Hour 3-4: Security Patches
- [ ] **Fix CORS for production** - Set specific allowed origins instead of ["*"]
- [ ] **Add rate limiting** - Basic rate limiting using slowapi (10 req/sec)
- [ ] **Add security headers** - HSTS, X-Frame-Options, CSP basics
- [ ] **Implement refresh tokens** - Add 7-day refresh token to JWT flow

### Hour 5-6: Database Quick Wins
- [ ] **Add composite index** - Create (asset_id, date) index for performance
- [ ] **Configure connection pooling** - Set pool_size=20, max_overflow=40
- [ ] **Add created_at/updated_at** - Add timestamp fields to critical tables
- [ ] **Implement basic caching** - Cache frequently accessed data in memory

### Hour 7-8: Error Handling & Monitoring
- [ ] **Add global error handler** - Catch all exceptions with proper logging
- [ ] **Add correlation IDs** - Track requests across the system
- [ ] **Create error response standard** - Consistent error format
- [ ] **Add basic metrics endpoint** - /metrics for monitoring

## Implementation Code Snippets

### 1. Fix Data Deletion (refresh.py)
```python
# REPLACE dangerous deletion
# OLD: db.query(Price).delete()

# NEW: Incremental update
def safe_refresh_prices(db: Session, new_prices: List[Price]):
    # Backup existing data
    existing = db.query(Price).all()
    backup_data = [p.dict() for p in existing]
    
    try:
        # Update or insert new prices
        for price in new_prices:
            existing = db.query(Price).filter(
                Price.asset_id == price.asset_id,
                Price.date == price.date
            ).first()
            
            if existing:
                existing.close = price.close
                existing.volume = price.volume
            else:
                db.add(price)
        
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Refresh failed: {e}")
        # Restore from backup if needed
        raise
```

### 2. Add Rate Limiting
```python
# requirements.txt
slowapi==0.1.9

# main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# On endpoints
@app.get("/api/v1/index")
@limiter.limit("10/second")
async def get_index(...):
    pass
```

### 3. Security Headers Middleware
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

### 4. Connection Pooling
```python
# core/database.py
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### 5. Global Error Handler
```python
from fastapi import Request, status
from fastapi.responses import JSONResponse
import uuid

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_id = str(uuid.uuid4())
    logger.error(f"Error {error_id}: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "error_id": error_id,
            "message": str(exc) if settings.DEBUG else "An error occurred"
        }
    )
```

### 6. Add Composite Index (Alembic migration)
```sql
-- Quick SQL fix if Alembic not set up
CREATE INDEX idx_price_asset_date ON prices(asset_id, date);
CREATE INDEX idx_allocation_date ON allocations(date);
CREATE INDEX idx_index_value_date ON index_values(date);

-- Add audit fields
ALTER TABLE prices ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE prices ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
```

## Testing Checklist

### Quick Smoke Tests (30 minutes)
- [ ] Verify refresh doesn't delete data
- [ ] Test rate limiting works
- [ ] Check CORS blocks unauthorized origins
- [ ] Verify error handling returns proper format
- [ ] Test database queries are faster with indexes
- [ ] Check connection pool is working

## Deployment Steps

1. **Backup Production Database** (15 min)
2. **Deploy Code Changes** (15 min)
3. **Run Database Migrations** (10 min)
4. **Smoke Test Production** (20 min)

## What We're NOT Doing Today

These are important but not critical for day 1:
- Full test suite
- Complete authorization system
- Redis caching
- Background task queue
- Comprehensive monitoring
- API versioning strategy
- Full migration to repository pattern

## Success Metrics

After this 1-day sprint:
- ✅ Zero data loss risk
- ✅ Basic security in place
- ✅ 50% faster queries
- ✅ Proper error handling
- ✅ Can handle 100 concurrent users

## Next Steps (Future)

Once critical fixes are done, prioritize:
1. Implement Alembic for proper migrations
2. Add comprehensive testing
3. Set up Redis caching
4. Implement background tasks
5. Add monitoring (Prometheus/Grafana)

---

**Remember**: This is a band-aid approach. Technical debt still needs to be addressed, but these fixes prevent immediate disasters.