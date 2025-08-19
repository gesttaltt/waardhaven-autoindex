# Root Router

## Overview
Root endpoint router providing API information, health checks, and endpoint discovery.

## Location
`apps/api/app/routers/root.py`

## Purpose
Provides essential API metadata, health monitoring, and service discovery endpoints at the root level.

## Endpoints

### GET /
Root endpoint with comprehensive API information.

**Response:**
```json
{
  "name": "Waardhaven Autoindex API",
  "version": "0.1.0",
  "status": "running",
  "documentation": "/docs",
  "health": "/health",
  "endpoints": {
    "auth": "/api/v1/auth",
    "index": "/api/v1/index",
    "benchmark": "/api/v1/benchmark",
    "strategy": "/api/v1/strategy",
    "diagnostics": "/api/v1/diagnostics",
    "tasks": "/api/v1/tasks",
    "manual": "/api/v1/manual"
  }
}
```

**Features:**
- Service discovery for available endpoints
- API version information
- Links to documentation and health check
- No authentication required

**Note:** Currently missing `background` and `news` routers from the endpoint list.

### GET /health
Simple health check endpoint for monitoring.

**Response:**
```json
{
  "status": "ok",
  "service": "api"
}
```

**Features:**
- Quick liveness check
- No database dependency
- Suitable for load balancer health checks
- Always returns 200 OK if service is running

### GET /api
API version and base path information.

**Response:**
```json
{
  "version": "v1",
  "base_path": "/api/v1",
  "documentation": "/docs"
}
```

**Features:**
- API versioning information
- Base path for all versioned endpoints
- Link to interactive documentation

## Use Cases

### Service Discovery
Clients can query the root endpoint to discover available API endpoints without hardcoding paths.

```javascript
// Example client usage
const response = await fetch('https://api.waardhaven.com/');
const apiInfo = await response.json();
const authEndpoint = apiInfo.endpoints.auth;
```

### Health Monitoring
Load balancers and monitoring systems can use `/health` for:
- Kubernetes liveness probes
- Docker health checks
- Uptime monitoring
- Service mesh health checks

### API Version Detection
Clients can determine API version and adjust behavior accordingly:
```javascript
const apiResponse = await fetch('https://api.waardhaven.com/api');
const { version, base_path } = await apiResponse.json();
```

## Security Considerations
- All endpoints are public (no authentication required)
- Suitable for public API discovery
- No sensitive information exposed
- Rate limiting should be applied in production

## Integration with OpenAPI
The `/docs` endpoint referenced provides interactive Swagger/OpenAPI documentation generated automatically by FastAPI.

## Missing Endpoints
The endpoint discovery currently doesn't list:
- `/api/v1/background` - Background task management
- `/api/v1/news` - News and sentiment analysis

Consider updating the root router to include all registered endpoints.

## Dependencies
- FastAPI's APIRouter
- No database dependencies
- No external service dependencies

## Related Documentation
- Main application setup: `app/main.py`
- API documentation: Available at `/docs` when running
- Router registration: Defined in main application