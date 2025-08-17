# Backend API Refactoring TODO

## Priority: HIGH - API Architecture & Performance Issues

### Current State Analysis
The FastAPI backend has grown organically and shows several architectural and performance issues that need addressing for scalability and maintainability.

### Architectural Problems

#### 1. **Database Architecture Issues**
- [ ] **No connection pooling configuration** - Using default SQLAlchemy settings
- [ ] **Missing database migrations** - No Alembic setup for schema versioning
- [ ] **No database indexing strategy** - Performance issues with large datasets
- [ ] **Lack of database constraints** - Potential data integrity issues
- [ ] **No database partitioning** - Will struggle with large time-series data
- [ ] **Missing soft delete patterns** - Hard deletes may cause data loss

#### 2. **API Design Issues**
- [ ] **Inconsistent error handling** - No centralized error management
- [ ] **No request/response validation middleware** - Potential security risks
- [ ] **Missing API versioning strategy** - Breaking changes will affect clients
- [ ] **No rate limiting** - Vulnerable to DoS attacks
- [ ] **Lack of request correlation IDs** - Difficult debugging
- [ ] **No API documentation standards** - Inconsistent OpenAPI specs

#### 3. **Security Vulnerabilities**
- [ ] **CORS configuration issues** - Allows all origins in development
- [ ] **No input sanitization** - SQL injection and XSS risks
- [ ] **Weak authentication** - Simple JWT without refresh tokens
- [ ] **No authorization layers** - All authenticated users have same permissions
- [ ] **Missing security headers** - No CSP, HSTS, etc.
- [ ] **No audit logging** - Cannot track user actions

#### 4. **Performance Issues**
- [ ] **N+1 query problems** - Multiple database queries in loops
- [ ] **No caching layer** - Repeated expensive calculations
- [ ] **Synchronous external API calls** - Blocking TwelveData requests
- [ ] **Large object serialization** - Full datasets returned without pagination
- [ ] **No background task queue** - Long-running operations block responses
- [ ] **Missing query optimization** - No EXPLAIN plan analysis

#### 5. **Service Layer Problems**
- [ ] **Tight coupling** - Services directly access database models
- [ ] **Mixed responsibilities** - Business logic scattered across layers
- [ ] **No dependency injection** - Hard to test and mock dependencies
- [ ] **Inconsistent error handling** - Different patterns across services
- [ ] **No circuit breaker pattern** - External API failures cascade
- [ ] **Missing retry mechanisms** - No resilience for transient failures

### Code Quality Issues

#### 1. **Type Safety**
- [ ] **Inconsistent typing** - Some functions lack proper type hints
- [ ] **Mixed return types** - Functions return different types based on conditions
- [ ] **No validation of external API responses** - TwelveData response not validated
- [ ] **Missing domain models** - Using database models for business logic

#### 2. **Error Handling**
- [ ] **Generic exception handling** - Catching all exceptions without specifics
- [ ] **No error context** - Logs don't include enough debugging information
- [ ] **Inconsistent error responses** - Different error formats across endpoints
- [ ] **Missing error boundaries** - Errors propagate without proper handling

#### 3. **Testing Issues**
- [ ] **No unit tests** - Critical business logic untested
- [ ] **No integration tests** - API endpoints not validated
- [ ] **No database testing** - Migration and schema changes not tested
- [ ] **No performance testing** - No benchmarks for critical operations
- [ ] **No API contract testing** - No validation of OpenAPI specs

#### 4. **Logging & Monitoring**
- [ ] **Inconsistent logging levels** - Debug info mixed with errors
- [ ] **No structured logging** - Difficult to parse and analyze
- [ ] **Missing business metrics** - No tracking of portfolio performance
- [ ] **No health check endpoints** - Cannot monitor service health
- [ ] **No distributed tracing** - Cannot track requests across services

## Specific Critical Issues

