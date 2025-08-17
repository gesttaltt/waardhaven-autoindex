# Frontend-Backend Integration Guide

## Overview

This guide documents how the Next.js frontend connects to the FastAPI backend in the Waardhaven AutoIndex application. It covers API configuration, authentication flow, data synchronization, and best practices.

## API Connection Configuration

### Environment Setup

#### Backend (FastAPI)
```python
# apps/api/app/core/config.py
CORS_ORIGINS = [
    "http://localhost:3000",  # Local development
    "https://waardhaven-web.onrender.com",  # Production
]
```

#### Frontend (Next.js)
```typescript
// apps/web/.env.local (development)
NEXT_PUBLIC_API_URL=http://localhost:8000

// apps/web/.env.production (production)
NEXT_PUBLIC_API_URL=https://waardhaven-api.onrender.com
```

### API Client Architecture

```
Frontend                    Backend
────────                    ────────
React Component
    ↓
Custom Hook
    ↓
API Service Layer  ──────>  FastAPI Router
    ↓                           ↓
Axios/Fetch Client          Service Layer
    ↓                           ↓
HTTP Request       ──────>  Database
```

## Authentication Flow

### 1. User Registration

```typescript
// Frontend: apps/web/app/services/auth.ts
const register = async (email: string, password: string) => {
  const response = await api.post('/api/v1/auth/register', {
    email,
    password
  });
  
  // Store token
  localStorage.setItem('token', response.data.access_token);
  
  return response.data;
};
```

```python
# Backend: apps/api/app/routers/auth.py
@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    # Create user
    user = User(email=req.email, password_hash=get_password_hash(req.password))
    db.add(user)
    db.commit()
    
    # Generate token
    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token)
```

### 2. User Login

```typescript
// Frontend
const login = async (email: string, password: string) => {
  const response = await api.post('/api/v1/auth/login', {
    email,
    password
  });
  
  localStorage.setItem('token', response.data.access_token);
  return response.data;
};
```

### 3. Authenticated Requests

```typescript
// Frontend: Axios interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

```python
# Backend: Dependency injection
def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[JWT_ALGORITHM])
    user_id = int(payload.get("sub"))
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
```

## Core API Integrations

### 1. Portfolio Data

#### Get Current Allocations

```typescript
// Frontend
const getAllocations = async () => {
  const response = await portfolioService.getCurrentAllocations();
  return response.allocations;
};

// Usage in React component
const PortfolioView = () => {
  const { data, isLoading } = useQuery(
    'allocations',
    getAllocations
  );
  
  if (isLoading) return <Spinner />;
  
  return <AllocationChart data={data} />;
};
```

```python
# Backend
@router.get("/current", response_model=IndexCurrentResponse)
def get_current_index(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    latest_date = db.query(func.max(Allocation.date)).scalar()
    allocations = db.query(Allocation, Asset).join(Asset).filter(
        Allocation.date == latest_date
    ).all()
    
    return IndexCurrentResponse(
        date=latest_date,
        allocations=[
            AllocationItem(
                symbol=asset.symbol,
                name=asset.name,
                sector=asset.sector,
                weight=alloc.weight
            )
            for alloc, asset in allocations
        ]
    )
```

### 2. Historical Performance

```typescript
// Frontend: Fetch historical data
const getHistoricalData = async () => {
  const [indexData, benchmarkData] = await Promise.all([
    portfolioService.getIndexHistory(),
    marketService.getBenchmarkHistory()
  ]);
  
  return {
    index: indexData.series,
    benchmark: benchmarkData.series
  };
};
```

### 3. Investment Simulation

```typescript
// Frontend
interface SimulationParams {
  amount: number;
  startDate: string;
  currency: string;
}

const runSimulation = async (params: SimulationParams) => {
  return await portfolioService.runSimulation({
    amount: params.amount,
    start_date: params.startDate,
    currency: params.currency
  });
};

// React Hook
export const useSimulation = () => {
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState(false);
  
  const simulate = async (params: SimulationParams) => {
    setLoading(true);
    try {
      const data = await runSimulation(params);
      setResult(data);
    } catch (error) {
      console.error('Simulation failed:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return { simulate, result, loading };
};
```

### 4. Strategy Management

```typescript
// Frontend: Update strategy configuration
const updateStrategy = async (config: Partial<StrategyConfig>) => {
  // Validate weights sum to 1.0
  const totalWeight = 
    (config.momentum_weight || 0) +
    (config.market_cap_weight || 0) +
    (config.risk_parity_weight || 0);
  
  if (Math.abs(totalWeight - 1.0) > 0.001) {
    throw new Error('Strategy weights must sum to 1.0');
  }
  
  return await strategyApi.updateConfig(config, true);
};
```

## Real-time Data Updates

### Polling Strategy

```typescript
// Frontend: Auto-refresh hook
export const useAutoRefresh = (interval = 60000) => {
  const queryClient = useQueryClient();
  
  useEffect(() => {
    const timer = setInterval(() => {
      queryClient.invalidateQueries('portfolio');
      queryClient.invalidateQueries('metrics');
    }, interval);
    
    return () => clearInterval(timer);
  }, [interval, queryClient]);
};
```

### Smart Refresh

```typescript
// Frontend: Smart refresh with rate limiting
const smartRefresh = async () => {
  try {
    // Check current data freshness
    const status = await marketDataApi.getRefreshStatus();
    
    if (status.prices.needs_update) {
      // Use appropriate refresh mode based on data age
      const mode = status.prices.days_old > 7 ? 'full' : 'minimal';
      await marketDataApi.triggerSmartRefresh(mode);
    }
  } catch (error) {
    console.error('Smart refresh failed:', error);
    // Fallback to cached data
    await marketDataApi.triggerSmartRefresh('cached');
  }
};
```

## Error Handling

### Frontend Error Handling

```typescript
// Global error interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired - redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    } else if (error.response?.status === 429) {
      // Rate limited
      toast.error('Too many requests. Please wait.');
    } else if (error.response?.status >= 500) {
      // Server error
      toast.error('Server error. Please try again later.');
    }
    
    return Promise.reject(error);
  }
);

// Component-level error handling
const PortfolioComponent = () => {
  const { data, error, isLoading } = useQuery(
    'portfolio',
    fetchPortfolio,
    {
      onError: (error) => {
        console.error('Portfolio fetch failed:', error);
        toast.error('Failed to load portfolio data');
      },
      retry: 3,
      retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000)
    }
  );
  
  if (error) return <ErrorMessage error={error} />;
  if (isLoading) return <Skeleton />;
  
  return <PortfolioView data={data} />;
};
```

### Backend Error Responses

```python
# Structured error responses
class ErrorResponse(BaseModel):
    detail: str
    status_code: int
    type: str = "error"

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
            "status_code": 400,
            "type": "validation_error"
        }
    )
