# Deployment Configuration

## Overview

The application is deployed on Render.com with separate services for the frontend and backend, connected to a PostgreSQL database.

## Deployment Architecture

```
┌─────────────────────────────────────────┐
│            Render.com                    │
├─────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐  │
│  │  Web Service │    │  API Service │  │
│  │   (Next.js)  │───▶│  (FastAPI)   │  │
│  └──────────────┘    └──────────────┘  │
│                            │            │
│                      ┌──────────────┐  │
│                      │  PostgreSQL  │  │
│                      │   Database   │  │
│                      └──────────────┘  │
└─────────────────────────────────────────┘
```

## Render Configuration

### render.yaml

```yaml
services:
  # Web Service (Frontend)
  - type: web
    name: waardhaven-web
    env: node
    region: oregon
    plan: starter
    buildCommand: cd apps/web && npm install && npm run build
    startCommand: cd apps/web && npm start
    envVars:
      - key: NODE_ENV
        value: production
      - key: NEXT_PUBLIC_API_URL
        value: https://waardhaven-api.onrender.com
      - key: NEXT_PUBLIC_GOOGLE_CLIENT_ID
        fromDatabase:
          name: waardhaven-secrets
          property: googleClientId
    autoDeploy: true
    branch: main

  # API Service (Backend)
  - type: web
    name: waardhaven-api
    env: python
    region: oregon
    plan: starter
    buildCommand: cd apps/api && pip install -r requirements.txt
    startCommand: cd apps/api && uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: waardhaven-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: TWELVEDATA_API_KEY
        fromDatabase:
          name: waardhaven-secrets
          property: twelvedataApiKey
      - key: FRONTEND_URL
        value: https://waardhaven-web.onrender.com
      - key: REDIS_URL
        fromDatabase:
          name: waardhaven-redis
          property: connectionString
    autoDeploy: true
    branch: main

databases:
  # PostgreSQL Database
  - name: waardhaven-db
    databaseName: waardhaven
    user: waardhaven
    region: oregon
    plan: starter

  # Redis Cache
  - name: waardhaven-redis
    type: redis
    region: oregon
    plan: starter

  # Secrets Store
  - name: waardhaven-secrets
    databaseName: secrets
    plan: starter
```

## Environment Configuration

### Frontend Environment Variables

```env
# .env.production (apps/web)
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://waardhaven-api.onrender.com
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
NEXT_PUBLIC_GA_ID=your-google-analytics-id
```

### Backend Environment Variables

```env
# .env.production (apps/api)
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=your-secret-key
ADMIN_TOKEN=your-admin-token
TWELVEDATA_API_KEY=your-twelvedata-key
FRONTEND_URL=https://waardhaven-web.onrender.com
REDIS_URL=redis://user:pass@host:6379
SKIP_STARTUP_REFRESH=false
```

## Docker Configuration

### Frontend Dockerfile

```dockerfile
# apps/web/Dockerfile
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build the application
ENV NEXT_TELEMETRY_DISABLED 1
RUN npm run build

# Production image
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
```

### Backend Dockerfile

```dockerfile
# apps/api/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 api && chown -R api:api /app
USER api

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Build Configuration

### Next.js Configuration

```javascript
// apps/web/next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    domains: ['waardhaven-api.onrender.com'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_GOOGLE_CLIENT_ID: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID,
  },
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on'
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY'
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block'
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin'
          },
        ],
      },
    ];
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
```

### Build Scripts

```json
// package.json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "build:production": "NODE_ENV=production next build",
    "analyze": "ANALYZE=true next build",
    "type-check": "tsc --noEmit",
    "lint": "eslint . --ext .ts,.tsx",
    "test": "jest",
    "test:ci": "jest --ci --coverage"
  }
}
```

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to Render

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test
      
      - name: Type check
        run: npm run type-check
      
      - name: Lint
        run: npm run lint

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Render
        env:
          RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
        run: |
          curl -X POST \
            -H "Authorization: Bearer $RENDER_API_KEY" \
            -H "Content-Type: application/json" \
            -d '{"serviceId": "${{ secrets.RENDER_SERVICE_ID }}"}' \
            https://api.render.com/v1/services/${{ secrets.RENDER_SERVICE_ID }}/deploys
```

## Performance Optimization

### CDN Configuration

