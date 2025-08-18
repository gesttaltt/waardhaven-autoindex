# Base Provider Documentation

## Overview
The Base Provider is an abstract class that implements common functionality for all external data providers, including circuit breakers, retry logic, rate limiting, and statistics tracking.

## Location
`app/providers/base.py`

## Class Hierarchy
```
BaseProvider (Abstract)
├── TwelveDataProvider (Market Data)
└── MarketauxProvider (News & Sentiment)
└── Future Providers...
```

## Core Components

### 1. Circuit Breaker
Prevents cascade failures by temporarily blocking requests after consecutive failures.

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = "closed"  # closed, open, half-open
```

**States:**
- **CLOSED**: Normal operation, requests pass through
- **OPEN**: Failures exceeded threshold, requests blocked
- **HALF-OPEN**: Testing recovery after timeout

**Configuration:**
- Failure threshold: 5 consecutive failures
- Recovery timeout: 60 seconds
- Auto-recovery: Attempts half-open after timeout

### 2. Retry Logic
Implements exponential backoff for transient failures.

```python
@retry_with_backoff(max_retries=3, base_delay=1.0)
def make_request(self, endpoint, params):
    # Automatic retry with exponential backoff
```

**Features:**
- Max retries: 3 attempts
- Exponential backoff: 1s → 2s → 4s
- Rate limit aware: Uses Retry-After header
- Smart handling: No retry on 4xx errors

### 3. Provider Statistics
Tracks provider performance and health.

```python
def get_stats(self) -> Dict[str, Any]:
    return {
        "provider": self.get_provider_name(),
        "requests": self._request_count,
        "successes": self._success_count,
        "errors": self._error_count,
        "error_rate": self._error_count / max(self._request_count, 1),
        "circuit_breaker_state": self.circuit_breaker.state,
        "last_request": self._last_request_time
    }
```

## Abstract Methods

Every provider must implement these methods:

### 1. get_provider_name()
Returns the provider's name for identification.

```python
@abstractmethod
def get_provider_name(self) -> str:
    """Return provider name."""
    pass
```

### 2. validate_config()
Validates provider configuration (API keys, settings).

```python
@abstractmethod
def validate_config(self) -> bool:
    """Validate provider configuration."""
    pass
```

### 3. health_check()
Checks provider health status.

```python
@abstractmethod
def health_check(self) -> ProviderStatus:
    """Check provider health."""
    pass
```

### 4. _execute_request()
Executes the actual API request.

```python
@abstractmethod
def _execute_request(self, endpoint: str, params: Optional[Dict] = None) -> Any:
    """Execute API request."""
    pass
```

## Exception Hierarchy

```python
ProviderError (Base)
├── RateLimitError
│   └── retry_after: int
├── APIError
│   └── status_code: int
└── CircuitBreakerError
```

### Usage Example
```python
try:
    result = provider.make_request("/endpoint", params)
except RateLimitError as e:
    # Wait and retry after e.retry_after seconds
    time.sleep(e.retry_after)
except CircuitBreakerError:
    # Use cached data or fallback
    result = get_from_cache()
except APIError as e:
    if e.status_code == 404:
        # Handle not found
    else:
        # Handle other API errors
```

## Provider Status Enum

```python
class ProviderStatus(Enum):
    HEALTHY = "healthy"      # All systems operational
    DEGRADED = "degraded"     # Partial functionality
    UNHEALTHY = "unhealthy"   # Major issues
    UNKNOWN = "unknown"       # Status cannot be determined
