# Pydantic Schemas

## Overview
Complete reference for all Pydantic schemas used for API request/response validation and serialization.

## Schema Architecture

### Domain Organization
1. **Authentication**: `auth.py` - User authentication and authorization
2. **Index Management**: `index.py` - Portfolio index operations
3. **Strategy Configuration**: `strategy.py` - Investment strategy settings
4. **Benchmarking**: `benchmark.py` - Performance comparison data
5. **Security Validation**: `validation.py` - Enhanced security schemas

## Authentication Schemas (`app/schemas/auth.py`)

### RegisterRequest
User registration input validation.

```python
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
```

#### Validation Rules
- **email**: Must be valid email format (EmailStr)
- **password**: String (validated by `PasswordValidator` in router)

#### Example
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

### LoginRequest
User login input validation.

```python
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
```

#### Usage
- Accepts email and password for authentication
- Password validated against stored hash
- Returns JWT token on success

### TokenResponse
JWT authentication response.

```python
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

#### Token Format
- **access_token**: JWT token string
- **token_type**: Always "bearer"
- **Expiration**: 24 hours (configurable)

## Index Management Schemas (`app/schemas/index.py`)

### AllocationItem
Individual asset allocation in the portfolio.

```python
class AllocationItem(BaseModel):
    symbol: str = Field(..., description="Asset ticker symbol")
    weight: float = Field(..., ge=0, le=1, description="Weight in portfolio (0-1)")
    name: Optional[str] = Field(None, description="Asset name")
    sector: Optional[str] = Field(None, description="Asset sector")
    daily_return: Optional[float] = Field(None, description="Daily return percentage")
    ytd_return: Optional[float] = Field(None, description="Year-to-date return percentage")
```

#### Field Validation
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| symbol | str | Required | Ticker symbol (e.g., "AAPL") |
| weight | float | 0.0 ≤ weight ≤ 1.0 | Portfolio allocation weight |
| name | str | Optional | Full asset name |
| sector | str | Optional | Sector classification |
| daily_return | float | Optional | Daily return percentage |
| ytd_return | float | Optional | Year-to-date return |

### IndexCurrentResponse
Current portfolio composition response.

```python
class IndexCurrentResponse(BaseModel):
    date: DateType = Field(..., description="Date of the allocation")
    allocations: List[AllocationItem] = Field(..., description="List of asset allocations")
    total_assets: Optional[int] = Field(None, description="Total number of assets")
```

#### Business Rules
- Allocation weights should sum to 1.0
- Date represents the allocation calculation date
- Used for current portfolio visualization

### SeriesPoint
Time series data point for charts and analysis.

```python
class SeriesPoint(BaseModel):
    date: DateType = Field(..., description="Date of the data point")
    value: float = Field(..., description="Value at this date (base 100)")
```

#### Usage Patterns
- Index performance tracking (base 100)
- Price history visualization
- Benchmark comparison data
- Simulation results

### IndexHistoryResponse
Historical index performance data.

```python
class IndexHistoryResponse(BaseModel):
    series: List[SeriesPoint] = Field(..., description="Time series of index values")
    start_date: Optional[DateType] = Field(None, description="Start date of the series")
    end_date: Optional[DateType] = Field(None, description="End date of the series")
```

### SimulationRequest
Investment simulation input parameters.

```python
class SimulationRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Investment amount")
    start_date: DateType = Field(..., description="Simulation start date")
    currency: str = Field("USD", description="Currency code")
```

#### Validation Rules
- **amount**: Must be positive (> 0)
- **start_date**: Valid date, not in future
- **currency**: 3-letter currency code

### SimulationResponse
Investment simulation results.

```python
class SimulationResponse(BaseModel):
    start_date: DateType
    end_date: DateType
    start_value: float
    end_value: float
    amount_initial: float
    amount_final: float
    roi_pct: float = Field(..., description="Return on investment percentage")
    currency: str
    series: List[SeriesPoint] = Field(..., description="Value progression over time")
```

#### Calculation Logic
```python
# ROI calculation
roi_pct = ((amount_final - amount_initial) / amount_initial) * 100

