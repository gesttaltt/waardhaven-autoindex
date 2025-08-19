# Deployment Automation & CI/CD Fixes

**Priority**: P0 - CRITICAL  
**Status**: 🔴 Broken  
**Estimated**: 1 day  
**Platform**: GitHub Actions, Render.com

## 🎯 Objective

Fix critical CI/CD pipeline issues and implement fully automated deployment:
- Remove `|| true` statements hiding failures
- Setup Render CLI integration
- Automate database migrations
- Add proper health checks
- Implement rollback capability

## 📋 Current Critical Issues

### 🔴 Pipeline Hides Failures
All test failures are hidden with `|| true` statements, making the pipeline always green even when broken.

### 🔴 No Automated Deployment
Deploy workflows contain placeholder commands - manual deployment required.

### 🔴 No Render CLI Integration
Missing proper Render deployment automation.

## 📋 Task Breakdown

### Phase 1: Fix Test Execution (CRITICAL - 1 hour)

#### Task 1.1: Remove Failure Hiding
**File**: `.github/workflows/ci-cd.yml`

```yaml
# Lines to fix:
- [ ] Line 96: npm run lint || true → npm run lint
- [ ] Line 97: npm run type-check || true → npm run type-check  
- [ ] Line 141: pytest tests/ || true → pytest tests/
- [ ] Line 170: npm run test || true → npm run test
- [ ] Line 171: npm run test:e2e || true → # npm run test:e2e (comment out)
```

#### Task 1.2: Add Proper Error Handling
```yaml
# Add error catching:
- [ ] Set continue-on-error: false
- [ ] Add failure notifications
- [ ] Implement retry logic for flaky tests
```

### Phase 2: Render CLI Setup (2 hours)

#### Task 2.1: Install Render CLI
**File**: `.github/workflows/deploy.yml`

```yaml
- name: Install Render CLI
  run: |
    curl -fsSL https://render.com/install.sh | sh
    echo "$HOME/.render/bin" >> $GITHUB_PATH
```

#### Task 2.2: Configure GitHub Secrets
```
Required secrets:
- [ ] RENDER_API_KEY
- [ ] RENDER_API_SERVICE_ID  
- [ ] RENDER_WEB_SERVICE_ID
- [ ] DATABASE_URL
- [ ] SECRET_KEY
- [ ] TWELVEDATA_API_KEY
- [ ] MARKETAUX_API_KEY
```

#### Task 2.3: Deployment Commands
```yaml
# API deployment:
- [ ] render deploy --service-id $API_ID --key $KEY
# Web deployment:
- [ ] render deploy --service-id $WEB_ID --key $KEY
# Migration job:
- [ ] render job:run --service-id $API_ID --command "alembic upgrade head"
```

### Phase 3: Complete Deploy Workflow (3 hours)

#### Task 3.1: Production Deploy Workflow
**File**: `.github/workflows/deploy-production.yml`

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  test:
    # Run all tests first
    
  deploy-api:
    needs: test
    # Deploy backend
    
  migrate-database:
    needs: deploy-api
    # Run migrations
    
  deploy-web:
    needs: migrate-database
    # Deploy frontend
    
  health-check:
    needs: [deploy-api, deploy-web]
    # Verify deployment
```

#### Task 3.2: Staging Deploy Workflow
**File**: `.github/workflows/deploy-staging.yml`

```yaml
# Deploy to staging on PR merge to develop
- [ ] Setup staging environment
- [ ] Run integration tests
- [ ] Deploy with feature flags
```

### Phase 4: Database Migration Automation (2 hours)

#### Task 4.1: Migration Job
**File**: `.github/workflows/migrate.yml`

```yaml
name: Run Database Migrations

jobs:
  backup:
    # Backup database first
    
  migrate:
    # Run Alembic migrations
    
  verify:
    # Check migration success
    
  rollback:
    if: failure()
    # Rollback on failure
```

#### Task 4.2: Migration Scripts
**File**: `apps/api/scripts/migrate.sh`

```bash
#!/bin/bash
# Safe migration script:
- [ ] Check database connectivity
- [ ] Create backup
- [ ] Run migrations
- [ ] Verify schema
- [ ] Rollback on error
```

### Phase 5: Health Checks & Monitoring (2 hours)

#### Task 5.1: Health Check Endpoints
**File**: `apps/api/app/routers/health.py`

```python
# Endpoints to implement:
- [ ] GET /health - Basic health
- [ ] GET /health/ready - Readiness probe
- [ ] GET /health/live - Liveness probe
- [ ] GET /health/dependencies - Check all deps
```

#### Task 5.2: Deployment Verification
```yaml
# Health check job:
- [ ] Wait for service ready
- [ ] Check all endpoints
- [ ] Verify database connection
- [ ] Test critical paths
```

### Phase 6: Rollback Capability (1 hour)

#### Task 6.1: Rollback Workflow
**File**: `.github/workflows/rollback.yml`

```yaml
name: Rollback Deployment

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to rollback to'
        required: true

jobs:
  rollback:
    # Rollback steps
```

## 📊 Complete Workflow Examples

### Fixed CI/CD Workflow

```yaml
# .github/workflows/ci-cd.yml