```

## Implementation Example

```python
class MyProvider(BaseProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key, cache_enabled=True)
        self.base_url = "https://api.example.com"
    
    def get_provider_name(self) -> str:
        return "MyProvider"
    
    def validate_config(self) -> bool:
        return bool(self.api_key)
    
    def health_check(self) -> ProviderStatus:
        try:
            response = self._execute_request("/health")
            return ProviderStatus.HEALTHY if response else ProviderStatus.DEGRADED
        except Exception:
            return ProviderStatus.UNHEALTHY
    
    def _execute_request(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        response = requests.get(
            f"{self.base_url}{endpoint}",
            params=params,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        response.raise_for_status()
        return response.json()
```

## Best Practices

### 1. Always Use make_request()
Never call `_execute_request()` directly. Use `make_request()` to benefit from retry logic and circuit breaker.

```python
# Good
result = provider.make_request("/data", {"symbol": "AAPL"})

# Bad
result = provider._execute_request("/data", {"symbol": "AAPL"})
```

### 2. Handle All Exception Types
Always handle provider-specific exceptions:

```python
try:
    data = provider.make_request(endpoint, params)
except RateLimitError as e:
    logger.warning(f"Rate limited, retry after {e.retry_after}s")
except CircuitBreakerError:
    logger.error("Circuit breaker open, using fallback")
except APIError as e:
    logger.error(f"API error {e.status_code}: {e}")
except ProviderError as e:
    logger.error(f"Provider error: {e}")
```

### 3. Monitor Provider Health
Regularly check provider health:

```python
status = provider.health_check()
if status == ProviderStatus.UNHEALTHY:
    # Switch to backup provider or alert
    notify_ops_team()
```

### 4. Track Statistics
Monitor provider performance:

```python
stats = provider.get_stats()
if stats["error_rate"] > 0.05:  # 5% error rate
    logger.warning(f"High error rate for {stats['provider']}: {stats['error_rate']:.2%}")
```

## Configuration

### Environment Variables
```env
# Provider configuration
PROVIDER_CIRCUIT_BREAKER_THRESHOLD=5
PROVIDER_CIRCUIT_BREAKER_TIMEOUT=60
PROVIDER_MAX_RETRIES=3
PROVIDER_RETRY_BASE_DELAY=1.0
```

### Python Configuration
```python
from app.providers.base import BaseProvider

class CustomProvider(BaseProvider):
    def __init__(self):
        super().__init__(
            api_key="your_key",
            cache_enabled=True
        )
        # Custom circuit breaker settings
        self.circuit_breaker.failure_threshold = 10
        self.circuit_breaker.recovery_timeout = 120
```

## Testing

### Unit Test Example
```python
def test_circuit_breaker_opens():
    provider = MockProvider()
    
    # Simulate failures
    for _ in range(5):
        with pytest.raises(Exception):
            provider.make_request("/fail", {})
    
    # Circuit should be open
    assert provider.circuit_breaker.state == "open"
    
    # Next request should raise CircuitBreakerError
    with pytest.raises(CircuitBreakerError):
        provider.make_request("/any", {})
```

### Mocking for Tests
```python
@patch('app.providers.base.BaseProvider._execute_request')
def test_with_mock(mock_execute):
    mock_execute.return_value = {"data": "test"}
    provider = MyProvider("test_key")
    result = provider.make_request("/test", {})
    assert result["data"] == "test"
```

## Monitoring

### Metrics to Track
- Request count per provider
- Success/failure rates
- Circuit breaker state changes
- Average response time
- Rate limit hits

### Logging
```python
import logging

logger = logging.getLogger(__name__)

# Log circuit breaker state changes
logger.warning(f"Circuit breaker opened for {provider.get_provider_name()}")

# Log rate limits
logger.info(f"Rate limited, waiting {retry_after}s")

# Log errors with context
logger.error(f"Provider error", extra={
    "provider": provider.get_provider_name(),
    "endpoint": endpoint,
    "error": str(error)
})
```

## Performance Considerations

### Caching
Providers should implement caching to reduce API calls:

```python
def _get_from_cache(self, key: str) -> Optional[Any]:
    if not self.cache_enabled:
        return None
    return cache.get(key)

def _set_cache(self, key: str, value: Any, ttl: int):
    if self.cache_enabled:
        cache.set(key, value, ttl)
```

### Batch Operations
Optimize by batching requests when possible:

```python
# Instead of multiple single requests
for symbol in symbols:
    data = provider.get_data(symbol)

# Use batch operation
data = provider.get_batch_data(symbols)
```

## Troubleshooting

### Circuit Breaker Always Open
- Check failure threshold setting
- Verify recovery timeout
- Review error logs for root cause
- Ensure provider health check works

### High Error Rate
- Check API key validity
- Verify network connectivity
- Review rate limits
- Check provider service status

### Slow Response Times
- Enable caching
- Use batch operations
- Check network latency
- Review retry settings