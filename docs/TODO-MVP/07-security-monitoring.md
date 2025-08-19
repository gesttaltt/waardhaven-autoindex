# Security & Monitoring Implementation

**Priority**: P1 - HIGH  
**Status**: 🔴 Minimal  
**Estimated**: 2 days  
**Focus**: Security hardening, observability, alerting

## 🎯 Objective

Implement comprehensive security and monitoring to ensure:
- Protection against common vulnerabilities
- Real-time error tracking
- Performance monitoring
- Audit logging
- Incident response capability

## 📋 Current State

### Security
- ✅ JWT authentication
- ✅ Password hashing (bcrypt)
- ✅ Basic CORS configuration
- 🔴 No rate limiting per user
- 🔴 No security headers
- 🔴 No input sanitization
- 🔴 No SQL injection protection beyond ORM

### Monitoring
- 🔴 No error tracking (Sentry)
- 🔴 No metrics collection
- 🔴 No distributed tracing
- 🔴 No alerting system
- 🔴 Basic logging only

## 📋 Task Breakdown

### Phase 1: Security Hardening (4 hours)

#### Task 1.1: Security Headers
**File**: `apps/api/app/middleware/security.py`

```python
# Headers to implement:
- [ ] X-Content-Type-Options: nosniff
- [ ] X-Frame-Options: DENY
- [ ] X-XSS-Protection: 1; mode=block
- [ ] Strict-Transport-Security
- [ ] Content-Security-Policy
```

#### Task 1.2: Advanced Rate Limiting
**File**: `apps/api/app/middleware/rate_limit.py`

```python
# Features:
- [ ] Per-user rate limiting
- [ ] Endpoint-specific limits
- [ ] IP-based limiting
- [ ] Distributed rate limiting (Redis)
- [ ] Exponential backoff
```

#### Task 1.3: Input Validation & Sanitization
```python
# Implement:
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] Path traversal prevention
- [ ] Command injection prevention
- [ ] Schema validation everywhere
```

#### Task 1.4: Authentication Enhancements
```python
# Add:
- [ ] Token rotation
- [ ] Session management
- [ ] 2FA support preparation
- [ ] Password complexity rules
- [ ] Account lockout mechanism
```

### Phase 2: Error Tracking (Sentry) (2 hours)

#### Task 2.1: Sentry Integration
**File**: `apps/api/app/core/monitoring.py`

```python
# Setup:
- [ ] Install Sentry SDK
- [ ] Configure for FastAPI
- [ ] Add user context
- [ ] Custom error grouping
- [ ] Performance monitoring
```

#### Task 2.2: Frontend Sentry
**File**: `apps/web/app/providers/ErrorBoundary.tsx`

```typescript
# Setup:
- [ ] Install @sentry/nextjs
- [ ] Configure error boundary
- [ ] Source map upload
- [ ] User feedback widget
```

### Phase 3: Metrics & Monitoring (3 hours)

#### Task 3.1: Prometheus Metrics
**File**: `apps/api/app/core/metrics.py`

```python
# Metrics to track:
- [ ] Request count/rate
- [ ] Response time histogram
- [ ] Error rate
- [ ] Database query time
- [ ] External API latency
- [ ] Cache hit rate
```

#### Task 3.2: Health Checks
**File**: `apps/api/app/routers/health.py`

```python
# Endpoints:
- [ ] /health - Basic health
- [ ] /health/ready - Readiness check
- [ ] /health/live - Liveness check
- [ ] /health/dependencies - Check all deps
```

#### Task 3.3: Structured Logging
**File**: `apps/api/app/core/logging.py`

```python
# Implement:
- [ ] JSON structured logs
- [ ] Correlation IDs
- [ ] Request/response logging
- [ ] Sensitive data masking
- [ ] Log aggregation ready
```

### Phase 4: Alerting System (2 hours)

#### Task 4.1: Alert Configuration
```yaml
# Alerts for:
- [ ] High error rate
- [ ] Slow response time
- [ ] Database connection issues
- [ ] API rate limit exceeded
- [ ] Security events
```

#### Task 4.2: Notification Channels
```python
# Implement:
- [ ] Slack notifications
- [ ] Email alerts
- [ ] PagerDuty integration
- [ ] Discord webhooks
```

### Phase 5: Audit Logging (2 hours)

#### Task 5.1: Audit Trail
**File**: `apps/api/app/services/audit.py`

```python
# Log events:
- [ ] User login/logout
- [ ] Data modifications
- [ ] Permission changes
- [ ] Failed auth attempts
- [ ] API key usage
```

#### Task 5.2: Compliance
```python
# Implement:
- [ ] GDPR compliance logs
- [ ] Data retention policies
- [ ] User activity reports
- [ ] Security event logs
```

### Phase 6: Security Testing (3 hours)