### 1. **refresh.py Service Issues**
```python
# Line 89-91: Dangerous operation
db.query(Price).delete()  # Deletes all prices without backup
db.commit()

# Line 41-44: Inefficient queries
for sym, name, sector in DEFAULT_ASSETS:
    exists = db.query(Asset).filter(Asset.symbol == sym).first()
    # N+1 query problem
```

### 2. **Models.py Issues**
```python
# Missing indexes for time-series queries
class Price(Base):
    date = Column(Date, index=True)  # Should be composite index with asset_id
    
# No soft delete capability
# No created_at/updated_at audit fields
# No data validation constraints
```

### 3. **Strategy.py Issues**
```python
# No input validation
def compute_index_and_allocations(db: Session, config: Dict = None):
    # Large data processing without streaming
    # No error recovery mechanisms
    # Complex calculations without unit tests
```

### 4. **Database Performance**
- [ ] **Missing composite indexes** on (asset_id, date) for time-series queries
- [ ] **No query plan analysis** - Slow queries not identified
- [ ] **Full table scans** in allocation calculations
- [ ] **No database connection monitoring** - Connection leaks possible

## Refactoring Plan

### Phase 1: Foundation & Security (Week 1-2)
- [ ] Implement proper database migrations with Alembic
- [ ] Add comprehensive input validation with Pydantic
- [ ] Implement proper error handling middleware
- [ ] Add security headers and CORS configuration
- [ ] Set up structured logging with correlation IDs
- [ ] Add basic health check endpoints

### Phase 2: Database Optimization (Week 2-3)
- [ ] Add proper database indexes for time-series queries
- [ ] Implement connection pooling with monitoring
- [ ] Add database query profiling and optimization
- [ ] Implement soft delete patterns
- [ ] Add audit fields (created_at, updated_at, deleted_at)
- [ ] Create database performance monitoring

### Phase 3: Service Layer Refactoring (Week 3-4)
- [ ] Implement repository pattern for data access
- [ ] Create proper domain models separate from database models
- [ ] Add dependency injection container
- [ ] Implement circuit breaker for external APIs
- [ ] Add retry mechanisms with exponential backoff
- [ ] Create service interfaces and implementations

### Phase 4: Performance Optimization (Week 4-5)
- [ ] Implement Redis caching layer
- [ ] Add background task queue (Celery/RQ)
- [ ] Implement async external API calls
- [ ] Add response pagination for large datasets
- [ ] Optimize database queries with EXPLAIN analysis
- [ ] Implement data compression for historical data

### Phase 5: Testing & Monitoring (Week 5-6)
- [ ] Add comprehensive unit test suite
- [ ] Implement integration tests with test database
- [ ] Add performance benchmarks
- [ ] Set up application monitoring (Prometheus/Grafana)
- [ ] Implement distributed tracing
- [ ] Add business metrics collection

### Phase 6: Advanced Features (Week 6-8)
- [ ] Implement API rate limiting
- [ ] Add proper authorization with role-based access
- [ ] Implement API versioning strategy
- [ ] Add real-time data streaming capabilities
- [ ] Implement data archiving strategy
- [ ] Add automated backup and recovery

## Proposed Architecture

### File Structure
```
apps/api/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── portfolio.py
│   │   │   ├── market.py
│   │   │   └── admin.py
│   │   └── dependencies.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   ├── logging.py
│   │   └── cache.py
│   ├── domain/
│   │   ├── models/
│   │   │   ├── portfolio.py
│   │   │   ├── asset.py
│   │   │   └── user.py
│   │   ├── services/
│   │   │   ├── portfolio_service.py
│   │   │   ├── market_service.py
│   │   │   └── strategy_service.py
│   │   └── repositories/
│   │       ├── base.py
│   │       ├── asset_repository.py
│   │       └── portfolio_repository.py
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── models.py
│   │   │   ├── migrations/
│   │   │   └── repositories.py
│   │   ├── external/
│   │   │   ├── twelve_data.py
│   │   │   └── currency_api.py
│   │   └── cache/
│   │       └── redis_cache.py
│   ├── schemas/
│   │   ├── portfolio.py
│   │   ├── auth.py
│   │   └── market.py
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── performance/
│   └── utils/
│       ├── validators.py
│       ├── formatters.py
│       └── exceptions.py
```

