# Strategy Service

## Overview
Implements investment strategy logic for portfolio management and asset allocation.

## Location
`apps/api/app/services/strategy.py`

## Purpose
Core business logic for index strategy implementation and portfolio optimization.

## Strategy Components

### 1. Momentum Strategy (40% weight)
- Filters assets based on performance
- Configurable lookback period
- Threshold-based selection
- Trend following approach

### 2. Market Cap Strategy (30% weight)
- Weights by market capitalization
- Large-cap bias
- Liquidity consideration
- Index-like exposure

### 3. Risk Parity Strategy (30% weight)
- Inverse volatility weighting
- Risk-balanced allocation
- Volatility normalization
- Equal risk contribution

## Core Functions

### calculate_allocations(assets, prices, config)
- Main allocation engine
- Combines strategies
- Applies constraints
- Returns weights

### apply_momentum_filter(assets, threshold)
- Performance filtering
- Remove underperformers
- Dynamic threshold
- Trend analysis

### calculate_market_cap_weights(assets)
- Market cap calculation
- Weight normalization
- Cap constraints
- Rebalancing logic

### calculate_risk_parity_weights(assets, returns)
- Volatility calculation
- Inverse weighting
- Risk normalization
- Portfolio optimization

## Strategy Configuration

### Parameters
- **momentum_weight**: 0.4
- **market_cap_weight**: 0.3
- **risk_parity_weight**: 0.3
- **performance_threshold**: -1%
- **rebalance_frequency**: daily/weekly/monthly
- **min_assets**: 3
- **max_weight**: 0.4

### Dynamic Adjustment
- Market condition adaptation
- Volatility regime changes
- Correlation adjustments
- Risk management rules

## Allocation Process

1. **Data Collection**
   - Fetch current prices
   - Calculate returns
   - Get market caps

2. **Strategy Application**
   - Run momentum filter
   - Calculate individual weights
   - Combine strategies

3. **Constraint Application**
   - Max weight limits
   - Min diversification
   - Sector limits

4. **Final Allocation**
   - Normalize weights
   - Store allocations
   - Track changes

## Risk Management

### Position Limits
- Maximum single asset: 40%
- Minimum position: 1%
- Sector concentration: 50%

### Volatility Controls
- Target volatility: 15%
- Vol scaling
- Risk budgeting

### Drawdown Protection
- Maximum drawdown monitoring
- Risk reduction triggers
- Capital preservation

## Performance Metrics

### Return Metrics
- Absolute returns
- Risk-adjusted returns
- Alpha generation
- Tracking error

### Risk Metrics
- Volatility
- Sharpe ratio
- Maximum drawdown
- Value at Risk

## Data Quality

### Validation
- Price sanity checks
- Return calculations
- Outlier detection
- Missing data handling

### Filtering
- Z-score outliers (3σ)
- Return capping (±50%)
- Price minimums ($1.00)
- Volume requirements

## Optimization Techniques

### Computational
- Vectorized operations
- Caching calculations
- Batch processing

### Portfolio
- Mean-variance optimization
- Risk parity
- Equal weighting fallback

## Dependencies
- pandas: Data manipulation
- numpy: Calculations
- Database models
- TwelveData service

## Related Modules
- routers/strategy.py: API endpoints
- refresh.py: Data updates
- models.py: Strategy config