# Value progression
# series shows portfolio value over time
```

## Strategy Configuration Schemas (`app/schemas/strategy.py`)

### StrategyConfigRequest
Strategy parameter updates (partial updates allowed).

```python
class StrategyConfigRequest(BaseModel):
    momentum_weight: Optional[float] = Field(None, ge=0, le=1)
    market_cap_weight: Optional[float] = Field(None, ge=0, le=1)
    risk_parity_weight: Optional[float] = Field(None, ge=0, le=1)
    min_price_threshold: Optional[float] = Field(None, gt=0)
    max_daily_return: Optional[float] = Field(None, gt=0)
    min_daily_return: Optional[float] = Field(None, lt=0)
    max_forward_fill_days: Optional[int] = Field(None, ge=0, le=5)
    outlier_std_threshold: Optional[float] = Field(None, gt=0)
    rebalance_frequency: Optional[Literal["daily", "weekly", "monthly"]] = None
    daily_drop_threshold: Optional[float] = Field(None, lt=0)
```

#### Weight Validation
```python
# Total weights must sum to 1.0
total = momentum_weight + market_cap_weight + risk_parity_weight
assert abs(total - 1.0) < 0.001
```

#### Parameter Constraints
| Parameter | Constraints | Default | Description |
|-----------|-------------|---------|-------------|
| momentum_weight | 0.0-1.0 | 0.4 | Momentum factor weight |
| market_cap_weight | 0.0-1.0 | 0.3 | Market cap factor weight |
| risk_parity_weight | 0.0-1.0 | 0.3 | Risk parity factor weight |
| min_price_threshold | > 0 | 1.0 | Minimum asset price |
| max_daily_return | > 0 | 0.5 | Daily return cap |
| min_daily_return | < 0 | -0.5 | Daily return floor |
| max_forward_fill_days | 0-5 | 2 | Missing data fill limit |
| outlier_std_threshold | > 0 | 3.0 | Outlier detection threshold |
| daily_drop_threshold | < 0 | -0.01 | Alert threshold |

### StrategyConfigResponse
Complete strategy configuration data.

```python
class StrategyConfigResponse(BaseModel):
    momentum_weight: float
    market_cap_weight: float
    risk_parity_weight: float
    min_price_threshold: float
    max_daily_return: float
    min_daily_return: float
    max_forward_fill_days: int
    outlier_std_threshold: float
    rebalance_frequency: str
    daily_drop_threshold: float
    ai_adjusted: bool = False
    ai_adjustment_reason: Optional[str] = None
    ai_confidence_score: Optional[float] = None
    last_rebalance: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

### RiskMetric
Individual risk metric data point.

```python
class RiskMetric(BaseModel):
    date: DateType
    total_return: float
    annualized_return: Optional[float] = None
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    current_drawdown: float
    volatility: Optional[float] = None
    var_95: Optional[float] = Field(None, description="95% Value at Risk")
    var_99: Optional[float] = Field(None, description="99% Value at Risk")
    beta_sp500: Optional[float] = Field(None, description="Beta relative to S&P 500")
    correlation_sp500: Optional[float] = Field(None, description="Correlation with S&P 500")
```

#### Risk Metric Definitions
| Metric | Range | Description |
|--------|-------|-------------|
| sharpe_ratio | Any | Risk-adjusted return (higher is better) |
| sortino_ratio | Any | Downside risk-adjusted return |
| max_drawdown | 0 to -1 | Maximum peak-to-trough decline |
| current_drawdown | 0 to -1 | Current decline from peak |
| volatility | 0-1 | Annualized volatility (as decimal) |
| var_95 | Negative | 5% chance of exceeding this loss |
| var_99 | Negative | 1% chance of exceeding this loss |
| beta_sp500 | Any | Volatility relative to S&P 500 |
| correlation_sp500 | -1 to 1 | Correlation with S&P 500 |

## Benchmark Schemas (`app/schemas/benchmark.py`)

### BenchmarkResponse
Benchmark performance comparison data.

