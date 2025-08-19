# API Dockerfile

## Overview
Docker configuration for the FastAPI backend application.

## Location
`apps/api/Dockerfile`

## Actual Implementation

### Base Image
- Python 3.11-slim
- Lightweight Debian-based image
- No multi-stage build (single stage)

### Build Process
```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
```

### Dependencies Installation
```dockerfile
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
```

**Features:**
- No system packages installed (uses pure Python)
- Direct pip install from requirements.txt
- No cache to reduce image size

### Application Setup
```dockerfile
COPY app ./app
COPY scripts ./scripts
RUN chmod +x scripts/startup.sh
```

**File Structure:**
```
/app
├── app/          # Application code
├── scripts/      # Startup scripts
└── requirements.txt
```

### Environment Configuration
- `PORT`: Default 10000 (for Render deployment)
- `PYTHONDONTWRITEBYTECODE`: Prevents .pyc files
- `PYTHONUNBUFFERED`: Ensures stdout/stderr are unbuffered

### Startup Configuration
```dockerfile
CMD ["./scripts/startup.sh"]
```

Uses `scripts/startup.sh` for environment-based configuration:
- Determines worker count based on environment
- Configures uvicorn with appropriate settings
- Handles different deployment scenarios

## Port Configuration
- Exposed port: Uses `${PORT}` environment variable
- Default: 10000 (Render.com standard)
- Configurable via environment

## Build Commands

### Local Build
```bash
docker build -t waardhaven-api .
```

### Run Locally
```bash
docker run -p 8000:10000 \
  -e DATABASE_URL="postgresql://..." \
  -e SECRET_KEY="..." \
  waardhaven-api
```

## Security Notes
- Runs as root user (no non-root user configured)
- No health check configured in Dockerfile
- Relies on deployment platform for health monitoring

## Differences from Documentation
The actual Dockerfile is much simpler than previously documented:
- No multi-stage build
- No system packages installation
- No health check configuration
- No volume mounts defined
- No debug mode configuration
- Uses startup script for flexibility

## Dependencies
All dependencies managed via `requirements.txt`:
- FastAPI
- SQLAlchemy
- Uvicorn
- Other Python packages

## Deployment
Optimized for Render.com deployment:
- Uses PORT environment variable
- Startup script handles configuration
- No hardcoded values