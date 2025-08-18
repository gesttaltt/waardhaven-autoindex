# Component Structure

## Overview

The component architecture follows atomic design principles with clear separation between presentational and container components. Components are organized by feature and complexity level.

## Component Hierarchy

```
┌─────────────────────────────────────────┐
│              Pages                      │
│         (Route Components)               │
├─────────────────────────────────────────┤
│            Templates                    │
│         (Layout Components)              │
├─────────────────────────────────────────┤
│            Organisms                    │
│      (Complex Components)                │
├─────────────────────────────────────────┤
│            Molecules                    │
│      (Composite Components)              │
├─────────────────────────────────────────┤
│              Atoms                      │
│        (Basic Components)                │
└─────────────────────────────────────────┘
```

## Directory Structure

```
app/
├── components/
│   ├── shared/               # Reusable components
│   │   ├── Button/
│   │   │   ├── Button.tsx
│   │   │   ├── Button.styles.ts
│   │   │   ├── Button.types.ts
│   │   │   └── index.ts
│   │   ├── Card/
│   │   ├── ErrorBoundary.tsx
│   │   └── LoadingSkeleton.tsx
│   ├── dashboard/           # Feature-specific components
│   │   ├── PerformanceChart.tsx
│   │   ├── PortfolioAllocation.tsx
│   │   ├── TopHoldings.tsx
│   │   └── SimulationPanel.tsx
│   └── auth/
│       └── LoginForm.tsx
├── core/presentation/
│   ├── components/
│   │   ├── ProtectedRoute.tsx
│   │   └── auth/
│   │       └── LoginForm.tsx
│   └── contexts/
│       └── AuthContext.tsx
└── [pages]/                 # Next.js pages
    ├── page.tsx
    └── layout.tsx
```

## Component Categories

### 1. Atoms (Basic Components)

Smallest building blocks with single responsibility.

#### Button Component
```typescript
// Button.types.ts
export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
  className?: string;
  type?: 'button' | 'submit' | 'reset';
}

// Button.tsx
import { ButtonProps } from './Button.types';
import { buttonStyles } from './Button.styles';

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'medium',
  disabled = false,
  loading = false,
  onClick,
  children,
  className,
  type = 'button',
}) => {
  const styles = buttonStyles({ variant, size, disabled, loading });

  return (
    <button
      type={type}
      className={`${styles} ${className || ''}`}
      disabled={disabled || loading}
      onClick={onClick}
    >
      {loading ? <LoadingSpinner /> : children}
    </button>
  );
};

// Button.styles.ts
import { cva } from 'class-variance-authority';

export const buttonStyles = cva(
  'inline-flex items-center justify-center rounded-lg font-medium transition-colors focus:outline-none focus:ring-2',
  {
    variants: {
      variant: {
        primary: 'bg-blue-600 text-white hover:bg-blue-700',
        secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300',
        danger: 'bg-red-600 text-white hover:bg-red-700',
      },
      size: {
        small: 'px-3 py-1.5 text-sm',
        medium: 'px-4 py-2 text-base',
        large: 'px-6 py-3 text-lg',
      },
      disabled: {
        true: 'opacity-50 cursor-not-allowed',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'medium',
    },
  }
);
```

#### Input Component
```typescript
interface InputProps {
  type?: 'text' | 'email' | 'password' | 'number';
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  disabled?: boolean;
  required?: boolean;
  label?: string;
}

export const Input: React.FC<InputProps> = ({
  type = 'text',
  placeholder,
  value,
  onChange,
  error,
  disabled,
  required,
  label,
}) => {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        className={`
          w-full px-4 py-2 border rounded-lg
          focus:ring-2 focus:ring-blue-500 focus:border-transparent
          ${error ? 'border-red-500' : 'border-gray-300'}
          ${disabled ? 'bg-gray-100 cursor-not-allowed' : ''}
        `}
      />
      {error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}
    </div>
  );
};
```

### 2. Molecules (Composite Components)

Combinations of atoms forming more complex units.

#### Form Group Component
```typescript
interface FormGroupProps {
  label: string;
  error?: string;
  required?: boolean;
  children: React.ReactNode;
  helpText?: string;
}

export const FormGroup: React.FC<FormGroupProps> = ({
  label,
  error,
  required,
  children,
  helpText,
}) => {
  return (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      {children}
      {helpText && !error && (
        <p className="mt-1 text-sm text-gray-500">{helpText}</p>
      )}
      {error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}
    </div>
  );
};
```

