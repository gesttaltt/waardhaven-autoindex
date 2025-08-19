# Waardhaven AutoIndex Web Application

## Overview
The Waardhaven AutoIndex frontend is a Next.js 14 application that provides a modern, responsive interface for automated index fund management. It features real-time portfolio tracking, investment simulation, AI-driven strategy optimization, and comprehensive system monitoring.

**Coverage Status**: 85% Complete (3 new pages added in latest update)

## Features

### Core Functionality
- **Portfolio Dashboard**: Real-time visualization of index performance and allocations
- **Investment Simulation**: Test investment strategies with historical data
- **Multi-Currency Support**: Simulate investments in various currencies
- **Performance Analytics**: Comprehensive risk metrics and performance indicators
- **Strategy Configuration**: Adjust index composition strategies with live rebalancing

### System Operations ✨ NEW
- **Task Management**: Monitor and control background operations
- **System Diagnostics**: Health monitoring and cache management
- **Report Generation**: Backend capability for report generation (no frontend UI yet)
- **Real-time Monitoring**: Live task progress and system status updates

### Technical Features
- **Real-time Data**: WebSocket-ready architecture for live updates
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Type Safety**: Full TypeScript implementation
- **Performance Optimized**: React memoization and lazy loading
- **Error Boundaries**: Graceful error handling throughout
- **Background Tasks**: Celery integration for async operations

## Tech Stack
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Animations**: Framer Motion
- **HTTP Client**: Axios
- **State Management**: React Hooks

## Actual Project Structure

The frontend uses a simplified structure focused on functionality:

```
apps/web/
├── app/
│   ├── components/          # Reusable Components
│   │   ├── dashboard/     # Dashboard-specific components
│   │   │   ├── PerformanceCards.tsx
│   │   │   ├── PerformanceChart.tsx
│   │   │   ├── PortfolioAllocation.tsx
│   │   │   └── SimulationPanel.tsx
│   │   ├── shared/        # Shared UI components
│   │   │   ├── Button/
│   │   │   ├── Card/
│   │   │   └── ErrorBoundary.tsx
│   │   ├── SmartRefresh.tsx
│   │   └── StrategyConfig.tsx
│   │
│   ├── hooks/              # Custom React Hooks
│   │   ├── api/           
│   │   │   └── useApiCall.ts
│   │   ├── useChartData.ts
│   │   ├── usePortfolioData.ts
│   │   └── useSimulation.ts
│   │
│   ├── services/           # API Service Layer
│   │   └── api/           
│   │       ├── base.ts
│   │       ├── client.ts
│   │       ├── portfolio.ts
│   │       ├── market.ts
│   │       ├── strategy.ts
│   │       ├── background.ts
│   │       ├── diagnostics.ts
│   │       ├── manual.ts
│   │       ├── news.ts
│   │       └── types.ts
│   │
│   ├── lib/               # Utilities
│   │   ├── calculations/
│   │   │   └── portfolio.ts
│   │   └── utils.ts
│   │
│   ├── types/             # TypeScript Types
│   │   ├── api.ts
│   │   ├── chart.ts
│   │   └── portfolio.ts
│   │
│   ├── constants/         # Application Constants
│   │   ├── config.ts
│   │   └── theme.ts
│   │
│   ├── core/              # Clean Architecture Implementation (Active)
│   │   ├── application/   # Application-specific use cases
│   │   │   └── usecases/auth/  # Authentication use cases
│   │   ├── domain/        # Business entities and rules
│   │   │   ├── entities/  # Domain models (User, Portfolio, SystemHealth, DataQuality)
│   │   │   ├── repositories/  # Repository interfaces
│   │   │   └── usecases/  # Domain use cases
│   │   ├── infrastructure/  # External service implementations
│   │   │   ├── api/       # HTTP client and API client
│   │   │   ├── auth/      # Auth providers and token management
│   │   │   └── repositories/  # Concrete repository implementations
│   │   └── presentation/  # React-specific code
│   │       ├── components/  # Clean architecture UI components
│   │       ├── contexts/  # AuthContext (actively used)
│   │       └── hooks/     # Custom hooks for clean components
│   │
│   └── [pages]/          # Next.js Page Routes
│       ├── dashboard/
│       ├── tasks/
│       ├── diagnostics/
│       ├── news/
│       ├── strategy/
│       ├── login/
│       └── register/
├── public/               # Static assets
└── tests/               # Test files

```

