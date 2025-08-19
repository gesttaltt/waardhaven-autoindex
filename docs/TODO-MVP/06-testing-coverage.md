# Testing Coverage Expansion

**Priority**: P1 - HIGH  
**Status**: 🟡 Basic (25% coverage)  
**Estimated**: 2 days  
**Current**: 16 tests across 9 files  
**Target**: 80% coverage with comprehensive test suite

## 🎯 Objective

Build comprehensive test coverage to ensure:
- Code reliability and stability
- Safe refactoring capability
- Regression prevention
- Documentation through tests
- CI/CD confidence

## 📋 Current State

### Backend (FastAPI)
- ✅ 9 test files exist
- ✅ 16 basic tests
- 🔴 ~25% coverage
- 🔴 No integration tests
- 🔴 No performance tests

### Frontend (Next.js)
- 🔴 No test files
- 🔴 0% coverage
- 🔴 No component tests
- 🔴 No E2E tests

## 📋 Task Breakdown

### Phase 1: Backend Unit Tests (6 hours)

#### Task 1.1: Service Layer Tests
**Directory**: `apps/api/tests/unit/services/`

```python
# Test files to create:
- [ ] test_calculation_service.py
- [ ] test_twelvedata_service.py
- [ ] test_marketaux_service.py
- [ ] test_portfolio_service.py
- [ ] test_allocation_service.py
```

#### Task 1.2: Model Tests
**Directory**: `apps/api/tests/unit/models/`

```python
# Test files to create:
- [ ] test_user_model.py
- [ ] test_asset_model.py
- [ ] test_price_model.py
- [ ] test_allocation_model.py
- [ ] test_index_model.py
```

#### Task 1.3: Schema Tests
**Directory**: `apps/api/tests/unit/schemas/`

```python
# Test validation:
- [ ] Input validation
- [ ] Output serialization
- [ ] Edge cases
- [ ] Type checking
```

### Phase 2: Backend Integration Tests (4 hours)

#### Task 2.1: API Endpoint Tests
**Directory**: `apps/api/tests/integration/`

```python
# Test files to create:
- [ ] test_auth_endpoints.py
- [ ] test_portfolio_endpoints.py
- [ ] test_calculation_endpoints.py
- [ ] test_market_data_endpoints.py
- [ ] test_news_endpoints.py
```

#### Task 2.2: Database Tests
```python
# Test scenarios:
- [ ] Transaction rollback
- [ ] Concurrent access
- [ ] Migration testing
- [ ] Data integrity
```

#### Task 2.3: External API Tests
```python
# Mock external services:
- [ ] TwelveData responses
- [ ] Marketaux responses
- [ ] Error scenarios
- [ ] Rate limiting
```

### Phase 3: Frontend Unit Tests (6 hours)

#### Task 3.1: Component Tests
**Directory**: `apps/web/tests/components/`

```typescript
# Test files to create:
- [ ] Dashboard.test.tsx
- [ ] Portfolio.test.tsx
- [ ] PerformanceChart.test.tsx
- [ ] AllocationTable.test.tsx
- [ ] Navigation.test.tsx
```

#### Task 3.2: Hook Tests
**Directory**: `apps/web/tests/hooks/`

```typescript
# Test custom hooks:
- [ ] useAuth.test.ts
- [ ] usePortfolio.test.ts
- [ ] useCalculations.test.ts
- [ ] useMarketData.test.ts
```

#### Task 3.3: Utility Tests
```typescript
# Test utilities:
- [ ] formatters.test.ts
- [ ] validators.test.ts
- [ ] api-client.test.ts
```

### Phase 4: Frontend Integration Tests (4 hours)

#### Task 4.1: Page Tests
**Directory**: `apps/web/tests/pages/`

```typescript
# Test pages:
- [ ] login.test.tsx
- [ ] dashboard.test.tsx
- [ ] portfolio.test.tsx
- [ ] settings.test.tsx
```

#### Task 4.2: User Flow Tests
```typescript
# Test flows:
- [ ] Login → Dashboard
- [ ] Create portfolio
- [ ] Update allocations
- [ ] View performance
```

### Phase 5: E2E Tests (4 hours)

#### Task 5.1: Playwright Setup
```bash
npm install --save-dev @playwright/test
npx playwright install
```

#### Task 5.2: E2E Scenarios
**Directory**: `tests/e2e/`

