# CI/CD Pipeline Documentation

## Overview

Production CI/CD pipeline implemented with GitHub Actions providing automated testing, security scanning, and deployment to Render.com. The pipeline ensures code quality, security, and zero-downtime deployments.

## Pipeline Architecture

### GitHub Actions (Production)
- **Location**: `.github/workflows/`
- **Main Pipeline**: `ci-cd.yml` - Complete CI/CD workflow
- **Reusable Workflows**: 
  - `reusable-docker-build.yml` - Docker image building
  - `reusable-node-test.yml` - Frontend testing
  - `reusable-python-test.yml` - Backend testing
- **Specialized Pipelines**: 
  - `deploy.yml` - Production deployment
  - `security.yml` - Security scanning
- **Status**: Active and operational

## Pipeline Stages

### 1. Setup & Detection
- Detects changes in specific components (API, Web, Docs)
- Determines which jobs need to run
- Sets up environment variables

### 2. Code Quality
- **Linting**: Python (ruff, black, mypy) and TypeScript (ESLint, TSC)
- **Formatting**: Automatic code formatting checks
- **Type Checking**: Static type analysis

### 3. Testing
- **Backend Tests**: 10 test files with pytest
  - Unit tests for services
  - Integration tests for API endpoints
  - Provider tests with mocking
  - Performance calculation tests
- **Coverage**: 70%+ target with HTML reports
- **Database**: PostgreSQL test fixtures
- **Test Results**: pytest-xml reporting

### 4. Security Scanning
- **Dependency Scanning**: Check for vulnerable dependencies
- **Container Scanning**: Trivy vulnerability scanning
- **Secret Detection**: Gitleaks and TruffleHog
- **SAST**: Static Application Security Testing with Semgrep
- **License Compliance**: License checking

### 5. Build
- **API**: Docker containerization (`apps/api/Dockerfile.api`)
- **Web**: Next.js production build with TypeScript
- **Optimization**: 
  - Multi-stage Docker builds
  - Layer caching
  - Production dependencies only
- **Artifacts**: Build artifact storage in GitHub

### 6. Deployment (Render.com)
- **Environment**: Production (waardhaven-*.onrender.com)
- **Strategy**: Blue-green deployment with zero downtime
- **Services Deployed**:
  - API: Docker web service
  - Web: Docker web service
  - Database: PostgreSQL managed instance
- **Automatic**: Triggered on main branch push
- **Health Checks**: `/api/v1/health` validation

## Environment Configuration

### GitHub Actions Secrets (Configured)
```yaml
# Automatically Provided
GITHUB_TOKEN         # GitHub API access

# Render Deployment
RENDER_API_KEY      # Render deployment API
RENDER_SERVICE_ID   # Service identifiers

# Application Secrets
DATABASE_URL        # PostgreSQL connection
SECRET_KEY          # JWT signing key
ADMIN_TOKEN         # Admin access token

# External APIs
TWELVEDATA_API_KEY  # Market data API
MARKETAUX_API_KEY   # News API (optional)

# Optional
REDIS_URL           # Redis connection
GOOGLE_CLIENT_ID    # OAuth configuration
```

### Azure DevOps Variable Groups
```yaml
waardhaven-common:
  - dockerRegistry
  - apiUrl
  - databaseUrl
  
waardhaven-dev:
  - environment specific vars
  
waardhaven-staging:
  - environment specific vars
  
waardhaven-prod:
  - environment specific vars
```

## Migration Guide

### From GitHub Actions to Azure DevOps

1. **Variables**: Convert GitHub secrets to Azure DevOps variable groups
2. **Service Connections**: Set up Azure service connections
3. **Environments**: Configure Azure DevOps environments with approvals
4. **Triggers**: Adjust branch policies and triggers

### From Azure DevOps to GitHub Actions

1. **Secrets**: Add secrets to GitHub repository settings
2. **Environments**: Configure GitHub environments with protection rules
3. **Runners**: Ensure GitHub runners have necessary tools
4. **Permissions**: Set up GITHUB_TOKEN permissions

## Clean Architecture Practices

### 1. Separation of Concerns
- Reusable workflows for common tasks
- Templates for repeated patterns
- Environment-specific configurations

### 2. Configuration as Code
- All pipeline configuration in version control
- Environment variables in centralized locations
- Secrets managed through platform features

### 3. Immutable Infrastructure
- Docker containers for consistent deployments
- Version tagging for all artifacts
- No manual server configuration

### 4. Testing Pyramid
- Unit tests (fast, many)
- Integration tests (moderate)
- E2E tests (slow, few)
- Smoke tests (critical paths only)

### 5. Security by Design
- Security scanning at multiple stages
- Dependency vulnerability checking
- Container image scanning
- Secret detection

## Usage

### Running Pipelines Manually

#### GitHub Actions
```bash
# Trigger deployment workflow
gh workflow run deploy.yml -f environment=staging -f version=v1.2.3
```

#### Azure DevOps
```bash
# Queue a build
az pipelines run --name "CI/CD Pipeline" --branch main
```

### Local Testing

#### Test GitHub Actions locally
```bash
# Install act
brew install act

# Run workflow
act -j test-api
```

#### Test Azure Pipelines locally
```bash
# Install Azure Pipelines agent
# Follow: https://docs.microsoft.com/en-us/azure/devops/pipelines/agents/

# Run pipeline
./run.sh
```

## Monitoring & Alerts

### Metrics to Track
- Build success rate
- Deployment frequency
- Lead time for changes
- Mean time to recovery (MTTR)
- Test coverage trends

### Notifications
- Slack integration for deployment status
- Email alerts for failures
- PR comments for security issues

## Best Practices

1. **Keep pipelines fast**: Parallelize where possible
2. **Cache dependencies**: Use caching for faster builds
3. **Fail fast**: Run quick checks first
4. **Version everything**: Tag all deployments
5. **Monitor continuously**: Track pipeline metrics
6. **Document changes**: Update this README when modifying pipelines

## Troubleshooting

### Common Issues

#### Pipeline fails with permission error
- Check service connection permissions
- Verify secret/variable access

#### Tests pass locally but fail in CI
- Check environment variables
- Verify database connections
- Review timezone differences

#### Docker build fails
- Check Dockerfile paths
- Verify base image availability
- Review build context size

## Support

For pipeline issues:
1. Check workflow run logs
2. Review this documentation
3. Contact DevOps team
4. Create an issue in the repository