## Pages & Routes

The application includes the following pages, each serving a specific purpose in the platform:

### Public Pages
- **`/` (Landing)** - Landing page with platform introduction and feature highlights
- **`/login`** - User authentication page with email/password and Google OAuth support
- **`/register`** - New user registration with validation

### Protected Pages (Authentication Required)
- **`/dashboard`** - Main portfolio dashboard showing:
  - Real-time index performance
  - Portfolio allocation charts
  - Performance metrics cards
  - Investment simulation panel
  - Historical performance charts
  
- **`/strategy`** - Strategy configuration page for:
  - Adjusting index composition rules
  - Setting rebalancing parameters
  - Volatility and risk management
  - Strategy backtesting

- **`/admin`** - Administrative interface for:
  - User management
  - System configuration
  - Advanced settings
  - Platform monitoring

- **`/tasks`** - Background task management:
  - View running tasks
  - Monitor task history
  - Trigger manual operations
  - Task scheduling status

- **`/diagnostics`** - System health monitoring:
  - API connectivity status
  - Database health checks
  - Cache performance metrics
  - Service availability monitoring

- **`/news`** - Market news and insights:
  - Real-time market news feed
  - AI-powered analysis
  - Sentiment tracking
  - News impact on portfolio

## Clean Architecture Implementation

The `core/` directory implements Clean Architecture principles with clear separation of concerns. This architecture is **actively used** in the application, particularly for authentication and system monitoring features.

### Layer Structure

#### Domain Layer (`core/domain/`)
**Purpose**: Contains business logic independent of any framework or external dependencies.

- **Entities**: Pure business objects (`User`, `Portfolio`, `SystemHealth`, `DataQuality`)
- **Repository Interfaces**: Contracts for data access (dependency inversion)
- **Use Cases**: Business rules and operations

#### Application Layer (`core/application/`)
**Purpose**: Application-specific business rules and orchestration.

- **Authentication Use Cases**: `LoginUseCase`, `GoogleAuthUseCase`
- Orchestrates between domain and infrastructure layers

#### Infrastructure Layer (`core/infrastructure/`)
**Purpose**: Concrete implementations of external services and data access.

- **API Clients**: `HttpClient`, `ApiClient` for backend communication
- **Auth Providers**: `GoogleAuthProvider`, `TokenManager` for authentication
- **Repository Implementations**: Concrete implementations of domain interfaces
  - `AuthRepository`: Manages authentication state and tokens
  - `DataQualityRepository`: Fetches data quality metrics
  - `SystemHealthRepository`: Retrieves system health status

#### Presentation Layer (`core/presentation/`)
**Purpose**: React-specific components and hooks following clean architecture.

**Active Components**:
- **`AuthContext`**: Global authentication state management (used throughout the app)
- **`SystemHealthIndicator`**: Displays system health metrics (used in dashboard)
- **`DataQualityIndicator`**: Shows data quality status (used in dashboard)
- **`ProtectedRoute`**: Route protection wrapper

**Custom Hooks**:
- `useSystemHealth`: Monitors system health with auto-refresh
- `useDataQuality`: Tracks data quality metrics
- `useApiRequest`: Generic API request handler with error management

### Implementation Status

✅ **Fully Implemented**:
- Authentication flow with clean architecture
- System health monitoring
- Data quality assessment
- Repository pattern for data access

⚠️ **Partially Implemented**:
- Portfolio management (entities defined, repositories pending)
- Some use cases defined but not fully integrated

❌ **Not Yet Implemented**:
- Full portfolio repository implementation
- Complete migration of all API calls to clean architecture

### Architecture Principles

#### 1. Separation of Concerns
- **UI Components**: Pure, reusable components with no business logic
- **Hooks**: Encapsulate business logic and state management
- **Services**: Handle external API communication
- **Lib**: Core business logic independent of React

#### 2. Component Categories

