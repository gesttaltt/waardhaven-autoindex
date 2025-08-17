# Diagnostics Router

## Overview
System diagnostics and health monitoring endpoints for operational visibility.

## Location
`apps/api/app/routers/diagnostics.py`

## Purpose
Provides system health checks, performance metrics, and debugging information.

## Endpoints

### GET /api/v1/diagnostics/health
- System health status
- Component availability
- Database connectivity
- External service status

### GET /api/v1/diagnostics/metrics
- Performance metrics
- Resource utilization
- Request statistics
- Error rates

### GET /api/v1/diagnostics/cache
- Cache statistics
- Hit/miss rates
- Memory usage
- Key distribution

### GET /api/v1/diagnostics/database
- Connection pool status
- Query performance
- Active connections
- Slow query log

### GET /api/v1/diagnostics/services
- TwelveData API status
- Service availability
- Rate limit status
- Response times

## Health Check Response

### Status Codes
- **200 OK**: All systems operational
- **503 Service Unavailable**: Critical component down
- **206 Partial Content**: Degraded performance

### Response Format
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "components": {
    "database": "healthy",
    "cache": "healthy",
    "market_data": "healthy",
    "api": "healthy"
  },
  "version": "1.0.0",
  "uptime": 86400
}
```

## Performance Metrics

### System Metrics
- CPU usage
- Memory utilization
- Disk I/O
- Network traffic

### Application Metrics
- Request rate
- Response times
- Error rates
- Active users

### Business Metrics
- Portfolio updates/hour
- Data refresh success rate
- Strategy execution time
- API calls remaining

## Monitoring Integration

### Prometheus Metrics
- Custom metrics export
- Standard metrics
- Histogram data
- Counter values

### Logging
- Structured logs
- Log levels
- Error tracking
- Performance logs

## Debugging Features

### Debug Endpoints
- `/api/v1/diagnostics/debug/config` - Configuration dump
- `/api/v1/diagnostics/debug/env` - Environment variables
- `/api/v1/diagnostics/debug/routes` - Available routes
- `/api/v1/diagnostics/debug/dependencies` - Dependency versions

### Profiling
- Request profiling
- Memory profiling
- Database query analysis
- CPU profiling

## Cache Diagnostics

### Cache Information
- Total keys
- Memory usage
- Eviction statistics
- TTL distribution

### Cache Operations
- Clear cache
- Invalidate keys
- Refresh cache
- Export cache data

## Database Diagnostics

### Connection Pool
- Active connections
- Idle connections
- Pool size
- Wait queue

### Query Analysis
- Slow queries
- Most frequent queries
- Index usage
- Lock statistics

## Service Dependencies

### External Services
- TwelveData API health
- Database server status
- Cache server status
- Message queue status

### Internal Services
- Background tasks
- Scheduled jobs
- Worker processes
- Queue status

## Error Tracking

### Error Statistics
- Error counts by type
- Error trends
- Stack traces
- User impact

### Alert Triggers
- High error rate
- Service downtime
- Performance degradation
- Resource exhaustion

## Security Considerations

### Access Control
- Admin-only endpoints
- IP whitelisting
- Authentication required
- Rate limiting

### Data Privacy
- No sensitive data in logs
- PII redaction
- Secure transmission
- Audit logging

## Usage Examples

### Health Check
```bash
curl http://api.example.com/api/v1/diagnostics/health
```

### Metrics Export
```bash
curl http://api.example.com/api/v1/diagnostics/metrics \
  -H "Authorization: Bearer <admin-token>"
```

## Dependencies
- System monitoring libraries
- Database connection pool
- Cache client
- External service clients