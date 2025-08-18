"""Unit tests for performance calculation service."""

import pytest
import numpy as np
from datetime import date

from app.services.performance import PerformanceCalculator, calculate_portfolio_metrics
from app.models import IndexValue, Asset, Price


class TestPerformanceCalculator:
    """Test performance calculation methods."""

    @pytest.mark.unit
    def test_sharpe_ratio_calculation(self):
        """Test Sharpe ratio calculation."""
        calc = PerformanceCalculator()

        # Test with positive returns
        returns = np.array([0.01, 0.02, -0.01, 0.015, 0.005])
        sharpe = calc.sharpe_ratio(returns, risk_free_rate=0.02)

        # Sharpe ratio should be calculated correctly
        assert isinstance(sharpe, float)
        assert not np.isnan(sharpe)

        # Test with zero volatility (should return 0)
        constant_returns = np.array([0.01, 0.01, 0.01, 0.01])
        sharpe_zero = calc.sharpe_ratio(constant_returns)
        assert sharpe_zero == 0.0

        # Test with empty returns
        empty_sharpe = calc.sharpe_ratio(np.array([]))
        assert empty_sharpe == 0.0

    @pytest.mark.unit
    def test_sortino_ratio_calculation(self):
        """Test Sortino ratio calculation."""
        calc = PerformanceCalculator()

        # Test with mixed returns
        returns = np.array([0.02, -0.01, 0.03, -0.02, 0.01])
        sortino = calc.sortino_ratio(returns, risk_free_rate=0.02)

        assert isinstance(sortino, float)
        assert not np.isnan(sortino)

        # Test with only positive returns (no downside)
        positive_returns = np.array([0.01, 0.02, 0.015, 0.025])
        sortino_positive = calc.sortino_ratio(positive_returns)
        # Should be very high or infinite (we cap it)
        assert sortino_positive > 0

    @pytest.mark.unit
    def test_max_drawdown_calculation(self):
        """Test maximum drawdown calculation."""
        calc = PerformanceCalculator()

        # Test with price series that has clear drawdown
        prices = [100, 110, 120, 100, 90, 95, 100, 110]
        max_dd, peak_idx, trough_idx = calc.max_drawdown(prices)

        # Maximum drawdown should be from 120 to 90
        expected_dd = ((90 - 120) / 120) * 100
        assert abs(max_dd - expected_dd) < 0.01
        assert peak_idx == 2  # Index of 120
        assert trough_idx == 4  # Index of 90

        # Test with increasing prices (no drawdown)
        increasing_prices = [100, 110, 120, 130, 140]
        max_dd_none, _, _ = calc.max_drawdown(increasing_prices)
        assert max_dd_none == 0.0

    @pytest.mark.unit
    def test_current_drawdown_calculation(self, test_db):
        """Test current drawdown calculation."""
        # Create index values with drawdown
        values = [
            IndexValue(date=date(2024, 1, 1), value=100),
            IndexValue(date=date(2024, 1, 2), value=110),
            IndexValue(date=date(2024, 1, 3), value=120),  # Peak
            IndexValue(date=date(2024, 1, 4), value=115),
            IndexValue(date=date(2024, 1, 5), value=108),  # Current
        ]
        for v in values:
            test_db.add(v)
        test_db.commit()

        # Calculate metrics
        metrics = calculate_portfolio_metrics(test_db)

        # Current drawdown should be from peak (120) to current (108)
        expected_current_dd = ((108 - 120) / 120) * 100
        assert "current_drawdown" in metrics
        assert abs(metrics["current_drawdown"] - expected_current_dd) < 0.1

    @pytest.mark.unit
    def test_correlation_calculation(self, test_db, sample_assets):
        """Test S&P 500 correlation calculation."""
        # Create correlated index and benchmark data
        dates = [date(2024, 1, i) for i in range(1, 11)]

        # Index values with some correlation to benchmark
        index_values = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109]
        benchmark_values = [450, 452, 451, 454, 456, 455, 457, 459, 458, 460]

        for i, d in enumerate(dates):
            test_db.add(IndexValue(date=d, value=index_values[i]))

        # Add S&P 500 asset and prices
        sp500 = test_db.query(Asset).filter(Asset.symbol == "SPY").first()
        if not sp500:
            sp500 = Asset(symbol="SPY", name="S&P 500", sector="Benchmark")
            test_db.add(sp500)
            test_db.commit()
            test_db.refresh(sp500)

        for i, d in enumerate(dates):
            test_db.add(
                Price(
                    asset_id=sp500.id, date=d, close=benchmark_values[i], volume=1000000
                )
            )
        test_db.commit()

        # Calculate metrics
        metrics = calculate_portfolio_metrics(test_db)

        # Should have positive correlation
        assert "correlation_sp500" in metrics
        assert 0 < metrics["correlation_sp500"] <= 1.0

    @pytest.mark.unit
    def test_volatility_calculation(self):
        """Test volatility calculation."""
        calc = PerformanceCalculator()

        # Test with known volatility
        returns = np.array([0.01, -0.01, 0.02, -0.02, 0.015, -0.015])
        volatility = calc.volatility(returns, annualized=False)

        # Should match standard deviation
        expected_vol = np.std(returns)
        assert abs(volatility - expected_vol) < 0.0001

        # Test annualized volatility
        ann_volatility = calc.volatility(returns, annualized=True)
        assert ann_volatility > volatility  # Annualized should be larger
        assert abs(ann_volatility - volatility * np.sqrt(252)) < 0.0001

    @pytest.mark.unit
    def test_beta_calculation(self):
        """Test beta calculation."""
        calc = PerformanceCalculator()

        # Portfolio that moves exactly with market has beta = 1
        market_returns = np.array([0.01, -0.02, 0.03, -0.01, 0.02])
        portfolio_returns = market_returns.copy()

        beta = calc.beta(portfolio_returns, market_returns)
        assert abs(beta - 1.0) < 0.01

        # Portfolio that moves opposite to market has negative beta
        inverse_returns = -market_returns
        negative_beta = calc.beta(inverse_returns, market_returns)
        assert negative_beta < 0

        # Portfolio with double volatility has beta ~= 2
        double_returns = market_returns * 2
        double_beta = calc.beta(double_returns, market_returns)
        assert abs(double_beta - 2.0) < 0.01

    @pytest.mark.unit
    def test_information_ratio(self):
        """Test information ratio calculation."""
        calc = PerformanceCalculator()

        # Portfolio returns
        portfolio = np.array([0.12, 0.08, 0.15, 0.10, 0.09])
        # Benchmark returns
        benchmark = np.array([0.10, 0.09, 0.11, 0.08, 0.10])

        ir = calc.information_ratio(portfolio, benchmark)

        # Should be positive if portfolio outperforms
        assert ir > 0
        assert isinstance(ir, float)
        assert not np.isnan(ir)


