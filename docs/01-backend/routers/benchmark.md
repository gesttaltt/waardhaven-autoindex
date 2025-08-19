# Benchmark Router

## Overview
Provides S&P 500 benchmark data for portfolio performance comparison.

## Location
`apps/api/app/routers/benchmark.py`

## Actual Implementation

### GET /api/v1/benchmark/sp500
Fetches S&P 500 historical data as a normalized series.

**Features:**
- Tries multiple S&P 500 symbols (^GSPC, SPY, SPX, .SPX, ^SPX)
- Returns empty series if data not found (prevents frontend crashes)
- Normalizes values to base 100
- Cached responses available

**Response Model:** `BenchmarkResponse`
```json
{
  "series": [
    {
      "date": "2024-01-01",
      "value": 100.0
    }
  ]
}
```

### GET /api/v1/benchmark/compare
Compares portfolio performance against S&P 500 benchmark.

**Query Parameters:**
- `start_date` (optional): Start date for comparison
- `end_date` (optional): End date for comparison

**Features:**
- Fetches index values and S&P 500 data for same period
- Calculates performance metrics for both
- Returns comparative analysis
- Handles missing data gracefully

**Response includes:**
- Index performance data
- S&P 500 performance data
- Calculated metrics (returns, volatility, etc.)
- Correlation analysis

## Data Sources

### Market Data
- Uses S&P 500 asset from database (multiple symbol fallbacks)
- TwelveData integration for price updates
- Historical prices stored in Price model

### Calculations
- Simple normalization to base 100
- Returns calculation using numpy
- Basic statistical metrics

## Error Handling
- Returns empty series instead of 404 for missing benchmark
- Logs warnings for missing data
- HTTPException for comparison when no data available

## Dependencies
- Price and Asset models
- Database session
- User authentication
- NumPy for calculations