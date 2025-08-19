# GitHub Actions CI/CD Pipeline

## Overview

The Waardhaven AutoIndex project uses GitHub Actions for continuous integration and deployment. The pipeline includes testing, security scanning, building, and automated deployment to Render.com.

**Last Updated**: 2025-01-17  
**Status**: ✅ All deprecated actions updated to v4

## Workflow Files

### Main Workflows

1. **ci-cd.yml** - Main CI/CD pipeline
2. **deploy.yml** - Deployment workflow
3. **security.yml** - Security scanning workflow

### Reusable Workflows

1. **reusable-docker-build.yml** - Docker image building
2. **reusable-node-test.yml** - Node.js testing (Frontend)
3. **reusable-python-test.yml** - Python testing (Backend)

## Recent Updates (2025-01-17)

### Fixed Deprecation Issues

All deprecated GitHub Actions have been updated:
- `actions/upload-artifact@v3` → `actions/upload-artifact@v4` ✅
- `actions/download-artifact@v3` → `actions/download-artifact@v4` ✅
- `actions/cache@v3` → `actions/cache@v4` ✅

### Package Manager Standardization

- Standardized to npm across entire monorepo
- All frontend builds use npm
- Consistent dependency management

## Workflow Details

### CI/CD Pipeline (ci-cd.yml)

**Trigger**: Push to main/develop, Pull requests

**Jobs**:
1. **Setup** - Matrix strategy configuration
2. **API Tests** - Python backend testing with PostgreSQL
3. **Web Tests** - Frontend testing with Next.js
4. **Build API** - Docker image for backend
5. **Build Web** - Next.js production build
6. **Security Scan** - Trivy security scanning

**Key Features**:
- Parallel test execution
- Docker layer caching
- Artifact uploads for build outputs
- PostgreSQL service container for tests

### Security Workflow (security.yml)

**Trigger**: Push, PR, Weekly schedule (Mondays 2 AM)

**Scans**:
1. **Dependency Scan** - Python (Safety, Bandit) and Node (npm audit, Snyk)
2. **CodeQL Analysis** - Static analysis for Python and JavaScript
3. **Container Scan** - Trivy vulnerability scanner for Docker images
4. **Secrets Scan** - Gitleaks and TruffleHog
5. **SAST Analysis** - Semgrep security patterns
6. **License Scan** - License compliance checking

**Outputs**:
- Security reports as artifacts
- SARIF files for GitHub Security tab
- Consolidated security report

### Reusable Workflows

#### Python Test Workflow
```yaml
uses: ./.github/workflows/reusable-python-test.yml
with:
  python-version: '3.11'
  working-directory: './apps/api'
secrets:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  JWT_SECRET_KEY: ${{ secrets.JWT_SECRET_KEY }}
```

#### Node Test Workflow
```yaml
uses: ./.github/workflows/reusable-node-test.yml
with:
  node-version: '20'
  working-directory: './apps/web'
secrets:
  NEXT_PUBLIC_API_URL: ${{ secrets.API_URL }}
```

## Environment Variables

### Required Secrets

**Backend Testing**:
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - JWT signing key
- `TWELVEDATA_API_KEY` - Market data API key

**Frontend Testing**:
- `NEXT_PUBLIC_API_URL` - Backend API URL

**Deployment**:
- `RENDER_API_KEY` - Render deployment key
- `DOCKER_REGISTRY` - Docker registry URL
- `DOCKER_USERNAME` - Registry username
- `DOCKER_PASSWORD` - Registry password

## Actions Used

### Core Actions (v4)
- `actions/checkout@v4` - Repository checkout
- `actions/setup-node@v4` - Node.js setup
- `actions/setup-python@v5` - Python setup
- `actions/cache@v4` - Dependency caching
- `actions/upload-artifact@v4` - Artifact uploads
- `actions/download-artifact@v4` - Artifact downloads

### Security Actions
- `github/codeql-action/*@v2` - CodeQL analysis
- `aquasecurity/trivy-action@master` - Container scanning
- `gitleaks/gitleaks-action@v2` - Secret detection
- `trufflesecurity/trufflehog@main` - Secret scanning
- `returntocorp/semgrep-action@v1` - SAST analysis

### Deployment Actions
- `docker/setup-buildx-action@v3` - Docker buildx
- `docker/login-action@v3` - Registry authentication
- `docker/build-push-action@v5` - Image building

## Caching Strategy

### Python Dependencies
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

### Node Dependencies
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
```

### Docker Layers
```yaml
- uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

## Troubleshooting

### Common Issues

1. **Artifact Upload Failures**
   - Ensure using `actions/upload-artifact@v4`
   - Check artifact name uniqueness
   - Verify path exists

2. **Cache Misses**
   - Verify cache key includes dependency file hash
   - Check restore-keys for fallback
   - Clear cache if corrupted

3. **Test Failures**
   - Check PostgreSQL service is running
   - Verify environment variables are set
   - Review test logs in artifacts

4. **Security Scan Failures**
   - Most scans use `|| true` to prevent blocking
   - Check individual scan reports in artifacts
   - Review SARIF files in Security tab

## Best Practices

1. **Use Reusable Workflows** - Reduce duplication
2. **Pin Action Versions** - Avoid unexpected changes
3. **Cache Dependencies** - Speed up builds
4. **Upload Artifacts** - Preserve test results
5. **Run Security Scans** - Catch vulnerabilities early
6. **Use Matrix Builds** - Test multiple versions
7. **Fail Fast** - Stop on first failure in matrix

## Monitoring

### GitHub UI
- Actions tab for workflow runs
- Security tab for vulnerability alerts
- Pull request checks for status

### Notifications
- Email notifications for failures
- Slack integration (if configured)
- GitHub mobile app alerts

## Cost Optimization

1. **Use Concurrency Limits**
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

2. **Conditional Jobs**
```yaml
if: github.event_name == 'push' && github.ref == 'refs/heads/main'
```

3. **Artifact Retention**
```yaml
retention-days: 7  # Reduce storage costs
```

## Future Improvements

1. **Performance**
   - Implement job dependency optimization
   - Add parallel test splitting
   - Use self-hosted runners for heavy workloads

2. **Security**
   - Add DAST (Dynamic Application Security Testing)
   - Implement security policy enforcement
   - Add compliance scanning

3. **Deployment**
   - Add blue-green deployment support
   - Implement automatic rollback
   - Add smoke tests post-deployment

## Maintenance

### Regular Updates
- Check for action updates quarterly
- Review deprecated features in changelog
- Update to latest major versions when stable

### Action Updates Changelog
- 2025-01-17: Updated all artifact actions to v4
- 2025-01-17: Updated cache actions to v4
- 2025-01-17: Standardized package manager to npm

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Artifact Actions v4 Migration](https://github.blog/changelog/2024-04-16-deprecation-notice-v3-of-the-artifact-actions/)
- [Render.com CI/CD](https://render.com/docs/deploy-hooks)