### Technology Stack Additions
- **Database**: PostgreSQL with proper indexing and partitioning
- **Caching**: Redis for session and query caching
- **Queue**: Celery with Redis broker for background tasks
- **Monitoring**: Prometheus + Grafana for metrics
- **Logging**: Structured logging with ELK stack
- **Testing**: pytest with factory_boy for test data
- **Security**: OAuth2 with refresh tokens, rate limiting

## Critical Fixes Needed Immediately

### 1. **Data Loss Prevention**
```python
# Current dangerous code in refresh.py:89-91
db.query(Price).delete()  # DANGEROUS!

# Should be:
# 1. Backup existing data
# 2. Soft delete or archive
# 3. Implement incremental updates
```

### 2. **Query Performance**
```python
# Add composite indexes
CREATE INDEX idx_prices_asset_date ON prices(asset_id, date);
CREATE INDEX idx_allocations_date_asset ON allocations(date, asset_id);
CREATE INDEX idx_index_values_date ON index_values(date);
```

### 3. **Error Handling**
```python
# Replace generic except blocks with specific error handling
try:
    result = external_api_call()
except requests.RequestException as e:
    logger.error(f"API call failed: {e}")
    raise HTTPException(status_code=503, detail="External service unavailable")
```

### 4. **Input Validation**
```python
# Add proper validation to all endpoints
from pydantic import BaseModel, validator

class SimulationRequest(BaseModel):
    amount: float
    start_date: date
    currency: str = "USD"
    
    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v
```

## Success Metrics

### Performance Targets
- [ ] Database query response time < 100ms for 95th percentile
- [ ] API response time < 500ms for 95th percentile
- [ ] External API failure rate < 1%
- [ ] Memory usage stable under load
- [ ] Zero data loss incidents

### Quality Targets
- [ ] Test coverage > 80%
- [ ] Code quality score > 8/10 (SonarQube)
- [ ] Zero critical security vulnerabilities
- [ ] API documentation completeness > 95%
- [ ] Error handling coverage > 90%

## Implementation Priority

### Immediate (This week)
1. Fix data deletion issue in refresh service
2. Add basic input validation
3. Implement proper error handling
4. Add database indexes for performance

### Short-term (Next 2 weeks)
1. Implement repository pattern
2. Add caching layer
3. Set up proper logging
4. Add basic monitoring

### Medium-term (Month 2)
1. Complete service layer refactoring
2. Add comprehensive testing
3. Implement background tasks
4. Add advanced security features

### Long-term (Month 3-4)
1. Implement real-time features
2. Add advanced monitoring
3. Optimize for high availability
4. Implement data archiving

## Migration Strategy

### Phase 1: Backward Compatible Changes
- Add new endpoints while keeping old ones
- Implement feature flags for gradual rollout
- Add monitoring before making changes
- Create rollback procedures

### Phase 2: Breaking Changes
- Version the API (v2)
- Migrate clients gradually
- Deprecate old endpoints with proper notice
- Maintain dual-write for critical data

### Phase 3: Legacy Cleanup
- Remove deprecated endpoints
- Clean up old code and migrations
- Optimize database schema
- Archive old data

## Notes

The current backend implementation works for MVP but has significant technical debt that will cause issues as the system scales. The refactoring should prioritize data integrity and security first, then performance and maintainability.

The most critical issues are:
1. Data loss risk in refresh operations
2. Performance issues with database queries
3. Lack of proper error handling and monitoring
4. Security vulnerabilities in authentication and authorization

Each change should be thoroughly tested and deployed gradually to minimize risk to the production system.