```

## Data Synchronization

### Optimistic Updates

```typescript
// Frontend: Optimistic UI updates
const updateAllocation = useMutation(
  (data: AllocationUpdate) => portfolioService.updateAllocation(data),
  {
    // Optimistically update the UI
    onMutate: async (newData) => {
      await queryClient.cancelQueries('allocations');
      
      const previousData = queryClient.getQueryData('allocations');
      
      queryClient.setQueryData('allocations', (old) => ({
        ...old,
        allocations: old.allocations.map(a =>
          a.id === newData.id ? { ...a, ...newData } : a
        )
      }));
      
      return { previousData };
    },
    
    // Rollback on error
    onError: (err, newData, context) => {
      queryClient.setQueryData('allocations', context.previousData);
      toast.error('Failed to update allocation');
    },
    
    // Refetch after success
    onSettled: () => {
      queryClient.invalidateQueries('allocations');
    }
  }
);
```

### Cache Management

```typescript
// Frontend: Cache configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false,
      retry: 3
    }
  }
});

// Selective cache invalidation
const refreshPortfolioData = () => {
  queryClient.invalidateQueries('portfolio');
  queryClient.invalidateQueries('allocations');
  // Don't invalidate historical data - it changes less frequently
};
```

## Type Safety

### Shared Types

```typescript
// Frontend: apps/web/app/types/api.ts
export interface AllocationItem {
  symbol: string;
  name: string;
  sector: string;
  weight: number;
}

export interface IndexCurrentResponse {
  date: string;
  allocations: AllocationItem[];
}
```

```python
# Backend: apps/api/app/schemas/index.py
class AllocationItem(BaseModel):
    symbol: str
    name: str
    sector: str
    weight: float

class IndexCurrentResponse(BaseModel):
    date: date
    allocations: List[AllocationItem]
```

### Type Generation (Future Enhancement)

```bash
# Generate TypeScript types from OpenAPI schema
npx openapi-typescript http://localhost:8000/openapi.json \
  --output apps/web/app/types/generated.ts
