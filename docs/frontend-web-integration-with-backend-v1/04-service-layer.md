# Service Layer Documentation

## Overview

The service layer provides a clean, type-safe interface between the frontend components and the backend API. Each service is responsible for a specific domain of the application, encapsulating API calls and data transformations.

## Service Architecture

```
┌─────────────────────────────────────────┐
│           React Components              │
├─────────────────────────────────────────┤
│      Domain-Specific Services           │
│  (Portfolio, News, Strategy, etc.)      │
├─────────────────────────────────────────┤
│         Base ApiService Class           │
├─────────────────────────────────────────┤
│      HTTP Client / Fetch API            │
└─────────────────────────────────────────┘
```

## Base Service Class

### ApiService (`app/services/api/base.ts`)

All services extend this base class which provides common HTTP methods and error handling.

```typescript
export class ApiService {
  protected baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  protected getAuthHeaders(): HeadersInit {
    const token = typeof window !== 'undefined' 
      ? localStorage.getItem('token') 
      : null;
    
    return token
      ? {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        }
      : {
          'Content-Type': 'application/json',
        };
  }

  protected async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error: ApiError = {
        message: 'API request failed',
        status: response.status,
      };

      try {
        const errorData = await response.json();
        error.message = errorData.detail || errorData.message || error.message;
        error.detail = errorData.detail;
      } catch {
        error.message = response.statusText || error.message;
      }

      throw error;
    }

    try {
      return await response.json();
    } catch {
      return {} as T; // Handle empty responses
    }
  }

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

  protected async put<T>(endpoint: string, data?: any): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: data ? JSON.stringify(data) : undefined,
    });
    return this.handleResponse<T>(response);
  }

  protected async delete<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders(),
    });
    return this.handleResponse<T>(response);
  }
}
```

## Domain Services

### 1. Portfolio Service (`app/services/api/portfolio.ts`)

Manages portfolio data, allocations, and simulations.

```typescript
interface IndexHistoryResponse {
  series: SeriesPoint[];
}

interface IndexCurrentResponse {
  date: string;
  allocations: AllocationItem[];
}

interface SimulationResponse {
  amount_final: number;
  roi_pct: number;
  currency: string;
  series: SeriesPoint[];
}

class PortfolioService extends ApiService {
  /**
   * Get historical index values
   */
  async getIndexHistory(): Promise<IndexHistoryResponse> {
    return this.get<IndexHistoryResponse>('/api/v1/index/history');
  }

  /**
   * Get current portfolio allocations
   */
  async getCurrentAllocations(): Promise<IndexCurrentResponse> {
    return this.get<IndexCurrentResponse>('/api/v1/index/current');
  }

  /**
   * Get historical data for a specific asset
   */
  async getAssetHistory(symbol: string): Promise<IndexHistoryResponse> {
    return this.get<IndexHistoryResponse>(
      `/api/v1/index/assets/${symbol}/history`
    );
  }

  /**
   * Run portfolio simulation
   */
  async runSimulation(request: SimulationRequest): Promise<SimulationResponse> {
    const payload = {
      amount: request.amount,
      start_date: request.startDate,
      currency: request.currency,
    };
    return this.post<SimulationResponse>('/api/v1/index/simulate', payload);
  }

  /**
   * Get available currencies
   */
  async getCurrencies(): Promise<CurrencyMap> {
    return this.get<CurrencyMap>('/api/v1/index/currencies');
  }

  /**
   * Trigger portfolio refresh
   */
  async refreshPortfolio(): Promise<any> {
    return this.post('/api/v1/tasks/refresh');
  }
}

export const portfolioService = new PortfolioService();
```

### 2. News Service (`app/services/api/news.ts`)

Handles news articles, sentiment analysis, and trending entities.

