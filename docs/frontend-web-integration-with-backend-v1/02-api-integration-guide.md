# API Integration Guide

## Overview

The frontend integrates with the FastAPI backend through a structured service layer that provides type-safe API calls with built-in error handling, authentication, and retry logic.

## API Client Architecture

```
┌──────────────────────────────────────┐
│         Component/Page               │
├──────────────────────────────────────┤
│         Service Layer                │
│   (portfolioService, newsService)   │
├──────────────────────────────────────┤
│         Base ApiService              │
├──────────────────────────────────────┤
│         HTTP Client                  │
├──────────────────────────────────────┤
│      Request Interceptors            │
├──────────────────────────────────────┤
│         Fetch API                    │
└──────────────────────────────────────┘
```

## Core Components

### 1. HttpClient (`app/core/infrastructure/api/HttpClient.ts`)

The foundation of all API communications with interceptor support.

```typescript
export class HttpClient {
  private baseURL: string;
  private defaultHeaders: Record<string, string>;
  private requestInterceptors: Interceptor<RequestConfig>[] = [];
  private responseInterceptors: Interceptor<Response>[] = [];

  async request<T>(
    method: string,
    endpoint: string,
    data?: any,
    config: RequestConfig = {}
  ): Promise<Response<T>> {
    // Apply request interceptors
    const finalConfig = await this.applyRequestInterceptors(config);
    
    // Build URL with params
    const url = this.buildURL(endpoint, finalConfig.params);
    
    // Make request
    const response = await fetch(url, fetchConfig);
    
    // Apply response interceptors
    return await this.applyResponseInterceptors(httpResponse);
  }
}
```

### 2. ApiClient Singleton (`app/core/infrastructure/api/ApiClient.ts`)

Configured HTTP client with authentication and retry logic.

```typescript
export class ApiClient {
  private static instance: ApiClient;
  private httpClient: HttpClient;
  private tokenManager: TokenManager;

  private setupInterceptors() {
    // Auth token interceptor
    this.httpClient.addRequestInterceptor({
      onRequest: (config) => {
        const token = this.tokenManager.getAccessToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      }
    });

    // Token refresh interceptor
    this.httpClient.addResponseInterceptor({
      onError: async (error: HttpError) => {
        if (error.status === 401) {
          // Attempt token refresh
          const refreshToken = this.tokenManager.getRefreshToken();
          if (refreshToken) {
            // Refresh and retry
          }
        }
        throw error;
      }
    });
  }
}
```

### 3. Base ApiService (`app/services/api/base.ts`)

Base class for all service implementations.

```typescript
export class ApiService {
  protected baseUrl: string;

  protected async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });
    return this.handleResponse<T>(response);
  }

  protected async post<T>(endpoint: string, data?: any): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: data ? JSON.stringify(data) : undefined,
    });
    return this.handleResponse<T>(response);
  }

  protected async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error = await this.parseError(response);
      throw error;
    }
    return await response.json();
  }
}
```

## Service Implementations

### Portfolio Service (`app/services/api/portfolio.ts`)

```typescript
class PortfolioService extends ApiService {
  async getIndexHistory(): Promise<IndexHistoryResponse> {
    return this.get<IndexHistoryResponse>('/api/v1/index/history');
  }

  async getCurrentAllocations(): Promise<IndexCurrentResponse> {
    return this.get<IndexCurrentResponse>('/api/v1/index/current');
  }

  async runSimulation(request: SimulationRequest): Promise<SimulationResponse> {
    return this.post<SimulationResponse>('/api/v1/index/simulate', {
      amount: request.amount,
      start_date: request.startDate,
      currency: request.currency,
    });
  }

  async getCurrencies(): Promise<CurrencyMap> {
    return this.get<CurrencyMap>('/api/v1/index/currencies');
  }
}

export const portfolioService = new PortfolioService();
```

### News Service (`app/services/api/news.ts`)

```typescript
class NewsService extends ApiService {
  async searchNews(params: {
    symbols?: string[];
    keywords?: string;
    sentimentMin?: number;
    sentimentMax?: number;
    limit?: number;
  }): Promise<NewsArticle[]> {
    const queryParams = new URLSearchParams();
    
    if (params.symbols?.length) {
      queryParams.append('symbols', params.symbols.join(','));
    }
    // ... build other params
    
    return this.get<NewsArticle[]>(`/api/v1/news/search?${queryParams}`);
  }

  async getEntitySentiment(symbol: string): Promise<EntitySentiment> {
    return this.get<EntitySentiment>(`/api/v1/news/sentiment/${symbol}`);
  }

  async getTrendingEntities(): Promise<TrendingEntity[]> {
    return this.get<TrendingEntity[]>('/api/v1/news/trending');
  }
}

export const newsService = new NewsService();
```

## Request Interceptors

### Authentication Interceptor
Automatically adds JWT token to requests:

