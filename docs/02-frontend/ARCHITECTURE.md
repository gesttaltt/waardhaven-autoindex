# Frontend Architecture Documentation

## Overview
The Waardhaven AutoIndex frontend is built with Next.js 14 using the App Router, implementing Clean Architecture principles for maintainability and scalability.

## Tech Stack
- **Framework**: Next.js 14.2.32
- **UI Library**: React 18.3.1
- **Language**: TypeScript 5.5.4
- **Styling**: Tailwind CSS 3.4.7
- **State Management**: React Query (TanStack Query) 5.51.1
- **Charts**: Recharts 2.12.7
- **HTTP Client**: Axios 1.11.0
- **Authentication**: JWT with jwt-decode 4.0.0
- **Animations**: Framer Motion 12.23.12

## Architecture Pattern: Clean Architecture

### Layer Structure
```
app/
├── core/                        # Clean Architecture Layers
│   ├── domain/                  # Business Logic (Framework Independent)
│   │   ├── entities/           # Business Entities
│   │   ├── repositories/      # Repository Interfaces
│   │   └── usecases/          # Business Use Cases
│   │
│   ├── application/            # Application-Specific Logic
│   │   └── usecases/          # Application Use Cases
│   │
│   ├── infrastructure/         # External Services
│   │   ├── api/              # API Clients
│   │   ├── auth/             # Authentication Providers
│   │   └── repositories/     # Repository Implementations
│   │
│   └── presentation/           # UI Layer
│       ├── components/        # React Components
│       ├── contexts/         # React Contexts
│       └── hooks/            # Custom Hooks
│
├── components/                  # Shared UI Components
├── services/                   # Direct API Services
├── hooks/                      # General Hooks
├── utils/                      # Utility Functions
└── [routes]/                   # Next.js Pages
```

### Clean Architecture Benefits
1. **Separation of Concerns**: Each layer has a single responsibility
2. **Testability**: Business logic can be tested without UI
3. **Maintainability**: Changes are isolated to specific layers
4. **Framework Independence**: Core business logic doesn't depend on React/Next.js
5. **Dependency Inversion**: High-level modules don't depend on low-level modules

## Domain Layer

### Entities
Pure TypeScript classes representing business concepts:

```typescript
// core/domain/entities/Portfolio.ts
export class Portfolio {
  constructor(
    public readonly id: string,
    public readonly name: string,
    public readonly totalValue: number,
    public readonly allocations: Allocation[],
    public readonly performance: PerformanceMetrics
  ) {}

  get returns(): number {
    return this.performance.totalReturn;
  }

  get riskLevel(): RiskLevel {
    return calculateRiskLevel(this.performance.volatility);
  }
}
```

### Repository Interfaces
Contracts for data access:

```typescript
// core/domain/repositories/IPortfolioRepository.ts
export interface IPortfolioRepository {
  getPortfolio(id: string): Promise<Portfolio>;
  updateAllocations(id: string, allocations: Allocation[]): Promise<void>;
  getPerformance(id: string, period: Period): Promise<PerformanceMetrics>;
}
```

### Use Cases
Business rules and workflows:

```typescript
// core/domain/usecases/MonitorSystemHealthUseCase.ts
export class MonitorSystemHealthUseCase {
  constructor(
    private healthRepository: ISystemHealthRepository
  ) {}

  async execute(): Promise<SystemHealth> {
    const health = await this.healthRepository.getSystemHealth();
    
    if (health.status === 'critical') {
      // Business rule: Alert on critical status
      this.notifyAdministrators(health);
    }
    
    return health;
  }
}
```

## Infrastructure Layer

### API Client
Centralized HTTP client configuration:

```typescript
// core/infrastructure/api/ApiClient.ts
export class ApiClient {
  private axiosInstance: AxiosInstance;

  constructor(baseURL: string) {
    this.axiosInstance = axios.create({
      baseURL,
      timeout: 10000,
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor for auth
    this.axiosInstance.interceptors.request.use(
      (config) => {
        const token = TokenManager.getAccessToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      }
    );

    // Response interceptor for error handling
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          await TokenManager.refreshToken();
          return this.axiosInstance.request(error.config);
        }
        throw error;
      }
    );
  }
}
```

### Repository Implementations
Concrete implementations of repository interfaces:

