# API Dockerfile

## Overview
Docker configuration for the FastAPI backend application.

## Location
`apps/api/Dockerfile`

## Build Stages

### Stage 1: Dependencies
- Python 3.11 base image
- System dependencies
- Python packages
- Requirements installation

### Stage 2: Application
- Code copying
- Environment setup
- User configuration
- Entry point

## Base Image
- Python 3.11-slim
- Debian-based
- Minimal footprint
- Security updates

## Dependencies Installation

### System Packages
- PostgreSQL client
- Build essentials
- Security updates
- Cleanup after install

### Python Packages
- requirements.txt
- Pip upgrade
- No cache dir
- Version pinning

## Application Setup

### File Structure
```
/app
├── app/
│   ├── core/
│   ├── routers/
│   ├── services/
│   └── ...
├── requirements.txt
└── startup.sh
```

### Environment Variables
- DATABASE_URL
- SECRET_KEY
- TWELVEDATA_API_KEY
- NODE_ENV

## Security Configuration

### User Setup
- Non-root user
- Minimal permissions
- Read-only filesystem
- No shell access

### Network Security
- Single port exposure (8000)
- No unnecessary services
- Firewall ready

## Optimization

### Layer Caching
- Dependency layer
- Code layer separation
- Cache bust strategies
- Build optimization

### Size Reduction
- Multi-stage builds
- Slim base image
- Package cleanup
- No dev dependencies

## Health Check
- Endpoint: /health
- Interval: 30s
- Timeout: 10s
- Retries: 3

## Entry Point

### Startup Script
- Database initialization
- Migration check
- Server launch
- Error handling

### Command
```bash
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4
```

## Build Process

### Local Build
```bash
docker build -t waardhaven-api .
```

### Production Build
```bash
docker build \
  --build-arg NODE_ENV=production \
  -t waardhaven-api:prod .
```

## Runtime Configuration

### Port Mapping
- Container: 8000
- Host: configurable
- Protocol: HTTP

### Volume Mounts
- Logs: /app/logs
- Static files: /app/static
- Temp files: /tmp

## Debugging

### Debug Mode
- Hot reload enabled
- Verbose logging
- Debug endpoints
- Stack traces

### Logging
- Stdout/stderr
- JSON format
- Log levels
- Rotation strategy

## Dependencies
- Python 3.11
- FastAPI
- PostgreSQL client
- Uvicorn server