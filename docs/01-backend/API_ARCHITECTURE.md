# Waardhaven AutoIndex API Architecture

## Overview

The Waardhaven AutoIndex API is built with FastAPI and follows a modular, domain-driven design pattern. The backend is organized into distinct layers for better maintainability, testability, and scalability.

## Directory Structure

```
apps/api/
├── app/
│   ├── core/           # Core functionality and configuration
│   │   ├── config.py   # Application settings
│   │   └── database.py # Database connection and session management
│   │
│   ├── models/         # SQLAlchemy ORM models (domain-organized)
│   │   ├── __init__.py # Model exports and Base
│   │   ├── user.py     # User authentication models
│   │   ├── asset.py    # Asset and pricing models
│   │   ├── index.py    # Index composition models
│   │   ├── trading.py  # Trading order models
│   │   └── strategy.py # Strategy and risk models
│   │
│   ├── schemas/        # Pydantic validation schemas (domain-organized)
│   │   ├── __init__.py # Schema exports
│   │   ├── auth.py     # Authentication schemas
│   │   ├── index.py    # Index management schemas
│   │   ├── benchmark.py# Benchmark comparison schemas
│   │   ├── broker.py   # Trading schemas
│   │   └── strategy.py # Strategy configuration schemas
│   │
│   ├── routers/        # API endpoint routers
│   │   ├── auth.py     # Authentication endpoints
│   │   ├── index.py    # Index data endpoints
│   │   ├── benchmark.py# Benchmark comparison endpoints
│   │   ├── broker.py   # Trading endpoints
│   │   ├── strategy.py # Strategy management endpoints
│   │   ├── diagnostics.py # System health endpoints
│   │   └── manual_refresh.py # Manual data refresh endpoints
│   │
│   ├── services/       # Business logic layer
│   │   ├── currency.py # Currency conversion service
│   │   ├── performance.py # Performance metrics calculation
│   │   ├── refresh.py  # Data refresh orchestration
│   │   ├── strategy.py # Strategy implementation
│   │   └── twelvedata.py # Market data integration
│   │
│   ├── utils/          # Utility functions
│   │   ├── security.py # Password hashing and JWT
│   │   └── token_dep.py# Authentication dependencies
│   │
│   └── main.py         # FastAPI application entry point
```

## Architecture Layers

### 1. **Presentation Layer (Routers)**
- **Purpose**: Handle HTTP requests/responses
- **Location**: `/app/routers/`
- **Responsibilities**:
  - Request validation
  - Response formatting
  - HTTP status codes
  - Authentication checks

### 2. **Business Logic Layer (Services)**
- **Purpose**: Core business logic and orchestration
- **Location**: `/app/services/`
- **Responsibilities**:
  - Data processing
  - Business rules
  - External API integration
  - Complex calculations

### 3. **Data Access Layer (Models)**
- **Purpose**: Database interaction
- **Location**: `/app/models/`
- **Responsibilities**:
  - ORM definitions
  - Database relationships
  - Data persistence

### 4. **Validation Layer (Schemas)**
- **Purpose**: Data validation and serialization
- **Location**: `/app/schemas/`
- **Responsibilities**:
  - Request/response validation
  - Data transformation
  - API documentation

## Key Components

### Core Configuration (`/app/core/`)

#### `config.py`
Manages application settings using Pydantic BaseSettings:
- Environment variables
- API keys
- Database URLs
- Feature flags

#### `database.py`
Database connection management:
- SQLAlchemy engine setup
- Session factory
- Base model class

### Models (`/app/models/`)

Domain-driven model organization:

#### User Domain (`user.py`)
- `User`: User accounts and authentication

#### Asset Domain (`asset.py`)
- `Asset`: Financial instruments
- `Price`: Historical price data

#### Index Domain (`index.py`)
- `IndexValue`: Index performance history
- `Allocation`: Portfolio composition

#### Strategy Domain (`strategy.py`)
- `StrategyConfig`: Strategy parameters
- `RiskMetrics`: Performance metrics
- `MarketCapData`: Market capitalization data

### Schemas (`/app/schemas/`)

Request/response validation schemas organized by domain:

#### Authentication (`auth.py`)
- `RegisterRequest`/`LoginRequest`: User authentication
- `TokenResponse`: JWT token response

