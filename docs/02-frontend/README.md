# Waardhaven AutoIndex Web Application

## Overview
The Waardhaven AutoIndex frontend is a production-ready Next.js 14 application implementing Clean Architecture with Domain-Driven Design. It provides a comprehensive interface for portfolio management, featuring real-time data visualization, investment strategy configuration, and system monitoring.

**Status**: Production-Ready (90%+ feature complete)
**Architecture**: Clean Architecture with SOLID principles
**Type Safety**: Full TypeScript implementation

## Implemented Features

### Core Pages (9 Routes)
- **Dashboard** (`/dashboard`): Portfolio overview with performance charts
- **Login/Register** (`/login`, `/register`): JWT authentication with Google OAuth
- **Strategy** (`/strategy`): Investment strategy configuration
- **News** (`/news`): Financial news feed with sentiment analysis
- **Tasks** (`/tasks`): Background task monitoring
- **Diagnostics** (`/diagnostics`): System health and cache status
- **Admin** (`/admin`): Administrative functions
- **Landing** (`/`): Public landing page

### Technical Capabilities
- **Authentication**: JWT with refresh tokens, AuthProvider context
- **State Management**: React Query for server state
- **API Integration**: Type-safe service layer with HttpClient
- **Clean Architecture**: Domain, Application, Infrastructure, Presentation layers
- **Performance**: React memoization, lazy loading, optimized re-renders
- **Error Handling**: Error boundaries with user-friendly messages

### Technical Features
- **Real-time Data**: WebSocket-ready architecture for live updates
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Type Safety**: Full TypeScript implementation
- **Performance Optimized**: React memoization and lazy loading
- **Error Boundaries**: Graceful error handling throughout
- **Background Tasks**: Celery integration for async operations

## Tech Stack
- **Framework**: Next.js 14 (App Router with SSR)
- **Language**: TypeScript 5.x
- **UI Library**: React 18
- **Styling**: Tailwind CSS 3.x
- **Charts**: Recharts for financial visualizations
- **State Management**: React Context + React Query
- **HTTP Client**: Custom HttpClient with interceptors
- **Authentication**: JWT with secure token management

## Clean Architecture Implementation (2025-01-19)

The frontend has been refactored to follow Clean Architecture principles with clear separation of concerns:

```
apps/web/app/
├── core/                    # Clean Architecture Layers
│   ├── domain/             # Business entities and rules
│   │   ├── entities/       # Pure business objects
│   │   ├── repositories/   # Repository interfaces
│   │   └── use-cases/      # Business use cases
│   ├── application/        # Application-specific logic
│   │   ├── auth/          # Authentication use cases
│   │   └── portfolio/     # Portfolio management
│   ├── infrastructure/     # External service implementations
│   │   ├── api/           # API clients
│   │   ├── repositories/  # Concrete repositories
│   │   └── token/         # Token management
│   └── presentation/       # React-specific code
│       ├── hooks/         # Custom React hooks
│       ├── contexts/      # React contexts
│       └── components/    # UI components
│   │
├── components/             # Shared UI Components
│   ├── Button/            # Typed button component
│   ├── Card/              # Reusable card component
│   ├── SystemHealthIndicator/ # Health monitoring
│   └── DataQualityIndicator/ # Data quality display
│
├── services/              # API Service Layer
│   ├── api/              # Direct API calls
│   │   ├── client.ts     # HttpClient configuration
│   │   ├── auth.ts       # Authentication endpoints
│   │   ├── portfolio.ts  # Portfolio endpoints
│   │   └── tasks.ts      # Task management
│   │
│   ├── lib/               # Core Business Logic
│   │   ├── calculations/ # Business calculations
│   │   ├── validators/   # Input validation
│   │   └── formatters/   # Data formatting
│   │
│   ├── types/             # Type Definitions
│   │   ├── api/          # API response types
│   │   ├── domain/       # Domain models
│   │   └── ui/           # UI component props
│   │
│   ├── styles/            # Styling
│   │   ├── components/   # Component-specific styles
│   │   ├── themes/       # Theme definitions
│   │   └── globals.css   # Global styles
│   │
│   ├── constants/         # Application Constants
│   │   ├── config.ts
│   │   ├── routes.ts
│   │   └── theme.ts
│   │
│   └── [pages]/          # Page Components (Smart Components)
│       ├── dashboard/
│       ├── tasks/
│       ├── diagnostics/
│       └── reports/
├── public/               # Static assets
└── tests/               # Test files

```

### Architecture Principles (SOLID)

#### 1. Single Responsibility Principle
- **Domain Layer**: Pure business logic only
- **Infrastructure**: External service integration only
- **Presentation**: UI rendering and user interaction only
- **Application**: Use case orchestration only

#### 2. Dependency Inversion Principle
- Domain defines interfaces (repositories)
- Infrastructure implements interfaces
- Presentation depends on abstractions
- No direct dependencies on external services

#### 3. Component Structure Pattern

Each component follows a consistent structure:
```
ComponentName/
├── index.ts              # Public API export
├── ComponentName.tsx     # Component implementation
├── ComponentName.types.ts # TypeScript interfaces
└── ComponentName.styles.ts # Styling constants
```

**Benefits:**
- Clear separation of concerns
- Type safety throughout
- Easy testing and maintenance
- Consistent codebase structure
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

### Reports & Analytics (`/reports`) ✨ NEW
Report generation center offering:
- Multiple report types (performance, allocation, risk)
- Custom time period selection
- Report generation progress tracking
- Historical report archive
- Quick report templates

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