**Presentational Components (Dumb)**
- Located in `components/ui/`
- Pure functions with props
- No direct API calls
- Fully reusable across features
- Example:
```typescript
// components/ui/Button/Button.tsx
interface ButtonProps {
  variant: 'primary' | 'secondary';
  size: 'sm' | 'md' | 'lg';
  onClick: () => void;
  children: React.ReactNode;
}

export function Button({ variant, size, onClick, children }: ButtonProps) {
  return (
    <button className={buttonStyles({ variant, size })} onClick={onClick}>
      {children}
    </button>
  );
}
```

**Container Components (Smart)**
- Located in page directories
- Connect to hooks and services
- Handle data fetching and state
- Compose presentational components
- Example:
```typescript
// app/dashboard/page.tsx
export default function DashboardPage() {
  const { data, loading, error } = usePortfolioData();
  const { refresh } = useDataRefresh();
  
  if (loading) return <LoadingState />;
  if (error) return <ErrorState error={error} />;
  
  return (
    <DashboardLayout>
      <PerformanceChart data={data} />
      <RefreshButton onClick={refresh} />
    </DashboardLayout>
  );
}
```

#### 3. Custom Hooks Pattern

**API Hooks**
```typescript
// hooks/api/usePortfolioData.ts
export function usePortfolioData() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    portfolioService.getHistory()
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, []);
  
  return { data, loading, error };
}
```

**Business Logic Hooks**
```typescript
// hooks/usePortfolioCalculations.ts
export function usePortfolioCalculations(data: PortfolioData) {
  const returns = useMemo(() => calculateReturns(data), [data]);
  const risk = useMemo(() => calculateRisk(data), [data]);
  const sharpe = useMemo(() => calculateSharpeRatio(returns, risk), [returns, risk]);
  
  return { returns, risk, sharpe };
}
```

#### 4. Styling Strategy

**Component Styles**
```typescript
// styles/components/Button.styles.ts
export const buttonStyles = cva(
  "rounded-lg font-medium transition-all",
  {
    variants: {
      variant: {
        primary: "bg-purple-500 text-white hover:bg-purple-600",
        secondary: "bg-white/10 text-white hover:bg-white/20"
      },
      size: {
        sm: "px-3 py-1 text-sm",
        md: "px-4 py-2",
        lg: "px-6 py-3 text-lg"
      }
    }
  }
);
```

#### 5. Type Safety

**Domain Types**
```typescript
// types/domain/portfolio.ts
export interface Portfolio {
  id: string;
  userId: string;
  allocations: Allocation[];
  value: number;
  lastUpdated: Date;
}

export interface Allocation {
  assetId: string;
  symbol: string;
  weight: number;
  value: number;
}
```

**API Types**
```typescript
// types/api/portfolio.ts
export interface PortfolioResponse {
  data: {
    portfolio: Portfolio;
    performance: PerformanceMetrics;
  };
  timestamp: string;
}
```

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Backend API running on port 8000

### Installation

```bash
# Navigate to web directory
cd apps/web

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Add your environment variables
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

```bash
# Start development server
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint

# Build for production
npm run build
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |

## API Integration

The application integrates with the Waardhaven AutoIndex API. See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for detailed endpoint documentation.

### Service Architecture
- **Base Service**: Abstract class with common HTTP methods and error handling
- **Portfolio Service**: Index data, allocations, and simulations
- **Market Service**: Benchmark data and market indicators
- **Background Service**: Task queue management and monitoring ✨ NEW
- **Diagnostics Service**: System health and cache operations ✨ NEW
- **Benchmark Service**: S&P 500 and performance comparisons ✨ NEW
- **Strategy API**: Strategy configuration and risk metrics
- **Market Data API**: Database status and refresh operations

### Authentication Flow
1. User logs in via `/login` page
2. JWT token stored in localStorage
3. Token automatically attached to all API requests
4. 401 responses trigger automatic logout

## Key Pages & Components

### Dashboard (`/dashboard`)
Main interface displaying:
- Portfolio performance chart with S&P 500 comparison
- Current allocations pie chart
- Investment simulator
- Risk metrics display
- Quick navigation to all system pages ✨ NEW