```javascript
// next.config.js
module.exports = {
  images: {
    loader: 'cloudinary',
    path: 'https://res.cloudinary.com/waardhaven/',
  },
  assetPrefix: process.env.CDN_URL || '',
};
```

### Caching Headers

```javascript
// pages/api/[...path].ts
export default function handler(req: NextApiRequest, res: NextApiResponse) {
  // Cache static assets for 1 year
  if (req.url?.startsWith('/_next/static')) {
    res.setHeader('Cache-Control', 'public, max-age=31536000, immutable');
  }
  
  // Cache API responses for 1 minute
  if (req.url?.startsWith('/api')) {
    res.setHeader('Cache-Control', 'public, max-age=60, s-maxage=60');
  }
}
```

## Monitoring & Logging

### Application Monitoring

```javascript
// utils/monitoring.ts
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 0.1,
  beforeSend(event) {
    // Filter sensitive data
    if (event.request) {
      delete event.request.cookies;
      delete event.request.headers;
    }
    return event;
  },
});
```

### Health Checks

```typescript
// pages/api/health.ts
export default function handler(req: NextApiRequest, res: NextApiResponse) {
  const health = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV,
  };
  
  res.status(200).json(health);
}
```

## Security Configuration

### Content Security Policy

```javascript
// middleware.ts
export function middleware(request: NextRequest) {
  const response = NextResponse.next();
  
  response.headers.set(
    'Content-Security-Policy',
    [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://accounts.google.com",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: https:",
      "font-src 'self' data:",
      "connect-src 'self' https://waardhaven-api.onrender.com",
      "frame-src 'self' https://accounts.google.com",
    ].join('; ')
  );
  
  return response;
}
```

## Database Migrations

### Migration Script

```bash
#!/bin/bash
# scripts/migrate.sh

echo "Running database migrations..."

# Export DATABASE_URL from Render
export DATABASE_URL=$DATABASE_URL

# Run migrations
cd apps/api
alembic upgrade head

echo "Migrations completed"
```

## Backup Strategy

### Automated Backups

```yaml
# render.yaml addition
crons:
  - type: scheduler
    name: database-backup
    env: python
    schedule: "0 2 * * *"  # Daily at 2 AM
    buildCommand: pip install pg_dump
    command: |
      pg_dump $DATABASE_URL | gzip > backup_$(date +%Y%m%d).sql.gz
      aws s3 cp backup_*.sql.gz s3://waardhaven-backups/
```

## Rollback Procedure

### Deployment Rollback

```bash
# Rollback to previous deployment
curl -X POST \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  https://api.render.com/v1/services/$SERVICE_ID/rollback

# Or using Render CLI
render rollback --service waardhaven-web
```

## Environment-Specific Configuration

### Development

```javascript
// config/development.js
export default {
  apiUrl: 'http://localhost:8000',
  debug: true,
  logLevel: 'debug',
};
```

### Staging

```javascript
// config/staging.js
export default {
  apiUrl: 'https://waardhaven-staging-api.onrender.com',
  debug: true,
  logLevel: 'info',
};
```

### Production

```javascript
// config/production.js
export default {
  apiUrl: 'https://waardhaven-api.onrender.com',
  debug: false,
  logLevel: 'error',
};
```

## SSL/TLS Configuration

Render provides automatic SSL certificates via Let's Encrypt. Custom domains can be configured in the Render dashboard.

## Scaling Configuration

### Horizontal Scaling

```yaml
# render.yaml
services:
  - type: web
    name: waardhaven-web
    scaling:
      minInstances: 2
      maxInstances: 10
      targetMemoryPercent: 80
      targetCPUPercent: 70
```

## Deployment Checklist

- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] SSL certificates active
- [ ] Health checks passing
- [ ] Monitoring configured
- [ ] Backup strategy implemented
- [ ] Rate limiting configured
- [ ] CORS settings verified
- [ ] Security headers set
- [ ] Error tracking enabled
- [ ] Performance monitoring active
- [ ] CDN configured
- [ ] Cache headers optimized
- [ ] Logs aggregation setup
- [ ] Rollback procedure tested

## Next Steps

- Review [Performance Optimization](./11-performance-optimization.md)
- Learn about [Security Best Practices](./12-security-best-practices.md)
- Understand [Troubleshooting Guide](./13-troubleshooting-guide.md)