```python
class BenchmarkResponse(BaseModel):
    series: List[SeriesPoint] = Field(..., description="Benchmark time series (base 100)")
    benchmark_name: str = Field("S&P 500", description="Name of the benchmark")
```

#### Usage
- S&P 500 performance data
- Normalized to base 100 for comparison
- Used for relative performance analysis

## Security Validation Schemas (`app/schemas/validation.py`)

### SecureStrategyConfig
Enhanced strategy configuration with security constraints.

```python
class SecureStrategyConfig(BaseModel):
    momentum_weight: float = Field(default=0.4, ge=0.0, le=1.0)
    market_cap_weight: float = Field(default=0.3, ge=0.0, le=1.0)
    risk_parity_weight: float = Field(default=0.3, ge=0.0, le=1.0)
    # ... additional security validations
```

#### Security Features
- Range validation on all numeric inputs
- Regex validation for string inputs
- Business rule validation (weights sum to 1.0)
- Prevents injection attacks

### SecureAssetSymbol
Validated asset symbol to prevent injection.

```python
class SecureAssetSymbol(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    
    @field_validator('symbol')
    def validate_symbol(cls, v):
        if not re.match(r'^[A-Z0-9\.\-]+$', v.upper()):
            raise ValueError("Symbol must contain only letters, numbers, dots, and hyphens")
        return v.upper()
```

#### Protection Features
- Alphanumeric + dots/hyphens only
- Path traversal prevention
- Length limits
- Case normalization

### SecureSimulationRequest
Validated simulation request with bounds checking.

```python
class SecureSimulationRequest(BaseModel):
    amount: float = Field(..., gt=0, le=1000000000)  # Max 1 billion
    currency: str = Field(default="USD", min_length=3, max_length=3)
    start_date: Optional[date] = Field(default=None)
```

## Schema Validation Patterns

### Field Validators
```python
@field_validator('email')
def validate_email(cls, v):
    # Custom email validation
    return v

@field_validator('weights')
def validate_weights_sum(cls, v, values):
    # Ensure weights sum to 1.0
    total = sum(values.values())
    if abs(total - 1.0) > 0.001:
        raise ValueError("Weights must sum to 1.0")
    return v
```

### Model Validators
```python
@model_validator(mode='after')
def validate_model(self):
    # Cross-field validation
    if self.start_date > self.end_date:
        raise ValueError("Start date must be before end date")
    return self
```

### Custom Validators
```python
from pydantic import validator

def validate_positive(cls, v):
    if v <= 0:
        raise ValueError("Value must be positive")
    return v
```

## Response Serialization

### JSON Schema Generation
```python
# Automatic OpenAPI schema generation
model_config = ConfigDict(
    json_schema_extra={
        "example": {
            "field": "value"
        }
    }
)
```

### Serialization Options
```python
# Include/exclude fields
response.model_dump(exclude={'password_hash'})

# Custom serializers
class DateTimeSerializer:
    @staticmethod
    def serialize_datetime(dt):
        return dt.isoformat()
```

## Error Handling

### Validation Errors
```python
from pydantic import ValidationError

try:
    model = Schema(**data)
except ValidationError as e:
    # Handle validation errors
    errors = e.errors()
```

### Custom Error Messages
```python
class CustomSchema(BaseModel):
    field: int = Field(..., ge=0, description="Must be non-negative")
    
    @field_validator('field')
    def validate_field(cls, v):
        if v < 0:
            raise ValueError("Custom error message")
        return v
```

## Best Practices

### Schema Design
1. Use descriptive field names
2. Add field descriptions
3. Set appropriate constraints
4. Provide example values
5. Use Optional for optional fields

### Validation Strategy
1. Validate at schema level first
2. Add business logic validation in routers
3. Use custom validators for complex rules
4. Provide clear error messages

### Performance
1. Use Field constraints instead of validators when possible
2. Cache compiled schema for repeated use
3. Use exclude_unset for partial updates
4. Minimize nested schema complexity

### Security
1. Validate all user inputs
2. Sanitize string inputs
3. Set reasonable field limits
4. Use whitelist validation for enums
5. Prevent injection attacks