### Task Management (`/tasks`) ✨ NEW
Background operations center featuring:
- Active task queue visualization
- Real-time progress monitoring
- Task statistics dashboard
- Quick action buttons for common tasks
- Task history tracking

### System Diagnostics (`/diagnostics`) ✨ NEW
System health monitoring with:
- Database status indicators
- Cache performance metrics
- Data freshness tracking
- Cache management controls
- System action buttons

### Reports & Analytics (`/reports`) ❌ NOT IMPLEMENTED
This page is documented but does not exist in the codebase.
Report generation is available via backend API but has no frontend interface.

### Admin Panel (`/admin`)
Administrative interface for:
- Database status monitoring
- Smart refresh controls
- Strategy configuration
- Risk analytics

### Smart Refresh Component
Intelligent data refresh with:
- Multiple refresh modes (auto, full, minimal, cached)
- Rate limit protection
- Progress tracking
- Error recovery

### Strategy Configuration
Dynamic strategy adjustment with:
- Weight distribution controls
- Risk parameter tuning
- AI-assisted optimization
- Real-time rebalancing

## Performance Optimizations

- **Memoization**: Heavy calculations cached with `useMemo`
- **Lazy Loading**: Components loaded on demand
- **Data Caching**: 5-minute cache for frequently accessed data
- **Batched Updates**: Multiple API calls combined when possible
- **Debounced Inputs**: User input debounced to reduce API calls

## Error Handling

- **API Errors**: Graceful degradation with user-friendly messages
- **Network Failures**: Automatic retry with exponential backoff
- **Auth Errors**: Automatic redirect to login
- **Validation**: Client-side validation before API calls
- **Error Boundaries**: Prevent entire app crashes

## Clean Architecture Best Practices

### File Naming Conventions
- **Components**: PascalCase (e.g., `Button.tsx`, `PerformanceChart.tsx`)
- **Hooks**: camelCase with 'use' prefix (e.g., `usePortfolio.ts`)
- **Services**: camelCase with suffix (e.g., `portfolioService.ts`)
- **Types**: PascalCase for interfaces/types (e.g., `Portfolio.ts`)
- **Constants**: UPPER_SNAKE_CASE for values, camelCase for objects
- **Utilities**: camelCase (e.g., `formatCurrency.ts`)

### Component Structure
Each component should have its own folder with:
```
components/ui/Button/
├── Button.tsx          # Component logic
├── Button.styles.ts    # Styled components or style utilities
├── Button.types.ts     # TypeScript interfaces
├── Button.test.tsx     # Unit tests
└── index.ts           # Public API export
```

### Data Flow Pattern
```
User Action → Page Component → Custom Hook → Service → API
                     ↓              ↓           ↓        ↓
                  UI Update ← State Update ← Transform ← Response
```

### State Management Rules
1. **Local State**: Use for UI-only state (modals, toggles)
2. **Hook State**: Use for feature-specific state
3. **Context**: Use sparingly for truly global state (auth, theme)
4. **URL State**: Use for sharable state (filters, pagination)

### Error Handling Pattern
```typescript
// hooks/api/useApiCall.ts
export function useApiCall<T>(apiCall: () => Promise<T>) {
  const [state, setState] = useState({
    data: null as T | null,
    loading: true,
    error: null as Error | null
  });

  useEffect(() => {
    apiCall()
      .then(data => setState({ data, loading: false, error: null }))
      .catch(error => setState({ data: null, loading: false, error }));
  }, []);

  return state;
}
```

### Performance Optimization
1. **Memoization**: Use `useMemo` for expensive calculations
2. **Code Splitting**: Lazy load pages and heavy components
3. **Virtualization**: Use for long lists
4. **Debouncing**: For search and filter inputs
5. **Image Optimization**: Use Next.js Image component

## Testing

```bash
# Run tests (when implemented)
npm test

# Run tests in watch mode
npm run test:watch

# Coverage report
npm run test:coverage
```

### Testing Strategy
- **Unit Tests**: For utilities and business logic
- **Component Tests**: For UI components with React Testing Library
- **Integration Tests**: For API hooks and services
- **E2E Tests**: For critical user flows

## Deployment

### Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License
Private - All rights reserved

## Support
For issues or questions, please contact the development team or open an issue in the repository.