#### Task 6.1: Security Tests
```python
# Test for:
- [ ] SQL injection
- [ ] XSS attacks
- [ ] CSRF protection
- [ ] Authentication bypass
- [ ] Rate limiting
```

#### Task 6.2: Dependency Scanning
```yaml
# CI/CD integration:
- [ ] Snyk/Dependabot setup
- [ ] License checking
- [ ] Vulnerability scanning
- [ ] Docker image scanning
```

## 📊 Implementation Examples

### Advanced Rate Limiting

```python
# apps/api/app/middleware/rate_limit.py

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import redis.asyncio as redis
import hashlib
import time
from typing import Optional

class RateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window: int,
        cost: int = 1
    ) -> tuple[bool, Optional[dict]]:
        """
        Token bucket algorithm with Redis
        """
        now = time.time()
        pipe = self.redis.pipeline()
        
        # Get current bucket state
        pipe.hgetall(key)
        pipe.expire(key, window * 2)
        
        bucket_data, _ = await pipe.execute()
        
        if not bucket_data:
            # Initialize bucket
            bucket_data = {
                b'tokens': str(limit).encode(),
                b'last_refill': str(now).encode()
            }
        
        tokens = float(bucket_data[b'tokens'])
        last_refill = float(bucket_data[b'last_refill'])
        
        # Calculate tokens to add
        time_passed = now - last_refill
        tokens_to_add = time_passed * (limit / window)
        tokens = min(limit, tokens + tokens_to_add)
        
        if tokens >= cost:
            # Consume tokens
            tokens -= cost
            
            # Update bucket
            pipe = self.redis.pipeline()
            pipe.hset(key, mapping={
                'tokens': tokens,
                'last_refill': now
            })
            pipe.expire(key, window * 2)
            await pipe.execute()
            
            return True, {
                'X-RateLimit-Limit': str(limit),
                'X-RateLimit-Remaining': str(int(tokens)),
                'X-RateLimit-Reset': str(int(now + window))
            }
        else:
            # Rate limit exceeded
            retry_after = (cost - tokens) * (window / limit)
            
            return False, {
                'X-RateLimit-Limit': str(limit),
                'X-RateLimit-Remaining': '0',
                'X-RateLimit-Reset': str(int(now + retry_after)),
                'Retry-After': str(int(retry_after))
            }

class RateLimitMiddleware:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.limiter = RateLimiter(self.redis)
        
        # Define limits per endpoint
        self.limits = {
            '/api/v1/auth/login': (5, 300),  # 5 per 5 minutes
            '/api/v1/auth/register': (3, 3600),  # 3 per hour
            '/api/v1/calculations': (100, 60),  # 100 per minute
            'default': (1000, 3600)  # 1000 per hour
        }
    
    async def __call__(self, request: Request, call_next):
        # Get user identifier
        user_id = request.headers.get('X-User-ID')
        ip_address = request.client.host
        
        # Create rate limit key
        identifier = user_id or ip_address
        endpoint = request.url.path
        key = f"rate_limit:{identifier}:{endpoint}"
        
        # Get limits for endpoint
        limit, window = self.limits.get(endpoint, self.limits['default'])
        
        # Check rate limit
        allowed, headers = await self.limiter.check_rate_limit(
            key, limit, window
        )
        
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
                headers=headers
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        for header, value in headers.items():
            response.headers[header] = value
        
        return response
```

### Sentry Integration

```python
# apps/api/app/core/monitoring.py

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
import os

def init_sentry():
    """Initialize Sentry error tracking"""
    
    if not os.getenv("SENTRY_DSN"):
        return
    
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        environment=os.getenv("ENVIRONMENT", "production"),
        
        # Integrations
        integrations=[
            FastApiIntegration(
                transaction_style="endpoint",
                failed_request_status_codes=[400, 403, 404, 405, 406, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 421, 422, 423, 424, 425, 426, 428, 429, 431, 451]
            ),
            SqlalchemyIntegration(),
            RedisIntegration(),
        ],
        
        # Performance monitoring
        traces_sample_rate=0.1,  # 10% of transactions
        profiles_sample_rate=0.1,  # 10% profiling
        
        # Release tracking
        release=os.getenv("GIT_COMMIT_SHA"),
        
        # Filtering
        before_send=before_send_filter,
        
        # Options
        attach_stacktrace=True,
        send_default_pii=False,  # Don't send PII
        request_bodies="medium",
        max_breadcrumbs=50,
    )

def before_send_filter(event, hint):
    """Filter sensitive data before sending to Sentry"""
    
    # Remove sensitive headers
    if 'request' in event and 'headers' in event['request']:
        sensitive_headers = ['authorization', 'cookie', 'x-api-key']
        for header in sensitive_headers:
            event['request']['headers'].pop(header, None)
    
    # Remove sensitive data from extra context
    if 'extra' in event:
        sensitive_keys = ['password', 'token', 'secret', 'api_key']
        for key in sensitive_keys:
            event['extra'].pop(key, None)
    
    return event

# Custom error capturing with context
def capture_error(error: Exception, user_id: Optional[int] = None, **kwargs):
    """Capture error with additional context"""
    
    with sentry_sdk.push_scope() as scope:
        if user_id:
            scope.set_user({"id": user_id})
        
        for key, value in kwargs.items():
            scope.set_extra(key, value)
        
        sentry_sdk.capture_exception(error)
```

