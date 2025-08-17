# Frontend Refactoring TODO

*Last Updated: 2025-08-17*

## Current Frontend Status Summary

### ✅ Implemented Features
- **Pages**: Landing, Login, Register, Dashboard, Admin Panel, AI Insights
- **Tech Stack**: Next.js 14.2.5, React 18.3.1, TypeScript 5.5.4, Tailwind CSS
- **Charts**: Recharts for data visualization
- **Animation**: Framer Motion for UI animations
- **Data Fetching**: Axios with custom API service layer
- **Authentication**: JWT token-based auth with localStorage

### ⚠️ Critical Gaps Identified
1. **No Testing Framework** - Zero test files present
2. **No State Management** - No global state solution (Redux/Zustand/Context)
3. **No Error Boundaries** - Component created but not implemented
4. **TypeScript Strict Mode Disabled** - `strict: false` in tsconfig.json
5. **Missing Utility Functions** - Utils folders exist but are empty
6. **No Environment Variables** - API URL hardcoded
7. **No CI/CD Pipeline** - No GitHub Actions or deployment automation
8. **No Code Quality Tools** - Missing ESLint, Prettier configs

## Priority: HIGH - Dashboard Component Refactoring

### Current Issues
The dashboard component (`apps/web/app/dashboard/page.tsx`) has grown to 1121+ lines and violates several clean architecture principles.

### ✅ COMPLETED - Initial Refactoring (Phase 1)
The following architectural improvements have been implemented:

#### 1. **Component Size & Complexity** ✅
- [x] Component refactored from 1121 lines to ~200 lines
- [x] Responsibilities properly separated
- [x] Now maintainable and testable

#### 2. **Separation of Concerns** ✅
- [x] Data fetching logic extracted to custom hooks
- [x] Business logic moved to service layer
- [x] State management organized with custom hooks
- [x] Clear boundaries between layers established

#### 3. **Code Quality Improvements** ✅
- [x] Reduced from 15+ useState to 5 in main component
- [x] Complex conditionals simplified
- [x] Magic numbers extracted to constants
- [x] Repetitive patterns eliminated
- [x] Strong typing added (most `any` types removed)

## ✅ Completed Refactoring Tasks

### Phase 1: Extract Custom Hooks ✅
- [x] Created `usePortfolioData` hook for data fetching
- [x] Created `useSimulation` hook for simulation logic
- [x] Created `useChartData` hook for chart data transformation
- [x] Performance metrics calculation included in hooks
- [x] Technical indicators logic integrated

### Phase 2: Component Decomposition ✅
- [x] Extracted `PerformanceCards` component
- [x] Extracted `PerformanceChart` component
- [x] Extracted `SimulationPanel` component
- [x] Extracted `PortfolioAllocation` component
- [x] Extracted `TopHoldings` component
- [x] Chart controls integrated into `PerformanceChart`
- [x] Data panel integrated as subcomponent

### Phase 3: Type Safety ✅
- [x] Created proper TypeScript interfaces in `/types` folder
- [x] Removed most `any` types
- [x] Added proper type definitions for all data structures
- [x] Created domain models for portfolio, chart, and API types

### Phase 4: API Layer ✅
- [x] Created API service layer with base class
- [x] Implemented proper error handling
- [x] Created separate services for portfolio and market
- [x] Added proper API response types

### Phase 5: Constants & Configuration ✅
- [x] Extracted all magic numbers to config
- [x] Created theme constants for colors
- [x] Centralized chart configuration
- [x] Defined application constants

### Phase 6: Shared Components ✅
- [x] Created `LoadingSkeleton` component
- [x] Created `ErrorBoundary` component
- [x] Implemented reusable loading states

## 🚨 CRITICAL - Immediate Priority Tasks

### 1. Testing Infrastructure (BLOCKER)
- [ ] **Setup Testing Framework**
  - [ ] Install and configure Jest + React Testing Library
  - [ ] Create test setup files
  - [ ] Add npm scripts for testing
  - [ ] Write initial smoke tests for each page
  - [ ] Add component testing for extracted components

### 2. TypeScript Strict Mode (HIGH)
- [ ] **Enable TypeScript Strict Mode**
  - [ ] Set `strict: true` in tsconfig.json
  - [ ] Fix all resulting type errors
  - [ ] Remove remaining `any` types
  - [ ] Add proper type guards

### 3. Environment Configuration (HIGH)
- [ ] **Setup Environment Variables**
  - [ ] Create `.env.local` file
  - [ ] Move API URLs to env vars
  - [ ] Add environment validation
  - [ ] Document env vars in README

### 4. Error Handling (HIGH)
- [ ] **Implement Error Boundaries**
  - [ ] Wrap main layout with ErrorBoundary
  - [ ] Add error boundaries to each page
  - [ ] Create fallback UI components
  - [ ] Add error logging service