#### Index Management (`index.py`)
- `AllocationItem`: Asset allocation details
- `IndexCurrentResponse`: Current portfolio state
- `SimulationRequest`/`Response`: Investment simulation

#### Strategy (`strategy.py`)
- `StrategyConfigRequest`: Strategy updates
- `RiskMetric`: Risk metrics data
- `RiskMetricsResponse`: Risk analysis results

### Services (`/app/services/`)

#### Data Refresh Pipeline (`refresh.py`, `refresh_optimized.py`)
Orchestrates market data updates:
1. Fetch latest prices from TwelveData
2. Store in database
3. Calculate new allocations
4. Update index values
5. Calculate risk metrics

#### Performance Analytics (`performance.py`)
Calculates portfolio metrics:
- Sharpe/Sortino ratios
- Maximum drawdown
- Volatility
- Beta relative to S&P 500

#### Strategy Engine (`strategy.py`)
Implements portfolio allocation strategies:
- Momentum weighting
- Market cap weighting
- Risk parity weighting
- Dynamic rebalancing

## API Endpoints

### Authentication (`/api/v1/auth/`)
- `POST /register`: Create new account
- `POST /login`: Authenticate user
- `GET /me`: Get current user

### Index Management (`/api/v1/index/`)
- `GET /current`: Current portfolio allocation
- `GET /history`: Historical performance
- `POST /simulate`: Investment simulation
- `GET /currencies`: Supported currencies
- `GET /assets/{symbol}/history`: Individual asset history

### Benchmark (`/api/v1/benchmark/`)
- `GET /sp500`: S&P 500 comparison data

### Strategy (`/api/v1/strategy/`)
- `GET /config`: Current strategy configuration
- `PUT /config`: Update strategy parameters
- `GET /risk-metrics`: Risk analytics
- `POST /rebalance`: Trigger rebalancing

### System (`/api/v1/diagnostics/`)
- `GET /database-status`: Database health
- `GET /refresh-status`: Data freshness
- `POST /test-refresh`: Test data pipeline

## Data Flow

### 1. Market Data Update Flow
```
TwelveData API → refresh_service → Price table → strategy_service → Allocation table → IndexValue table → RiskMetrics table
```

### 2. Client Request Flow
```
Client → Router → Authentication → Service → Database → Response Schema → Client
```

### 3. Portfolio Rebalancing Flow
```
Trigger → StrategyConfig → Calculate Weights → New Allocations → Update Index → Calculate Metrics
```

## Security

### Authentication
- JWT-based authentication
- Password hashing with bcrypt
- Token expiration handling

### Authorization
- Dependency injection for route protection
- User context in all protected endpoints

### Data Validation
- Pydantic schemas for all inputs
- Type checking and constraints
- SQL injection prevention via ORM

## Performance Optimizations

### Database
- Indexed columns for frequent queries
- Batch operations for bulk updates
- Connection pooling

### Caching
- Market data caching to reduce API calls
- In-memory caching for frequently accessed data

### Rate Limiting
- Respect TwelveData API limits
- Smart refresh modes based on plan tier
- Graceful degradation

## Error Handling

### Structured Error Responses
```python
{
    "detail": "Error message",
    "status_code": 400,
    "type": "validation_error"
}
```

### Logging
- Structured logging with context
- Error tracking
- Performance monitoring

## Testing Strategy

### Unit Tests
- Service layer logic
- Calculation accuracy
- Data validation

### Integration Tests
- API endpoint testing
- Database operations
- External API mocking

### Performance Tests
- Load testing
- Database query optimization
- API response times

## Deployment Considerations

### Environment Variables
Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing key
- `TWELVEDATA_API_KEY`: Market data API key

### Database Migrations
- Alembic for schema migrations
- Backward compatibility
- Rollback procedures

### Monitoring
- Health check endpoints
- Metrics collection
- Alert thresholds

## Future Enhancements

### Planned Improvements
1. GraphQL API layer
2. WebSocket real-time updates
3. Redis caching layer
4. Microservices architecture
5. Event-driven architecture with message queues

### Scalability Considerations
- Horizontal scaling with load balancing
- Database read replicas
- Async task processing with Celery
- CDN for static assets

## API Documentation

The API is self-documenting via FastAPI:
- Interactive docs: `/docs` (Swagger UI)
- Alternative docs: `/redoc` (ReDoc)
- OpenAPI schema: `/openapi.json`