```typescript
# Test scenarios:
- [ ] Complete user journey
- [ ] Portfolio management
- [ ] Data refresh
- [ ] Error recovery
```

### Phase 6: Performance Tests (2 hours)

#### Task 6.1: Load Testing
**File**: `tests/performance/load_test.py`

```python
# Using locust:
- [ ] API endpoint load
- [ ] Concurrent users
- [ ] Database stress
- [ ] Cache performance
```

#### Task 6.2: Benchmark Tests
```python
# Measure:
- [ ] Calculation speed
- [ ] Query performance
- [ ] Response times
- [ ] Memory usage
```

## 📊 Test Implementation Examples

### Backend Service Test

```python
# apps/api/tests/unit/services/test_calculation_service.py

import pytest
import numpy as np
from datetime import datetime, timedelta
from app.services.calculations import CalculationService

class TestCalculationService:
    
    @pytest.fixture
    def service(self, db_session):
        return CalculationService(db_session)
    
    @pytest.fixture
    def sample_prices(self):
        return [100, 102, 98, 105, 110, 108, 115]
    
    def test_calculate_returns(self, service, sample_prices):
        """Test return calculation accuracy"""
        result = service.calculate_returns(sample_prices)
        
        assert 'daily' in result
        assert 'total' in result
        assert 'annualized' in result
        
        # Check total return calculation
        expected_total = (115 - 100) / 100  # 15% return
        assert abs(result['total'] - expected_total) < 0.001
        
        # Check daily returns length
        assert len(result['daily']) == len(sample_prices) - 1
    
    def test_calculate_volatility(self, service, sample_prices):
        """Test volatility calculation"""
        returns = service.calculate_returns(sample_prices)
        volatility = service.calculate_volatility(returns['daily'])
        
        assert volatility > 0
        assert isinstance(volatility, float)
    
    def test_calculate_sharpe_ratio(self, service, sample_prices):
        """Test Sharpe ratio calculation"""
        returns = service.calculate_returns(sample_prices)
        sharpe = service.calculate_sharpe_ratio(
            returns['daily'],
            risk_free_rate=0.02
        )
        
        assert isinstance(sharpe, float)
        # Sharpe should be reasonable
        assert -5 < sharpe < 5
    
    def test_calculate_max_drawdown(self, service, sample_prices):
        """Test maximum drawdown calculation"""
        max_dd, current_dd = service.calculate_max_drawdown(sample_prices)
        
        assert 0 <= max_dd <= 1  # Percentage
        assert 0 <= current_dd <= 1
        
        # For this sample, max drawdown should be from 102 to 98
        expected_max_dd = (102 - 98) / 102
        assert abs(max_dd - expected_max_dd) < 0.01
    
    @pytest.mark.parametrize("prices,expected", [
        ([], {'daily': [], 'total': 0, 'annualized': 0}),
        ([100], {'daily': [], 'total': 0, 'annualized': 0}),
        ([100, 100], {'daily': [0], 'total': 0, 'annualized': 0}),
    ])
    def test_edge_cases(self, service, prices, expected):
        """Test edge cases with empty or single price"""
        result = service.calculate_returns(prices)
        
        assert result['total'] == expected['total']
        assert len(result['daily']) == len(expected['daily'])
```

### Frontend Component Test

```typescript
// apps/web/tests/components/Dashboard.test.tsx

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Dashboard from '@/app/dashboard/page';
import { mockPortfolioData } from '../mocks/portfolio';

// Mock the API calls
jest.mock('@/services/api/portfolio', () => ({
  portfolioApi: {
    getPortfolio: jest.fn().mockResolvedValue(mockPortfolioData),
    getMetrics: jest.fn().mockResolvedValue({
      totalValue: 100000,
      dailyReturn: 0.02,
      totalReturn: 0.15,
    }),
  },
}));

describe('Dashboard', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });
  });

  const renderDashboard = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <Dashboard />
      </QueryClientProvider>
    );
  };

  it('renders dashboard components', async () => {
    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText('Portfolio Overview')).toBeInTheDocument();
      expect(screen.getByText('Performance Chart')).toBeInTheDocument();
      expect(screen.getByText('Asset Allocation')).toBeInTheDocument();
    });
  });

  it('displays portfolio metrics', async () => {
    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText('$100,000')).toBeInTheDocument();
      expect(screen.getByText('+2.00%')).toBeInTheDocument();
      expect(screen.getByText('+15.00%')).toBeInTheDocument();
    });
  });

  it('handles refresh button click', async () => {
    const user = userEvent.setup();
    renderDashboard();

    const refreshButton = await screen.findByRole('button', { name: /refresh/i });
    await user.click(refreshButton);

    // Check that API was called again
    expect(portfolioApi.getPortfolio).toHaveBeenCalledTimes(2);
  });

  it('shows loading state', () => {
    renderDashboard();
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  it('handles error state', async () => {
    portfolioApi.getPortfolio.mockRejectedValueOnce(new Error('API Error'));
    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText('Failed to load portfolio')).toBeInTheDocument();
    });
  });
});
```

