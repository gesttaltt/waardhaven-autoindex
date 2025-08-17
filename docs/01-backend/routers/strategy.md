# Strategy Router

## Overview
Manages investment strategy configuration and parameters.

## Location
`apps/api/app/routers/strategy.py`

## Endpoints

### GET /api/v1/strategy/config
- Get current strategy configuration
- Active parameters
- Weight allocations
- Threshold settings

### PUT /api/v1/strategy/config
- Update strategy parameters
- Validation checks
- Apply changes
- Trigger rebalancing

### GET /api/v1/strategy/available
- List available strategies
- Strategy descriptions
- Parameter ranges
- Performance history

### POST /api/v1/strategy/backtest
- Run strategy backtest
- Historical simulation
- Performance metrics
- Risk analysis

### GET /api/v1/strategy/performance
- Strategy performance metrics
- Attribution analysis
- Comparison data
- Historical results

## Strategy Types

### Momentum Strategy
- Performance-based filtering
- Lookback periods
- Threshold configuration
- Trend following

### Market Cap Strategy
- Size-based weighting
- Cap limits
- Rebalancing rules
- Index tracking

### Risk Parity Strategy
- Volatility weighting
- Risk budgeting
- Correlation consideration
- Portfolio balance

### Custom Strategies
- User-defined rules
- Parameter combinations
- Constraint settings
- Optimization goals

## Configuration Parameters

### Weight Settings
- Strategy weights (0-1)
- Minimum allocations
- Maximum concentrations
- Rebalancing bands

### Risk Parameters
- Volatility targets
- Drawdown limits
- Correlation thresholds
- Risk budgets

### Timing Parameters
- Rebalancing frequency
- Lookback periods
- Signal delays
- Execution windows

## Validation Rules

### Parameter Validation
- Range checking
- Sum constraints
- Logical consistency
- Business rules

### Strategy Validation
- Minimum diversification
- Risk limits
- Regulatory compliance
- Performance targets

## Backtesting Engine

### Simulation Parameters
- Start/end dates
- Initial capital
- Transaction costs
- Slippage assumptions

### Performance Metrics
- Total return
- Sharpe ratio
- Maximum drawdown
- Win rate

### Risk Analysis
- VaR calculations
- Stress testing
- Scenario analysis
- Sensitivity testing

## Response Formats

### Config Response
```json
{
  "momentum_weight": 0.4,
  "market_cap_weight": 0.3,
  "risk_parity_weight": 0.3,
  "rebalance_frequency": "monthly",
  "performance_threshold": -0.01
}
```

### Backtest Response
```json
{
  "returns": [...],
  "metrics": {
    "total_return": 0.25,
    "sharpe_ratio": 1.2,
    "max_drawdown": -0.15
  },
  "trades": [...]
}
```

## Dependencies
- Strategy service
- Database models
- Calculation engine
- Validation utilities