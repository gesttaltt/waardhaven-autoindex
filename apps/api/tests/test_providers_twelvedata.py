"""
Unit tests for TwelveData provider.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import date
import pandas as pd

from app.providers.market_data import TwelveDataProvider, QuoteData, ExchangeRate
from app.providers.base import APIError, ProviderStatus


@pytest.fixture
def mock_td_client():
    """Mock TDClient for testing."""
    with patch("app.providers.market_data.twelvedata.TDClient") as mock_client:
        yield mock_client


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    with patch("app.providers.market_data.twelvedata.get_redis_client") as mock_redis:
        redis_instance = MagicMock()
        redis_instance.is_connected = True
        redis_instance.get.return_value = None
        redis_instance.set.return_value = True
        mock_redis.return_value = redis_instance
        yield redis_instance


@pytest.fixture
def provider(mock_td_client, mock_redis):
    """Create TwelveData provider with mocked dependencies."""
    with patch("app.providers.market_data.twelvedata.settings") as mock_settings:
        mock_settings.TWELVEDATA_API_KEY = "test_api_key"
        mock_settings.TWELVEDATA_RATE_LIMIT = 8
        mock_settings.ENABLE_MARKET_DATA_CACHE = True

        provider = TwelveDataProvider(api_key="test_api_key")
        return provider


class TestTwelveDataProvider:
    """Test TwelveData provider functionality."""

    def test_provider_initialization(self, provider):
        """Test provider initializes correctly."""
        assert provider.get_provider_name() == "TwelveData"
        assert provider.validate_config() is True
        assert provider.api_key == "test_api_key"

    def test_provider_without_api_key(self, mock_redis):
        """Test provider raises error without API key."""
        with patch("app.providers.market_data.twelvedata.settings") as mock_settings:
            mock_settings.TWELVEDATA_API_KEY = ""

            with pytest.raises(ValueError, match="API key not configured"):
                TwelveDataProvider()

    def test_fetch_historical_prices_success(self, provider):
        """Test successful historical price fetching."""
        # Mock API response
        mock_ts = MagicMock()
        mock_df = pd.DataFrame(
            {
                "close": [150.0, 151.0, 152.0],
                "open": [149.0, 150.5, 151.5],
                "high": [151.0, 152.0, 153.0],
                "low": [148.5, 150.0, 151.0],
                "volume": [1000000, 1100000, 1200000],
            },
            index=pd.date_range("2024-01-01", periods=3),
        )

        mock_ts.as_pandas.return_value = mock_df
        provider.client.time_series.return_value = mock_ts

        # Fetch prices
        result = provider.fetch_historical_prices(
            symbols=["AAPL"], start_date=date(2024, 1, 1), end_date=date(2024, 1, 3)
        )

        assert not result.empty
        assert len(result) == 3
        assert "AAPL" in result.columns.get_level_values(0)

        # Verify API was called
        provider.client.time_series.assert_called_once()

    def test_fetch_historical_prices_with_cache(self, provider, mock_redis):
        """Test historical prices are cached and retrieved."""
        # Setup cache hit
        cached_data = pd.DataFrame(
            {"Close": [150.0, 151.0], "Open": [149.0, 150.5]},
            index=["2024-01-01", "2024-01-02"],
        ).to_json()

        mock_redis.get.return_value = cached_data

        # Fetch prices
        result = provider.fetch_historical_prices(
            symbols=["AAPL"], start_date=date(2024, 1, 1), end_date=date(2024, 1, 2)
        )

        assert not result.empty
        assert "AAPL" in result.columns.get_level_values(0)

        # Verify API was NOT called (cache hit)
        provider.client.time_series.assert_not_called()

    def test_fetch_historical_prices_batch(self, provider):
        """Test batch fetching for multiple symbols."""
        # Mock batch response
        mock_ts = MagicMock()
        batch_data = {
            "AAPL": {
                "values": [
                    {
                        "datetime": "2024-01-01",
                        "close": 150.0,
                        "open": 149.0,
                        "high": 151.0,
                        "low": 148.5,
                        "volume": 1000000,
                    }
                ]
            },
            "MSFT": {
                "values": [
                    {
                        "datetime": "2024-01-01",
                        "close": 380.0,
                        "open": 378.0,
                        "high": 381.0,
                        "low": 377.0,
                        "volume": 2000000,
                    }
                ]
            },
        }
        mock_ts.as_json.return_value = batch_data
        provider.client.time_series.return_value = mock_ts

        # Fetch prices
        result = provider.fetch_historical_prices(
            symbols=["AAPL", "MSFT"],
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 1),
        )

        assert not result.empty
        assert "AAPL" in result.columns.get_level_values(0)
        assert "MSFT" in result.columns.get_level_values(0)

    def test_get_quotes_success(self, provider):
        """Test successful quote fetching."""
        # Mock quote response
        mock_quote = MagicMock()
        quote_data = {
            "symbol": "AAPL",
            "close": 150.0,
            "change": 2.5,
            "percent_change": 1.69,
            "volume": 50000000,
            "timestamp": 1704067200,
            "open": 148.0,
            "high": 151.0,
            "low": 147.5,
            "previous_close": 147.5,
        }
        mock_quote.as_json.return_value = quote_data
        provider.client.quote.return_value = mock_quote

        # Get quotes
        quotes = provider.get_quotes(["AAPL"])

        assert "AAPL" in quotes
        assert isinstance(quotes["AAPL"], QuoteData)
        assert quotes["AAPL"].price == 150.0
        assert quotes["AAPL"].symbol == "AAPL"

    def test_get_quotes_batch(self, provider):
        """Test batch quote fetching."""
        # Mock batch quote response
        mock_quote = MagicMock()
        batch_data = {
            "AAPL": {
                "symbol": "AAPL",
                "close": 150.0,
                "change": 2.5,
                "percent_change": 1.69,
                "volume": 50000000,
                "timestamp": 1704067200,
                "open": 148.0,
                "high": 151.0,
                "low": 147.5,
                "previous_close": 147.5,
            },
            "MSFT": {
                "symbol": "MSFT",
                "close": 380.0,
                "change": 5.0,
                "percent_change": 1.33,
                "volume": 30000000,
                "timestamp": 1704067200,
                "open": 376.0,
                "high": 381.0,
                "low": 375.0,
                "previous_close": 375.0,
            },
        }
        mock_quote.as_json.return_value = batch_data
        provider.client.quote.return_value = mock_quote

        # Get quotes
        quotes = provider.get_quotes(["AAPL", "MSFT"])

        assert len(quotes) == 2
        assert "AAPL" in quotes
        assert "MSFT" in quotes
        assert quotes["AAPL"].price == 150.0
        assert quotes["MSFT"].price == 380.0

    def test_get_exchange_rate_success(self, provider):
        """Test successful exchange rate fetching."""
        # Mock exchange rate response
        mock_rate = MagicMock()
        rate_data = {"symbol": "EUR/USD", "rate": 1.0856, "timestamp": 1704067200}
        mock_rate.as_json.return_value = rate_data
        provider.client.exchange_rate.return_value = mock_rate

        # Get exchange rate
        rate = provider.get_exchange_rate("EUR", "USD")

        assert isinstance(rate, ExchangeRate)
        assert rate.from_currency == "EUR"
        assert rate.to_currency == "USD"
        assert rate.rate == 1.0856

    def test_get_exchange_rate_same_currency(self, provider):
        """Test exchange rate for same currency returns 1.0."""
        rate = provider.get_exchange_rate("USD", "USD")

        assert rate.rate == 1.0
        assert rate.from_currency == "USD"
        assert rate.to_currency == "USD"

    def test_validate_symbols(self, provider):
        """Test symbol validation."""

        # Mock validation responses
        def time_series_side_effect(symbol, **kwargs):
            mock_ts = MagicMock()
            if symbol == "AAPL":
                mock_ts.as_json.return_value = {"values": [{"close": 150}]}
            else:
                mock_ts.as_json.return_value = None
            return mock_ts

        provider.client.time_series.side_effect = time_series_side_effect

        # Validate symbols
        results = provider.validate_symbols(["AAPL", "INVALID"])

        assert results["AAPL"] is True
        assert results["INVALID"] is False

    def test_rate_limiter(self, provider):
        """Test rate limiter functionality."""
        # Test that rate limiter tracks credits
        provider.rate_limiter.credits_per_minute = 2

        # First request should pass
        provider.rate_limiter.wait_if_needed(1)
        assert len(provider.rate_limiter.credits_used) == 1

        # Second request should pass
        provider.rate_limiter.wait_if_needed(1)
        assert len(provider.rate_limiter.credits_used) == 2

        # Third request should wait (mocked to be fast)
        with patch("time.sleep") as mock_sleep:
            provider.rate_limiter.wait_if_needed(1)
            mock_sleep.assert_called_once()

    def test_health_check(self, provider):
        """Test health check functionality."""
        # Mock API usage response
        mock_usage = MagicMock()
        mock_usage.as_json.return_value = {"current_usage": 100, "plan_limit": 800}
        provider.client.api_usage.return_value = mock_usage

        # Check health
        status = provider.health_check()

        assert status == ProviderStatus.HEALTHY
        provider.client.api_usage.assert_called_once()

    def test_api_error_handling(self, provider):
        """Test API error handling."""
        from twelvedata.exceptions import TwelveDataError

        # Mock API error
        provider.client.time_series.side_effect = TwelveDataError("API Error")

        # Should raise APIError
        with pytest.raises(APIError, match="TwelveData API error"):
            provider.fetch_historical_prices(
                symbols=["AAPL"], start_date=date(2024, 1, 1)
            )

    def test_cache_key_generation(self, provider):
        """Test cache key generation."""
        key = provider._get_cache_key(
            "prices", symbol="AAPL", start="2024-01-01", end="2024-01-31"
        )

        assert "twelvedata:prices" in key
        assert "symbol:AAPL" in key
        assert "start:2024-01-01" in key
        assert "end:2024-01-31" in key

    def test_empty_symbols_handling(self, provider):
        """Test handling of empty symbol lists."""
        # Empty symbols should return empty DataFrame
        result = provider.fetch_historical_prices(
            symbols=[], start_date=date(2024, 1, 1)
        )

        assert result.empty

        # Empty quotes should return empty dict
        quotes = provider.get_quotes([])
        assert quotes == {}

    def test_process_price_data_validation(self, provider):
        """Test price data validation and cleaning."""
        # Create test data with invalid values
        df = pd.DataFrame(
            {
                "close": [150.0, -10.0, None, 200.0],  # Invalid: negative and None
                "open": [149.0, 151.0, 152.0, 199.0],
                "high": [151.0, 152.0, 153.0, 201.0],
                "low": [148.5, 150.0, 151.0, 198.0],
                "volume": [1000000, 1100000, 1200000, 1300000],
            }
        )

        # Process data
        cleaned = provider._process_price_data(df, "TEST")

        # Should remove invalid rows
        assert len(cleaned) == 2  # Only rows with valid positive close prices
        assert all(cleaned["Close"] > 0)
        assert cleaned["Close"].notna().all()
