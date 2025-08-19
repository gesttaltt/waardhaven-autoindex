# API Schemas Documentation

## Overview
Pydantic schemas used for request/response validation in the Waardhaven AutoIndex API.

## Authentication Schemas (`app/schemas/auth.py`)

### RegisterRequest
```python
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    username: Optional[str] = None
```

### LoginRequest
```python
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
```

### GoogleAuthRequest
```python
class GoogleAuthRequest(BaseModel):
    email: EmailStr
```

### TokenResponse
```python
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

## Index Schemas (`app/schemas/index.py`)

### IndexHistoryResponse
```python
class IndexHistoryResponse(BaseModel):
    series: List[SeriesPoint]
    
class SeriesPoint(BaseModel):
    date: str
    value: float
```

### IndexCurrentResponse
```python
class IndexCurrentResponse(BaseModel):
    allocations: List[AllocationItem]
    
class AllocationItem(BaseModel):
    symbol: str
    weight: float
    name: Optional[str]
    sector: Optional[str]
```

### SimulationRequest
```python
class SimulationRequest(BaseModel):
    amount: float
    currency: str = "USD"
    start_date: Optional[str]
```

### SimulationResponse
```python
class SimulationResponse(BaseModel):
    amount_initial: float
    amount_final: float
    roi_pct: float
    currency: str
```

## Strategy Schemas (`app/schemas/strategy.py`)

### StrategyConfigSchema
```python
class StrategyConfigSchema(BaseModel):
    momentum_weight: float = Field(ge=0, le=1, default=0.4)
    market_cap_weight: float = Field(ge=0, le=1, default=0.3)
    risk_parity_weight: float = Field(ge=0, le=1, default=0.3)
    
    rebalance_frequency: str = Field(default="weekly")
    lookback_period: int = Field(ge=1, le=365, default=30)
    
    daily_drop_threshold: float = Field(le=0, default=-0.01)
    max_daily_return: float = Field(ge=0, default=0.5)
    min_daily_return: float = Field(le=0, default=-0.5)
    
    min_price_threshold: float = Field(ge=0, default=1.0)
    force_rebalance: bool = False
    
    @validator('momentum_weight', 'market_cap_weight', 'risk_parity_weight')
    def weights_sum_to_one(cls, v, values):
        # Validation logic to ensure weights sum to 1.0
        pass
```

### RiskMetricsResponse
```python
class RiskMetricsResponse(BaseModel):
    metrics: List[RiskMetric]
    
class RiskMetric(BaseModel):
    period_days: int
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    current_drawdown: float
    var_95: float
    var_99: float
    beta_sp500: Optional[float]
    correlation_sp500: Optional[float]
```

## Benchmark Schemas (`app/schemas/benchmark.py`)

### BenchmarkResponse
```python
class BenchmarkResponse(BaseModel):
    series: List[BenchmarkPoint]
    
class BenchmarkPoint(BaseModel):
    date: str
    value: float
    sp500_value: float
```

### ComparisonMetrics
```python
class ComparisonMetrics(BaseModel):
    portfolio_return: float
    benchmark_return: float
    excess_return: float
    tracking_error: float
    information_ratio: float
```

## News Schemas (`app/schemas/news.py`)

### NewsSearchRequest
```python
class NewsSearchRequest(BaseModel):
    symbols: Optional[List[str]]
    keywords: Optional[str]
    sentiment_min: Optional[float] = Field(ge=-1, le=1)
    sentiment_max: Optional[float] = Field(ge=-1, le=1)
    published_after: Optional[datetime]
    published_before: Optional[datetime]
    limit: int = Field(default=50, le=100)
    offset: int = Field(default=0, ge=0)
```

### NewsArticleResponse
```python
class NewsArticleResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    url: str
    source: str
    published_at: datetime
    sentiment_score: Optional[float]
    entities: List[str]
```

### EntitySentimentResponse
```python
class EntitySentimentResponse(BaseModel):
    symbol: str
    name: str
    current_sentiment: float
    sentiment_trend: str
    article_count_24h: int
    article_count_7d: int
    sentiment_history: List[SentimentPoint]
    
class SentimentPoint(BaseModel):
    date: str
    sentiment_score: float
    article_count: int
```

## Validation Schemas (`app/schemas/validation.py`)

### PaginationParams
```python
class PaginationParams(BaseModel):
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
```

### DateRangeParams
```python
class DateRangeParams(BaseModel):
    start_date: Optional[date]
    end_date: Optional[date]
    
    @validator('end_date')
    def end_after_start(cls, v, values):
        if 'start_date' in values and v and values['start_date']:
            if v < values['start_date']:
                raise ValueError('end_date must be after start_date')
        return v
```

### RefreshRequest
```python
class RefreshRequest(BaseModel):
    mode: str = Field(default="smart", regex="^(smart|full)$")
    symbols: Optional[List[str]]
    force: bool = False
```

## Background Task Schemas

### TaskResponse
```python
class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: Optional[str]
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
```

### TaskListResponse
```python
class TaskListResponse(BaseModel):
    tasks: List[TaskInfo]
    total: int
    
class TaskInfo(BaseModel):
    task_id: str
    task_type: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
```

## Common Response Patterns

### Success Response
```python
class SuccessResponse(BaseModel):
    status: str = "success"
    message: str
    data: Optional[Dict[str, Any]]
```

### Error Response
```python
class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    detail: Optional[Dict[str, Any]]
    error_code: Optional[str]
```

### Health Check Response
```python
class HealthResponse(BaseModel):
    status: str
    version: str
    database: bool
    redis: bool
    celery: bool
    timestamp: datetime
```

## Validation Features

### Field Validators
- Email validation using `EmailStr`
- Range validation using `Field(ge=, le=)`
- String pattern validation using `Field(regex=)`
- Custom validators using `@validator`

### Model Configuration
```python
class Config:
    # Allow field population by field name or alias
    allow_population_by_field_name = True
    
    # Use enum values instead of names
    use_enum_values = True
    
    # Validate on assignment
    validate_assignment = True
    
    # Custom JSON encoders
    json_encoders = {
        datetime: lambda v: v.isoformat(),
        date: lambda v: v.isoformat()
    }
```

## Request/Response Examples

### Authentication Flow
```json
// Register Request
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}

// Token Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Strategy Configuration
```json
// Update Strategy Request
{
  "momentum_weight": 0.5,
  "market_cap_weight": 0.3,
  "risk_parity_weight": 0.2,
  "rebalance_frequency": "monthly",
  "lookback_period": 60
}

// Risk Metrics Response
{
  "metrics": [{
    "period_days": 30,
    "total_return": 0.05,
    "annualized_return": 0.65,
    "volatility": 0.15,
    "sharpe_ratio": 2.1,
    "max_drawdown": -0.03
  }]
}
```

## Schema Evolution

### Versioning Strategy
- New fields are optional with defaults
- Deprecated fields marked with warnings
- Breaking changes require new endpoint versions

### Migration Path
1. Add new optional field with default
2. Update clients to use new field
3. Mark old field as deprecated
4. Remove old field in next major version

## Best Practices

1. **Always use Pydantic models** for request/response validation
2. **Include field descriptions** for API documentation
3. **Use appropriate field types** (EmailStr, HttpUrl, etc.)
4. **Implement custom validators** for business logic
5. **Return consistent error formats** across all endpoints
6. **Version schemas** when making breaking changes
7. **Document example values** in field descriptions