#### Card Component
```typescript
// Card.types.ts
export interface CardProps {
  title?: string;
  subtitle?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  variant?: 'default' | 'elevated' | 'outlined';
  padding?: 'none' | 'small' | 'medium' | 'large';
  className?: string;
}

// Card.tsx
export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  children,
  footer,
  variant = 'default',
  padding = 'medium',
  className,
}) => {
  const paddingClasses = {
    none: '',
    small: 'p-3',
    medium: 'p-6',
    large: 'p-8',
  };

  const variantClasses = {
    default: 'bg-white shadow-sm',
    elevated: 'bg-white shadow-lg',
    outlined: 'bg-white border border-gray-200',
  };

  return (
    <div className={`
      rounded-lg
      ${variantClasses[variant]}
      ${paddingClasses[padding]}
      ${className || ''}
    `}>
      {(title || subtitle) && (
        <div className="mb-4">
          {title && <h3 className="text-lg font-semibold">{title}</h3>}
          {subtitle && <p className="text-sm text-gray-600">{subtitle}</p>}
        </div>
      )}
      <div>{children}</div>
      {footer && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          {footer}
        </div>
      )}
    </div>
  );
};
```

### 3. Organisms (Complex Components)

Complex components with business logic.

#### Portfolio Allocation Component
```typescript
interface PortfolioAllocationProps {
  allocations: AllocationItem[];
  onAllocationClick?: (symbol: string) => void;
  showChart?: boolean;
}

export const PortfolioAllocation: React.FC<PortfolioAllocationProps> = ({
  allocations,
  onAllocationClick,
  showChart = true,
}) => {
  const pieData = useMemo(() => 
    allocations.map(item => ({
      name: item.symbol,
      value: item.weight * 100,
      sector: item.sector,
    })),
    [allocations]
  );

  const COLORS = ['#8b5cf6', '#ec4899', '#10b981', '#f59e0b', '#3b82f6'];

  return (
    <Card title="Portfolio Allocation" variant="elevated">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {showChart && (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(entry) => `${entry.name}: ${entry.value.toFixed(1)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={COLORS[index % COLORS.length]}
                    onClick={() => onAllocationClick?.(entry.name)}
                    style={{ cursor: 'pointer' }}
                  />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        )}
        
        <div className="space-y-2">
          {allocations.map((allocation, index) => (
            <motion.div
              key={allocation.symbol}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
              onClick={() => onAllocationClick?.(allocation.symbol)}
            >
              <div className="flex items-center gap-3">
                <div 
                  className="w-4 h-4 rounded-full"
                  style={{ backgroundColor: COLORS[index % COLORS.length] }}
                />
                <div>
                  <p className="font-medium">{allocation.symbol}</p>
                  <p className="text-sm text-gray-600">{allocation.name}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-semibold">{(allocation.weight * 100).toFixed(2)}%</p>
                {allocation.value && (
                  <p className="text-sm text-gray-600">
                    ${allocation.value.toLocaleString()}
                  </p>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </Card>
  );
};
```

#### Performance Chart Component
```typescript
interface PerformanceChartProps {
  data: SeriesPoint[];
  comparisonData?: SeriesPoint[];
  showControls?: boolean;
  height?: number;
}

export const PerformanceChart: React.FC<PerformanceChartProps> = ({
  data,
  comparisonData,
  showControls = true,
  height = 400,
}) => {
  const [timeRange, setTimeRange] = useState<string>('all');
  const [showComparison, setShowComparison] = useState(true);

  const filteredData = useMemo(() => {
    // Filter data based on timeRange
    return filterDataByTimeRange(data, timeRange);
  }, [data, timeRange]);

  return (
    <Card title="Performance" className="w-full">
      {showControls && (
        <div className="flex justify-between items-center mb-4">
          <div className="flex gap-2">
            {['1M', '3M', '6M', '1Y', 'ALL'].map(range => (
              <Button
                key={range}
                variant={timeRange === range ? 'primary' : 'secondary'}
                size="small"
                onClick={() => setTimeRange(range)}
              >
                {range}
              </Button>
            ))}
          </div>
          
          {comparisonData && (
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={showComparison}
                onChange={(e) => setShowComparison(e.target.checked)}
              />
              <span className="text-sm">Show S&P 500</span>
            </label>
          )}
        </div>
      )}
      
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={filteredData}>
          <defs>
            <linearGradient id="colorMain" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.1}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="date" 
            tickFormatter={(date) => formatDate(date)}
          />
          <YAxis tickFormatter={(value) => `$${value.toFixed(0)}`} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          
          <Area
            type="monotone"
            dataKey="value"
            stroke="#8b5cf6"
            fillOpacity={1}
            fill="url(#colorMain)"
            name="Portfolio"
          />
          
          {showComparison && comparisonData && (
            <Line
              type="monotone"
              dataKey="benchmark"
              stroke="#ec4899"
              strokeWidth={2}
              dot={false}
              name="S&P 500"
            />
          )}
        </AreaChart>
      </ResponsiveContainer>
    </Card>
  );
};
```

### 4. Templates (Layout Components)

Page layouts and structural components.

#### Dashboard Layout
```typescript
interface DashboardLayoutProps {
  children: React.ReactNode;
  sidebar?: React.ReactNode;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  children,
  sidebar,
}) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="lg:hidden p-2"
              >
                <MenuIcon />
              </button>
              <h1 className="text-xl font-semibold">Waardhaven AutoIndex</h1>
            </div>
            <UserMenu />
          </div>
        </div>
      </nav>

      <div className="flex">
        {/* Sidebar */}
        {sidebar && (
          <aside className={`
            lg:block lg:w-64 bg-white border-r
            ${sidebarOpen ? 'block' : 'hidden'}
          `}>
            {sidebar}
          </aside>
        )}

        {/* Main Content */}
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  );
};
```

### 5. Pages (Route Components)

Top-level components mapped to routes.

#### Dashboard Page
```typescript
export default function DashboardPage() {
  const [indexSeries, setIndexSeries] = useState<SeriesPoint[]>([]);
  const [allocations, setAllocations] = useState<AllocationItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [indexRes, allocRes] = await Promise.all([
        portfolioService.getIndexHistory(),
        portfolioService.getCurrentAllocations(),
      ]);
      
      setIndexSeries(indexRes.series);
      setAllocations(allocRes.allocations);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSkeleton />;
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <PerformanceCards data={indexSeries} />
        <PerformanceChart data={indexSeries} />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <PortfolioAllocation allocations={allocations} />
          <TopHoldings allocations={allocations} />
        </div>
      </div>
    </DashboardLayout>
  );
}
```

## Component Patterns

### 1. Container/Presentational Pattern

```typescript
// Container Component (Smart)
const PortfolioContainer: React.FC = () => {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    portfolioService.getIndexHistory().then(setData);
  }, []);
  
  return <PortfolioView data={data} />;
};