## 🔄 Next Steps - Backend Integration

### Immediate Tasks
- [ ] **Connect refactored frontend to backend API**
  - [ ] Test all API endpoints with new service layer
  - [ ] Validate data flow through custom hooks
  - [ ] Ensure error handling works end-to-end
  - [ ] Test WebSocket connections if applicable

### API Integration Checklist
- [ ] **Authentication Flow**
  - [ ] Verify JWT token handling in API service
  - [ ] Test token refresh mechanism
  - [ ] Validate protected route access
  - [ ] Add auth context/provider
  
- [ ] **Data Fetching**
  - [ ] Test portfolio data loading
  - [ ] Verify market data updates
  - [ ] Validate individual asset fetching
  - [ ] Test simulation endpoint
  
- [ ] **Error Scenarios**
  - [ ] Handle network failures gracefully
  - [ ] Test rate limiting responses
  - [ ] Validate error message display
  - [ ] Test retry mechanisms with exponential backoff

### Performance Testing
- [ ] Measure initial load time
- [ ] Test with large datasets
- [ ] Validate chart rendering performance
- [ ] Check memory usage patterns
- [ ] Add performance monitoring (Web Vitals)

## 📋 Remaining Optimization Tasks

### Phase 7: Advanced State Management (NEEDED)
- [ ] **Implement Global State Solution**
  - [ ] Choose between Zustand, Jotai, or Context API
  - [ ] Create auth store/context
  - [ ] Create portfolio data store
  - [ ] Add optimistic UI updates
  - [ ] Implement proper cache invalidation
  - [ ] Add real-time data subscriptions

### Phase 8: Performance Optimization
- [ ] Implement React.memo for expensive components
- [ ] Add virtualization for large lists
- [ ] Optimize bundle size with code splitting
- [ ] Implement progressive loading

### Phase 9: Testing (CRITICAL - Currently 0% coverage)
- [ ] **Unit Testing**
  - [ ] Add unit tests for all hooks
  - [ ] Test API service layer
  - [ ] Test utility functions
  - [ ] Test type definitions
- [ ] **Component Testing**
  - [ ] Test all dashboard components
  - [ ] Test form components (login/register)
  - [ ] Test chart components
  - [ ] Test loading states
- [ ] **Integration Testing**
  - [ ] Test page flows
  - [ ] Test API integration
  - [ ] Test auth flows
- [ ] **E2E Testing**
  - [ ] Setup Playwright or Cypress
  - [ ] Test critical user journeys
  - [ ] Test multi-browser support

### Phase 10: Accessibility & UX
- [ ] Add ARIA labels
- [ ] Implement keyboard navigation
- [ ] Improve contrast ratios
- [ ] Add screen reader support
- [ ] Implement responsive design improvements

## File Structure Proposal

```
apps/web/
├── app/
│   ├── dashboard/
│   │   ├── page.tsx (main page - max 200 lines)
│   │   ├── layout.tsx
│   │   └── loading.tsx
│   ├── components/
│   │   ├── dashboard/
│   │   │   ├── PerformanceCards.tsx
│   │   │   ├── PerformanceChart.tsx
│   │   │   ├── SimulationPanel.tsx
│   │   │   ├── PortfolioAllocation.tsx
│   │   │   ├── TopHoldings.tsx
│   │   │   ├── ChartControls.tsx
│   │   │   └── DataPanel.tsx
│   │   └── shared/
│   │       ├── LoadingSkeleton.tsx
│   │       ├── ErrorBoundary.tsx
│   │       └── Card.tsx
│   ├── hooks/
│   │   ├── usePortfolioData.ts
│   │   ├── useSimulation.ts
│   │   ├── useChartData.ts
│   │   ├── usePerformanceMetrics.ts
│   │   └── useTechnicalIndicators.ts
│   ├── services/
│   │   ├── api/
│   │   │   ├── portfolio.ts
│   │   │   ├── simulation.ts
│   │   │   └── market.ts
│   │   └── utils/
│   │       ├── calculations.ts
│   │       ├── formatters.ts
│   │       └── validators.ts
│   ├── types/
│   │   ├── portfolio.ts
│   │   ├── chart.ts
│   │   └── api.ts
│   └── constants/
│       ├── theme.ts
│       └── config.ts
```

## Specific Issues to Fix

### Tooltip Contrast Issue
- [x] Portfolio allocation pie chart tooltip has black text on dark background
- [ ] Need to set proper text color in all tooltip configurations
- [ ] Should use consistent tooltip styling across all charts

### Data Fetching Issues
- [ ] No proper error handling UI
- [ ] No retry mechanisms
- [ ] No cancellation of requests
- [ ] Loading states not properly managed

