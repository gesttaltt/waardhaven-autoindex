# Frontend Refactoring TODO

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
  
- [ ] **Data Fetching**
  - [ ] Test portfolio data loading
  - [ ] Verify market data updates
  - [ ] Validate individual asset fetching
  - [ ] Test simulation endpoint
  
- [ ] **Error Scenarios**
  - [ ] Handle network failures gracefully
  - [ ] Test rate limiting responses
  - [ ] Validate error message display
  - [ ] Test retry mechanisms

### Performance Testing
- [ ] Measure initial load time
- [ ] Test with large datasets
- [ ] Validate chart rendering performance
- [ ] Check memory usage patterns

## 📋 Remaining Optimization Tasks

### Phase 7: Advanced State Management
- [ ] Consider implementing Zustand for global state
- [ ] Add optimistic UI updates
- [ ] Implement proper cache invalidation
- [ ] Add real-time data subscriptions

### Phase 8: Performance Optimization
- [ ] Implement React.memo for expensive components
- [ ] Add virtualization for large lists
- [ ] Optimize bundle size with code splitting
- [ ] Implement progressive loading

### Phase 9: Testing
- [ ] Add unit tests for all hooks
- [ ] Create component tests
- [ ] Add integration tests
- [ ] Implement E2E test suite

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

## Implementation Priority

1. **Immediate** (Week 1)
   - Fix tooltip contrast issue
   - Extract critical business logic to hooks
   - Create basic component separation

2. **Short-term** (Week 2-3)
   - Implement proper state management
   - Create reusable components
   - Add proper TypeScript types

3. **Medium-term** (Week 4-6)
   - Complete component refactoring
   - Add comprehensive testing
   - Optimize performance

4. **Long-term** (Month 2-3)
   - Implement design system
   - Add E2E testing
   - Complete accessibility improvements

## Success Metrics

- [ ] No component exceeds 300 lines
- [ ] 80%+ test coverage
- [ ] Lighthouse performance score > 90
- [ ] Zero TypeScript `any` types
- [ ] Load time < 2 seconds
- [ ] Time to interactive < 3 seconds

## Additional Considerations

### Design Patterns to Implement
- Container/Presentational component pattern
- Compound component pattern for complex UI
- Render props or custom hooks for logic sharing
- Factory pattern for creating chart configurations

### Libraries to Consider
- **State Management**: Zustand or Jotai (lighter than Redux)
- **Data Fetching**: TanStack Query (React Query)
- **Forms**: React Hook Form with Zod validation
- **Virtualization**: TanStack Virtual
- **Animation**: Keep Framer Motion but optimize usage

### Code Quality Tools
- [ ] Set up ESLint with strict rules
- [ ] Configure Prettier for consistent formatting
- [ ] Add Husky for pre-commit hooks
- [ ] Implement SonarQube for code quality metrics

## Notes

The current dashboard implementation works but is not maintainable or scalable. The refactoring should be done incrementally to avoid breaking existing functionality. Each phase should be thoroughly tested before moving to the next.

Priority should be given to extracting business logic and creating a proper component hierarchy, as these changes will have the most immediate impact on maintainability and developer experience.