### Prometheus Metrics

```python
# apps/api/app/core/metrics.py

from prometheus_client import Counter, Histogram, Gauge, generate_latest
from prometheus_client import REGISTRY
from fastapi import Request, Response
import time
from functools import wraps

# Define metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

active_requests = Gauge(
    'http_requests_active',
    'Active HTTP requests'
)

db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['operation', 'table']
)

cache_hits = Counter(
    'cache_hits_total',
    'Cache hits',
    ['cache_name']
)

cache_misses = Counter(
    'cache_misses_total',
    'Cache misses',
    ['cache_name']
)

external_api_duration = Histogram(
    'external_api_duration_seconds',
    'External API call duration',
    ['api_name', 'endpoint']
)

class MetricsMiddleware:
    async def __call__(self, request: Request, call_next):
        # Track active requests
        active_requests.inc()
        
        # Start timer
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Record metrics
            duration = time.time() - start_time
            
            request_count.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code
            ).inc()
            
            request_duration.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)
            
            return response
            
        finally:
            active_requests.dec()

def track_db_query(operation: str, table: str):
    """Decorator to track database query performance"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start
                db_query_duration.labels(
                    operation=operation,
                    table=table
                ).observe(duration)
        return wrapper
    return decorator

# Metrics endpoint
async def metrics_endpoint():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(REGISTRY),
        media_type="text/plain"
    )
```

### Audit Logging

```python
# apps/api/app/services/audit.py

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.audit import AuditLog
import json

class AuditLogger:
    def __init__(self, db: Session):
        self.db = db
    
    async def log_event(
        self,
        event_type: str,
        user_id: Optional[int],
        resource_type: Optional[str],
        resource_id: Optional[str],
        action: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log an audit event"""
        
        audit_log = AuditLog(
            event_type=event_type,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            details=json.dumps(details) if details else None,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow()
        )
        
        self.db.add(audit_log)
        await self.db.commit()
    
    async def log_login(self, user_id: int, success: bool, ip: str, user_agent: str):
        """Log login attempt"""
        await self.log_event(
            event_type="AUTH",
            user_id=user_id if success else None,
            action="LOGIN_SUCCESS" if success else "LOGIN_FAILURE",
            details={"success": success},
            ip_address=ip,
            user_agent=user_agent
        )
    
    async def log_data_access(
        self,
        user_id: int,
        resource: str,
        action: str,
        ip: str
    ):
        """Log data access"""
        await self.log_event(
            event_type="DATA_ACCESS",
            user_id=user_id,
            resource_type=resource,
            action=action,
            ip_address=ip
        )
```

## 🧪 Security Testing

```python
# tests/security/test_vulnerabilities.py

import pytest
from fastapi.testclient import TestClient

class TestSecurity:
    
    def test_sql_injection(self, client: TestClient):
        """Test SQL injection prevention"""
        response = client.get(
            "/api/v1/users",
            params={"id": "1' OR '1'='1"}
        )
        assert response.status_code != 200
    
    def test_xss_prevention(self, client: TestClient):
        """Test XSS prevention"""
        response = client.post(
            "/api/v1/portfolio",
            json={"name": "<script>alert('XSS')</script>"}
        )
        # Check response doesn't contain unescaped script
        assert "<script>" not in response.text
    
    def test_rate_limiting(self, client: TestClient):
        """Test rate limiting"""
        # Make many requests
        for _ in range(10):
            response = client.post(
                "/api/v1/auth/login",
                json={"email": "test@test.com", "password": "wrong"}
            )
        
        # Should be rate limited
        assert response.status_code == 429
```

## 📈 Success Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Security headers | None | All | 🔴 |
| Error tracking | None | Sentry | 🔴 |
| Metrics collection | None | Prometheus | 🔴 |
| Audit logging | None | Complete | 🔴 |
| Vulnerability scan | None | Automated | 🔴 |

## 🔄 Dependencies

```txt
# Backend
sentry-sdk[fastapi]>=1.30.0
prometheus-client>=0.17.0
python-multipart>=0.0.6
secure>=0.3.0

# Security scanning
bandit>=1.7.0
safety>=2.3.0
```

---

**Next**: Continue with [08-performance-optimization.md](./08-performance-optimization.md)