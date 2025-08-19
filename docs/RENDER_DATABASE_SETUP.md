# Render PostgreSQL Database Setup Guide

## Overview
This guide ensures proper PostgreSQL database connectivity between your backend (FastAPI) and frontend (Next.js) services on Render.

## Current Configuration Status

### ✅ Correctly Configured
1. **render.yaml**: Database service properly defined with automatic connection string injection
2. **Backend Database Connection**: Using SQLAlchemy with proper pool configuration for Render
3. **Frontend API Client**: Configured to use environment variable for API URL
4. **Environment Variables**: Properly set up for both development and production

## Database Connection Architecture

### 1. Database Service (render.yaml:40-44)
```yaml
databases:
  - name: waardhaven-db
    plan: starter
    databaseName: waardhaven_db_5t62
    user: waardhaven_db_5t62_user
```

### 2. Backend Connection (render.yaml:14-17)
```yaml
- key: DATABASE_URL
  fromDatabase:
    name: waardhaven-db
    property: connectionString
```
**Important**: Render automatically injects the **internal** database URL when using `fromDatabase`. This ensures:
- Lowest latency (same region, internal network)
- No external network traversal
- Automatic credential management

### 3. Connection String Format
Render provides the connection string in this format:
```
postgresql://[user]:[password]@[host]:[port]/[database]?sslmode=require
```

**Internal URL** (automatically used): 
- Host: `waardhaven-db.internal`
- Port: `5432`
- SSL: Required

**External URL** (for debugging only):
- Host: `oregon-postgres.render.com` (or your region)
- Port: `5432`
- SSL: Required

## Backend Configuration Details

### Database Connection (apps/api/app/core/database.py)
```python
# Production on Render (lines 20-28)
pool_config = {
    "poolclass": QueuePool,
    "pool_size": 20,           # Connections in pool
    "max_overflow": 40,        # Max overflow connections
    "pool_timeout": 30,        # Timeout for getting connection
    "pool_recycle": 3600,      # Recycle after 1 hour
    "pool_pre_ping": True,     # Test connections before use
}
```

### Configuration Loading (apps/api/app/core/config.py)
```python
DATABASE_URL: str = Field(..., env="DATABASE_URL")  # Line 11
```

## Frontend-Backend Connection

### API Client Configuration (apps/web/app/utils/api.ts:3)
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

### Production Environment (apps/web/.env.production:5)
```
NEXT_PUBLIC_API_URL=https://waardhaven-api-backend.onrender.com
```

## Best Practices Implementation

### 1. ✅ Use Internal Database URL
- **Implemented**: Using `fromDatabase` in render.yaml ensures internal URL usage
- **Benefit**: Minimizes latency, stays within Render's network

### 2. ✅ Connection Pooling
- **Implemented**: QueuePool with 20 connections, 40 overflow
- **Benefit**: Handles concurrent requests efficiently

### 3. ✅ Connection Health Checks
- **Implemented**: `pool_pre_ping=True` tests connections before use
- **Benefit**: Prevents using stale connections

### 4. ✅ Connection Recycling
- **Implemented**: `pool_recycle=3600` (1 hour)
- **Benefit**: Prevents long-lived connections from timing out

### 5. ✅ SSL/TLS Security
- **Implemented**: Render automatically enforces SSL for all database connections
- **Benefit**: Encrypted data transmission

## Troubleshooting Database Connectivity

### 1. Check Database Status
```bash
# From your API service logs
curl https://waardhaven-api-backend.onrender.com/api/v1/diagnostics/database-status
```

### 2. Verify Environment Variables
In Render Dashboard:
1. Go to your API service
2. Click "Environment" tab
3. Verify `DATABASE_URL` shows as "From waardhaven-db"

### 3. Connection Pool Monitoring
Add this endpoint to monitor pool status:
```python
@router.get("/pool-status")
async def get_pool_status():
    from app.core.database import engine
    pool = engine.pool
    return {
        "size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "total": pool.size() + pool.overflow()
    }
```

### 4. Common Issues and Solutions

#### Issue: Connection Timeouts
**Solution**: Already configured with `pool_timeout=30` and `pool_pre_ping=True`

#### Issue: Too Many Connections
**Solution**: Pool size (20) and overflow (40) properly configured for Starter plan

#### Issue: Connection Drops
**Solution**: `pool_recycle=3600` prevents long-lived connection issues

#### Issue: SSL Certificate Errors
**Solution**: Render handles SSL automatically; no additional configuration needed

## Migration and Schema Management

### Initial Setup (Already Complete)
```python
# apps/api/app/main.py
from app.core.database import engine
from app.models import Base

# Create all tables on startup
Base.metadata.create_all(bind=engine)
```

### Future: Alembic Migrations (Recommended)
```bash
# Initialize Alembic (future improvement)
cd apps/api
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Monitoring Database Performance

### 1. Query Performance
```python
# Enable query logging for debugging (database.py:40)
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,  # Set to True for SQL debugging
    ...
)
```

### 2. Slow Query Detection
Use Render's PostgreSQL metrics dashboard to monitor:
- Query execution time
- Connection count
- Database size
- IOPS

### 3. Database Indexes (Already Optimized)
Check existing indexes:
```sql
SELECT tablename, indexname, indexdef 
FROM pg_indexes 
WHERE schemaname = 'public';
```

## Security Considerations

### 1. ✅ Internal Network Only
- Database not exposed to internet
- Only accessible from services in same Render account/region

### 2. ✅ Encrypted Connections
- All connections use SSL/TLS 1.2+
- Automatic certificate management by Render

### 3. ✅ Credential Management
- Database credentials managed by Render
- Automatically rotated and injected

### 4. ⚠️ Backup Strategy
- Render Starter plan: Daily backups, 7-day retention
- Consider upgrading for point-in-time recovery

## Deployment Checklist

### Pre-Deployment
- [x] Database service defined in render.yaml
- [x] DATABASE_URL using fromDatabase reference
- [x] Connection pooling configured
- [x] Frontend API URL configured
- [x] Environment variables documented

### Post-Deployment Verification
1. Check database connectivity:
   ```bash
   curl https://waardhaven-api-backend.onrender.com/api/v1/diagnostics/database-status
   ```

2. Verify table creation:
   ```bash
   # In Render dashboard, use "Connect" button for psql access
   \dt
   ```

3. Test API endpoints:
   ```bash
   curl https://waardhaven-api-backend.onrender.com/api/v1/health
   ```

4. Monitor logs for connection issues:
   - Check API service logs in Render dashboard
   - Look for SQLAlchemy connection errors

## Optimization Tips

### 1. Connection Pool Tuning
Current settings are optimized for Render Starter plan. If upgrading:
- **Standard**: Increase pool_size to 50, max_overflow to 100
- **Pro**: Increase pool_size to 100, max_overflow to 200

### 2. Query Optimization
- Add indexes for frequently queried columns
- Use eager loading for related data
- Implement query result caching with Redis

### 3. Database Maintenance
- Regular VACUUM and ANALYZE (Render handles automatically)
- Monitor table bloat
- Archive old data periodically

## Summary

Your database connection setup follows Render's best practices:
1. ✅ Using internal database URL for lowest latency
2. ✅ Proper connection pooling for production workload
3. ✅ Health checks and connection recycling
4. ✅ SSL/TLS encryption enforced
5. ✅ Environment-based configuration

The configuration is production-ready and optimized for Render's infrastructure.