```typescript
// core/infrastructure/repositories/PortfolioRepository.ts
export class PortfolioRepository implements IPortfolioRepository {
  constructor(private apiClient: ApiClient) {}

  async getPortfolio(id: string): Promise<Portfolio> {
    const response = await this.apiClient.get(`/portfolio/${id}`);
    return PortfolioMapper.toDomain(response.data);
  }
}
```

## Presentation Layer

### Component Structure
Each component follows a consistent structure:

```
ComponentName/
├── index.ts                    # Public API
├── ComponentName.tsx           # Component logic
├── ComponentName.types.ts      # TypeScript interfaces
└── ComponentName.styles.ts     # Styled components/constants
```

### Custom Hooks
Encapsulate stateful logic:

```typescript
// core/presentation/hooks/useSystemHealth.ts
export function useSystemHealth() {
  const queryClient = useQueryClient();
  const healthUseCase = useMemo(
    () => new MonitorSystemHealthUseCase(new SystemHealthRepository()),
    []
  );

  return useQuery({
    queryKey: ['system-health'],
    queryFn: () => healthUseCase.execute(),
    refetchInterval: 30000, // Refresh every 30s
    staleTime: 20000,
  });
}
```

### Context Providers
Global state management:

```typescript
// core/presentation/contexts/AuthContext.tsx
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = TokenManager.getAccessToken();
      if (token) {
        const user = await authRepository.getCurrentUser();
        setUser(user);
      }
      setLoading(false);
    };
    initAuth();
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
```

## Routing Structure

### App Router Organization
```
app/
├── layout.tsx                  # Root layout with providers
├── page.tsx                    # Home page
├── dashboard/
│   └── page.tsx               # Dashboard (protected)
├── auth/
│   ├── login/
│   │   └── page.tsx          # Login page
│   └── register/
│       └── page.tsx          # Registration page
├── portfolio/
│   ├── page.tsx              # Portfolio overview
│   └── [id]/
│       └── page.tsx          # Portfolio details
├── strategy/
│   └── page.tsx              # Strategy configuration
├── news/
│   └── page.tsx              # News & sentiment
├── tasks/
│   └── page.tsx              # Task management
└── admin/
    └── page.tsx              # Admin panel (role-protected)
```

### Protected Routes
Route protection implementation:

```typescript
// core/presentation/components/ProtectedRoute.tsx
export function ProtectedRoute({ children, requiredRole }: Props) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push('/auth/login');
    }
    
    if (requiredRole && user?.role !== requiredRole) {
      router.push('/unauthorized');
    }
  }, [user, loading, requiredRole]);

  if (loading) return <LoadingSkeleton />;
  if (!user) return null;

  return <>{children}</>;
}
```

## State Management

### React Query Configuration
```typescript
// app/providers/index.tsx
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      retry: 3,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 2,
    },
  },
});
```

### Query Key Convention
```typescript
// Consistent query key structure
const queryKeys = {
  portfolio: (id: string) => ['portfolio', id],
  portfolioList: () => ['portfolios'],
  performance: (id: string, period: string) => ['performance', id, period],
  systemHealth: () => ['system-health'],
  user: (id: string) => ['user', id],
};
```

## Data Flow

### Request Lifecycle
1. **User Action** → Component event handler
2. **Use Case Execution** → Business logic processing
3. **Repository Call** → Data fetching/mutation
4. **API Request** → HTTP call to backend
5. **Response Mapping** → Transform to domain entities
6. **State Update** → React Query cache update
7. **UI Re-render** → Component updates with new data

### Example Flow
```typescript
// User clicks "Refresh Portfolio"
const handleRefresh = async () => {
  // 1. Execute use case
  const refreshUseCase = new RefreshPortfolioUseCase(portfolioRepo);
  
  // 2. Optimistic update
  queryClient.setQueryData(['portfolio', id], (old) => ({
    ...old,
    refreshing: true,
  }));
  
  // 3. Perform refresh
  try {
    const updated = await refreshUseCase.execute(id);
    
    // 4. Update cache
    queryClient.setQueryData(['portfolio', id], updated);
    
    // 5. Invalidate related queries
    queryClient.invalidateQueries(['performance', id]);
  } catch (error) {
    // 6. Rollback on error
    queryClient.setQueryData(['portfolio', id], (old) => ({
      ...old,
      refreshing: false,
    }));
  }
};
```

## Component Examples

