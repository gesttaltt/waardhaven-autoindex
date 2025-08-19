# Frontend Refactoring Tasks

**Priority**: P2 - MEDIUM  
**Status**: 🔴 Minimal Progress  
**Estimated**: 2-3 days  
**Framework**: Next.js 14, React 18, TypeScript

## 🎯 Objective

Refactor frontend for better maintainability, performance, and user experience:
- Consolidate authentication logic
- Standardize data fetching
- Improve component architecture
- Add mobile responsiveness
- Optimize performance

## 📋 Current Issues

### 🔴 Critical Problems
- Calculations still in frontend (should be backend)
- No unified auth hook
- Inconsistent error handling
- Poor mobile experience
- No loading/error states

### 🟡 Architecture Issues
- Mixed data fetching patterns
- No component library
- Prop drilling in places
- State management scattered

## 📋 Task Breakdown

### Phase 1: Remove Frontend Calculations (Critical - 4 hours)

#### Task 1.1: Delete Calculation Files
```bash
# Files to remove:
- [ ] apps/web/app/lib/calculations/portfolio.ts
- [ ] apps/web/app/lib/calculations/technical.ts
- [ ] apps/web/app/lib/calculations/risk.ts
- [ ] apps/web/app/lib/calculations/index.ts
```

#### Task 1.2: Replace with API Calls
**File**: `apps/web/app/services/api/calculations.ts`

```typescript
// API service methods:
- [ ] getPortfolioMetrics()
- [ ] getTechnicalIndicators()
- [ ] getRiskMetrics()
- [ ] getPerformanceData()
```

### Phase 2: Authentication Consolidation (3 hours)

#### Task 2.1: Create Unified Auth Hook
**File**: `apps/web/app/hooks/useAuth.ts`

```typescript
// Hook features:
- [ ] Login/logout methods
- [ ] Current user state
- [ ] Token management
- [ ] Auto-refresh
- [ ] Protected route wrapper
```

#### Task 2.2: Auth Context Provider
**File**: `apps/web/app/providers/AuthProvider.tsx`

```typescript
// Provider features:
- [ ] JWT token storage
- [ ] User session management
- [ ] Automatic token refresh
- [ ] Logout on 401
```

#### Task 2.3: Protected Route Component
**File**: `apps/web/app/components/auth/ProtectedRoute.tsx`

```typescript
// Component features:
- [ ] Check authentication
- [ ] Redirect to login
- [ ] Loading state
- [ ] Role-based access
```

### Phase 3: Data Fetching Standardization (4 hours)

#### Task 3.1: Setup React Query
```bash
npm install @tanstack/react-query @tanstack/react-query-devtools
```

#### Task 3.2: Query Client Configuration
**File**: `apps/web/app/providers/QueryProvider.tsx`

```typescript
// Configuration:
- [ ] Default stale time
- [ ] Cache time
- [ ] Retry logic
- [ ] Error handling
```

#### Task 3.3: Custom Hooks
**Directory**: `apps/web/app/hooks/queries/`

```typescript
// Hooks to create:
- [ ] usePortfolio()
- [ ] useAssets()
- [ ] useMarketData()
- [ ] useAllocations()
- [ ] usePerformance()
```

### Phase 4: Component Architecture (6 hours)

#### Task 4.1: Component Library Setup
**Directory**: `apps/web/app/components/ui/`

```typescript
// Base components:
- [ ] Button
- [ ] Input
- [ ] Card
- [ ] Modal
- [ ] Table
- [ ] Chart
- [ ] Spinner
- [ ] Alert
```

#### Task 4.2: Layout Components
**Directory**: `apps/web/app/components/layout/`

```typescript
// Layout components:
- [ ] Header
- [ ] Sidebar
- [ ] Footer
- [ ] PageContainer
- [ ] ContentGrid
```

#### Task 4.3: Feature Components
```typescript
// Refactor existing:
- [ ] Dashboard
- [ ] Portfolio
- [ ] Analytics
- [ ] Settings
```

### Phase 5: Mobile Responsiveness (4 hours)

#### Task 5.1: Responsive Utilities
**File**: `apps/web/app/styles/responsive.css`

```css
/* Breakpoints:
- [ ] Mobile: 320px - 768px
- [ ] Tablet: 768px - 1024px
- [ ] Desktop: 1024px+
*/
```

#### Task 5.2: Mobile Navigation
**File**: `apps/web/app/components/layout/MobileNav.tsx`

```typescript
// Features:
- [ ] Hamburger menu
- [ ] Drawer navigation
- [ ] Touch gestures
- [ ] Bottom tab bar
```

#### Task 5.3: Responsive Components
```typescript
// Components to make responsive:
- [ ] Tables → Cards on mobile
- [ ] Charts → Scrollable
- [ ] Forms → Stack vertically
- [ ] Modals → Full screen on mobile
```

### Phase 6: Performance Optimization (3 hours)

#### Task 6.1: Code Splitting
```typescript
// Implement dynamic imports:
- [ ] Route-based splitting
- [ ] Component lazy loading
- [ ] Suspense boundaries
```

