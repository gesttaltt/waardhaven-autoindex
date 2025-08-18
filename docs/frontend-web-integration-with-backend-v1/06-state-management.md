# State Management

## Overview

The application uses a hybrid state management approach combining React Context for global state, React Query for server state, and local component state for UI-specific data.

## State Management Architecture

```
┌──────────────────────────────────────────┐
│          Global State                     │
│    (Auth Context, Theme Context)          │
├──────────────────────────────────────────┤
│          Server State                     │
│         (React Query)                     │
├──────────────────────────────────────────┤
│          Local State                      │
│    (useState, useReducer)                 │
└──────────────────────────────────────────┘
```

## State Categories

### 1. Global Application State

Managed through React Context API for cross-cutting concerns.

#### Authentication State
```typescript
// AuthContext.tsx
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

interface AuthContextValue extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ 
  children 
}) => {
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
  });

  const login = async (credentials: LoginCredentials) => {
    try {
      const tokens = await authRepository.login(credentials);
      const user = await authRepository.getCurrentUser();
      setState({
        user,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      throw error;
    }
  };

  return (
    <AuthContext.Provider value={{ ...state, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  );
};
```

#### Theme Context
```typescript
interface ThemeContextValue {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ 
  children 
}) => {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark';
    if (savedTheme) {
      setTheme(savedTheme);
      document.documentElement.classList.toggle('dark', savedTheme === 'dark');
    }
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.classList.toggle('dark', newTheme === 'dark');
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
```

### 2. Server State Management

Using React Query (TanStack Query) for server state synchronization.

#### Query Client Configuration
```typescript
// providers/index.tsx
export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,      // Consider data stale after 1 minute
            gcTime: 5 * 60 * 1000,      // Keep in cache for 5 minutes
            retry: 1,                   // Retry failed requests once
            refetchOnWindowFocus: false,// Don't refetch on window focus
          },
          mutations: {
            retry: 1,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        {children}
      </AuthProvider>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

#### Custom Query Hooks
```typescript
// hooks/usePortfolioData.ts
export function usePortfolioData() {
  return useQuery({
    queryKey: ['portfolio', 'current'],
    queryFn: () => portfolioService.getCurrentAllocations(),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
}

export function useIndexHistory(timeRange?: string) {
  return useQuery({
    queryKey: ['portfolio', 'history', timeRange],
    queryFn: () => portfolioService.getIndexHistory(timeRange),
    staleTime: 60 * 1000,
  });
}

// Usage in component
const PortfolioComponent = () => {
  const { data, isLoading, error, refetch } = usePortfolioData();

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return <PortfolioView data={data} onRefresh={refetch} />;
};
```

#### Mutations
```typescript
// hooks/useStrategyMutation.ts
export function useStrategyUpdate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (config: Partial<StrategyConfig>) => 
      strategyService.updateConfig(config),
    onSuccess: (data) => {
      // Invalidate and refetch related queries
      queryClient.invalidateQueries({ queryKey: ['strategy'] });
      queryClient.setQueryData(['strategy', 'config'], data);
    },
    onError: (error) => {
      console.error('Failed to update strategy:', error);
    },
  });
}