### Performance Issues
- [ ] Chart data recalculated on every render
- [ ] No debouncing for user inputs
- [ ] Large component re-renders unnecessarily
- [ ] No lazy loading for heavy components

### Accessibility Issues
- [ ] Missing ARIA labels
- [ ] No keyboard navigation support
- [ ] Poor contrast ratios in some areas
- [ ] No screen reader support

## Implementation Priority (REVISED)

### 🔴 Week 1 - Critical Foundation
1. **Testing Setup** (Day 1-2)
   - Install Jest + React Testing Library
   - Write smoke tests for all pages
   - Achieve minimum 20% coverage

2. **TypeScript Strict Mode** (Day 3-4)
   - Enable strict mode
   - Fix type errors systematically
   - Document type conventions

3. **Environment Setup** (Day 5)
   - Implement env variables
   - Setup development/production configs
   - Add validation

### 🟡 Week 2-3 - Core Infrastructure
1. **State Management** (Week 2)
   - Implement Zustand or Context API
   - Migrate auth to global state
   - Add data caching layer

2. **Error Handling** (Week 2)
   - Implement ErrorBoundary properly
   - Add error logging
   - Create user-friendly error pages

3. **Code Quality** (Week 3)
   - Setup ESLint + Prettier
   - Add pre-commit hooks
   - Configure CI/CD pipeline

### 🟢 Week 4-6 - Optimization & Polish
1. **Performance** (Week 4)
   - Implement code splitting
   - Add React.memo where needed
   - Optimize bundle size

2. **Testing Coverage** (Week 5)
   - Achieve 60%+ test coverage
   - Add integration tests
   - Setup E2E testing

3. **Documentation** (Week 6)
   - Complete API documentation
   - Add component storybook
   - Update deployment guides

## Success Metrics (UPDATED)

### Current Status
- [x] Dashboard refactored from 1121 to ~200 lines ✅
- [ ] Test coverage: **0%** 🔴
- [ ] TypeScript strict mode: **Disabled** 🔴
- [ ] Lighthouse score: **Not measured**
- [ ] `any` types: **Multiple remaining** 🟡

### Target Metrics
- [ ] No component exceeds 300 lines
- [ ] 80%+ test coverage (Currently: 0%)
- [ ] Lighthouse performance score > 90
- [ ] Zero TypeScript `any` types
- [ ] Load time < 2 seconds
- [ ] Time to interactive < 3 seconds
- [ ] 100% TypeScript strict compliance

## Additional Considerations

### Design Patterns to Implement
- Container/Presentational component pattern
- Compound component pattern for complex UI
- Render props or custom hooks for logic sharing
- Factory pattern for creating chart configurations

### Libraries to Consider
- **State Management**: Zustand or Jotai (lighter than Redux) ⚠️ NEEDED
- **Data Fetching**: TanStack Query (React Query) for caching
- **Forms**: React Hook Form with Zod validation
- **Virtualization**: TanStack Virtual for large lists
- **Animation**: Keep Framer Motion but optimize usage
- **Testing**: Jest + React Testing Library ⚠️ CRITICAL
- **E2E**: Playwright or Cypress ⚠️ NEEDED

### Code Quality Tools (ALL MISSING)
- [ ] Set up ESLint with strict rules ⚠️ NEEDED
- [ ] Configure Prettier for consistent formatting ⚠️ NEEDED
- [ ] Add Husky for pre-commit hooks ⚠️ NEEDED
- [ ] Implement SonarQube for code quality metrics
- [ ] Add bundle analyzer for size optimization
- [ ] Setup GitHub Actions for CI/CD ⚠️ CRITICAL

## Notes

### ✅ Progress Made
- Dashboard successfully refactored from 1121 lines to modular components
- Custom hooks created for data fetching and business logic
- API service layer implemented with proper error handling
- TypeScript types defined (though strict mode still disabled)

### 🔴 Critical Gaps
The frontend has **ZERO TESTING** and lacks essential development infrastructure:
- No test files exist in the entire frontend codebase
- TypeScript strict mode is disabled, allowing potential type safety issues
- No state management solution for auth or global data
- No environment variables configuration
- No code quality tools (ESLint, Prettier, Husky)
- No CI/CD pipeline

### 💡 Recommendations
1. **IMMEDIATE ACTION**: Set up testing infrastructure - this is blocking production readiness
2. **HIGH PRIORITY**: Enable TypeScript strict mode to catch type errors
3. **IMPORTANT**: Implement global state management for auth and data
4. **CRITICAL**: Add error boundaries to prevent app crashes

Priority should be given to testing and TypeScript strict mode, as these will prevent bugs and improve code quality immediately.