name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint-and-type-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run linting
        run: npm run lint
        # No || true - fail on lint errors
      
      - name: Run type checking
        run: npm run type-check
        # No || true - fail on type errors

  test-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd apps/api
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:testpass@localhost/testdb
          SECRET_KEY: test-secret-key
        run: |
          cd apps/api
          pytest tests/ -v --cov=app --cov-report=xml
        # No || true - fail on test failures
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./apps/api/coverage.xml

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install dependencies
        run: |
          cd apps/web
          npm ci
      
      - name: Run tests
        run: |
          cd apps/web
          npm run test
        # No || true - fail on test failures

  deploy:
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    needs: [lint-and-type-check, test-backend, test-frontend]
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Render CLI
        run: |
          curl -fsSL https://render.com/install.sh | sh
          echo "$HOME/.render/bin" >> $GITHUB_PATH
      
      - name: Deploy API to Render
        env:
          RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
        run: |
          render deploy \
            --service-id ${{ secrets.RENDER_API_SERVICE_ID }} \
            --key $RENDER_API_KEY \
            --commit ${{ github.sha }}
      
      - name: Run Database Migrations
        env:
          RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
        run: |
          render job:run \
            --service-id ${{ secrets.RENDER_API_SERVICE_ID }} \
            --command "alembic upgrade head" \
            --key $RENDER_API_KEY
      
      - name: Deploy Web to Render
        env:
          RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
        run: |
          render deploy \
            --service-id ${{ secrets.RENDER_WEB_SERVICE_ID }} \
            --key $RENDER_API_KEY \
            --commit ${{ github.sha }}
      
      - name: Health Check
        run: |
          for i in {1..30}; do
            if curl -f https://waardhaven-api.onrender.com/health; then
              echo "API is healthy"
              break
            fi
            echo "Waiting for API... (attempt $i/30)"
            sleep 10
          done
          
          for i in {1..30}; do
            if curl -f https://waardhaven-web.onrender.com; then
              echo "Web is healthy"
              break
            fi
            echo "Waiting for Web... (attempt $i/30)"
            sleep 10
          done
```

### Deployment Script

```bash
#!/bin/bash
# apps/api/scripts/deploy.sh

set -e  # Exit on error

echo "🚀 Starting deployment..."

# Check environment
if [ -z "$RENDER_API_KEY" ]; then
  echo "❌ RENDER_API_KEY not set"
  exit 1
fi

# Backup database
echo "📦 Creating database backup..."
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Run migrations
echo "🔄 Running database migrations..."
alembic upgrade head || {
  echo "❌ Migration failed, rolling back..."
  alembic downgrade -1
  exit 1
}

# Deploy API
echo "🌐 Deploying API..."
render deploy --service-id $RENDER_API_SERVICE_ID --key $RENDER_API_KEY

# Health check
echo "❤️ Running health checks..."
for i in {1..30}; do
  if curl -f https://waardhaven-api.onrender.com/health; then
    echo "✅ API is healthy"
    break
  fi
  sleep 10
done

# Deploy Web
echo "🎨 Deploying frontend..."
render deploy --service-id $RENDER_WEB_SERVICE_ID --key $RENDER_API_KEY

echo "✅ Deployment complete!"
```

## 🧪 Testing Checklist

### Pipeline Tests
- [ ] Linting catches errors
- [ ] Type checking works
- [ ] Tests fail properly
- [ ] Coverage reports generated
- [ ] Deployment triggered on main

### Deployment Tests
- [ ] Render CLI works
- [ ] Migrations run successfully
- [ ] Health checks pass
- [ ] Rollback works
- [ ] Notifications sent

## 📈 Success Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Pipeline reliability | 0% | 99% | 🔴 |
| Deploy automation | Manual | Full | 🔴 |
| Deploy time | >30min | <10min | 🔴 |
| Rollback time | N/A | <5min | 🔴 |
| Test visibility | Hidden | Full | 🔴 |

## 🔄 GitHub Secrets Required

```yaml
# Production secrets
RENDER_API_KEY: rnd_xxxxxxxxxxxx
RENDER_API_SERVICE_ID: srv-xxxxxxxxxxxx
RENDER_WEB_SERVICE_ID: srv-xxxxxxxxxxxx
DATABASE_URL: postgresql://user:pass@host/db
SECRET_KEY: your-secret-key
TWELVEDATA_API_KEY: your-api-key
MARKETAUX_API_KEY: your-api-key
SENTRY_DSN: https://xxx@xxx.ingest.sentry.io/xxx

# Notification secrets
SLACK_WEBHOOK: https://hooks.slack.com/services/xxx
DISCORD_WEBHOOK: https://discord.com/api/webhooks/xxx
```

## ⚠️ Critical Actions

1. **IMMEDIATELY**: Remove all `|| true` statements
2. **TODAY**: Setup Render CLI in workflows
3. **TODAY**: Add all required secrets to GitHub
4. **TOMORROW**: Test full deployment pipeline

---

**Next**: Continue with [06-testing-coverage.md](./06-testing-coverage.md)