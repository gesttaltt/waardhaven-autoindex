# Render.yaml Configuration

## Overview
The `render.yaml` file defines the infrastructure-as-code configuration for deploying the Waardhaven AutoIndex application on Render.com.

## Location
`render.yaml` (repository root)

## Structure

### Services

#### 1. waardhaven-api (Backend)
- **Type**: Web service
- **Environment**: Docker
- **Plan**: Starter
- **Port**: 10000
- **Root Directory**: `apps/api`
- **Dockerfile**: `./Dockerfile` (relative to rootDir)

##### Environment Variables
| Variable | Type | Description |
|----------|------|-------------|
| PORT | Static | Service port (10000) |
| SECRET_KEY | Secret | JWT authentication key |
| DATABASE_URL | Dynamic | From database connection |
| ADMIN_TOKEN | Secret | Admin API access token |
| TWELVEDATA_API_KEY | Secret | Market data API key |
| DAILY_DROP_THRESHOLD | Static | -0.01 (-1% daily drop filter) |
| ASSET_DEFAULT_START | Static | 2018-01-01 (historical data start) |
| SP500_TICKER | Static | ^GSPC (S&P 500 symbol) |
| FRONTEND_URL | Secret | CORS allowed origin |
| SKIP_STARTUP_REFRESH | Static | false (refresh on startup) |

#### 2. waardhaven-web (Frontend)
- **Type**: Web service
- **Environment**: Docker
- **Plan**: Starter
- **Port**: 10000
- **Root Directory**: `apps/web`
- **Dockerfile**: `./Dockerfile` (relative to rootDir)

##### Environment Variables
| Variable | Type | Description |
|----------|------|-------------|
| PORT | Static | Service port (10000) |
| NEXT_PUBLIC_API_URL | Secret | Backend API URL |

### Database

#### waardhaven-db
- **Type**: PostgreSQL
- **Plan**: Starter
- **Database Name**: waardhaven_db_5t62
- **User**: waardhaven_db_5t62_user
- **Connection**: Automatically injected into API service

## Environment Variable Types

### Static Values (`value`)
Hard-coded values in the configuration file.

### Secrets (`sync: false`)
Sensitive values that must be set manually in Render dashboard:
1. Go to service settings
2. Navigate to Environment section
3. Add secret values
4. Values are encrypted at rest

### Database Connection (`fromDatabase`)
Automatically populated from the database service connection string.

## Deployment Process

### Initial Setup
1. Connect GitHub repository to Render
2. Render reads `render.yaml` automatically
3. Creates all defined services and database
4. Set secret environment variables in dashboard
5. Deploy services

### Updates
1. Push changes to repository
2. Render auto-deploys on push to main branch
3. Services restart with new configuration

### Manual Deploy
```bash
# Via Render CLI
render deploy

# Via Dashboard
# Click "Manual Deploy" button
```

## Docker Configuration

### API Dockerfile Path
- Located at: `apps/api/Dockerfile`
- Context: `apps/api/`
- Builds Python 3.11 slim image
- Installs requirements
- Runs startup script

### Web Dockerfile Path
- Located at: `apps/web/Dockerfile`
- Context: `apps/web/`
- Multi-stage Node.js build
- Builds Next.js application
- Serves on configured PORT

## Service Plans

### Starter Plan Features
- 512 MB RAM
- 0.5 CPU
- Auto-scaling disabled
- Free SSL certificates
- Custom domains supported

### Upgrade Considerations
For production:
- Upgrade to Standard or Pro plans
- Enable auto-scaling
- Add Redis service for caching
- Configure health checks
- Set up monitoring

## Health Checks
Services expose health endpoints:
- API: `/health`
- Web: Render's default Node.js health check

## Networking
- Services communicate via internal network
- Public URLs auto-generated
- SSL/TLS handled by Render
- CORS configured via environment

## Backup and Recovery
- Database: Daily automatic backups (7-day retention on Starter)
- Code: Version controlled in Git
- Secrets: Store copies securely outside Render

## Monitoring
- Basic metrics in Render dashboard
- Service logs available
- Set up external monitoring (recommended):
  - Datadog
  - New Relic
  - Custom solution

## Troubleshooting

### Common Issues
1. **Build Failures**
   - Check Dockerfile paths
   - Verify rootDir settings
   - Review build logs

2. **Service Won't Start**
   - Check PORT configuration
   - Verify environment variables
   - Review startup logs

3. **Database Connection Issues**
   - Ensure DATABASE_URL is properly set
   - Check network configuration
   - Verify database is running

4. **Secret Variables Not Working**
   - Must set manually in dashboard
   - Check for typos in variable names
   - Verify sync: false is set

## Best Practices
1. Keep secrets out of render.yaml
2. Use environment-specific configurations
3. Test locally with Docker first
4. Monitor resource usage
5. Set up alerting for failures
6. Regular backup verification
7. Document all manual configurations

## Related Files
- `apps/api/Dockerfile` - API container definition
- `apps/web/Dockerfile` - Web container definition
- `apps/api/scripts/startup.sh` - API startup script
- `.env.example` files - Local development configuration