```typescript
export interface NewsArticle {
  id: string;
  title: string;
  description: string;
  url: string;
  published_at: string;
  source: string;
  symbols: string[];
  sentiment_score?: number;
  relevance_score?: number;
}

export interface EntitySentiment {
  symbol: string;
  name: string;
  sentiment_score: number;
  mention_count: number;
  articles: NewsArticle[];
}

export interface TrendingEntity {
  symbol: string;
  name: string;
  mention_count: number;
  sentiment_score: number;
  trend: 'up' | 'down' | 'stable';
}

class NewsService extends ApiService {
  /**
   * Search news with filters
   */
  async searchNews(params: {
    symbols?: string[];
    keywords?: string;
    sentimentMin?: number;
    sentimentMax?: number;
    publishedAfter?: string;
    publishedBefore?: string;
    limit?: number;
    offset?: number;
  }): Promise<NewsArticle[]> {
    const queryParams = new URLSearchParams();
    
    if (params.symbols?.length) {
      queryParams.append('symbols', params.symbols.join(','));
    }
    if (params.keywords) {
      queryParams.append('keywords', params.keywords);
    }
    if (params.sentimentMin !== undefined) {
      queryParams.append('sentiment_min', params.sentimentMin.toString());
    }
    if (params.sentimentMax !== undefined) {
      queryParams.append('sentiment_max', params.sentimentMax.toString());
    }
    // ... other params
    
    return this.get<NewsArticle[]>(
      `/api/v1/news/search?${queryParams.toString()}`
    );
  }

  /**
   * Get sentiment for specific entity
   */
  async getEntitySentiment(symbol: string): Promise<EntitySentiment> {
    return this.get<EntitySentiment>(`/api/v1/news/sentiment/${symbol}`);
  }

  /**
   * Get trending entities
   */
  async getTrendingEntities(): Promise<TrendingEntity[]> {
    return this.get<TrendingEntity[]>('/api/v1/news/trending');
  }

  /**
   * Refresh news data
   */
  async refreshNews(): Promise<{ message: string }> {
    return this.post('/api/v1/news/refresh');
  }
}

export const newsService = new NewsService();
```

### 3. Strategy Service (`app/services/api/strategy.ts`)

Manages investment strategy configuration and risk metrics.

```typescript
export interface StrategyConfig {
  momentum_weight: number;
  market_cap_weight: number;
  risk_parity_weight: number;
  min_price_threshold: number;
  max_daily_return: number;
  min_daily_return: number;
  max_forward_fill_days: number;
  outlier_std_threshold: number;
  rebalance_frequency: 'daily' | 'weekly' | 'monthly';
  daily_drop_threshold: number;
  ai_adjusted?: boolean;
  ai_adjustment_reason?: string;
  ai_confidence_score?: number;
  last_rebalance?: string;
  updated_at?: string;
}

export interface RiskMetric {
  date: string;
  total_return: number;
  annualized_return?: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  max_drawdown: number;
  current_drawdown: number;
  volatility?: number;
  var_95?: number;
  var_99?: number;
  beta_sp500?: number;
  correlation_sp500?: number;
}

class StrategyService extends ApiService {
  /**
   * Get current strategy configuration
   */
  async getConfig(): Promise<StrategyConfig> {
    return this.get<StrategyConfig>('/api/v1/strategy/config');
  }

  /**
   * Update strategy configuration
   */
  async updateConfig(
    config: Partial<StrategyConfig>, 
    recompute: boolean = true
  ): Promise<StrategyConfig> {
    return this.put<StrategyConfig>(
      `/api/v1/strategy/config?recompute=${recompute}`,
      config
    );
  }

  /**
   * Apply AI-suggested adjustments
   */
  async aiAdjust(
    adjustments: Partial<StrategyConfig>,
    reason: string,
    confidence: number
  ): Promise<StrategyConfig> {
    return this.post<StrategyConfig>('/api/v1/strategy/config/ai-adjust', {
      adjustments,
      reason,
      confidence
    });
  }

  /**
   * Get risk metrics
   */
  async getRiskMetrics(limit: number = 30): Promise<RiskMetricsResponse> {
    return this.get<RiskMetricsResponse>(
      `/api/v1/strategy/risk-metrics?limit=${limit}`
    );
  }

  /**
   * Trigger portfolio rebalancing
   */
  async triggerRebalance(force: boolean = false): Promise<RebalanceResponse> {
    return this.post<RebalanceResponse>(
      `/api/v1/strategy/rebalance?force=${force}`
    );
  }
}

export const strategyService = new StrategyService();
```

### 4. Background Task Service (`app/services/api/background.ts`)

Manages long-running background tasks.

