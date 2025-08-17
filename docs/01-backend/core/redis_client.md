# Redis Client Module

## Overview
The Redis client module (`app/core/redis_client.py`) provides a robust Redis connection manager with connection pooling, error handling, and graceful fallback.

## Location
`apps/api/app/core/redis_client.py`

## Core Components

### RedisClient Class
```python
class RedisClient:
    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self.client: Optional[redis.Redis] = None
        self.is_connected = False
```

### Connection Pool Configuration
```python
pool = redis.ConnectionPool.from_url(
    redis_url,
    max_connections=50,
    decode_responses=True,
    socket_keepalive=True,
    socket_keepalive_options={
        1: 1,  # TCP_KEEPIDLE
        2: 1,  # TCP_KEEPINTVL
        3: 5,  # TCP_KEEPCNT
    }
)
```

## Key Features

### Connection Management
- Automatic connection pooling (50 max connections)
- Keep-alive for persistent connections
- Health check functionality
- Graceful degradation when Redis unavailable

### Error Handling
```python
try:
    self.client.ping()
    self.is_connected = True
except (redis.ConnectionError, redis.TimeoutError):
    self.client = None
    self.is_connected = False
```

## Core Methods

### get(key: str) -> Optional[Any]
Retrieve value from cache with automatic JSON deserialization.

### set(key: str, value: Any, expire: Optional[Union[int, timedelta]])
Store value with optional expiration, automatic JSON serialization.

### delete(key: str) -> bool
Remove key from cache.

### exists(key: str) -> bool
Check if key exists in cache.

### expire(key: str, seconds: int) -> bool
Set/update expiration time for a key.

### flush_pattern(pattern: str) -> int
Delete all keys matching pattern (e.g., "user:*").

### health_check() -> bool
Test Redis connection status.

## Usage Examples

### Basic Operations
```python
from app.core.redis_client import get_redis_client

redis = get_redis_client()

# Set value with TTL
redis.set("user:123", {"name": "John"}, expire=300)

# Get value
user_data = redis.get("user:123")

# Check existence
if redis.exists("user:123"):
    print("User cached")

# Delete
redis.delete("user:123")
```

### Pattern Operations
```python
# Delete all user cache entries
count = redis.flush_pattern("user:*")
print(f"Deleted {count} user cache entries")
```

### Health Monitoring
```python
if redis.health_check():
    print("Redis is healthy")
else:
    print("Redis is down, running without cache")
```

## Connection Pooling

### Pool Settings
- **max_connections**: 50 concurrent connections
- **decode_responses**: Automatic string decoding
- **socket_keepalive**: Prevent idle disconnections

### Keep-Alive Configuration
- TCP_KEEPIDLE: 1 second
- TCP_KEEPINTVL: 1 second  
- TCP_KEEPCNT: 5 probes

## Error Handling Strategies

### Connection Failures
- Returns None for get operations
- Returns False for set/delete operations
- Logs warning but doesn't crash app

### Graceful Fallback
```python
if not redis.is_connected:
    # Fallback to direct database queries
    return fetch_from_database()
```

## JSON Serialization

### Automatic Handling
- Complex objects serialized to JSON on set
- JSON strings deserialized on get
- Raw strings passed through unchanged

### Custom Objects
```python
# Storing complex data
redis.set("config", {
    "weights": [0.3, 0.3, 0.4],
    "timestamp": datetime.now().isoformat()
})
```

## TTL Management

### Expiration Options
```python
# Using seconds
redis.set("key", "value", expire=300)  # 5 minutes

# Using timedelta
from datetime import timedelta
redis.set("key", "value", expire=timedelta(hours=1))

# Update expiration
redis.expire("key", 600)  # 10 minutes
```

## Pattern Matching

### Supported Patterns
- `user:*` - All user keys
- `cache:index:*` - All index cache
- `*:2024-*` - Date-based patterns

### Bulk Operations
```python
# Clear specific cache types
redis.flush_pattern("index:*")
redis.flush_pattern("market:*")
redis.flush_pattern("user:123:*")
```

## Performance Considerations

### Connection Pool Benefits
- Reuses existing connections
- Reduces connection overhead
- Handles concurrent requests efficiently

### Best Practices
1. Use appropriate TTLs
2. Implement cache warming
3. Monitor memory usage
4. Use pattern deletion carefully (can be slow)

## Monitoring

### Key Metrics
```python
# Get Redis info
info = redis.client.info() if redis.is_connected else {}

# Memory usage
used_memory = info.get('used_memory_human')

# Connected clients
connected_clients = info.get('connected_clients')

# Operations per second
ops_per_sec = info.get('instantaneous_ops_per_sec')
```

## Configuration

### Environment Variables
- `REDIS_URL`: Connection string (redis://localhost:6379/0)
- `CACHE_TTL_SECONDS`: Default short TTL (300)
- `CACHE_TTL_LONG_SECONDS`: Default long TTL (3600)

### Database Selection
```python
# Use different databases for different purposes
redis://localhost:6379/0  # Cache
redis://localhost:6379/1  # Celery broker
redis://localhost:6379/2  # Sessions
```

## Integration Points

### Cache Utils
Used by `cache_utils.py` for decorator-based caching.

### Celery
Shares Redis instance for task queue broker/backend.

### API Routes
Direct usage in performance-critical endpoints.

## Error Recovery

### Automatic Reconnection
```python
def health_check(self):
    try:
        self.client.ping()
        self.is_connected = True
        return True
    except Exception:
        self.is_connected = False
        return False
```

### Circuit Breaker Pattern
Consider implementing circuit breaker for production:
```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure = None
```

## Security Considerations

### Connection Security
- Use Redis AUTH in production
- Enable SSL/TLS for remote connections
- Restrict network access

### Data Security
- Don't store sensitive data unencrypted
- Set appropriate TTLs
- Implement access controls

## Dependencies
- `redis==5.0.7`: Redis Python client
- `hiredis==2.3.2`: C parser for performance

## Related Modules
- `cache_utils.py`: Caching decorators
- `celery_app.py`: Task queue configuration
- All routers: Cache integration