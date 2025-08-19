# Testing Strategy Documentation

## Overview
Comprehensive testing strategy for Waardhaven AutoIndex covering unit, integration, end-to-end, and performance testing across both backend and frontend applications.

## Testing Philosophy
- **Test Pyramid**: More unit tests, fewer integration tests, minimal E2E tests
- **Coverage Target**: 80% for critical paths, 60% overall
- **Continuous Testing**: Tests run on every commit via CI/CD
- **Test-Driven Development**: Write tests before implementation for new features

## Backend Testing (FastAPI)

### Test Structure
```
apps/api/tests/
├── __init__.py
├── conftest.py                 # Shared fixtures
├── unit/                       # Unit tests
│   ├── test_models.py
│   ├── test_services.py
│   ├── test_utils.py
│   └── test_providers.py
├── integration/                # Integration tests
│   ├── test_api_endpoints.py
│   ├── test_database.py
│   └── test_external_apis.py
└── e2e/                       # End-to-end tests
    └── test_workflows.py
```

### Test Configuration

#### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --cov=app
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow tests
    external: Tests requiring external services
```

#### conftest.py
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with overridden dependencies."""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers(client):
    """Create authenticated headers for protected endpoints."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

### Unit Tests

#### Model Tests
```python
# tests/unit/test_models.py
import pytest
from datetime import datetime
from app.models import User, Asset, Portfolio

class TestUserModel:
    def test_user_creation(self):
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        assert user.email == "test@example.com"
        assert user.is_google_user is False
    
    def test_user_representation(self):
        user = User(email="test@example.com", password_hash="hash")
        assert str(user) == "<User(email='test@example.com', google=False)>"

class TestAssetModel:
    def test_asset_validation(self):
        asset = Asset(
            symbol="AAPL",
            name="Apple Inc.",
            asset_type="STOCK"
        )
        assert asset.symbol == "AAPL"
        assert asset.is_active is True
```

#### Service Tests
```python
# tests/unit/test_services.py
import pytest
from unittest.mock import Mock, patch
from app.services.performance import PerformanceService

class TestPerformanceService:
    @pytest.fixture
    def performance_service(self):
        return PerformanceService()
    
    def test_calculate_returns(self, performance_service):
        prices = [100, 105, 110, 108]
        returns = performance_service.calculate_returns(prices)
        
        assert len(returns) == 3
        assert returns[0] == pytest.approx(0.05, rel=1e-3)
        assert returns[1] == pytest.approx(0.0476, rel=1e-3)
        assert returns[2] == pytest.approx(-0.0182, rel=1e-3)
    
    def test_calculate_sharpe_ratio(self, performance_service):
        returns = [0.01, 0.02, -0.01, 0.03, 0.01]
        risk_free_rate = 0.02
        
        sharpe = performance_service.calculate_sharpe_ratio(
            returns, risk_free_rate
        )
        assert isinstance(sharpe, float)
        assert sharpe > -2 and sharpe < 5  # Reasonable range
    
    @patch('app.services.performance.get_risk_free_rate')
    def test_calculate_metrics_with_mock(self, mock_rate, performance_service):
        mock_rate.return_value = 0.03
        
        prices = [100, 105, 102, 108]
        metrics = performance_service.calculate_all_metrics(prices)
        
        assert 'returns' in metrics
        assert 'volatility' in metrics
        assert 'sharpe_ratio' in metrics
        mock_rate.assert_called_once()
```

#### Provider Tests
```python
# tests/unit/test_providers.py
import pytest
from unittest.mock import Mock, patch
from app.providers.market_data.twelvedata import TwelveDataProvider