```typescript
{
  onRequest: (config) => {
    const token = this.tokenManager.getAccessToken();
    if (token) {
      config.headers = {
        ...config.headers,
        Authorization: `Bearer ${token}`
      };
    }
    return config;
  }
}
```

### Request ID Interceptor
Adds unique ID for request tracking:

```typescript
{
  onRequest: (config) => {
    config.headers = {
      ...config.headers,
      'X-Request-ID': `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    };
    return config;
  }
}
```

## Response Interceptors

### Token Refresh Interceptor
Handles 401 errors by refreshing tokens:

```typescript
{
  onError: async (error: HttpError) => {
    if (error.status === 401) {
      const refreshToken = this.tokenManager.getRefreshToken();
      if (refreshToken) {
        try {
          const response = await this.httpClient.post('/api/v1/auth/refresh', {
            refresh_token: refreshToken
          });
          
          this.tokenManager.setTokens(response.data);
          // Retry original request
          return Promise.resolve(response);
        } catch (refreshError) {
          this.tokenManager.clearTokens();
          window.location.href = '/login';
        }
      }
    }
    throw error;
  }
}
```

## Error Handling

### Error Types

```typescript
export interface HttpError {
  message: string;
  status?: number;
  code?: string;
  details?: any;
}

export interface ApiError {
  message: string;
  status: number;
  detail?: string;
}
```

### Error Handling Flow

1. **API returns error** → Response interceptor checks status
2. **401 Unauthorized** → Attempt token refresh
3. **Token refresh fails** → Redirect to login
4. **Other errors** → Propagate to component

### Component Error Handling

```typescript
const MyComponent = () => {
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      const data = await portfolioService.getIndexHistory();
      // Handle success
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    }
  };
};
```

## Usage Patterns

### Basic GET Request

```typescript
// In component
const data = await portfolioService.getIndexHistory();
```

### POST with Data

```typescript
const result = await portfolioService.runSimulation({
  amount: 10000,
  startDate: '2024-01-01',
  currency: 'USD'
});
```

### Query Parameters

```typescript
const news = await newsService.searchNews({
  symbols: ['AAPL', 'GOOGL'],
  sentimentMin: 0.5,
  limit: 50
});
```

### With Loading State

```typescript
const [loading, setLoading] = useState(false);

const fetchData = async () => {
  setLoading(true);
  try {
    const data = await portfolioService.getCurrentAllocations();
    setAllocations(data.allocations);
  } finally {
    setLoading(false);
  }
};
```

## Custom Hooks for API Calls

### useApiRequest Hook

```typescript
export function useApiRequest<T>(
  apiFunction: (...args: any[]) => Promise<T>,
  options: UseApiRequestOptions = {}
): UseApiRequestResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<HttpError | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const execute = useCallback(async (...args: any[]): Promise<T | null> => {
    setIsLoading(true);
    setError(null);

    let attempt = 0;
    while (attempt <= retryCount) {
      try {
        const result = await apiFunction(...args);
        setData(result);
        return result;
      } catch (err) {
        if (attempt < retryCount) {
          await new Promise(resolve => setTimeout(resolve, retryDelay));
          attempt++;
        } else {
          setError(err as HttpError);
          return null;
        }
      }
    }
    setIsLoading(false);
  }, [apiFunction, retryCount, retryDelay]);

  return { data, error, isLoading, execute, reset };
}
```

### Usage with Hook

```typescript
const MyComponent = () => {
  const { data, error, isLoading, execute } = useApiRequest(
    portfolioService.getIndexHistory,
    { retryCount: 2, retryDelay: 1000 }
  );

  useEffect(() => {
    execute();
  }, []);

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  if (!data) return null;

  return <DataDisplay data={data} />;
};
```

## Environment Configuration

```env
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000

# .env.production
NEXT_PUBLIC_API_URL=https://api.waardhaven.com
```

## API Endpoints Reference

See [API Endpoints Reference](./15-api-endpoints-reference.md) for complete endpoint documentation.

## Best Practices

1. **Always handle errors** - Never assume API calls will succeed
2. **Use loading states** - Show feedback during API calls
3. **Implement retry logic** - For transient failures
4. **Cache when appropriate** - Use React Query for caching
5. **Type everything** - Full TypeScript coverage
6. **Validate responses** - Don't trust API data blindly
7. **Log errors** - For debugging and monitoring

## Testing API Integration

```typescript
// Mock service for testing
class MockPortfolioService extends PortfolioService {
  async getIndexHistory(): Promise<IndexHistoryResponse> {
    return Promise.resolve({
      series: [{ date: '2024-01-01', value: 100 }]
    });
  }
}

// In test
const mockService = new MockPortfolioService();
const result = await mockService.getIndexHistory();
expect(result.series).toHaveLength(1);
```

## Next Steps

- Learn about [Authentication System](./03-authentication-system.md)
- Review [Service Layer Documentation](./04-service-layer.md)
- Understand [Error Handling](./08-error-handling.md)