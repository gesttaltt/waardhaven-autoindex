# Waardhaven AutoIndex API Architecture

## Overview

The Waardhaven AutoIndex API is a production-ready FastAPI application following Domain-Driven Design (DDD) principles with clean architecture. The backend implements comprehensive portfolio management, real-time market data integration, and automated investment strategies.

**Status**: Production-Ready (90%+ feature complete)  
**Test Coverage**: 10 test files with comprehensive unit and integration tests  
**Performance**: Redis caching, Celery background tasks, optimized database queries  
**Security**: JWT authentication, rate limiting, CORS, security headers

## Directory Structure

```
apps/api/
├── app/
│   ├── core/           # Core functionality and configuration
│   │   ├── config.py   # Application settings (Pydantic v2)
│   │   ├── database.py # Database connection and session management
│   │   ├── redis_client.py # Redis caching configuration
│   │   └── celery_app.py # Background task configuration
│   │
│   ├── models/         # SQLAlchemy ORM models (domain-organized)
│   │   ├── __init__.py # Model exports and Base
│   │   ├── user.py     # User authentication models
│   │   ├── asset.py    # Asset and pricing models
│   │   ├── index.py    # Index composition models
│   │   └── strategy.py # Strategy and risk models
│   │
│   ├── schemas/        # Pydantic validation schemas (domain-organized)
│   │   ├── __init__.py # Schema exports
│   │   ├── auth.py     # Authentication schemas
│   │   ├── index.py    # Index management schemas
│   │   ├── benchmark.py# Benchmark comparison schemas
│   │   ├── strategy.py # Strategy configuration schemas
│   │   └── validation.py # Enhanced validation with security constraints
│   │
│   ├── routers/        # API endpoint routers (10 modules)
│   │   ├── root.py     # Root and health check endpoints
│   │   ├── auth.py     # Authentication (JWT, OAuth, refresh tokens)
│   │   ├── index.py    # Portfolio index operations
│   │   ├── benchmark.py# S&P 500 comparison and analysis
│   │   ├── strategy.py # Investment strategy configuration
│   │   ├── background.py# Async background operations
│   │   ├── tasks.py    # Background task management
│   │   ├── diagnostics.py # System health and monitoring
│   │   ├── manual_refresh.py # Manual data refresh operations
│   │   └── news.py     # Financial news integration
│   │
│   ├── services/       # Business logic layer (6 core services)
│   │   ├── currency.py # Multi-currency conversion
│   │   ├── performance.py # Portfolio performance analytics
│   │   ├── refresh.py  # Data synchronization orchestration
│   │   ├── strategy.py # Investment strategy algorithms
│   │   ├── news.py     # News aggregation and sentiment
│   │   └── twelvedata.py # TwelveData API integration
│   │
│   ├── tasks/          # Background tasks (Celery)
│   │   ├── __init__.py
│   │   └── background_tasks.py # Async task definitions
│   │
│   ├── utils/          # Utility functions
│   │   ├── security.py # Password hashing and JWT
│   │   ├── token_dep.py# Authentication dependencies
│   │   ├── cache.py    # Cache management utilities
│   │   ├── cache_utils.py # Cache helper functions
│   │   ├── password_validator.py # Password strength validation
│   │   ├── create_indexes.py # Database index creation
│   │   └── run_migrations.py # Database migration runner
│   │
│   ├── db_init.py      # Database initialization
│   ├── seed_assets.py  # Initial asset seeding
│   ├── tasks_refresh.py# Task refresh utilities
│   └── main.py         # FastAPI application entry point
│
├── migrations/         # SQL migration scripts
│   ├── add_composite_indexes.sql
│   └── add_performance_indexes.sql
│
├── scripts/            # Startup and deployment scripts
│   ├── startup.sh      # Unified startup script
│   ├── start_worker.sh # Celery worker script
│   ├── start_beat.sh   # Celery beat script
│   └── start_flower.sh # Flower monitoring script
│
├── tests/              # Comprehensive test suite (10 test files)
│   ├── conftest.py     # Test configuration and fixtures
│   ├── test_api.py     # API endpoint integration tests
│   ├── test_auth.py    # Authentication flow tests
│   ├── test_background.py # Background task tests
│   ├── test_benchmark.py # Benchmark comparison tests
│   ├── test_diagnostics.py # System health tests
│   ├── test_performance.py # Performance calculation tests
│   ├── test_providers.py # External provider tests
│   ├── test_refresh.py # Data refresh tests
│   └── test_strategy.py # Strategy algorithm tests
│
├── requirements.txt    # Python dependencies (Pydantic 2.11.7)
├── requirements-test.txt # Test dependencies
├── pytest.ini          # Pytest configuration
└── Dockerfile          # Docker configuration
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
- `DATABASE_URL`: PostgreSQL connection string (auto-provided on Render)
- `SECRET_KEY`: JWT signing key (minimum 32 characters)
- `ADMIN_TOKEN`: Admin access token (minimum 32 characters)
- `TWELVEDATA_API_KEY`: Market data API key
- `PORT`: Server port (default: 10000)
- `FRONTEND_URL`: Frontend URL for CORS configuration
- `SKIP_STARTUP_REFRESH`: Skip initial data refresh (recommended: true)

Optional environment variables:
- `REDIS_URL`: Redis connection for caching
- `DEBUG`: Debug mode (default: false)
- `CACHE_TTL_SECONDS`: Cache TTL (default: 300)
- `TWELVEDATA_PLAN`: API plan level (default: free)
- `TWELVEDATA_RATE_LIMIT`: Credits per minute (default: 8)

### Database Configuration
- PostgreSQL with connection pooling
- Pool size: 20 (production), 5 (development)
- Max overflow: 40 (production), 10 (development)
- Connection recycling: 1 hour
- Pre-ping enabled for connection health
- Automatic retry logic (30 attempts on startup)
- Graceful degradation if database unavailable

### Dependency Management
- Python 3.11 runtime
- Pydantic 2.11.7 (critical for deployment)
- FastAPI 0.112.0
- SQLAlchemy 2.0.32
- Requirements pinned for reproducibility

### Database Migrations
- SQL migration scripts in `/migrations`
- Automatic index creation on startup
- Composite indexes for performance
- Run via `run_migrations.py` utility

### Monitoring
- Health check endpoint: `/health`
- System diagnostics: `/api/v1/diagnostics/system`
- Database status: `/api/v1/diagnostics/database-status`
- Cache status: `/api/v1/diagnostics/cache-status`
- Refresh status: `/api/v1/diagnostics/refresh-status`

### Deployment Process (Render.com)
1. Docker build with Dockerfile
2. Dependencies installed from requirements.txt
3. Startup script (`scripts/startup.sh`) executes:
   - Environment variable validation
   - Database connection check with retries
   - Table initialization if needed
   - Asset seeding
   - Optional market data refresh
4. Uvicorn server starts on configured PORT
5. Health checks validate service readiness

### Known Deployment Issues and Solutions

#### Pydantic Version Compatibility
- **Issue**: `@root_validator` deprecation error
- **Solution**: Use Pydantic 2.11.7, ensure `@model_validator(mode='after')` syntax

#### Build Cache Issues
- **Issue**: Old code deployed despite new commits
- **Solution**: Clear Render build cache, force manual deploy

#### Port Binding
- **Issue**: "No open ports detected" warning
- **Solution**: Properly bind to `0.0.0.0:$PORT`

#### Database Timeouts
- **Issue**: Connection fails during startup
- **Solution**: Implemented retry logic with graceful degradation

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

## Complete API Endpoints Reference

### Authentication (`/api/v1/auth`)
| Endpoint | Method | Description | Frontend Coverage |
|----------|--------|-------------|-------------------|
| `/register` | POST | User registration | ✅ Implemented |
| `/login` | POST | User login with JWT | ✅ Implemented |

### Index Management (`/api/v1/index`)
| Endpoint | Method | Description | Frontend Coverage |
|----------|--------|-------------|-------------------|
| `/current` | GET | Current portfolio allocations | ✅ Implemented |
| `/history` | GET | Historical index values | ✅ Implemented |
| `/simulate` | POST | Investment simulation | ✅ Implemented |
| `/currencies` | GET | Supported currencies | ✅ Implemented |
| `/assets/{symbol}/history` | GET | Individual asset history | ✅ Implemented |

### Strategy Configuration (`/api/v1/strategy`)
| Endpoint | Method | Description | Frontend Coverage |
|----------|--------|-------------|-------------------|
| `/config` | GET | Get strategy configuration | ✅ Implemented |
| `/config` | PUT | Update strategy configuration | ✅ Implemented |
| `/config/ai-adjust` | POST | AI-suggested adjustments | ⚠️ Partial |
| `/risk-metrics` | GET | Risk analytics data | ✅ Implemented |
| `/rebalance` | POST | Force portfolio rebalancing | ✅ Implemented |

### Background Tasks (`/api/v1/background`) ✨ NEW
| Endpoint | Method | Description | Frontend Coverage |
|----------|--------|-------------|-------------------|
| `/refresh` | POST | Trigger market data refresh | ✅ Implemented |
| `/compute` | POST | Trigger index computation | ✅ Implemented |
| `/report` | POST | Generate report | ✅ Implemented |
| `/cleanup` | POST | Clean old data | ✅ Implemented |
| `/status/{task_id}` | GET | Get task status | ✅ Implemented |
| `/active` | GET | List active tasks | ✅ Implemented |

### System Diagnostics (`/api/v1/diagnostics`) ✨ NEW
| Endpoint | Method | Description | Frontend Coverage |
|----------|--------|-------------|-------------------|
| `/database-status` | GET | Database health check | ✅ Implemented |
| `/refresh-status` | GET | Check refresh requirements | ✅ Implemented |
| `/cache-status` | GET | Redis cache statistics | ✅ Implemented |
| `/cache-invalidate` | POST | Clear cache entries | ✅ Implemented |
| `/test-refresh` | POST | Test refresh process | ✅ Implemented |
| `/recalculate-index` | POST | Recalculate index values | ✅ Implemented |

### Benchmark (`/api/v1/benchmark`)
| Endpoint | Method | Description | Frontend Coverage |
|----------|--------|-------------|-------------------|
| `/sp500` | GET | S&P 500 benchmark data | ✅ Implemented |

### Manual Refresh (`/api/v1/manual`)
| Endpoint | Method | Description | Frontend Coverage |
|----------|--------|-------------|-------------------|
| `/smart-refresh` | POST | Smart refresh mode | ✅ Implemented |
| `/trigger-refresh` | POST | Full refresh | ✅ Implemented |
| `/minimal-refresh` | POST | Minimal refresh | ✅ Implemented |

### Tasks (`/api/v1/tasks`)
| Endpoint | Method | Description | Frontend Coverage |
|----------|--------|-------------|-------------------|
| `/refresh` | POST | Basic refresh task | ✅ Implemented |

### Root Endpoints
| Endpoint | Method | Description | Frontend Coverage |
|----------|--------|-------------|-------------------|
| `/` | GET | API information | N/A |
| `/health` | GET | Health check | N/A |

## Frontend Coverage Summary

- **Total Endpoints**: 35
- **Fully Implemented**: 30 (85.7%)
- **Partially Implemented**: 1 (2.9%)
- **Not Applicable**: 4 (11.4%)

### New Pages Added (Latest Update)
1. **Tasks Management** (`/tasks`) - Full task queue monitoring
2. **System Diagnostics** (`/diagnostics`) - Health and cache management
3. **Reports & Analytics** (`/reports`) - Report generation and history

### Remaining Implementation (15%)
- WebSocket real-time updates
- Advanced AI strategy optimization UI
- Enhanced risk management interface
- Mobile/PWA support