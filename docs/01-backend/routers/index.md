# Index Router

## Overview
Manages index portfolio operations including creation, tracking, and performance analysis.

## Location
`apps/api/app/routers/index.py`

## Endpoints

### GET /api/v1/index/performance
- Get index performance data
- Historical values
- Return calculations
- Requires authentication

### GET /api/v1/index/allocations
- Current portfolio allocations
- Asset weights
- Rebalancing information

### GET /api/v1/index/assets
- List of index assets
- Asset details
- Current prices

### POST /api/v1/index/rebalance
- Trigger manual rebalancing
- Apply strategy rules
- Update allocations

### GET /api/v1/index/metrics
- Portfolio metrics
- Risk statistics
- Performance indicators

## Core Functionality

### Performance Tracking
- Base 100 indexing
- Daily/weekly/monthly values
- Cumulative returns
- Comparison periods

### Allocation Management
- Dynamic weights
- Strategy-based allocation
- Rebalancing logic
- Asset filtering

### Metrics Calculation
- Return metrics
- Volatility measures
- Sharpe ratio
- Maximum drawdown

## Data Flow

1. **Fetch Market Data**
   - Get latest prices
   - Update database
   - Calculate changes

2. **Apply Strategy**
   - Filter assets
   - Calculate weights
   - Generate allocations

3. **Update Portfolio**
   - Store allocations
   - Calculate values
   - Track performance

## Strategy Integration
- Momentum strategy
- Market cap weighting
- Risk parity
- Custom parameters

## Response Formats

### Performance Response
```json
{
  "dates": [...],
  "values": [...],
  "returns": [...],
  "current_value": 123.45
}
```

### Allocation Response
```json
{
  "allocations": [
    {
      "symbol": "AAPL",
      "weight": 0.15,
      "value": 10000
    }
  ]
}
```

## Dependencies
- services/strategy.py
- services/refresh.py
- models.py: Index models
- Database session

## Related Modules
- benchmark.py: Comparison data
- strategy.py: Strategy config
- services/strategy.py: Core logic