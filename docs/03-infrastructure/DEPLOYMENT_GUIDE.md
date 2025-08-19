# Deployment Guide - Waardhaven AutoIndex

## Overview
This guide covers the complete deployment process for Waardhaven AutoIndex on Render.com, including environment setup, service configuration, and monitoring.

## Prerequisites
- GitHub repository with code
- Render.com account
- TwelveData API key
- MarketAux API key (optional)

## Architecture
```
┌─────────────────┐     ┌─────────────────┐
│   Web Service   │────▶│   API Service   │
│   (Next.js)     │     │   (FastAPI)     │
└─────────────────┘     └─────────────────┘
                              │
                              ▼
                        ┌─────────────────┐
                        │   PostgreSQL    │
                        │    Database     │
                        └─────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
              ┌─────────────┐    ┌─────────────┐
              │    Redis    │    │   Celery    │
              │    Cache    │    │   Workers   │
              └─────────────┘    └─────────────┘
```

## Render.com Configuration

### 1. Database Service
```yaml
databases:
  - name: waardhaven-db
    plan: starter  # $7/month
    databaseName: waardhaven_db_5t62
    user: waardhaven_db_5t62_user
```

### 2. API Service
```yaml
services:
  - type: web
    name: waardhaven-api
    env: docker
    dockerfilePath: ./Dockerfile
    dockerContext: .
    plan: starter  # $7/month
    rootDir: apps/api
    envVars:
      - key: PORT
        value: "10000"
      - key: DATABASE_URL
        fromDatabase:
          name: waardhaven-db
          property: connectionString
      - key: SECRET_KEY
        sync: false  # Set in dashboard
      - key: ADMIN_TOKEN
        sync: false  # Set in dashboard
      - key: TWELVEDATA_API_KEY
        sync: false  # Set in dashboard
      - key: MARKETAUX_API_KEY
        sync: false  # Set in dashboard
      - key: REDIS_URL
        sync: false  # Set in dashboard
      - key: FRONTEND_URL
        value: "https://waardhaven-web-frontend.onrender.com"
```

### 3. Web Service
```yaml
services:
  - type: web
    name: waardhaven-web
    env: docker
    dockerfilePath: ./Dockerfile
    dockerContext: .
    rootDir: apps/web
    plan: starter  # $7/month
    envVars:
      - key: PORT
        value: "10000"
      - key: NEXT_PUBLIC_API_URL
        value: "https://waardhaven-api.onrender.com"
```

## Environment Variables

### API Service Environment
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Authentication
SECRET_KEY=your-secret-key-min-32-chars
ADMIN_TOKEN=admin-access-token
JWT_ALGORITHM=HS256

# External APIs
TWELVEDATA_API_KEY=your-twelvedata-key
MARKETAUX_API_KEY=your-marketaux-key

# Redis (optional but recommended)
REDIS_URL=redis://default:password@host:6379

# CORS
FRONTEND_URL=https://waardhaven-web-frontend.onrender.com

# Feature Flags
SKIP_STARTUP_REFRESH=true  # Disable auto-refresh on startup
ENABLE_CACHE=true
ENABLE_BACKGROUND_TASKS=true

# Rate Limiting
RATE_LIMIT_CALLS=100
RATE_LIMIT_PERIOD=60
```

### Web Service Environment
```bash
# API Connection
NEXT_PUBLIC_API_URL=https://waardhaven-api.onrender.com

# Optional Analytics
NEXT_PUBLIC_GA_ID=GA-XXXXXXXXX
```

## Docker Configuration

### API Dockerfile
```dockerfile
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app ./app
COPY scripts ./scripts
RUN chmod +x scripts/startup.sh

# Configure port
ENV PORT=10000
EXPOSE ${PORT}

# Run startup script
CMD ["./scripts/startup.sh"]
```

### Web Dockerfile
```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# Install and build
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=10000

# Copy built application
COPY --from=builder /app/package.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/public* ./public/

EXPOSE ${PORT}
CMD ["sh", "-c", "npm run start -- -p ${PORT:-10000}"]
```

## Deployment Steps

### 1. Initial Setup
```bash
# 1. Fork/Clone repository
git clone https://github.com/yourusername/waardhaven-autoindex.git
cd waardhaven-autoindex

# 2. Create render.yaml in root
cp render.yaml.example render.yaml

# 3. Push to GitHub
git add .
git commit -m "Add deployment configuration"
git push origin main
```

### 2. Render Dashboard Setup
1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click "New +" → "Blueprint"
3. Connect GitHub repository
4. Select your repository
5. Name: "waardhaven-autoindex"
6. Branch: "main"
7. Click "Apply"

### 3. Configure Environment Variables
For each service in Render dashboard:

**waardhaven-api:**
1. Go to Environment tab
2. Add secret variables:
   - `SECRET_KEY`: Generate with `openssl rand -hex 32`
   - `ADMIN_TOKEN`: Create secure admin token
   - `TWELVEDATA_API_KEY`: From twelvedata.com
   - `MARKETAUX_API_KEY`: From marketaux.com
   - `REDIS_URL`: From Redis provider

**waardhaven-web:**
1. Go to Environment tab
2. Verify `NEXT_PUBLIC_API_URL` is set correctly

### 4. Deploy Services
```bash
# Trigger deployment
git push origin main

