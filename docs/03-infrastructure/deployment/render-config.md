# Render Deployment Configuration

## Overview
Production deployment configuration for Render.com platform. The system is currently deployed and operational with automatic CI/CD from GitHub.

## Location
`render.yaml`

## Services Configured

### API Service (waardhaven-api.onrender.com)
- Type: Web Service
- Runtime: Python 3.11
- Build: Docker (`apps/api/Dockerfile.api`)
- Port: 10000 (configured via PORT env var)
- Health check: `/api/v1/health`
- Startup script: `./scripts/startup.sh`
- Features:
  - FastAPI with 10 router modules
  - Redis caching integration
  - Celery background tasks
  - Automatic database migrations

### Web Service (waardhaven-web.onrender.com)
- Type: Web Service
- Build: Docker (`apps/web/Dockerfile.web`)
- Framework: Next.js 14 with React 18
- Port: 3000
- Auto-deploy: Enabled
- Features:
  - Clean Architecture implementation
  - 9 pages with type-safe API integration
  - JWT authentication with AuthProvider
  - Server-side rendering (SSR)

### Database (PostgreSQL)
- Type: Managed PostgreSQL
- Version: 14+
- Plan: Starter/Standard
- Backup: Daily automatic backups
- Features:
  - 6 domain models (User, Asset, Price, Index, Strategy, News)
  - Composite indexes for performance
  - Automatic migrations on startup
  - Connection pooling: 20 pool size, 40 max overflow

### Optional Services
- **Redis**: For caching and task queue
- **Celery Workers**: Background task processing
- **Flower**: Task monitoring dashboard

## Environment Variables

### API Environment (Required)
- `DATABASE_URL` - PostgreSQL connection string (auto-provided by Render)
- `SECRET_KEY` - JWT secret key (minimum 32 characters)
- `ADMIN_TOKEN` - Admin access token (minimum 32 characters)
- `TWELVEDATA_API_KEY` - Market data API key
- `FRONTEND_URL` - Frontend URL for CORS
- `PORT` - Server port (default: 10000)
- `SKIP_STARTUP_REFRESH` - Skip initial data refresh (recommended: true)

### API Environment (Optional)
- `REDIS_URL` - Redis connection for caching
- `MARKETAUX_API_KEY` - Financial news API key
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth secret
- `DEBUG` - Debug mode (default: false)
- `CACHE_TTL_SECONDS` - Cache TTL (default: 300)
- `TWELVEDATA_PLAN` - API plan level (default: free)
- `TWELVEDATA_RATE_LIMIT` - Credits per minute (default: 8)

### Web Environment
- `NEXT_PUBLIC_API_URL` - Production API URL (https://waardhaven-api.onrender.com/api/v1)
- `NEXT_PUBLIC_GOOGLE_CLIENT_ID` - Google OAuth client ID
- `NODE_ENV` - Environment (production)
- `BUILD_COMMAND` - Build command override (npm run build)

## Deployment Process

### Automatic Deployment (CI/CD)
1. Git push to main branch
2. GitHub Actions workflow triggered
3. Tests run (10 test files)
4. Render webhook triggered on success
5. Docker build process starts
6. Dependencies installed
7. Startup script executes:
   - Database connection validation
   - Automatic schema migrations
   - Composite index creation
   - Optional data refresh
8. Health checks validate service
9. Blue-green deployment with zero downtime
10. Old version graceful shutdown

### Manual Deployment
```bash
# From Render dashboard
1. Navigate to service
2. Click "Manual Deploy"
3. Select branch/commit
4. Monitor deployment logs
```

## Resolved Issues

### Authentication Integration (RESOLVED 2025-01-18)
**Issue**: `useAuth must be used within AuthProvider` error  
**Solution**: Fixed AuthProvider context wrapping and JWT implementation

### Pydantic Version (RESOLVED 2025-01-17)
**Issue**: Deployment fails with `@root_validator` error  
**Solution**: Updated to Pydantic 2.11.7 with v2 syntax

### Database Connection Timeout
**Issue**: Database connection fails during startup  
**Solution**: 
- Configured retry logic (30 attempts)
- Graceful degradation if database unavailable
- API starts with limited functionality

### Port Binding Issues
**Issue**: "No open ports detected" warning  
**Solution**: 
- Properly configured PORT environment variable
- Uvicorn binds to 0.0.0.0:$PORT
- Health check endpoint validates binding

## Build Cache Management
If deployment uses outdated code:
1. Clear build cache in Render dashboard
2. Trigger manual deploy from latest commit
3. Verify commit hash in deployment logs

## Performance Optimization

### Startup Optimization
- Set `SKIP_STARTUP_REFRESH=true` to skip initial data refresh
- Use Redis for caching frequently accessed data
- Enable Celery workers for background processing

### Database Performance
- Composite indexes automatically created on startup
- Connection pooling configured for high concurrency
- Query optimization with SQLAlchemy eager loading

### Monitoring
- Health endpoint: `/api/v1/health`
- Diagnostics: `/api/v1/diagnostics/health`
- Cache status: `/api/v1/diagnostics/cache-status`
- Task monitoring: Flower dashboard (if enabled)
- Use Redis caching for market data
- Enable smart refresh mode
- Configure connection pooling

## Monitoring and Health Checks
- Health endpoint: `/health`
- Diagnostics: `/api/v1/diagnostics/system`
- Cache status: `/api/v1/diagnostics/cache-status`
- Database status: `/api/v1/diagnostics/database-status`

## Scaling Options
- Horizontal scaling: Multiple instances
- Vertical scaling: Upgrade machine type
- Auto-scaling rules: Based on CPU/memory
- Load balancing: Automatic via Render
- Connection pooling: Configured for high concurrency