// Usage
const StrategyForm = () => {
  const mutation = useStrategyUpdate();

  const handleSubmit = (values: StrategyConfig) => {
    mutation.mutate(values, {
      onSuccess: () => {
        toast.success('Strategy updated successfully');
      },
      onError: (error) => {
        toast.error('Failed to update strategy');
      },
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
      <button type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? 'Updating...' : 'Update Strategy'}
      </button>
    </form>
  );
};
```

#### Optimistic Updates
```typescript
export function useAllocationUpdate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (allocations: Allocation[]) => 
      portfolioService.updateAllocations(allocations),
    onMutate: async (newAllocations) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['portfolio', 'allocations'] });

      // Snapshot previous value
      const previousAllocations = queryClient.getQueryData(['portfolio', 'allocations']);

      // Optimistically update
      queryClient.setQueryData(['portfolio', 'allocations'], newAllocations);

      // Return context with snapshot
      return { previousAllocations };
    },
    onError: (err, newAllocations, context) => {
      // Rollback on error
      if (context?.previousAllocations) {
        queryClient.setQueryData(
          ['portfolio', 'allocations'], 
          context.previousAllocations
        );
      }
    },
    onSettled: () => {
      // Always refetch after error or success
      queryClient.invalidateQueries({ queryKey: ['portfolio', 'allocations'] });
    },
  });
}
```

### 3. Local Component State

For UI-specific state that doesn't need to be shared.

#### Form State Management
```typescript
const LoginForm = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user types
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!isValidEmail(formData.email)) {
      newErrors.email = 'Invalid email format';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!validate()) return;
    
    setIsSubmitting(true);
    try {
      await login(formData);
    } catch (error) {
      setErrors({ general: 'Login failed' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
    </form>
  );
};
```

#### Complex State with useReducer
```typescript
interface DashboardState {
  timeRange: string;
  selectedAssets: string[];
  showComparison: boolean;
  chartType: 'line' | 'area' | 'candle';
  filters: {
    minValue: number;
    maxValue: number;
    sectors: string[];
  };
}

type DashboardAction =
  | { type: 'SET_TIME_RANGE'; payload: string }
  | { type: 'TOGGLE_ASSET'; payload: string }
  | { type: 'SET_CHART_TYPE'; payload: 'line' | 'area' | 'candle' }
  | { type: 'UPDATE_FILTERS'; payload: Partial<DashboardState['filters']> }
  | { type: 'RESET' };

const dashboardReducer = (
  state: DashboardState, 
  action: DashboardAction
): DashboardState => {
  switch (action.type) {
    case 'SET_TIME_RANGE':
      return { ...state, timeRange: action.payload };
    
    case 'TOGGLE_ASSET':
      const assets = state.selectedAssets.includes(action.payload)
        ? state.selectedAssets.filter(a => a !== action.payload)
        : [...state.selectedAssets, action.payload];
      return { ...state, selectedAssets: assets };
    
    case 'SET_CHART_TYPE':
      return { ...state, chartType: action.payload };
    
    case 'UPDATE_FILTERS':
      return { 
        ...state, 
        filters: { ...state.filters, ...action.payload } 
      };
    
    case 'RESET':
      return initialState;
    
    default:
      return state;
  }
};

const Dashboard = () => {
  const [state, dispatch] = useReducer(dashboardReducer, initialState);

  return (
    <div>
      <TimeRangeSelector
        value={state.timeRange}
        onChange={(range) => dispatch({ type: 'SET_TIME_RANGE', payload: range })}
      />
      <Chart type={state.chartType} data={filteredData} />
    </div>
  );
};
```

## State Persistence

### Local Storage Persistence
```typescript
// hooks/useLocalStorage.ts
export function useLocalStorage<T>(
  key: string, 
  initialValue: T
): [T, (value: T | ((prev: T) => T)) => void] {
  // Get from local storage then parse stored json or return initialValue
  const [storedValue, setStoredValue] = useState<T>(() => {
    if (typeof window === 'undefined') {
      return initialValue;
    }

    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error loading ${key} from localStorage:`, error);
      return initialValue;
    }
  });

  // Return a wrapped version of useState's setter function
  const setValue = (value: T | ((prev: T) => T)) => {
    try {
      // Allow value to be a function
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      }
    } catch (error) {
      console.error(`Error saving ${key} to localStorage:`, error);
    }
  };

  return [storedValue, setValue];
}

// Usage
const Settings = () => {
  const [preferences, setPreferences] = useLocalStorage('userPreferences', {
    theme: 'light',
    language: 'en',
    notifications: true,
  });

  return (
    <div>
      <Toggle
        checked={preferences.notifications}
        onChange={(checked) => 
          setPreferences(prev => ({ ...prev, notifications: checked }))
        }
      />
    </div>
  );
};
```

### Session Storage
```typescript
export function useSessionStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T) => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.sessionStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setValue = (value: T) => {
    try {
      setStoredValue(value);
      window.sessionStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(`Error saving to sessionStorage:`, error);
    }
  };

  return [storedValue, setValue];
}
```

## State Synchronization

### Cross-Tab Synchronization
```typescript
// hooks/useSyncedState.ts
export function useSyncedState<T>(
  key: string,
  initialValue: T
): [T, (value: T) => void] {
  const [state, setState] = useState<T>(initialValue);

  useEffect(() => {
    // Load initial value
    const stored = localStorage.getItem(key);
    if (stored) {
      setState(JSON.parse(stored));
    }

    // Listen for changes in other tabs
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === key && e.newValue) {
        setState(JSON.parse(e.newValue));
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [key]);

  const updateState = (value: T) => {
    setState(value);
    localStorage.setItem(key, JSON.stringify(value));
    
    // Dispatch custom event for same-tab updates
    window.dispatchEvent(new StorageEvent('storage', {
      key,
      newValue: JSON.stringify(value),
      url: window.location.href,
      storageArea: localStorage,
    }));
  };

  return [state, updateState];
}
```

### Real-time Updates with WebSocket
```typescript
// contexts/RealtimeContext.tsx
interface RealtimeContextValue {
  subscribe: (channel: string, callback: (data: any) => void) => void;
  unsubscribe: (channel: string) => void;
  isConnected: boolean;
}

const RealtimeContext = createContext<RealtimeContextValue | undefined>(undefined);

export const RealtimeProvider: React.FC<{ children: React.ReactNode }> = ({ 
  children 
}) => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const subscriptions = useRef<Map<string, Set<(data: any) => void>>>(new Map());

  useEffect(() => {
    const ws = new WebSocket(process.env.NEXT_PUBLIC_WS_URL!);

    ws.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const { channel, data } = JSON.parse(event.data);
      const callbacks = subscriptions.current.get(channel);
      callbacks?.forEach(callback => callback(data));
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');
    };

    setSocket(ws);

    return () => {
      ws.close();
    };
  }, []);

  const subscribe = (channel: string, callback: (data: any) => void) => {
    if (!subscriptions.current.has(channel)) {
      subscriptions.current.set(channel, new Set());
      socket?.send(JSON.stringify({ action: 'subscribe', channel }));
    }
    subscriptions.current.get(channel)?.add(callback);
  };

  const unsubscribe = (channel: string) => {
    subscriptions.current.delete(channel);
    socket?.send(JSON.stringify({ action: 'unsubscribe', channel }));
  };

  return (
    <RealtimeContext.Provider value={{ subscribe, unsubscribe, isConnected }}>
      {children}
    </RealtimeContext.Provider>
  );
};

// Usage
const PriceDisplay = ({ symbol }: { symbol: string }) => {
  const [price, setPrice] = useState<number>(0);
  const { subscribe, unsubscribe } = useRealtime();

  useEffect(() => {
    subscribe(`price:${symbol}`, (data) => {
      setPrice(data.price);
    });

    return () => unsubscribe(`price:${symbol}`);
  }, [symbol]);

  return <div>Current Price: ${price}</div>;
};
```

## State Performance Optimization

### Memoization
```typescript
const ExpensiveComponent = () => {
  const [filter, setFilter] = useState('');
  const [data, setData] = useState(largeDataset);

  // Memoize expensive filtering
  const filteredData = useMemo(() => {
    return data.filter(item => 
      item.name.toLowerCase().includes(filter.toLowerCase())
    );
  }, [data, filter]);

  // Memoize callbacks
  const handleItemClick = useCallback((id: string) => {
    console.log('Clicked item:', id);
  }, []);

  return (
    <div>
      <input value={filter} onChange={(e) => setFilter(e.target.value)} />
      {filteredData.map(item => (
        <Item key={item.id} onClick={handleItemClick} {...item} />
      ))}
    </div>
  );
};

// Memoize components
const Item = React.memo(({ id, name, onClick }) => {
  return (
    <div onClick={() => onClick(id)}>
      {name}
    </div>
  );
});
```

### State Splitting
```typescript
// Instead of one large state object
const [state, setState] = useState({
  user: null,
  posts: [],
  comments: [],
  settings: {},
});

// Split into separate states
const [user, setUser] = useState(null);
const [posts, setPosts] = useState([]);
const [comments, setComments] = useState([]);
const [settings, setSettings] = useState({});
```

## Testing State Management

### Testing Context Providers
```typescript
// test-utils.tsx
const AllTheProviders = ({ children }) => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        {children}
      </AuthProvider>
    </QueryClientProvider>
  );
};

const customRender = (ui, options) =>
  render(ui, { wrapper: AllTheProviders, ...options });

// Test
describe('AuthContext', () => {
  it('should login user', async () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: AllTheProviders,
    });

    await act(async () => {
      await result.current.login({
        email: 'test@example.com',
        password: 'password',
      });
    });

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toBeDefined();
  });
});
```

## Best Practices

1. **Minimize Global State** - Only put truly global data in context
2. **Colocate State** - Keep state as close to where it's used as possible
3. **Use React Query for Server State** - Don't duplicate server state in local state
4. **Normalize Complex State** - Use normalized data structures for complex state
5. **Avoid Prop Drilling** - Use context or component composition
6. **Memoize Expensive Operations** - Use useMemo and useCallback appropriately
7. **Split Large States** - Break down large state objects into smaller pieces
8. **Handle Loading and Error States** - Always consider loading and error cases

## Next Steps

- Review [Routes and Pages](./07-routes-and-pages.md)
- Learn about [Error Handling](./08-error-handling.md)
- Understand [Performance Optimization](./11-performance-optimization.md)