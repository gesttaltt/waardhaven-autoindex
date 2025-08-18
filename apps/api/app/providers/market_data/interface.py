"""
Market data provider interface and data models.
"""

from abc import abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, List, Optional, Any
import pandas as pd

from ..base import BaseProvider


@dataclass
class PriceData:
    """Historical price data model."""

    symbol: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    adjusted_close: Optional[float] = None


@dataclass
class QuoteData:
    """Real-time quote data model."""

    symbol: str
    price: float
    change: float
    percent_change: float
    volume: int
    timestamp: datetime
    open: float
    high: float
    low: float
    previous_close: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    bid_size: Optional[int] = None
    ask_size: Optional[int] = None
    market_cap: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "symbol": self.symbol,
            "price": self.price,
            "change": self.change,
            "percent_change": self.percent_change,
            "volume": self.volume,
            "timestamp": (
                self.timestamp.isoformat()
                if isinstance(self.timestamp, datetime)
                else self.timestamp
            ),
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "previous_close": self.previous_close,
            "bid": self.bid,
            "ask": self.ask,
            "bid_size": self.bid_size,
            "ask_size": self.ask_size,
            "market_cap": self.market_cap,
        }


@dataclass
class ExchangeRate:
    """Currency exchange rate model."""

    from_currency: str
    to_currency: str
    rate: float
    timestamp: datetime


@dataclass
class TechnicalIndicator:
    """Technical indicator data model."""

    symbol: str
    indicator: str
    value: float
    timestamp: datetime
    parameters: Optional[Dict[str, Any]] = None


class MarketDataProvider(BaseProvider):
    """
    Abstract interface for market data providers.
    All market data providers must implement this interface.
    """

    @abstractmethod
    def fetch_historical_prices(
        self,
        symbols: List[str],
        start_date: date,
        end_date: Optional[date] = None,
        interval: str = "1day",
    ) -> pd.DataFrame:
        """
        Fetch historical price data for multiple symbols.

        Args:
            symbols: List of stock symbols
            start_date: Start date for historical data
            end_date: End date (default: today)
            interval: Time interval (1day, 1hour, etc.)

        Returns:
            DataFrame with MultiIndex (date, symbol) and price columns
        """
        pass

    @abstractmethod
    def get_quotes(self, symbols: List[str]) -> Dict[str, QuoteData]:
        """
        Get real-time quotes for multiple symbols.

        Args:
            symbols: List of stock symbols

        Returns:
            Dictionary mapping symbols to QuoteData
        """
        pass

    @abstractmethod
    def get_exchange_rate(
        self, from_currency: str, to_currency: str = "USD"
    ) -> Optional[ExchangeRate]:
        """
        Get currency exchange rate.

        Args:
            from_currency: Source currency code
            to_currency: Target currency code

        Returns:
            ExchangeRate object or None if not available
        """
        pass

    @abstractmethod
    def validate_symbols(self, symbols: List[str]) -> Dict[str, bool]:
        """
        Validate if symbols are available from provider.

        Args:
            symbols: List of symbols to validate

        Returns:
            Dictionary mapping symbols to availability status
        """
        pass

    @abstractmethod
    def get_technical_indicators(
        self,
        symbol: str,
        indicators: List[str],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **params
    ) -> Dict[str, pd.Series]:
        """
        Get technical indicators for a symbol.

        Args:
            symbol: Stock symbol
            indicators: List of indicator names
            start_date: Start date
            end_date: End date
            **params: Additional parameters for indicators

        Returns:
            Dictionary mapping indicator names to pandas Series
        """
        pass

    def get_api_usage(self) -> Optional[Dict[str, Any]]:
        """
        Get API usage statistics.

        Returns:
            Dictionary with usage stats or None
        """
        return None