```typescript
export interface TaskResponse {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  result?: any;
  error?: string;
  created_at: string;
  completed_at?: string;
}

class BackgroundTaskService extends ApiService {
  /**
   * Trigger data refresh task
   */
  async triggerRefresh(params: RefreshRequest): Promise<TaskResponse> {
    return this.post<TaskResponse>('/api/v1/background/refresh', params);
  }

  /**
   * Trigger index computation
   */
  async triggerCompute(params: ComputeRequest): Promise<TaskResponse> {
    return this.post<TaskResponse>('/api/v1/background/compute', params);
  }

  /**
   * Get task status
   */
  async getTaskStatus(taskId: string): Promise<TaskResponse> {
    return this.get<TaskResponse>(`/api/v1/background/status/${taskId}`);
  }

  /**
   * Get active tasks
   */
  async getActiveTasks(): Promise<ActiveTasks> {
    return this.get<ActiveTasks>('/api/v1/background/active');
  }

  /**
   * Poll task until completion
   */
  async pollTaskStatus(
    taskId: string,
    onUpdate?: (status: TaskResponse) => void,
    interval: number = 1000,
    maxAttempts: number = 60
  ): Promise<TaskResponse> {
    let attempts = 0;
    
    while (attempts < maxAttempts) {
      const status = await this.getTaskStatus(taskId);
      
      if (onUpdate) {
        onUpdate(status);
      }
      
      if (status.status === 'completed' || status.status === 'failed') {
        return status;
      }
      
      await new Promise(resolve => setTimeout(resolve, interval));
      attempts++;
    }
    
    throw new Error('Task polling timeout');
  }
}

export const backgroundTaskService = new BackgroundTaskService();
```

### 5. Diagnostics Service (`app/services/api/diagnostics.ts`)

System health checks and diagnostics.

```typescript
export interface DatabaseStatus {
  timestamp: string;
  tables: {
    [tableName: string]: {
      count: number;
      status: 'OK' | 'EMPTY' | 'ERROR';
      earliest_date?: string;
      latest_date?: string;
      error?: string;
    };
  };
  simulation_ready: boolean;
  message: string;
}

class DiagnosticsService extends ApiService {
  /**
   * Get database status
   */
  async getDatabaseStatus(): Promise<DatabaseStatus> {
    return this.get<DatabaseStatus>('/api/v1/diagnostics/database-status');
  }

  /**
   * Get refresh status
   */
  async getRefreshStatus(): Promise<RefreshStatus> {
    return this.get<RefreshStatus>('/api/v1/diagnostics/refresh-status');
  }

  /**
   * Get cache status
   */
  async getCacheStatus(): Promise<CacheStatus> {
    return this.get<CacheStatus>('/api/v1/diagnostics/cache-status');
  }

  /**
   * Invalidate cache
   */
  async invalidateCache(pattern?: string): Promise<CacheInvalidateResponse> {
    return this.post<CacheInvalidateResponse>(
      '/api/v1/diagnostics/cache-invalidate',
      { pattern }
    );
  }

  /**
   * Test refresh process
   */
  async testRefresh(): Promise<TestRefreshResult> {
    return this.post<TestRefreshResult>('/api/v1/diagnostics/test-refresh');
  }

  /**
   * Recalculate index
   */
  async recalculateIndex(): Promise<RecalculateResult> {
    return this.post<RecalculateResult>('/api/v1/diagnostics/recalculate-index');
  }
}

export const diagnosticsService = new DiagnosticsService();
```

## Service Usage Patterns

### Basic Usage

```typescript
// In a React component
import { portfolioService } from '@/services/api';

const MyComponent = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const result = await portfolioService.getIndexHistory();
        setData(result.series);
      } catch (error) {
        console.error('Failed to load data:', error);
      }
    };
    
    loadData();
  }, []);

  return <div>{/* Render data */}</div>;
};
```

### With Loading State

```typescript
const [loading, setLoading] = useState(false);
const [error, setError] = useState<string | null>(null);

const fetchData = async () => {
  setLoading(true);
  setError(null);
  
  try {
    const data = await portfolioService.getCurrentAllocations();
    setAllocations(data.allocations);
  } catch (err: any) {
    setError(err.message || 'Failed to load allocations');
  } finally {
    setLoading(false);
  }
};
```

### Parallel Requests

```typescript
const loadDashboardData = async () => {
  try {
    const [indexRes, spRes, allocRes, currRes] = await Promise.all([
      portfolioService.getIndexHistory(),
      benchmarkService.getSP500Data(),
      portfolioService.getCurrentAllocations(),
      portfolioService.getCurrencies(),
    ]);
    
    // Process all responses
    setIndexSeries(indexRes.series);
    setSpSeries(spRes.series);
    setAllocations(allocRes.allocations);
    setCurrencies(currRes);
  } catch (error) {
    console.error('Failed to load dashboard data:', error);
  }
};
```

### With Polling

