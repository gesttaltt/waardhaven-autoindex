"""
Unit tests for base provider functionality.
"""

import pytest
from unittest.mock import Mock
import time

from app.providers.base import (
    BaseProvider,
    CircuitBreaker,
    RateLimitError,
    APIError,
    CircuitBreakerError,
    ProviderStatus,
    retry_with_backoff,
)


class TestCircuitBreaker:
    """Test circuit breaker functionality."""

    def test_circuit_breaker_opens_after_failures(self):
        """Circuit breaker should open after reaching failure threshold."""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=1)

        # Simulate failures
        for i in range(3):
            with pytest.raises(Exception):
                cb.call(lambda: (_ for _ in ()).throw(Exception("Test error")))

        assert cb.state == "open"

        # Should raise CircuitBreakerError when open
        with pytest.raises(CircuitBreakerError):
            cb.call(lambda: "test")

    def test_circuit_breaker_recovers(self):
        """Circuit breaker should recover after timeout."""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)

        # Open the circuit
        for i in range(2):
            with pytest.raises(Exception):
                cb.call(lambda: (_ for _ in ()).throw(Exception("Test")))

        assert cb.state == "open"

        # Wait for recovery
        time.sleep(0.2)

        # Should attempt half-open
        result = cb.call(lambda: "success")
        assert result == "success"
        assert cb.state == "closed"

    def test_circuit_breaker_resets_on_success(self):
        """Circuit breaker should reset failure count on success."""
        cb = CircuitBreaker(failure_threshold=3)

        # One failure
        with pytest.raises(Exception):
            cb.call(lambda: (_ for _ in ()).throw(Exception("Test")))

        assert cb.failure_count == 1

        # Success should reset
        cb.call(lambda: "success")
        assert cb.failure_count == 0
        assert cb.state == "closed"


class TestRetryWithBackoff:
    """Test retry decorator."""

    def test_retry_on_rate_limit(self):
        """Should retry on rate limit errors."""
        mock_func = Mock(
            side_effect=[RateLimitError("Rate limited", retry_after=0.1), "success"]
        )

        @retry_with_backoff(max_retries=3, base_delay=0.1)
        def test_func():
            return mock_func()

        result = test_func()
        assert result == "success"
        assert mock_func.call_count == 2

    def test_retry_on_server_error(self):
        """Should retry on 5xx errors."""
        mock_func = Mock(
            side_effect=[
                APIError("Server error", status_code=500),
                APIError("Server error", status_code=503),
                "success",
            ]
        )

        @retry_with_backoff(max_retries=3, base_delay=0.01)
        def test_func():
            return mock_func()

        result = test_func()
        assert result == "success"
        assert mock_func.call_count == 3

    def test_no_retry_on_client_error(self):
        """Should not retry on 4xx errors."""
        mock_func = Mock(side_effect=APIError("Bad request", status_code=400))

        @retry_with_backoff(max_retries=3)
        def test_func():
            return mock_func()

        with pytest.raises(APIError) as exc_info:
            test_func()

        assert exc_info.value.status_code == 400
        assert mock_func.call_count == 1

    def test_max_retries_exhausted(self):
        """Should raise after max retries."""
        mock_func = Mock(side_effect=RateLimitError("Rate limited"))

        @retry_with_backoff(max_retries=2, base_delay=0.01)
        def test_func():
            return mock_func()

        with pytest.raises(RateLimitError):
            test_func()

        assert mock_func.call_count == 2


class MockProvider(BaseProvider):
    """Mock provider for testing base functionality."""

    def get_provider_name(self) -> str:
        return "MockProvider"

    def validate_config(self) -> bool:
        return bool(self.api_key)

    def health_check(self) -> ProviderStatus:
        return ProviderStatus.HEALTHY

    def _execute_request(self, endpoint: str, params=None):
        return {"endpoint": endpoint, "params": params}


class TestBaseProvider:
    """Test base provider functionality."""

    def test_provider_initialization(self):
        """Test provider initialization."""
        provider = MockProvider(api_key="test_key", cache_enabled=True)

        assert provider.api_key == "test_key"
        assert provider.cache_enabled is True
        assert provider.get_provider_name() == "MockProvider"
        assert provider.validate_config() is True

    def test_provider_stats(self):
        """Test provider statistics tracking."""
        provider = MockProvider(api_key="test_key")

        # Initial stats
        stats = provider.get_stats()
        assert stats["provider"] == "MockProvider"
        assert stats["requests"] == 0
        assert stats["successes"] == 0
        assert stats["errors"] == 0

        # Make successful request
        provider._record_request()
        provider._record_success()

        stats = provider.get_stats()
        assert stats["requests"] == 1
        assert stats["successes"] == 1
        assert stats["errors"] == 0

        # Record error
        provider._record_request()
        provider._record_error()

        stats = provider.get_stats()
        assert stats["requests"] == 2
        assert stats["successes"] == 1
        assert stats["errors"] == 1
        assert stats["error_rate"] == 0.5

    def test_make_request_with_circuit_breaker(self):
        """Test make_request integrates with circuit breaker."""
        provider = MockProvider(api_key="test_key")

        # Successful request
        result = provider.make_request("test_endpoint", {"param": "value"})
        assert result["endpoint"] == "test_endpoint"
        assert result["params"]["param"] == "value"

        # Verify stats updated
        stats = provider.get_stats()
        assert stats["requests"] == 1
        assert stats["successes"] == 1

    def test_provider_without_api_key(self):
        """Test provider behavior without API key."""
        provider = MockProvider()

        assert provider.api_key is None
        assert provider.validate_config() is False

        # Should still be able to get stats
        stats = provider.get_stats()
        assert stats["provider"] == "MockProvider"
