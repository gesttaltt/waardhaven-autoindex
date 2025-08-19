# Testing Guide

## Overview
Testing documentation for the Waardhaven AutoIndex backend API.

## Current Test Coverage
- **Test Files**: 9 test modules
- **Test Count**: ~16 tests discovered
- **Coverage Target**: 70% (not yet measured)
- **Coverage Status**: Basic test suite implemented

## Test Structure

```
apps/api/tests/
├── __init__.py
├── conftest.py                 # Pytest fixtures and configuration
├── test_api.py                 # API endpoint integration tests
├── test_news_service.py        # News service tests
├── test_performance.py         # Performance calculation tests
├── test_providers_base.py      # Base provider tests
├── test_providers_marketaux.py # MarketAux provider tests
├── test_providers_twelvedata.py # TwelveData provider tests
├── test_refresh.py             # Data refresh tests
└── test_strategy.py            # Strategy service tests
```

## Running Tests

### All Tests
```bash
# From project root
cd apps/api
pytest

# With verbose output
pytest -v

# With coverage report (if pytest-cov installed)
pytest --cov=app --cov-report=html
```

### Specific Test Files
```bash
# Run single test file
pytest tests/test_api.py

# Run specific test
pytest tests/test_api.py::TestAuthEndpoints::test_login_success
```

### Test Categories
```bash
# Run only API tests
pytest -m api

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

## Test Configuration

### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    api: API endpoint tests
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
```

### conftest.py Fixtures

```python
@pytest.fixture
def db():
    """Test database session"""
    # Creates SQLite in-memory database for tests
    
@pytest.fixture
def client():
    """Test client for API requests"""
    # Creates FastAPI test client
    
@pytest.fixture
def test_user(db):
    """Creates a test user"""
    # Returns authenticated user for tests
    
@pytest.fixture
def mock_provider():
    """Mocked external provider"""
    # Mocks TwelveData/MarketAux API calls
```

## Test Categories

### 1. API Endpoint Tests (`test_api.py`)
Tests HTTP endpoints and request/response handling.

**Coverage:**
- Authentication (register, login, Google OAuth)
- Index operations
- Strategy configuration
- Background tasks

**Example:**
```python
def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "SecurePass123!"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### 2. Service Tests
Tests business logic in service layer.

**test_performance.py:**
- Sharpe ratio calculation
- Maximum drawdown
- Value at Risk (VaR)
- Annualized returns

**test_strategy.py:**
- Strategy weight validation
- Portfolio rebalancing
- Allocation calculations

**test_refresh.py:**
- Data refresh orchestration
- Backup creation
- Transaction handling

### 3. Provider Tests
Tests external API integrations.

**test_providers_base.py:**
- Retry logic
- Error handling
- Rate limiting

**test_providers_twelvedata.py:**
- Price fetching
- Batch requests
- Response parsing

**test_providers_marketaux.py:**
- News search
- Entity extraction
- Sentiment parsing

### 4. Integration Tests
Tests component interactions.

**Coverage:**
- Database operations
- Cache integration
- Background task queueing
- End-to-end workflows

## Mocking Strategies

### External APIs
```python
@patch('app.providers.market_data.twelvedata.TwelveDataProvider.fetch_time_series')
def test_price_fetch(mock_fetch):
    mock_fetch.return_value = pd.DataFrame({
        'date': ['2024-01-01'],
        'close': [150.0]
    })
    # Test logic here
```

### Database
```python
def test_with_rollback(db):
    db.add(test_object)
    db.commit()
    # Test logic
    db.rollback()  # Cleanup
```

### Redis Cache
```python
@patch('app.utils.cache.redis_client')
def test_with_cache(mock_redis):
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    # Test logic
```

## Test Data

### Fixtures
- `test_user`: Standard test user account
- `test_assets`: Default asset list (AAPL, MSFT, etc.)
- `test_prices`: Historical price data
- `test_strategy_config`: Default strategy configuration

### Factory Functions
```python
def create_test_price(asset_id, date, close):
    return Price(asset_id=asset_id, date=date, close=close)

def create_test_allocation(asset_id, weight):
    return Allocation(asset_id=asset_id, weight=weight)
```

## Current Test Gaps

### Missing Test Coverage:
1. **WebSocket connections** - Not implemented
2. **File uploads/downloads** - Report generation
3. **Email notifications** - Not implemented
4. **Advanced caching scenarios** - Redis integration
5. **Concurrent request handling** - Load testing
6. **Error recovery scenarios** - Partial failures

### Areas Needing More Tests:
1. **Edge cases** in calculations
2. **Invalid input validation**
3. **Database constraint violations**
4. **API rate limit handling**
5. **Background task failures**

## Best Practices

### Test Organization
1. **One test file per module** being tested
2. **Group related tests** in classes
3. **Use descriptive test names** (test_should_calculate_sharpe_ratio_correctly)
4. **Keep tests independent** - no shared state

### Test Design
1. **Arrange-Act-Assert** pattern
2. **Test one thing** per test
3. **Use fixtures** for common setup
4. **Mock external dependencies**
5. **Test both success and failure** cases

### Performance
1. **Use in-memory database** for speed
2. **Mock slow operations** (API calls, file I/O)
3. **Mark slow tests** with @pytest.mark.slow
4. **Run fast tests frequently**, slow tests in CI

## Continuous Integration

### GitHub Actions Workflow
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: pytest --cov=app
```

## Coverage Reports

### Generate Coverage
```bash
# HTML report
pytest --cov=app --cov-report=html

# Terminal report
pytest --cov=app --cov-report=term

# XML for CI
pytest --cov=app --cov-report=xml
```

### View Coverage
Open `htmlcov/index.html` in browser after generating HTML report.

## Testing Commands Reference

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific marker
pytest -m unit

# Run with verbose output
pytest -v

# Run with print statements visible
pytest -s

# Run until first failure
pytest -x

# Run failed tests from last run
pytest --lf

# Run tests in parallel (requires pytest-xdist)
pytest -n auto
```

## Future Improvements

1. **Increase coverage** to 80%+
2. **Add property-based tests** using Hypothesis
3. **Implement load testing** with Locust
4. **Add mutation testing** to verify test quality
5. **Create test data generators** for complex scenarios
6. **Add contract tests** for API compatibility
7. **Implement snapshot testing** for responses
8. **Add security testing** suite

## Troubleshooting

### Common Issues

1. **"Database is locked"**
   - Use separate test database
   - Ensure proper cleanup in fixtures

2. **"Import error"**
   - Check PYTHONPATH includes project root
   - Verify __init__.py files exist

3. **"Fixture not found"**
   - Import conftest fixtures
   - Check fixture scope

4. **"Flaky tests"**
   - Remove time dependencies
   - Mock random values
   - Ensure test isolation