```

## Performance Optimization

### Request Batching

```typescript
// Frontend: Batch multiple requests
const loadDashboardData = async () => {
  const [portfolio, metrics, alerts] = await Promise.all([
    portfolioService.getCurrentAllocations(),
    portfolioService.getRiskMetrics(),
    alertService.getActiveAlerts()
  ]);
  
  return { portfolio, metrics, alerts };
};
```

### Debouncing

```typescript
// Frontend: Debounce search requests
const useSearch = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  
  const debouncedSearch = useMemo(
    () => debounce(async (searchQuery: string) => {
      if (searchQuery.length < 3) return;
      
      const data = await api.get(`/api/v1/search?q=${searchQuery}`);
      setResults(data.results);
    }, 300),
    []
  );
  
  useEffect(() => {
    debouncedSearch(query);
  }, [query, debouncedSearch]);
  
  return { query, setQuery, results };
};
```

## Testing Integration

### Mock API for Testing

```typescript
// Frontend: Mock API service
class MockApiService {
  async getCurrentAllocations() {
    return {
      date: '2024-01-01',
      allocations: [
        { symbol: 'AAPL', name: 'Apple Inc.', sector: 'Technology', weight: 0.15 },
        { symbol: 'MSFT', name: 'Microsoft', sector: 'Technology', weight: 0.12 }
      ]
    };
  }
}

// Use in tests
describe('Portfolio Component', () => {
  it('displays allocations', async () => {
    const mockService = new MockApiService();
    const { getByText } = render(
      <Portfolio service={mockService} />
    );
    
    await waitFor(() => {
      expect(getByText('Apple Inc.')).toBeInTheDocument();
    });
  });
});
```

### Integration Tests

```python
# Backend: Test API endpoints
def test_get_current_allocations(client, auth_headers):
    response = client.get(
        "/api/v1/index/current",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "allocations" in data
    assert len(data["allocations"]) > 0
```

## Deployment Considerations

### Environment-Specific Configuration

```typescript
// Frontend: Environment detection
const getApiUrl = () => {
  if (process.env.NODE_ENV === 'production') {
    return 'https://waardhaven-api.onrender.com';
  }
  if (process.env.NODE_ENV === 'staging') {
    return 'https://waardhaven-api-staging.onrender.com';
  }
  return 'http://localhost:8000';
};
```

### CORS Configuration

```python
# Backend: Environment-specific CORS
if os.getenv("RENDER"):
    # Production
    origins = [
        "https://waardhaven-web.onrender.com",
        "https://waardhaven.com"  # Custom domain
    ]
else:
    # Development
    origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

## Monitoring & Debugging

### Request Logging

```typescript
// Frontend: Log API requests in development
if (process.env.NODE_ENV === 'development') {
  api.interceptors.request.use(request => {
    console.log('Starting Request:', request.url);
    return request;
  });
  
  api.interceptors.response.use(
    response => {
      console.log('Response:', response.status);
      return response;
    },
    error => {
      console.error('Error:', error.response?.data);
      return Promise.reject(error);
    }
  );
}
```

### Performance Monitoring

```typescript
// Frontend: Track API performance
const trackApiCall = async (name: string, apiCall: () => Promise<any>) => {
  const start = performance.now();
  
  try {
    const result = await apiCall();
    const duration = performance.now() - start;
    
    // Send to analytics
    analytics.track('api_call', {
      endpoint: name,
      duration,
      success: true
    });
    
    return result;
  } catch (error) {
    const duration = performance.now() - start;
    
    analytics.track('api_call', {
      endpoint: name,
      duration,
      success: false,
      error: error.message
    });
    
    throw error;
  }
};
```

## Best Practices

### 1. Use Service Layer Pattern
- Centralize API calls in service classes
- Abstract HTTP client from components
- Enable easy mocking for tests

### 2. Handle Loading States
- Show skeletons/spinners during loading
- Implement progressive loading
- Cache data appropriately

### 3. Validate Data
- Validate on frontend before sending
- Validate on backend before processing
- Use consistent validation rules

### 4. Secure Sensitive Data
- Never log sensitive information
- Use HTTPS in production
- Store tokens securely

### 5. Optimize Network Usage
- Batch requests when possible
- Implement pagination for large datasets
- Use compression for responses

### 6. Plan for Offline
- Cache critical data
- Queue failed requests
- Show appropriate offline UI

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Check allowed origins in backend
   - Ensure credentials are included
   - Verify preflight requests succeed

2. **Authentication Failures**
   - Check token expiration
   - Verify token format
   - Ensure headers are set correctly

3. **Data Mismatch**
   - Verify API contract matches
   - Check date/time formats
   - Validate number precision

4. **Performance Issues**
   - Implement pagination
   - Add caching layer
   - Optimize database queries

## Conclusion

The frontend-backend integration in Waardhaven AutoIndex follows modern best practices:

- **Type Safety**: Shared types between frontend and backend
- **Security**: JWT authentication with proper validation
- **Performance**: Caching, batching, and optimization
- **Error Handling**: Graceful degradation and user feedback
- **Testing**: Comprehensive test coverage
- **Monitoring**: Request tracking and performance metrics

This architecture ensures reliable, secure, and performant communication between the Next.js frontend and FastAPI backend.