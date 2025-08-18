# Testing Guide

## Testing Strategy

### Test Pyramid
- **Unit Tests** (70%) - Individual functions and components
- **Integration Tests** (20%) - Service interactions
- **E2E Tests** (10%) - Critical user flows

## Unit Testing

### Component Testing
```typescript
// __tests__/LoginForm.test.tsx
describe('LoginForm', () => {
  it('validates email format', async () => {
    const { getByLabelText, getByText } = render(<LoginForm />);
    const emailInput = getByLabelText(/email/i);
    
    fireEvent.change(emailInput, { target: { value: 'invalid' } });
    fireEvent.blur(emailInput);
    
    expect(getByText(/invalid email/i)).toBeInTheDocument();
  });
});
```

### Service Testing
```typescript
// __tests__/portfolioService.test.ts
describe('PortfolioService', () => {
  it('fetches index history', async () => {
    const mockData = { series: [{ date: '2024-01-01', value: 100 }] };
    fetchMock.mockResponseOnce(JSON.stringify(mockData));
    
    const result = await portfolioService.getIndexHistory();
    expect(result.series).toHaveLength(1);
  });
});
```

## Integration Testing

### API Integration
```typescript
// __tests__/integration/auth.test.ts
describe('Authentication Flow', () => {
  it('completes login flow', async () => {
    const response = await request(app)
      .post('/api/v1/auth/login')
      .send({ email: 'test@example.com', password: 'password' });
    
    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('access_token');
  });
});
```

## E2E Testing

### Playwright Setup
```typescript
// e2e/login.spec.ts
test('user can login', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[name=email]', 'test@example.com');
  await page.fill('[name=password]', 'password');
  await page.click('button[type=submit]');
  
  await expect(page).toHaveURL('/dashboard');
});
```

## Test Configuration

### Jest Config
```javascript
// jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/app/$1',
  },
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

## Mocking

### API Mocking
```typescript
// __mocks__/api.ts
export const mockApi = {
  get: jest.fn().mockResolvedValue({ data: {} }),
  post: jest.fn().mockResolvedValue({ data: {} }),
};
```

### Component Mocking
```typescript
jest.mock('../components/Chart', () => ({
  Chart: () => <div>Mock Chart</div>,
}));
```

## Testing Utilities

### Custom Render
```typescript
// test-utils.tsx
const customRender = (ui: ReactElement, options = {}) =>
  render(ui, {
    wrapper: ({ children }) => (
      <QueryClientProvider client={queryClient}>
        <AuthProvider>{children}</AuthProvider>
      </QueryClientProvider>
    ),
    ...options,
  });
```

## CI/CD Testing

### GitHub Actions
```yaml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm ci
      - run: npm test -- --coverage
      - run: npm run e2e
```

## Best Practices
- Test behavior, not implementation
- Use descriptive test names
- Keep tests isolated
- Mock external dependencies
- Test error scenarios
- Maintain test coverage above 70%