// Presentational Component (Dumb)
const PortfolioView: React.FC<{ data: any }> = ({ data }) => {
  if (!data) return <LoadingSpinner />;
  return <div>{/* Render data */}</div>;
};
```

### 2. Compound Component Pattern

```typescript
interface TabsContextValue {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const TabsContext = createContext<TabsContextValue | null>(null);

export const Tabs: React.FC<{ children: React.ReactNode }> & {
  List: typeof TabsList;
  Tab: typeof Tab;
  Panel: typeof TabPanel;
} = ({ children }) => {
  const [activeTab, setActiveTab] = useState('');
  
  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      {children}
    </TabsContext.Provider>
  );
};

const TabsList: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="flex border-b">{children}</div>
);

const Tab: React.FC<{ value: string; children: React.ReactNode }> = ({ 
  value, 
  children 
}) => {
  const context = useContext(TabsContext);
  return (
    <button
      className={context?.activeTab === value ? 'active' : ''}
      onClick={() => context?.setActiveTab(value)}
    >
      {children}
    </button>
  );
};

const TabPanel: React.FC<{ value: string; children: React.ReactNode }> = ({ 
  value, 
  children 
}) => {
  const context = useContext(TabsContext);
  if (context?.activeTab !== value) return null;
  return <div>{children}</div>;
};

Tabs.List = TabsList;
Tabs.Tab = Tab;
Tabs.Panel = TabPanel;

// Usage
<Tabs>
  <Tabs.List>
    <Tabs.Tab value="overview">Overview</Tabs.Tab>
    <Tabs.Tab value="details">Details</Tabs.Tab>
  </Tabs.List>
  <Tabs.Panel value="overview">Overview content</Tabs.Panel>
  <Tabs.Panel value="details">Details content</Tabs.Panel>
</Tabs>
```

### 3. Render Props Pattern

```typescript
interface DataFetcherProps<T> {
  url: string;
  children: (data: T | null, loading: boolean, error: Error | null) => React.ReactNode;
}

function DataFetcher<T>({ url, children }: DataFetcherProps<T>) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    fetch(url)
      .then(res => res.json())
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [url]);

  return <>{children(data, loading, error)}</>;
}

// Usage
<DataFetcher<User[]> url="/api/users">
  {(users, loading, error) => {
    if (loading) return <Spinner />;
    if (error) return <Error message={error.message} />;
    return <UserList users={users!} />;
  }}
</DataFetcher>
```

## Component Best Practices

1. **Single Responsibility** - Each component should do one thing well
2. **Composition over Inheritance** - Use composition to build complex UIs
3. **Type Safety** - Use TypeScript for all props and state
4. **Accessibility** - Include ARIA labels and keyboard navigation
5. **Performance** - Use React.memo for expensive components
6. **Testing** - Write unit tests for business logic
7. **Documentation** - Document complex components with JSDoc
8. **Error Boundaries** - Wrap components to catch errors gracefully

## Next Steps

- Review [State Management](./06-state-management.md)
- Learn about [Routes and Pages](./07-routes-and-pages.md)
- Understand [Testing Guide](./09-testing-guide.md)