### E2E Test

```typescript
// tests/e2e/portfolio-management.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Portfolio Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('[type="submit"]');
    
    // Wait for redirect to dashboard
    await page.waitForURL('/dashboard');
  });

  test('create new portfolio', async ({ page }) => {
    await page.click('text=Create Portfolio');
    
    // Fill portfolio form
    await page.fill('[name="name"]', 'Test Portfolio');
    await page.fill('[name="initialValue"]', '10000');
    
    // Add assets
    await page.click('text=Add Asset');
    await page.fill('[name="symbol"]', 'AAPL');
    await page.fill('[name="allocation"]', '50');
    
    await page.click('text=Add Asset');
    await page.fill('[name="symbol"]', 'GOOGL');
    await page.fill('[name="allocation"]', '50');
    
    // Submit
    await page.click('text=Create');
    
    // Verify portfolio created
    await expect(page.locator('text=Test Portfolio')).toBeVisible();
    await expect(page.locator('text=$10,000')).toBeVisible();
  });

  test('update allocations', async ({ page }) => {
    await page.click('text=Manage Portfolio');
    
    // Update allocation
    const appleAllocation = page.locator('[data-asset="AAPL"] input');
    await appleAllocation.clear();
    await appleAllocation.fill('60');
    
    const googleAllocation = page.locator('[data-asset="GOOGL"] input');
    await googleAllocation.clear();
    await googleAllocation.fill('40');
    
    await page.click('text=Save Changes');
    
    // Verify update
    await expect(page.locator('text=Allocations updated')).toBeVisible();
  });

  test('view performance metrics', async ({ page }) => {
    await page.click('text=Performance');
    
    // Check metrics are displayed
    await expect(page.locator('[data-metric="total-return"]')).toBeVisible();
    await expect(page.locator('[data-metric="volatility"]')).toBeVisible();
    await expect(page.locator('[data-metric="sharpe-ratio"]')).toBeVisible();
    
    // Check chart is rendered
    await expect(page.locator('canvas')).toBeVisible();
  });
});
```

## 🧪 Testing Infrastructure

### Test Configuration

```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/app/$1',
  },
  collectCoverageFrom: [
    'app/**/*.{js,jsx,ts,tsx}',
    '!app/**/*.d.ts',
    '!app/**/*.stories.tsx',
  ],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },
};
```

### GitHub Actions Test Job

```yaml
# .github/workflows/test.yml
test-coverage:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    
    - name: Run backend tests with coverage
      run: |
        cd apps/api
        pytest --cov=app --cov-report=xml --cov-report=html
    
    - name: Run frontend tests with coverage
      run: |
        cd apps/web
        npm run test:coverage
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        files: ./apps/api/coverage.xml,./apps/web/coverage/lcov.info
    
    - name: Comment PR with coverage
      uses: py-cov-action/python-coverage-comment-action@v3
      with:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 📈 Success Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Backend coverage | 25% | 80% | 🔴 |
| Frontend coverage | 0% | 70% | 🔴 |
| E2E tests | 0 | 10+ | 🔴 |
| Test execution time | N/A | <5min | 🔴 |
| Flaky tests | Unknown | 0 | 🔴 |

## 🔄 Testing Dependencies

### Backend
```txt
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-asyncio>=0.21.0
pytest-mock>=3.11.0
factory-boy>=3.3.0
faker>=19.0.0
httpx>=0.24.0
locust>=2.15.0
```

### Frontend
```json
{
  "devDependencies": {
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0",
    "@testing-library/user-event": "^14.0.0",
    "@playwright/test": "^1.40.0",
    "jest": "^29.0.0",
    "jest-environment-jsdom": "^29.0.0",
    "msw": "^2.0.0"
  }
}
```

---

**Next**: Continue with [07-security-monitoring.md](./07-security-monitoring.md)