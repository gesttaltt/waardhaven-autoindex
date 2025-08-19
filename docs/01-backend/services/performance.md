# Performance Service

## Overview
Portfolio performance metrics calculation service providing risk-adjusted return metrics.

## Location
`apps/api/app/services/performance.py`

## Purpose
Calculates comprehensive portfolio performance metrics including Sharpe ratio, Sortino ratio, maximum drawdown, and other key risk/return indicators.

## Constants
- `TRADING_DAYS_PER_YEAR`: 252 (standard trading days)
- `RISK_FREE_RATE`: 0.05 (5% annual risk-free rate)

## Class: PerformanceCalculator

Static methods for calculating various performance metrics.

### calculate_returns(values: List[float]) → np.ndarray
Calculate daily returns from a price series.

**Formula:** `(price[t] - price[t-1]) / price[t-1]`

**Returns:** Array of daily returns

### sharpe_ratio(returns: np.ndarray, risk_free_rate: float) → float
Calculate the Sharpe ratio (risk-adjusted returns).

**Formula:** `(mean(excess_returns) / std(excess_returns)) * sqrt(252)`

**Parameters:**
- `returns`: Daily returns array
- `risk_free_rate`: Annual risk-free rate (default: 5%)

**Returns:** Annualized Sharpe ratio

### sortino_ratio(returns: np.ndarray, risk_free_rate: float) → float
Calculate Sortino ratio using only downside volatility.

**Formula:** `(mean(excess_returns) / downside_std) * sqrt(252)`

**Features:**
- Only considers negative returns for risk calculation
- Better metric for strategies avoiding downside risk
- Returns high value (10.0) if no negative returns

**Returns:** Annualized Sortino ratio

### max_drawdown(values: List[float]) → Tuple[float, int, int]
Calculate maximum drawdown and its location.

**Returns:** Tuple of:
- Maximum drawdown percentage (negative value)
- Peak index
- Trough index

**Example:** `(-0.15, 45, 67)` means 15% drawdown from index 45 to 67

### calmar_ratio(returns: np.ndarray, max_dd: float) → float
Calculate Calmar ratio (return/drawdown ratio).

**Formula:** `annualized_return / abs(max_drawdown)`

**Interpretation:**
- Higher is better
- Measures return per unit of drawdown risk

### information_ratio(portfolio_returns: np.ndarray, benchmark_returns: np.ndarray) → float
Calculate information ratio vs benchmark.

**Formula:** `mean(active_returns) / std(active_returns) * sqrt(252)`

**Features:**
- Measures consistency of outperformance
- Active returns = portfolio - benchmark
- Higher IR indicates consistent alpha

### volatility(returns: np.ndarray, annualized: bool) → float
Calculate return volatility (standard deviation).

**Parameters:**
- `returns`: Daily returns
- `annualized`: Whether to annualize (default: True)

**Returns:** Volatility (annualized if specified)

### beta(portfolio_returns: np.ndarray, market_returns: np.ndarray) → float
Calculate portfolio beta vs market.

**Formula:** `covariance(portfolio, market) / variance(market)`

**Interpretation:**
- Beta = 1: Moves with market
- Beta > 1: More volatile than market
- Beta < 1: Less volatile than market

### alpha(portfolio_returns: np.ndarray, market_returns: np.ndarray, risk_free_rate: float) → float
Calculate Jensen's alpha (excess return).

**Formula:** `portfolio_return - (risk_free + beta * (market_return - risk_free))`

**Interpretation:**
- Positive alpha: Outperforming on risk-adjusted basis
- Negative alpha: Underperforming

## Module Functions

### calculate_portfolio_metrics(db: Session, lookback_days: Optional[int]) → Dict
Calculate comprehensive portfolio metrics.

**Process:**
1. Fetch index values for period
2. Calculate returns
3. Fetch benchmark (S&P 500) data
4. Calculate all metrics
5. Store in RiskMetrics table

**Returns dictionary with:**
- `sharpe_ratio`: Risk-adjusted return
- `sortino_ratio`: Downside risk-adjusted return
- `max_drawdown`: Maximum peak-to-trough decline
- `calmar_ratio`: Return per unit of drawdown
- `volatility`: Annualized standard deviation
- `total_return`: Total return for period
- `annualized_return`: Annualized return
- `beta`: Market sensitivity (if benchmark available)
- `alpha`: Excess return (if benchmark available)
- `information_ratio`: Consistency of outperformance
- `correlation`: Correlation with benchmark
- `var_95`: Value at Risk (95% confidence)
- `cvar_95`: Conditional VaR (expected shortfall)

### get_rolling_metrics(db: Session, window: int) → List[Dict]
Calculate rolling window metrics.

**Parameters:**
- `window`: Rolling window size in days (default: 30)

**Returns:** List of metrics for each window period

## Value at Risk (VaR) Calculation
```python
var_95 = np.percentile(returns, 5)  # 95% confidence level
cvar_95 = returns[returns <= var_95].mean()  # Expected shortfall
```

## Usage Examples

### Calculate Current Metrics
```python
from app.services.performance import calculate_portfolio_metrics
from app.core.database import get_db

db = next(get_db())
metrics = calculate_portfolio_metrics(db, lookback_days=365)
print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {metrics['max_drawdown']:.2%}")
```

### Calculate Rolling Metrics
```python
from app.services.performance import get_rolling_metrics

rolling = get_rolling_metrics(db, window=30)
for period in rolling:
    print(f"Date: {period['date']}, Sharpe: {period['sharpe_ratio']:.2f}")
```

### Direct Metric Calculation
```python
from app.services.performance import PerformanceCalculator

# Calculate Sharpe ratio from returns
returns = np.array([0.01, -0.02, 0.015, 0.005, -0.01])
sharpe = PerformanceCalculator.sharpe_ratio(returns)

# Calculate maximum drawdown
values = [100, 105, 110, 95, 100, 90, 95]
max_dd, peak_idx, trough_idx = PerformanceCalculator.max_drawdown(values)
```

## Dependencies
- `models.index`: IndexValue and Allocation models
- `models.asset`: Asset and Price models
- `models.strategy`: RiskMetrics model
- pandas & numpy for calculations
- SQLAlchemy for database queries

## Performance Considerations
- Caches frequently accessed metrics
- Uses vectorized numpy operations
- Batch processes historical data
- Stores calculated metrics in database

## Error Handling
- Returns 0.0 for undefined metrics (e.g., division by zero)
- Handles empty or insufficient data gracefully
- Logs calculation errors
- Falls back to simpler metrics if benchmark unavailable