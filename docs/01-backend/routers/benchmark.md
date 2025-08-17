# Benchmark Router

## Overview
Provides S&P 500 benchmark data for portfolio performance comparison.

## Location
`apps/api/app/routers/benchmark.py`

## Endpoints

### GET /api/v1/benchmark/sp500
- Fetch S&P 500 historical data
- Date range parameters
- Returns index values
- Cached responses

### GET /api/v1/benchmark/compare
- Portfolio vs benchmark comparison
- Relative performance
- Correlation analysis
- Risk-adjusted metrics

### GET /api/v1/benchmark/sectors
- Sector performance data
- Industry breakdowns
- Rotation analysis

## Data Sources

### Market Data
- SPY ETF as proxy
- TwelveData integration
- Historical prices
- Real-time updates

### Calculations
- Total return
- Price return
- Dividend adjustment
- Index reconstruction

## Comparison Metrics

### Performance Metrics
- Absolute return
- Relative return
- Excess return
- Tracking error

### Risk Metrics
- Beta calculation
- Correlation
- Information ratio
- Capture ratios

## Caching Strategy
- Daily cache refresh
- Historical data persistence
- Memory optimization
- Cache invalidation

## Response Format
```json
{
  "dates": [...],
  "values": [...],
  "returns": [...],
  "metrics": {
    "total_return": 0.15,
    "volatility": 0.18,
    "sharpe_ratio": 0.83
  }
}
```

## Dependencies
- TwelveData service
- Price models
- Cache layer
- Calculation utilities