class TestTwelveDataProvider:
    @pytest.fixture
    def provider(self):
        return TwelveDataProvider(api_key="test_key")
    
    @patch('requests.get')
    def test_fetch_price_success(self, mock_get, provider):
        mock_response = Mock()
        mock_response.json.return_value = {
            "values": [
                {"datetime": "2025-01-19", "close": "150.00"}
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        price = provider.fetch_price("AAPL", "2025-01-19")
        
        assert price == 150.00
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_fetch_price_api_error(self, mock_get, provider):
        mock_get.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            provider.fetch_price("AAPL", "2025-01-19")
```

### Integration Tests

#### API Endpoint Tests
```python
# tests/integration/test_api_endpoints.py
import pytest
from fastapi import status

class TestAuthEndpoints:
    def test_register_user(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123!"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert "user_id" in response.json()
    
    def test_login_valid_credentials(self, client, test_user):
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "testpass123"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()
    
    def test_login_invalid_credentials(self, client):
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrong@example.com",
                "password": "wrongpass"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

class TestPortfolioEndpoints:
    def test_get_portfolio_authenticated(self, client, auth_headers):
        response = client.get(
            "/api/v1/index/values",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert "values" in response.json()
    
    def test_get_portfolio_unauthenticated(self, client):
        response = client.get("/api/v1/index/values")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

#### Database Tests
```python
# tests/integration/test_database.py
import pytest
from sqlalchemy.orm import Session
from app.models import User, Asset, Price
from app.core.database import get_db

class TestDatabaseOperations:
    def test_user_crud(self, db_session: Session):
        # Create
        user = User(
            email="test@example.com",
            password_hash="hashed"
        )
        db_session.add(user)
        db_session.commit()
        
        # Read
        fetched_user = db_session.query(User).filter_by(
            email="test@example.com"
        ).first()
        assert fetched_user is not None
        assert fetched_user.email == "test@example.com"
        
        # Update
        fetched_user.is_google_user = True
        db_session.commit()
        
        updated_user = db_session.query(User).filter_by(
            email="test@example.com"
        ).first()
        assert updated_user.is_google_user is True
        
        # Delete
        db_session.delete(updated_user)
        db_session.commit()
        
        deleted_user = db_session.query(User).filter_by(
            email="test@example.com"
        ).first()
        assert deleted_user is None
    
    def test_cascade_delete(self, db_session: Session):
        # Create asset with prices
        asset = Asset(symbol="TEST", name="Test Asset")
        db_session.add(asset)
        db_session.commit()
        
        price1 = Price(asset_id=asset.id, date="2025-01-19", close=100)
        price2 = Price(asset_id=asset.id, date="2025-01-20", close=105)
        db_session.add_all([price1, price2])
        db_session.commit()
        
        # Delete asset should cascade to prices
        db_session.delete(asset)
        db_session.commit()
        
        prices = db_session.query(Price).filter_by(asset_id=asset.id).all()
        assert len(prices) == 0
```

### End-to-End Tests

```python
# tests/e2e/test_workflows.py
import pytest
from datetime import datetime, timedelta

class TestCompleteWorkflows:
    def test_user_registration_to_portfolio_creation(self, client):
        # 1. Register user
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "e2e@example.com",
                "password": "E2ETest123!"
            }
        )
        assert register_response.status_code == 201
        
        # 2. Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "e2e@example.com",
                "password": "E2ETest123!"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Configure strategy
        strategy_response = client.post(
            "/api/v1/strategy/update",
            headers=headers,
            json={
                "rebalance_frequency": "MONTHLY",
                "risk_level": "MODERATE"
            }
        )
        assert strategy_response.status_code == 200
        
        # 4. Compute index
        compute_response = client.post(
            "/api/v1/index/compute",
            headers=headers,
            json={
                "start_date": "2024-01-01",
                "end_date": "2024-12-31"
            }
        )
        assert compute_response.status_code == 200
        
        # 5. Get performance
        performance_response = client.get(
            "/api/v1/index/performance",
            headers=headers
        )
        assert performance_response.status_code == 200
        assert "returns" in performance_response.json()
```

## Frontend Testing (Next.js)

### Test Structure
```
apps/web/
├── __tests__/
│   ├── unit/                  # Unit tests
│   │   ├── domain/
│   │   ├── hooks/
│   │   └── utils/
│   ├── integration/           # Integration tests
│   │   ├── api/
│   │   └── components/
│   └── e2e/                   # E2E tests
│       └── flows/
├── jest.config.js
├── jest.setup.js
└── playwright.config.ts
```

### Jest Configuration

#### jest.config.js
```javascript
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  roots: ['<rootDir>'],
  testMatch: ['**/__tests__/**/*.test.{ts,tsx}'],
  transform: {
    '^.+\\.tsx?$': ['ts-jest', {
      tsconfig: {
        jsx: 'react-jsx',
      },
    }],
  },
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/app/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
  },
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  collectCoverageFrom: [
    'app/**/*.{ts,tsx}',
    '!app/**/*.d.ts',
    '!app/**/*.stories.tsx',
  ],
  coverageThresholds: {
    global: {
      branches: 60,
      functions: 60,
      lines: 60,
      statements: 60,
    },
  },
};
```

#### jest.setup.js
```javascript
import '@testing-library/jest-dom';
import { TextEncoder, TextDecoder } from 'util';

// Polyfills for Node environment
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
  useSearchParams: () => ({
    get: jest.fn(),
  }),
  usePathname: () => '',
}));
```

### Unit Tests

#### Domain Entity Tests
```typescript
// __tests__/unit/domain/Portfolio.test.ts
import { Portfolio, RiskLevel } from '@/core/domain/entities/Portfolio';

describe('Portfolio Entity', () => {
  it('should create portfolio with correct properties', () => {
    const portfolio = new Portfolio(
      '1',
      'My Portfolio',
      100000,
      [],
      {
        totalReturn: 0.15,
        volatility: 0.12,
        sharpe: 1.25,
      }
    );

    expect(portfolio.id).toBe('1');
    expect(portfolio.name).toBe('My Portfolio');
    expect(portfolio.totalValue).toBe(100000);
  });

  it('should calculate risk level based on volatility', () => {
    const lowRiskPortfolio = new Portfolio('1', 'Low Risk', 100000, [], {
      totalReturn: 0.05,
      volatility: 0.05,
      sharpe: 1.0,
    });

    const highRiskPortfolio = new Portfolio('2', 'High Risk', 100000, [], {
      totalReturn: 0.25,
      volatility: 0.25,
      sharpe: 1.0,
    });

    expect(lowRiskPortfolio.riskLevel).toBe(RiskLevel.LOW);
    expect(highRiskPortfolio.riskLevel).toBe(RiskLevel.HIGH);
  });
});
```

#### Hook Tests
```typescript
// __tests__/unit/hooks/usePortfolio.test.tsx
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { usePortfolio } from '@/hooks/usePortfolio';

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
  
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('usePortfolio', () => {
  it('should fetch portfolio data', async () => {
    const { result } = renderHook(() => usePortfolio('123'), {
      wrapper: createWrapper(),
    });

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toBeDefined();
  });

  it('should handle fetch error', async () => {
    // Mock API error
    global.fetch = jest.fn(() =>
      Promise.reject(new Error('API Error'))
    );

    const { result } = renderHook(() => usePortfolio('invalid'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
  });
});
```

### Integration Tests

#### Component Tests
```typescript
// __tests__/integration/components/Dashboard.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Dashboard } from '@/app/dashboard/page';
import { AuthProvider } from '@/contexts/AuthContext';

const MockedProviders = ({ children }: { children: React.ReactNode }) => (
  <AuthProvider>
    {children}
  </AuthProvider>
);

describe('Dashboard Component', () => {
  it('should render dashboard with user data', async () => {
    render(
      <MockedProviders>
        <Dashboard />
      </MockedProviders>
    );

    await waitFor(() => {
      expect(screen.getByText('Portfolio Overview')).toBeInTheDocument();
    });

    expect(screen.getByText('Total Value')).toBeInTheDocument();
    expect(screen.getByText('Performance')).toBeInTheDocument();
  });

  it('should handle refresh button click', async () => {
    const user = userEvent.setup();
    
    render(
      <MockedProviders>
        <Dashboard />
      </MockedProviders>
    );

    const refreshButton = await screen.findByRole('button', {
      name: /refresh/i,
    });

    await user.click(refreshButton);

    await waitFor(() => {
      expect(screen.getByText('Refreshing...')).toBeInTheDocument();
    });
  });
});
```

#### API Integration Tests
```typescript
// __tests__/integration/api/PortfolioService.test.ts
import { PortfolioService } from '@/services/api/portfolio';
import { ApiClient } from '@/core/infrastructure/api/ApiClient';

describe('PortfolioService Integration', () => {
  let service: PortfolioService;
  let apiClient: ApiClient;

  beforeEach(() => {
    apiClient = new ApiClient(process.env.NEXT_PUBLIC_API_URL!);
    service = new PortfolioService(apiClient);
  });

  it('should fetch portfolio data from API', async () => {
    const portfolio = await service.getPortfolio('test-id');
    
    expect(portfolio).toBeDefined();
    expect(portfolio.id).toBe('test-id');
    expect(portfolio.allocations).toBeInstanceOf(Array);
  });

  it('should update portfolio allocations', async () => {
    const newAllocations = [
      { symbol: 'AAPL', weight: 0.3 },
      { symbol: 'GOOGL', weight: 0.3 },
      { symbol: 'MSFT', weight: 0.4 },
    ];

    const result = await service.updateAllocations('test-id', newAllocations);
    
    expect(result.success).toBe(true);
  });
});
```

### End-to-End Tests (Playwright)

#### playwright.config.ts
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './__tests__/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

#### E2E Test Example
```typescript
// __tests__/e2e/flows/user-journey.spec.ts
import { test, expect } from '@playwright/test';

test.describe('User Journey', () => {
  test('complete user flow from login to portfolio view', async ({ page }) => {
    // Navigate to login
    await page.goto('/login');
    
    // Fill login form
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'TestPass123!');
    await page.click('button[type="submit"]');
    
    // Wait for navigation to dashboard
    await page.waitForURL('/dashboard');
    
    // Verify dashboard elements
    await expect(page.locator('h1')).toContainText('Dashboard');
    await expect(page.locator('[data-testid="portfolio-value"]')).toBeVisible();
    
    // Navigate to strategy configuration
    await page.click('a[href="/strategy"]');
    await page.waitForURL('/strategy');
    
    // Update strategy
    await page.selectOption('select[name="risk_level"]', 'AGGRESSIVE');
    await page.click('button:has-text("Save Strategy")');
    
    // Verify success message
    await expect(page.locator('.toast-success')).toContainText('Strategy updated');
    
    // Navigate back to dashboard
    await page.click('a[href="/dashboard"]');
    
    // Trigger data refresh
    await page.click('button:has-text("Refresh Data")');
    
    // Wait for refresh to complete
    await page.waitForSelector('[data-testid="refresh-complete"]');
    
    // Verify updated data
    await expect(page.locator('[data-testid="last-updated"]')).toContainText('Just now');
  });

  test('should handle authentication errors', async ({ page }) => {
    await page.goto('/login');
    
    // Try invalid credentials
    await page.fill('input[name="email"]', 'wrong@example.com');
    await page.fill('input[name="password"]', 'WrongPass');
    await page.click('button[type="submit"]');
    
    // Verify error message
    await expect(page.locator('.error-message')).toContainText('Invalid credentials');
    
    // Should stay on login page
    await expect(page).toHaveURL('/login');
  });
});
```

## Performance Testing

### Load Testing with k6
```javascript
// k6/load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 20 },  // Ramp up
    { duration: '1m', target: 20 },   // Stay at 20 users
    { duration: '30s', target: 0 },   // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
    http_req_failed: ['rate<0.1'],    // Error rate under 10%
  },
};

export default function () {
  // Login
  const loginRes = http.post(
    'http://localhost:8000/api/v1/auth/login',
    JSON.stringify({
      email: 'test@example.com',
      password: 'testpass123',
    }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  
  check(loginRes, {
    'login successful': (r) => r.status === 200,
  });
  
  const token = loginRes.json('access_token');
  
  // Get portfolio
  const portfolioRes = http.get(
    'http://localhost:8000/api/v1/index/values',
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
  
  check(portfolioRes, {
    'portfolio fetched': (r) => r.status === 200,
    'has values': (r) => JSON.parse(r.body).values.length > 0,
  });
  
  sleep(1);
}
```

## CI/CD Integration

### GitHub Actions Workflow
```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        working-directory: ./apps/api
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      
      - name: Run tests with coverage
        working-directory: ./apps/api
        run: |
          pytest --cov=app --cov-report=xml --cov-report=term
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./apps/api/coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install dependencies
        working-directory: ./apps/web
        run: npm ci
      
      - name: Run unit tests
        working-directory: ./apps/web
        run: npm test -- --coverage
      
      - name: Run E2E tests
        working-directory: ./apps/web
        run: |
          npx playwright install
          npm run test:e2e
```

## Test Commands

### Backend
```bash
# Run all tests
npm run test:api

# Run with coverage
npm run test:api:coverage

# Run specific marker
cd apps/api && pytest -m unit
cd apps/api && pytest -m integration

# Run specific file
cd apps/api && pytest tests/unit/test_services.py

# Run with verbose output
cd apps/api && pytest -vv
```

### Frontend
```bash
# Run unit tests
cd apps/web && npm test

# Run with coverage
cd apps/web && npm test -- --coverage

# Run in watch mode
cd apps/web && npm test -- --watch

# Run E2E tests
cd apps/web && npm run test:e2e

# Run E2E with UI
cd apps/web && npx playwright test --ui
```

## Coverage Reports
- Backend: `apps/api/htmlcov/index.html`
- Frontend: `apps/web/coverage/lcov-report/index.html`
- CI/CD: Available in GitHub Actions artifacts

## Best Practices

### 1. Test Naming
- Use descriptive test names
- Follow pattern: `test_<what>_<condition>_<expected>`
- Group related tests in classes or describe blocks

### 2. Test Data
- Use factories for test data creation
- Keep test data minimal but realistic
- Clean up after tests

### 3. Mocking
- Mock external dependencies
- Use dependency injection for testability
- Keep mocks simple and focused

### 4. Assertions
- One logical assertion per test
- Use appropriate matchers
- Include helpful error messages

### 5. Performance
- Keep tests fast (< 100ms for unit tests)
- Use parallel execution where possible
- Cache dependencies in CI/CD