# Or manually in Render dashboard:
# Click "Manual Deploy" → "Deploy latest commit"
```

## Post-Deployment Tasks

### 1. Database Initialization
```bash
# SSH into API service or run locally
python -m app.db_init
python -m app.seed_assets
```

### 2. Create Admin User
```bash
# Via API endpoint
curl -X POST https://waardhaven-api.onrender.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "secure-password"
  }'
```

### 3. Initial Data Load
```bash
# Trigger manual refresh
curl -X POST https://waardhaven-api.onrender.com/api/v1/manual/refresh-all \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Monitoring & Maintenance

### Health Checks
```bash
# API Health
curl https://waardhaven-api.onrender.com/health

# System Diagnostics
curl https://waardhaven-api.onrender.com/api/v1/diagnostics/system-health
```

### Logs
Access logs in Render dashboard:
1. Go to service
2. Click "Logs" tab
3. Filter by:
   - Time range
   - Log level
   - Search terms

### Metrics
Monitor in Render dashboard:
- CPU usage
- Memory usage
- Response times
- Error rates

## Celery Workers (Optional)

### Setup Redis
1. Use Redis provider (Redis Labs, Upstash)
2. Get connection URL
3. Add to API environment as `REDIS_URL`

### Deploy Worker Service
```yaml
services:
  - type: worker
    name: waardhaven-worker
    env: docker
    dockerfilePath: ./Dockerfile.worker
    dockerContext: .
    rootDir: apps/api
    plan: starter
    envVars:
      # Same as API service
```

### Worker Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
CMD ["celery", "-A", "app.core.celery_app", "worker", "--loglevel=info"]
```

## Troubleshooting

### Common Issues

#### 1. CORS Errors
```python
# Check allowed origins in apps/api/app/main.py
allowed_origins = [
    "https://waardhaven-web-frontend.onrender.com",
    # Add your custom domain
]
```

#### 2. Database Connection
```bash
# Verify DATABASE_URL format
postgresql://user:password@host:port/database

# Test connection
python -m app.test_db_connection
```

#### 3. Build Failures
```bash
# Check logs for specific errors
# Common fixes:
- Ensure all dependencies in requirements.txt
- Check Node version (needs 20+)
- Verify environment variables
```

#### 4. Slow Cold Starts
- Render free tier has cold starts
- Upgrade to paid tier for always-on
- Implement health check pings

## Performance Optimization

### 1. Enable Caching
```python
# Set in environment
ENABLE_CACHE=true
REDIS_URL=redis://...
```

### 2. Database Indexes
```sql
-- Run migrations
python -m app.utils.run_migrations
```

### 3. CDN for Static Assets
```javascript
// next.config.js
module.exports = {
  images: {
    domains: ['cdn.example.com'],
  },
}
```

## Security Best Practices

### 1. Environment Variables
- Never commit secrets to git
- Use Render's secret management
- Rotate keys regularly

### 2. HTTPS
- Render provides SSL automatically
- Enforce HTTPS in application

### 3. Rate Limiting
- Configured in middleware
- Adjust limits as needed

### 4. Authentication
- JWT tokens expire after 30 minutes
- Refresh tokens for extended sessions
- Implement 2FA for production

## Scaling Considerations

### Horizontal Scaling
```yaml
# In render.yaml
services:
  - name: waardhaven-api
    scaling:
      minInstances: 2
      maxInstances: 10
      targetMemoryPercent: 70
      targetCPUPercent: 70
```

### Database Scaling
- Upgrade to Professional plan
- Enable read replicas
- Implement connection pooling

### Caching Strategy
- Redis for session data
- CDN for static assets
- Database query optimization

## Backup & Recovery

### Database Backups
- Render auto-backups (daily)
- Manual backups before migrations
```bash
pg_dump $DATABASE_URL > backup.sql
```

### Application Backups
- Git repository as source of truth
- Tag releases for rollback
```bash
git tag -a v1.0.0 -m "Production release"
git push origin v1.0.0
```

## Cost Breakdown

### Render.com Pricing (as of 2025)
- **Database**: $7/month (Starter)
- **API Service**: $7/month (Starter)
- **Web Service**: $7/month (Starter)
- **Worker** (optional): $7/month
- **Total**: ~$21-28/month

### Optional Services
- **Redis**: $10/month (Redis Labs)
- **CDN**: $20/month (Cloudflare)
- **Monitoring**: $10/month (Datadog)

## Support & Resources

### Documentation
- [Render Docs](https://render.com/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Next.js Docs](https://nextjs.org/docs)

### Community
- GitHub Issues
- Discord/Slack channels
- Stack Overflow

### Monitoring Services
- Render Dashboard
- Flower (Celery monitoring)
- Application logs