#### Task 6.2: Image Optimization
```typescript
// Optimizations:
- [ ] Use next/image
- [ ] Lazy loading
- [ ] Responsive images
- [ ] WebP format
```

#### Task 6.3: Bundle Analysis
```bash
# Setup bundle analyzer:
npm install @next/bundle-analyzer
```

## 📊 Implementation Examples

### Unified Auth Hook

```typescript
// apps/web/app/hooks/useAuth.ts

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { authApi } from '@/services/api/auth';
import { User } from '@/types/user';

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
}

export const useAuth = () => {
  const router = useRouter();
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
    error: null,
  });

  // Check stored token on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      validateToken(token);
    } else {
      setState(prev => ({ ...prev, isLoading: false }));
    }
  }, []);

  const validateToken = async (token: string) => {
    try {
      const user = await authApi.validateToken(token);
      setState({
        user,
        isLoading: false,
        isAuthenticated: true,
        error: null,
      });
    } catch (error) {
      localStorage.removeItem('access_token');
      setState({
        user: null,
        isLoading: false,
        isAuthenticated: false,
        error: 'Session expired',
      });
    }
  };

  const login = useCallback(async (email: string, password: string) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const { user, access_token, refresh_token } = await authApi.login(email, password);
      
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      
      setState({
        user,
        isLoading: false,
        isAuthenticated: true,
        error: null,
      });
      
      router.push('/dashboard');
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error.message || 'Login failed',
      }));
    }
  }, [router]);

  const logout = useCallback(async () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    
    setState({
      user: null,
      isLoading: false,
      isAuthenticated: false,
      error: null,
    });
    
    router.push('/login');
  }, [router]);

  const refreshToken = useCallback(async () => {
    const refresh = localStorage.getItem('refresh_token');
    if (!refresh) {
      logout();
      return;
    }

    try {
      const { access_token } = await authApi.refreshToken(refresh);
      localStorage.setItem('access_token', access_token);
    } catch (error) {
      logout();
    }
  }, [logout]);

  return {
    ...state,
    login,
    logout,
    refreshToken,
  };
};
```

### React Query Setup

```typescript
// apps/web/app/providers/QueryProvider.tsx

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { ReactNode } from 'react';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      retry: 3,
      retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
});

export const QueryProvider = ({ children }: { children: ReactNode }) => {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {process.env.NODE_ENV === 'development' && <ReactQueryDevtools />}
    </QueryClientProvider>
  );
};
```

### Mobile Responsive Table

```typescript
// apps/web/app/components/ui/ResponsiveTable.tsx

import { useMediaQuery } from '@/hooks/useMediaQuery';

interface TableProps<T> {
  data: T[];
  columns: Column<T>[];
  onRowClick?: (row: T) => void;
}

export function ResponsiveTable<T>({ data, columns, onRowClick }: TableProps<T>) {
  const isMobile = useMediaQuery('(max-width: 768px)');

  if (isMobile) {
    return (
      <div className="space-y-4">
        {data.map((row, idx) => (
          <Card
            key={idx}
            onClick={() => onRowClick?.(row)}
            className="p-4 cursor-pointer hover:shadow-lg transition-shadow"
          >
            {columns.map(col => (
              <div key={col.key} className="flex justify-between py-2 border-b last:border-0">
                <span className="text-gray-600">{col.label}:</span>
                <span className="font-medium">{col.render(row)}</span>
              </div>
            ))}
          </Card>
        ))}
      </div>
    );
  }

  return (
    <table className="w-full">
      <thead>
        <tr>
          {columns.map(col => (
            <th key={col.key} className="text-left p-4">
              {col.label}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row, idx) => (
          <tr
            key={idx}
            onClick={() => onRowClick?.(row)}
            className="hover:bg-gray-50 cursor-pointer"
          >
            {columns.map(col => (
              <td key={col.key} className="p-4">
                {col.render(row)}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

## 🧪 Testing Checklist

### Component Tests
- [ ] Auth hook functionality
- [ ] Protected route behavior
- [ ] Data fetching hooks
- [ ] Component rendering
- [ ] Mobile responsiveness

### Integration Tests
- [ ] Login flow
- [ ] Data refresh
- [ ] Error handling
- [ ] Navigation
- [ ] State management

## 📈 Success Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Bundle size | >2MB | <500KB | 🔴 |
| First paint | >3s | <1s | 🔴 |
| Mobile score | 60 | 95+ | 🔴 |
| Code coverage | 10% | 70% | 🔴 |
| Component reuse | Low | High | 🔴 |

## 🔄 Dependencies

```json
{
  "dependencies": {
    "@tanstack/react-query": "^5.0.0",
    "@tanstack/react-query-devtools": "^5.0.0",
    "clsx": "^2.0.0",
    "react-hook-form": "^7.47.0",
    "zod": "^3.22.0"
  },
  "devDependencies": {
    "@next/bundle-analyzer": "^14.0.0",
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0"
  }
}
```

---

**Next**: Continue with [05-deployment-automation.md](./05-deployment-automation.md)