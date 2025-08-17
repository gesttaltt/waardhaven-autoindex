# Render Deployment Configuration

## Overview
Cloud deployment configuration for Render.com platform.

## Location
`render.yaml`

## Services Configured

### API Service
- Type: Web Service
- Runtime: Python 3.11
- Build: Docker
- Port: 10000 (configured via PORT env var)
- Health check: /health
- Startup script: `./scripts/startup.sh`

### Web Service
- Type: Static Site
- Build: Node.js 18
- Framework: Next.js
- Port: 3000
- Auto-deploy: Enabled

### Database
- Type: PostgreSQL
- Version: 14
- Plan: Starter/Standard
- Backup: Daily
- High availability: Optional
- Connection pooling: Configured (20 pool size, 40 max overflow)

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
- `DEBUG` - Debug mode (default: false)
- `CACHE_TTL_SECONDS` - Cache TTL (default: 300)
- `TWELVEDATA_PLAN` - API plan level (default: free)
- `TWELVEDATA_RATE_LIMIT` - Credits per minute (default: 8)

### Web Environment
- `NEXT_PUBLIC_API_URL` - Production API URL
- `NODE_ENV` - Environment (production)
- `BUILD_COMMAND` - Build command override

## Deployment Process
1. Git push to main
2. Render webhook triggered
3. Docker build process starts
4. Dependencies installed from `requirements.txt`
5. Startup script runs:
   - Database connection check
   - Table initialization
   - Asset seeding
   - Optional market data refresh
6. Health checks validate service
7. Traffic routing to new version
8. Old version graceful shutdown

## Known Issues and Solutions

### Pydantic Version Mismatch (RESOLVED)
**Issue**: Deployment fails with `@root_validator` error  
**Cause**: Pydantic version mismatch (2.8.2 vs 2.11.7)  
**Solution**: Updated `requirements.txt` to use Pydantic 2.11.7

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

## Startup Optimization
To speed up deployment:
- Set `SKIP_STARTUP_REFRESH=true`
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
