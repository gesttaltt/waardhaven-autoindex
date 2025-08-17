# Frontend Utility Functions

## Overview
Helper functions and utilities for the frontend application.

## API Utilities

### API Client (api.ts)
Core API communication utilities.

#### Functions
- `apiClient.get()` - GET requests
- `apiClient.post()` - POST requests
- `apiClient.put()` - PUT requests
- `apiClient.delete()` - DELETE requests

#### Features
- Automatic token attachment
- Error handling
- Response transformation
- Retry logic
- Loading states

## Data Formatting

### Number Formatting
```typescript
formatCurrency(value: number, currency: string): string
formatPercentage(value: number, decimals: number): string
formatNumber(value: number, decimals: number): string
abbreviateNumber(value: number): string
```

### Date Formatting
```typescript
formatDate(date: Date, format: string): string
formatRelativeTime(date: Date): string
getDateRange(period: string): {start: Date, end: Date}
isMarketOpen(): boolean
```

## Calculation Helpers

### Portfolio Calculations
```typescript
calculateTotalValue(positions: Position[]): number
calculateDailyChange(current: number, previous: number): number
calculateReturns(prices: number[]): number[]
calculateVolatility(returns: number[]): number
```

### Performance Metrics
```typescript
calculateSharpeRatio(returns: number[], riskFreeRate: number): number
calculateMaxDrawdown(values: number[]): number
calculateCAGR(startValue: number, endValue: number, years: number): number
```

## Validation Utilities

### Form Validation
```typescript
validateEmail(email: string): boolean
validatePassword(password: string): ValidationResult
validateAmount(amount: string): boolean
validateSymbol(symbol: string): boolean
```

### Data Validation
```typescript
isValidPrice(price: number): boolean
isValidAllocation(weights: number[]): boolean
isValidDateRange(start: Date, end: Date): boolean
```

## Storage Utilities

### Local Storage
```typescript
saveToLocalStorage(key: string, value: any): void
getFromLocalStorage(key: string): any
removeFromLocalStorage(key: string): void
clearLocalStorage(): void
```

### Session Storage
```typescript
saveToSession(key: string, value: any): void
getFromSession(key: string): any
clearSession(): void
```

## Chart Helpers

### Data Transformation
```typescript
prepareChartData(data: any[]): ChartData
formatAxisLabel(value: number, type: string): string
generateColorPalette(count: number): string[]
calculateChartDomain(data: number[]): [number, number]
```

### Chart Configuration
```typescript
getChartConfig(type: ChartType): ChartConfig
getTooltipContent(data: any): string
getResponsiveConfig(width: number): ResponsiveConfig
```

## Authentication Helpers

### Token Management
```typescript
getAuthToken(): string | null
setAuthToken(token: string): void
removeAuthToken(): void
isTokenExpired(token: string): boolean
decodeToken(token: string): TokenPayload
```

### User Session
```typescript
getCurrentUser(): User | null
isAuthenticated(): boolean
hasPermission(permission: string): boolean
refreshToken(): Promise<string>
```

## UI Helpers

### Theme Utilities
```typescript
getCurrentTheme(): Theme
setTheme(theme: Theme): void
toggleTheme(): void
getThemeColors(): ThemeColors
```

### Responsive Helpers
```typescript
isMobile(): boolean
isTablet(): boolean
isDesktop(): boolean
getBreakpoint(): string
```

### Animation Helpers
```typescript
fadeIn(element: HTMLElement): void
slideDown(element: HTMLElement): void
smoothScroll(target: string): void
```

## Error Handling

### Error Utilities
```typescript
handleApiError(error: ApiError): ErrorMessage
logError(error: Error, context?: any): void
showErrorToast(message: string): void
getErrorMessage(code: string): string
```

### Retry Logic
```typescript
retryWithBackoff(fn: Function, retries: number): Promise<any>
exponentialBackoff(attempt: number): number
withTimeout(promise: Promise, timeout: number): Promise<any>
```

## Performance Utilities

### Debouncing & Throttling
```typescript
debounce(func: Function, delay: number): Function
throttle(func: Function, limit: number): Function
```

### Memoization
```typescript
memoize(func: Function): Function
clearMemoCache(func: Function): void
```

### Lazy Loading
```typescript
lazyLoad(componentPath: string): React.Component
preloadComponent(componentPath: string): void
```

## Type Guards

### Data Type Guards
```typescript
isUser(obj: any): obj is User
isPortfolio(obj: any): obj is Portfolio
isAsset(obj: any): obj is Asset
isValidResponse(response: any): boolean
```

## Constants

### API Endpoints
```typescript
const API_ENDPOINTS = {
  AUTH: '/api/v1/auth',
  PORTFOLIO: '/api/v1/portfolio',
  MARKET: '/api/v1/market',
  // ...
}
```

### Configuration
```typescript
const CONFIG = {
  REFRESH_INTERVAL: 60000,
  MAX_RETRIES: 3,
  TIMEOUT: 30000,
  // ...
}
```

## Testing Utilities

### Mock Data
```typescript
generateMockPortfolio(): Portfolio
generateMockPrices(count: number): Price[]
generateMockUser(): User
```

### Test Helpers
```typescript
renderWithProviders(component: React.Component): RenderResult
createMockStore(initialState: any): Store
waitForAsync(callback: Function): Promise<void>
```