class TestPortfolioMetrics:
    """Test complete portfolio metrics calculation."""

    @pytest.mark.integration
    def test_complete_metrics_calculation(self, test_db, sample_assets):
        """Test calculation of all portfolio metrics."""
        # Create comprehensive test data
        dates = [date(2024, 1, i) for i in range(1, 31)]  # 30 days

        # Create index values with realistic pattern
        np.random.seed(42)
        base_value = 100
        values = [base_value]

        for _ in range(29):
            # Random walk with slight upward drift
            change = np.random.normal(0.002, 0.01)  # 0.2% daily return, 1% volatility
            new_value = values[-1] * (1 + change)
            values.append(new_value)

        for i, d in enumerate(dates):
            test_db.add(IndexValue(date=d, value=values[i]))

        # Add benchmark data (S&P 500)
        sp500 = Asset(symbol="SPY", name="S&P 500", sector="Benchmark")
        test_db.add(sp500)
        test_db.commit()
        test_db.refresh(sp500)

        benchmark_values = [450]
        for _ in range(29):
            change = np.random.normal(0.001, 0.008)  # Slightly different pattern
            benchmark_values.append(benchmark_values[-1] * (1 + change))

        for i, d in enumerate(dates):
            test_db.add(
                Price(
                    asset_id=sp500.id, date=d, close=benchmark_values[i], volume=1000000
                )
            )
        test_db.commit()

        # Calculate all metrics
        metrics = calculate_portfolio_metrics(test_db)

        # Verify all expected metrics are present
        expected_metrics = [
            "total_return",
            "annualized_return",
            "volatility",
            "sharpe_ratio",
            "sortino_ratio",
            "max_drawdown",
            "current_drawdown",
            "correlation_sp500",
            "beta",
            "information_ratio",
            "calmar_ratio",
        ]

        for metric in expected_metrics:
            assert metric in metrics, f"Missing metric: {metric}"
            assert metrics[metric] is not None
            assert not np.isnan(metrics[metric])

        # Sanity checks on values
        assert -100 <= metrics["total_return"] <= 1000  # Reasonable return range
        assert 0 <= metrics["volatility"] <= 1  # Volatility as decimal
        assert -100 <= metrics["max_drawdown"] <= 0  # Drawdown is negative
        assert -1 <= metrics["correlation_sp500"] <= 1  # Correlation bounds

    @pytest.mark.integration
    def test_metrics_with_missing_benchmark(self, test_db):
        """Test metrics calculation when benchmark data is missing."""
        # Create only index values, no S&P 500 data
        dates = [date(2024, 1, i) for i in range(1, 11)]

        for i, d in enumerate(dates):
            test_db.add(IndexValue(date=d, value=100 + i))
        test_db.commit()

        # Should still calculate basic metrics
        metrics = calculate_portfolio_metrics(test_db)

        # Basic metrics should be present
        assert "total_return" in metrics
        assert "volatility" in metrics
        assert "sharpe_ratio" in metrics

        # Benchmark-related metrics should be 0 or default
        assert metrics.get("correlation_sp500", 0) == 0
        assert metrics.get("beta", 1.0) == 1.0

    @pytest.mark.unit
    def test_metrics_with_insufficient_data(self, test_db):
        """Test metrics calculation with insufficient data."""
        # Add only one data point
        test_db.add(IndexValue(date=date(2024, 1, 1), value=100))
        test_db.commit()

        # Should return empty or default metrics
        metrics = calculate_portfolio_metrics(test_db)

        # Should handle gracefully
        assert metrics == {} or all(v in [0, 0.0, None] for v in metrics.values())