### Smart Component
```typescript
// components/dashboard/PortfolioOverview.tsx
export function PortfolioOverview() {
  const { data: portfolio, isLoading } = usePortfolio();
  const { mutate: updateStrategy } = useUpdateStrategy();
  
  if (isLoading) return <LoadingSkeleton />;
  
  return (
    <Card>
      <CardHeader>
        <h2>{portfolio.name}</h2>
        <Badge>{portfolio.riskLevel}</Badge>
      </CardHeader>
      <CardContent>
        <PerformanceChart data={portfolio.performance} />
        <AllocationPie allocations={portfolio.allocations} />
      </CardContent>
      <CardActions>
        <Button onClick={() => updateStrategy(portfolio.id)}>
          Update Strategy
        </Button>
      </CardActions>
    </Card>
  );
}
```

### Presentational Component
```typescript
// components/shared/Button/Button.tsx
export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'medium',
  loading = false,
  disabled = false,
  onClick,
  ...props
}) => {
  const styles = clsx(
    baseStyles,
    variantStyles[variant],
    sizeStyles[size],
    {
      'opacity-50 cursor-not-allowed': disabled || loading,
    }
  );

  return (
    <button
      className={styles}
      disabled={disabled || loading}
      onClick={onClick}
      {...props}
    >
      {loading ? <Spinner /> : children}
    </button>
  );
};
```

## Performance Optimizations

### Code Splitting
```typescript
// Dynamic imports for heavy components
const AdvancedAnalytics = dynamic(
  () => import('@/components/dashboard/AdvancedAnalytics'),
  {
    loading: () => <AnalyticsSkeleton />,
    ssr: false,
  }
);
```

### Memoization
```typescript
// Expensive calculations memoized
const portfolioMetrics = useMemo(
  () => calculateMetrics(portfolio),
  [portfolio]
);

// Component memoization
export const ExpensiveComponent = memo(({ data }) => {
  // Component logic
}, (prevProps, nextProps) => {
  return prevProps.data.id === nextProps.data.id;
});
```

### Virtual Scrolling
```typescript
// For large lists
import { FixedSizeList } from 'react-window';

export function LargeAssetList({ assets }) {
  return (
    <FixedSizeList
      height={600}
      itemCount={assets.length}
      itemSize={50}
      width="100%"
    >
      {({ index, style }) => (
        <AssetRow asset={assets[index]} style={style} />
      )}
    </FixedSizeList>
  );
}
```

## Testing Strategy

### Unit Tests
```typescript
// Domain logic tests
describe('Portfolio Entity', () => {
  it('should calculate risk level correctly', () => {
    const portfolio = new Portfolio(mockData);
    expect(portfolio.riskLevel).toBe('MODERATE');
  });
});
```

### Integration Tests
```typescript
// API integration tests
describe('Portfolio Repository', () => {
  it('should fetch portfolio data', async () => {
    const repo = new PortfolioRepository(mockApiClient);
    const portfolio = await repo.getPortfolio('123');
    expect(portfolio).toBeInstanceOf(Portfolio);
  });
});
```

### Component Tests
```typescript
// React component tests
describe('PortfolioOverview', () => {
  it('should display portfolio name', () => {
    render(<PortfolioOverview />);
    expect(screen.getByText('My Portfolio')).toBeInTheDocument();
  });
});
```

## Build & Deployment

### Build Configuration
```javascript
// next.config.js
module.exports = {
  reactStrictMode: true,
  images: {
    domains: ['cdn.example.com'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
  webpack: (config) => {
    // Custom webpack config
    return config;
  },
};
```

### Environment Variables
```bash
# .env.local (development)
NEXT_PUBLIC_API_URL=http://localhost:8000

# .env.production (production)
NEXT_PUBLIC_API_URL=https://waardhaven-api.onrender.com
```

## Best Practices

### 1. Component Guidelines
- Keep components small and focused
- Separate smart and presentational components
- Use composition over inheritance
- Implement proper error boundaries

### 2. State Management
- Use React Query for server state
- Keep local state minimal
- Avoid prop drilling with context
- Implement optimistic updates

### 3. Performance
- Lazy load heavy components
- Implement virtual scrolling for lists
- Use React.memo for expensive components
- Optimize bundle size with tree shaking

### 4. Code Quality
- Maintain TypeScript strict mode
- Follow ESLint rules
- Write comprehensive tests
- Document complex logic

### 5. Security
- Sanitize user inputs
- Implement CSP headers
- Use HTTPS in production
- Store tokens securely