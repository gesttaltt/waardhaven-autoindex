# Strategy Router

## Overview
Manages investment strategy configuration and parameters.

## Location
`apps/api/app/routers/strategy.py`

## Actual Implementation

### GET /api/v1/strategy/config
Get current strategy configuration.

**Response includes:**
- Weight allocations (momentum, market_cap, risk_parity)
- Price and return thresholds
- Rebalancing settings
- AI adjustment metadata
- Last update timestamps

**Response format:**
```json
{
  "momentum_weight": 0.4,
  "market_cap_weight": 0.3,
  "risk_parity_weight": 0.3,
  "min_price_threshold": 5.0,
  "max_daily_return": 0.5,
  "min_daily_return": -0.5,
  "max_forward_fill_days": 5,
  "outlier_std_threshold": 3.0,
  "rebalance_frequency": "monthly",
  "daily_drop_threshold": -0.01,
  "ai_adjusted": false,
  "ai_adjustment_reason": null,
  "ai_confidence_score": null,
  "last_rebalance": "2024-01-01T00:00:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### PUT /api/v1/strategy/config
Update strategy configuration with validation.

**Request Body:** `SecureStrategyConfig` schema
- Validates weight sum equals 1.0
- Ensures thresholds are within valid ranges
- Prevents invalid configurations

**Query Parameters:**
- `recompute` (bool, default=true): Whether to recompute index after update

**Features:**
- Input validation via Pydantic schema
- Stores adjustment history
- Optional index recomputation
- Returns updated configuration

### POST /api/v1/strategy/config/ai-adjust
Apply AI-suggested strategy adjustments.

**Request Body:**
```json
{
  "adjustments": {
    "momentum_weight": 0.5,
    "market_cap_weight": 0.25
  },
  "reason": "Market volatility detected",
  "confidence": 0.85
}
```

**Features:**
- Accepts AI-generated adjustments
- Tracks confidence scores
- Stores reason for adjustments
- Updates adjustment history

### GET /api/v1/strategy/risk-metrics
Get current risk metrics for the portfolio.

**Response includes:**
- Volatility measures
- Sharpe ratio
- Maximum drawdown
- Value at Risk (VaR)
- Other risk indicators

### POST /api/v1/strategy/rebalance
Trigger portfolio rebalancing.

**Features:**
- Forces immediate rebalancing
- Updates allocations
- Refreshes index values
- Returns rebalancing results

## Configuration Parameters

### Weight Settings
All weights must sum to 1.0:
- `momentum_weight`: Weight for momentum strategy (0-1)
- `market_cap_weight`: Weight for market cap strategy (0-1)
- `risk_parity_weight`: Weight for risk parity strategy (0-1)

### Data Quality Parameters
- `min_price_threshold`: Minimum valid price (default: 5.0)
- `max_daily_return`: Maximum allowed daily return
- `min_daily_return`: Minimum allowed daily return
- `max_forward_fill_days`: Max days to forward-fill missing data
- `outlier_std_threshold`: Standard deviations for outlier detection

### Rebalancing Parameters
- `rebalance_frequency`: How often to rebalance ("daily", "weekly", "monthly")
- `daily_drop_threshold`: Threshold for filtering daily drops

## Validation Rules

### Automatic Validation
- Weights must sum to exactly 1.0
- All weights must be between 0 and 1
- Thresholds must be within reasonable ranges
- Frequency must be valid option

### Business Logic
- At least one strategy must have non-zero weight
- Configuration changes trigger audit log entry
- AI adjustments tracked separately

## Adjustment History
All configuration changes are stored with:
- Timestamp
- Changed fields
- User ID or AI indicator
- Reason for change (if AI-adjusted)

## Dependencies
- StrategyConfig model
- RiskMetrics model
- SecureStrategyConfig schema for validation
- Database session
- User authentication