```typescript
const startBackgroundTask = async () => {
  const task = await backgroundTaskService.triggerRefresh({ mode: 'full' });
  
  // Poll for completion
  const result = await backgroundTaskService.pollTaskStatus(
    task.task_id,
    (status) => {
      console.log(`Task ${status.status}: ${status.result?.progress || 0}%`);
    },
    1000, // Check every second
    60    // Max 60 attempts
  );
  
  if (result.status === 'completed') {
    console.log('Task completed successfully');
  } else {
    console.error('Task failed:', result.error);
  }
};
```

## Service Testing

### Mock Services

```typescript
// Mock service for testing
class MockPortfolioService extends PortfolioService {
  async getIndexHistory(): Promise<IndexHistoryResponse> {
    return {
      series: [
        { date: '2024-01-01', value: 100 },
        { date: '2024-01-02', value: 102 },
      ]
    };
  }

  async getCurrentAllocations(): Promise<IndexCurrentResponse> {
    return {
      date: '2024-01-02',
      allocations: [
        { symbol: 'AAPL', weight: 0.5, name: 'Apple Inc.' },
        { symbol: 'GOOGL', weight: 0.5, name: 'Alphabet Inc.' },
      ]
    };
  }
}
```

### Service Testing

```typescript
describe('PortfolioService', () => {
  let service: PortfolioService;

  beforeEach(() => {
    service = new MockPortfolioService();
  });

  it('should fetch index history', async () => {
    const result = await service.getIndexHistory();
    expect(result.series).toHaveLength(2);
    expect(result.series[0].value).toBe(100);
  });

  it('should fetch current allocations', async () => {
    const result = await service.getCurrentAllocations();
    expect(result.allocations).toHaveLength(2);
    expect(result.allocations[0].symbol).toBe('AAPL');
  });
});
```

## Error Handling

### Service-Level Error Handling

```typescript
class EnhancedApiService extends ApiService {
  protected async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      // Log error for monitoring
      console.error(`API Error: ${response.status} ${response.statusText}`);
      
      // Parse error details
      const error = await this.parseError(response);
      
      // Throw typed error
      throw new ApiError(error.message, response.status, error.detail);
    }
    
    return super.handleResponse<T>(response);
  }
  
  private async parseError(response: Response): Promise<ApiError> {
    try {
      const data = await response.json();
      return {
        message: data.detail || data.message || 'Request failed',
        status: response.status,
        detail: data,
      };
    } catch {
      return {
        message: response.statusText || 'Request failed',
        status: response.status,
      };
    }
  }
}
```

### Component-Level Error Handling

```typescript
const handleApiError = (error: any): string => {
  if (error.status === 401) {
    return 'Please login to continue';
  }
  if (error.status === 403) {
    return 'You do not have permission to perform this action';
  }
  if (error.status === 404) {
    return 'The requested resource was not found';
  }
  if (error.status >= 500) {
    return 'Server error. Please try again later';
  }
  return error.message || 'An unexpected error occurred';
};
```

## Best Practices

1. **Always type responses** - Use TypeScript interfaces for all API responses
2. **Handle errors gracefully** - Provide user-friendly error messages
3. **Use loading states** - Show feedback during API calls
4. **Cache when appropriate** - Use React Query for caching
5. **Avoid duplicate requests** - Use debouncing and request cancellation
6. **Log errors** - For debugging and monitoring
7. **Test services** - Unit test service methods
8. **Document endpoints** - Keep service documentation up to date

## Performance Optimization

### Request Deduplication

```typescript
class CachedService extends ApiService {
  private cache = new Map<string, Promise<any>>();
  
  protected async get<T>(endpoint: string): Promise<T> {
    if (!this.cache.has(endpoint)) {
      this.cache.set(endpoint, super.get<T>(endpoint));
    }
    
    try {
      return await this.cache.get(endpoint);
    } finally {
      // Clear cache after request completes
      setTimeout(() => this.cache.delete(endpoint), 100);
    }
  }
}
```

### Request Cancellation

```typescript
const controller = new AbortController();

const fetchWithCancel = async () => {
  try {
    const response = await fetch(url, {
      signal: controller.signal
    });
    return await response.json();
  } catch (error) {
    if (error.name === 'AbortError') {
      console.log('Request cancelled');
    }
    throw error;
  }
};

// Cancel request
controller.abort();
```

## Next Steps

- Review [Component Structure](./05-component-structure.md)
- Learn about [State Management](./06-state-management.md)
- Understand [Error Handling](./08-error-handling.md)