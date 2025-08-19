# Index Router

## Overview
Manages index portfolio operations including current values, history, and investment simulation.

## Location
`apps/api/app/routers/index.py`

## Actual Implementation

### GET /api/v1/index/current
Get current index value and portfolio status.

**Response Model:** `IndexCurrentResponse`
```json
{
  "value": 123.45,
  "change_24h": 2.5,
  "change_pct_24h": 0.02,
  "last_updated": "2024-01-15T10:30:00Z"
}
```

**Features:**
- Latest index value
- 24-hour change metrics
- Percentage changes
- Update timestamp

### GET /api/v1/index/history
Get historical index values over time.

**Response Model:** `IndexHistoryResponse`
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

**Features:**
- Time series data
- Historical values
- Base 100 normalization

### POST /api/v1/index/simulate
Simulate investment with specified parameters.

**Request Body:**
- `initial_investment`: Starting amount
- `currency`: Investment currency
- Other simulation parameters

**Response Model:** `SimulationResponse`
```json
{
  "initial_investment": 10000,
  "current_value": 12500,
  "total_return": 2500,
  "return_percentage": 0.25,
  "simulation_period": "1 year",
  "currency": "USD"
}
```

**Features:**
- Investment simulation
- Multi-currency support
- Return calculations
- Performance metrics

### GET /api/v1/index/currencies
Get list of supported currencies.

**Response:**
```json
{
  "currencies": ["USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD"]
}
```

### GET /api/v1/index/assets/{symbol}/history
Get historical data for a specific asset in the index.

**Path Parameters:**
- `symbol`: Asset symbol (e.g., "AAPL")

**Response Model:** `IndexHistoryResponse`
- Same format as index history
- Asset-specific time series

## Data Sources
- IndexValue model for index data
- Price model for asset prices
- Database queries with date filtering

## Authentication
All endpoints require user authentication via JWT token.

## Error Handling
- 404 for missing data
- 401 for authentication failures
- 400 for invalid parameters

## Dependencies
- models.index: IndexValue model
- models.asset: Asset and Price models
- schemas: Response models
- User authentication