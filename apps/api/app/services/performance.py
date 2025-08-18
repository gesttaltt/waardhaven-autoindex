"""
Portfolio performance metrics calculation service.
Provides Sharpe ratio, Sortino ratio, max drawdown, and other key metrics.
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import date, timedelta
from sqlalchemy.orm import Session
import logging

from ..models.index import IndexValue
from ..models.asset import Asset, Price
from ..models.strategy import RiskMetrics
from ..core.config import settings

logger = logging.getLogger(__name__)

# Annual trading days
TRADING_DAYS_PER_YEAR = 252
# Risk-free rate (annual)
RISK_FREE_RATE = 0.05


class PerformanceCalculator:
    """Calculate portfolio performance metrics."""
    
    @staticmethod
    def calculate_returns(values: List[float]) -> np.ndarray:
        """Calculate daily returns from price series."""
        if len(values) < 2:
            return np.array([])
        
        prices = np.array(values)
        returns = (prices[1:] - prices[:-1]) / prices[:-1]
        return returns
    
    @staticmethod
    def sharpe_ratio(returns: np.ndarray, risk_free_rate: float = RISK_FREE_RATE) -> float:
        """
        Calculate Sharpe ratio.
        
        Args:
            returns: Daily returns
            risk_free_rate: Annual risk-free rate
        
        Returns:
            Annualized Sharpe ratio
        """
        if len(returns) == 0:
            return 0.0
        
        # Convert annual risk-free rate to daily
        daily_rf = risk_free_rate / TRADING_DAYS_PER_YEAR
        
        # Calculate excess returns
        excess_returns = returns - daily_rf
        
        # Annualized Sharpe ratio
        if excess_returns.std() == 0:
            return 0.0
        
        sharpe = (excess_returns.mean() / excess_returns.std()) * np.sqrt(TRADING_DAYS_PER_YEAR)
        return float(sharpe)
    
    @staticmethod
    def sortino_ratio(returns: np.ndarray, risk_free_rate: float = RISK_FREE_RATE) -> float:
        """
        Calculate Sortino ratio (Sharpe ratio using only downside volatility).
        
        Args:
            returns: Daily returns
            risk_free_rate: Annual risk-free rate
        
        Returns:
            Annualized Sortino ratio
        """
        if len(returns) == 0:
            return 0.0
        
        # Convert annual risk-free rate to daily
        daily_rf = risk_free_rate / TRADING_DAYS_PER_YEAR
        
        # Calculate excess returns
        excess_returns = returns - daily_rf
        
        # Calculate downside deviation (only negative returns)
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0:
            # No negative returns, return a high value
            return 10.0
        
        downside_std = np.sqrt(np.mean(downside_returns ** 2))
        
        if downside_std == 0:
            return 0.0
        
        sortino = (excess_returns.mean() / downside_std) * np.sqrt(TRADING_DAYS_PER_YEAR)
        return float(sortino)
    
    @staticmethod
    def max_drawdown(values: List[float]) -> Tuple[float, int, int]:
        """
        Calculate maximum drawdown.
        
        Args:
            values: Price series
        
        Returns:
            Tuple of (max_drawdown_percentage, peak_index, trough_index)
        """
        if len(values) < 2:
            return 0.0, 0, 0
        
        prices = np.array(values)
        cumulative_returns = prices / prices[0]
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - running_max) / running_max
        
        max_dd = drawdown.min()
        trough_idx = drawdown.argmin()
        
        # Find the peak before the trough
        peak_idx = running_max[:trough_idx + 1].argmax() if trough_idx > 0 else 0
        
        return float(max_dd * 100), int(peak_idx), int(trough_idx)
    
    @staticmethod
    def calmar_ratio(returns: np.ndarray, max_dd: float) -> float:
        """
        Calculate Calmar ratio (annual return / max drawdown).
        
        Args:
            returns: Daily returns
            max_dd: Maximum drawdown (as decimal, e.g., -0.20 for 20%)
        
        Returns:
            Calmar ratio
        """
        if len(returns) == 0 or max_dd == 0:
            return 0.0
        
        # Annualized return
        annual_return = (1 + returns.mean()) ** TRADING_DAYS_PER_YEAR - 1
        
        # Calmar ratio
        calmar = annual_return / abs(max_dd)
        return float(calmar)
    
    @staticmethod
    def information_ratio(portfolio_returns: np.ndarray, benchmark_returns: np.ndarray) -> float:
        """
        Calculate Information Ratio (active return / tracking error).
        
        Args:
            portfolio_returns: Portfolio daily returns
            benchmark_returns: Benchmark daily returns
        
        Returns:
            Information ratio
        """
        if len(portfolio_returns) == 0 or len(benchmark_returns) == 0:
            return 0.0
        
        # Align returns
        min_len = min(len(portfolio_returns), len(benchmark_returns))
        portfolio_returns = portfolio_returns[:min_len]
        benchmark_returns = benchmark_returns[:min_len]
        
        # Calculate active returns
        active_returns = portfolio_returns - benchmark_returns
        
        if active_returns.std() == 0:
            return 0.0
        
        # Annualized information ratio
        ir = (active_returns.mean() / active_returns.std()) * np.sqrt(TRADING_DAYS_PER_YEAR)
        return float(ir)
    
    @staticmethod
    def volatility(returns: np.ndarray, annualized: bool = True) -> float:
        """
        Calculate volatility (standard deviation of returns).
        
        Args:
            returns: Daily returns
            annualized: Whether to annualize the volatility
        
        Returns:
            Volatility
        """
        if len(returns) == 0:
            return 0.0
        
        vol = returns.std()
        
        if annualized:
            vol *= np.sqrt(TRADING_DAYS_PER_YEAR)
        
        return float(vol)
    
    @staticmethod
    def beta(portfolio_returns: np.ndarray, market_returns: np.ndarray) -> float:
        """
        Calculate beta (portfolio volatility relative to market).
        
        Args:
            portfolio_returns: Portfolio daily returns
            market_returns: Market daily returns
        
        Returns:
            Beta coefficient
        """
        if len(portfolio_returns) < 2 or len(market_returns) < 2:
            return 1.0
        
        # Align returns
        min_len = min(len(portfolio_returns), len(market_returns))
        portfolio_returns = portfolio_returns[:min_len]
        market_returns = market_returns[:min_len]
        
        # Calculate covariance and market variance
        covariance = np.cov(portfolio_returns, market_returns)[0, 1]
        market_variance = np.var(market_returns)
        
        if market_variance == 0:
            return 1.0
        
        beta = covariance / market_variance
        return float(beta)
    
    @staticmethod
    def alpha(portfolio_returns: np.ndarray, market_returns: np.ndarray, 
             beta: float, risk_free_rate: float = RISK_FREE_RATE) -> float:
        """
        Calculate Jensen's alpha.
        
        Args:
            portfolio_returns: Portfolio daily returns
            market_returns: Market daily returns
            beta: Portfolio beta
            risk_free_rate: Annual risk-free rate
        
        Returns:
            Annualized alpha
        """
        if len(portfolio_returns) == 0 or len(market_returns) == 0:
            return 0.0
        
        # Align returns
        min_len = min(len(portfolio_returns), len(market_returns))
        portfolio_returns = portfolio_returns[:min_len]
        market_returns = market_returns[:min_len]
        
        # Annualized returns
        portfolio_annual = (1 + portfolio_returns.mean()) ** TRADING_DAYS_PER_YEAR - 1
        market_annual = (1 + market_returns.mean()) ** TRADING_DAYS_PER_YEAR - 1
        
        # Calculate alpha
        alpha = portfolio_annual - (risk_free_rate + beta * (market_annual - risk_free_rate))
        return float(alpha)


def calculate_portfolio_metrics(db: Session, lookback_days: Optional[int] = None) -> Dict:
    """
    Calculate comprehensive portfolio performance metrics.
    
    Args:
        db: Database session
        lookback_days: Number of days to look back (None for all history)
    
    Returns:
        Dictionary of performance metrics
    """
    try:
        # Get index values
        query = db.query(IndexValue).order_by(IndexValue.date.asc())
        
        if lookback_days:
            start_date = date.today() - timedelta(days=lookback_days)
            query = query.filter(IndexValue.date >= start_date)
        
        index_values = query.all()
        
        if len(index_values) < 2:
            logger.warning("Insufficient data for metrics calculation")
            return {}
        
        # Extract values and dates
        values = [iv.value for iv in index_values]
        dates = [iv.date for iv in index_values]
        
        # Get S&P 500 benchmark data
        sp500_asset = db.query(Asset).filter(Asset.symbol == settings.SP500_TICKER).first()
        benchmark_values = []
        
        if sp500_asset:
            benchmark_prices = db.query(Price).filter(
                Price.asset_id == sp500_asset.id,
                Price.date >= dates[0],
                Price.date <= dates[-1]
            ).order_by(Price.date.asc()).all()
            
            if benchmark_prices:
                # Normalize to base 100
                base = benchmark_prices[0].close
                benchmark_values = [(p.close / base) * 100 for p in benchmark_prices]
        
        # Calculate returns
        calc = PerformanceCalculator()
        portfolio_returns = calc.calculate_returns(values)
        
        # Calculate metrics
        metrics = {
            "sharpe_ratio": calc.sharpe_ratio(portfolio_returns),
            "sortino_ratio": calc.sortino_ratio(portfolio_returns),
            "volatility": calc.volatility(portfolio_returns),
            "total_return": ((values[-1] / values[0]) - 1) * 100 if values else 0,
            "annualized_return": ((values[-1] / values[0]) ** (365 / len(values)) - 1) * 100 if len(values) > 1 else 0,
            "start_date": dates[0].isoformat() if dates else None,
            "end_date": dates[-1].isoformat() if dates else None,
            "days": len(values)
        }
        
        # Calculate max drawdown
        max_dd, peak_idx, trough_idx = calc.max_drawdown(values)
        metrics.update({
            "max_drawdown": max_dd,
            "max_drawdown_peak_date": dates[peak_idx].isoformat() if peak_idx < len(dates) else None,
            "max_drawdown_trough_date": dates[trough_idx].isoformat() if trough_idx < len(dates) else None,
            "calmar_ratio": calc.calmar_ratio(portfolio_returns, max_dd / 100)
        })
        
        # Calculate benchmark-relative metrics if available
        if benchmark_values and len(benchmark_values) >= 2:
            benchmark_returns = calc.calculate_returns(benchmark_values)
            
            beta = calc.beta(portfolio_returns, benchmark_returns)
            metrics.update({
                "information_ratio": calc.information_ratio(portfolio_returns, benchmark_returns),
                "beta": beta,
                "alpha": calc.alpha(portfolio_returns, benchmark_returns, beta),
                "benchmark_total_return": ((benchmark_values[-1] / benchmark_values[0]) - 1) * 100,
                "excess_return": metrics["total_return"] - ((benchmark_values[-1] / benchmark_values[0]) - 1) * 100
            })
        
        # Calculate current drawdown
        current_drawdown = 0.0
        if len(values) > 0:
            current_value = values[-1]
            running_max = max(values)
            if running_max > 0:
                current_drawdown = ((current_value - running_max) / running_max) * 100
        
        # Calculate correlation with S&P 500
        correlation_sp500 = 0.0
        if benchmark_returns is not None and len(benchmark_returns) > 1 and len(portfolio_returns) > 1:
            try:
                min_len = min(len(portfolio_returns), len(benchmark_returns))
                if min_len > 1:
                    correlation_matrix = np.corrcoef(portfolio_returns[:min_len], benchmark_returns[:min_len])
                    correlation_sp500 = float(correlation_matrix[0, 1])
                    if np.isnan(correlation_sp500):
                        correlation_sp500 = 0.0
            except Exception as e:
                logger.warning(f"Failed to calculate correlation: {e}")
                correlation_sp500 = 0.0
        
        # Store metrics in database
        risk_metrics = RiskMetrics(
            date=date.today(),
            sharpe_ratio=metrics["sharpe_ratio"],
            sortino_ratio=metrics["sortino_ratio"],
            max_drawdown=max_dd / 100,  # Store as decimal (0.20 for 20%)
            current_drawdown=current_drawdown / 100,  # Store as decimal
            volatility=metrics["volatility"],
            beta_sp500=metrics.get("beta", 1.0),
            correlation_sp500=correlation_sp500,
            total_return=metrics["total_return"],
            annualized_return=metrics.get("annualized_return", 0.0)
        )
        
        # Add to returned metrics
        metrics["current_drawdown"] = current_drawdown
        metrics["correlation_sp500"] = correlation_sp500
        
        # Update or create today's metrics
        existing = db.query(RiskMetrics).filter(RiskMetrics.date == date.today()).first()
        if existing:
            for key, value in metrics.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
        else:
            db.add(risk_metrics)
        
        db.commit()
        
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to calculate portfolio metrics: {e}")
        return {}


def get_rolling_metrics(db: Session, window: int = 30) -> List[Dict]:
    """
    Calculate rolling performance metrics.
    
    Args:
        db: Database session
        window: Rolling window size in days
    
    Returns:
        List of metrics for each window
    """
    try:
        index_values = db.query(IndexValue).order_by(IndexValue.date.asc()).all()
        
        if len(index_values) < window:
            return []
        
        calc = PerformanceCalculator()
        rolling_metrics = []
        
        for i in range(window, len(index_values)):
            window_values = [iv.value for iv in index_values[i-window:i]]
            window_returns = calc.calculate_returns(window_values)
            
            if len(window_returns) > 0:
                rolling_metrics.append({
                    "date": index_values[i].date.isoformat(),
                    "sharpe_ratio": calc.sharpe_ratio(window_returns),
                    "sortino_ratio": calc.sortino_ratio(window_returns),
                    "volatility": calc.volatility(window_returns, annualized=False),
                    "return": ((window_values[-1] / window_values[0]) - 1) * 100
                })
        
        return rolling_metrics
        
    except Exception as e:
        logger.error(f"Failed to calculate rolling metrics: {e}")
        return []