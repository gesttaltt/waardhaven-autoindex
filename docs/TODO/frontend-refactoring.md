# Frontend Refactoring TODO

## Priority: HIGH - Dashboard Component Refactoring

### Current Issues
The dashboard component (`apps/web/app/dashboard/page.tsx`) has grown to 1121+ lines and violates several clean architecture principles.

### Architectural Problems

#### 1. **Component Size & Complexity**
- [ ] Component exceeds 1000 lines (currently 1121 lines)
- [ ] Handles too many responsibilities
- [ ] Difficult to test and maintain

#### 2. **Separation of Concerns Violations**
- [ ] Data fetching logic mixed with UI
- [ ] Business logic embedded in component
- [ ] State management scattered throughout
- [ ] No clear boundaries between layers

#### 3. **Code Smells**
- [ ] Multiple `useState` hooks (15+ state variables)
- [ ] Complex nested conditionals
- [ ] Inline styles and magic numbers
- [ ] Repetitive code patterns
- [ ] `any` types used in several places

## Refactoring Plan

### Phase 1: Extract Custom Hooks
- [ ] Create `usePortfolioData` hook for data fetching
- [ ] Create `useSimulation` hook for simulation logic
- [ ] Create `useChartData` hook for chart data transformation
- [ ] Create `usePerformanceMetrics` hook for calculations
- [ ] Create `useTechnicalIndicators` hook for MA, volatility bands

### Phase 2: Component Decomposition
- [ ] Extract `PerformanceCards` component
- [ ] Extract `PerformanceChart` component
- [ ] Extract `SimulationPanel` component
- [ ] Extract `PortfolioAllocation` component
- [ ] Extract `TopHoldings` component
- [ ] Extract `ChartControls` component
- [ ] Extract `DataPanel` component

### Phase 3: State Management
- [ ] Implement proper state management (Context API or Zustand)
- [ ] Create `PortfolioContext` for shared state
- [ ] Create `ChartContext` for chart-specific state
- [ ] Implement proper error boundaries

### Phase 4: Type Safety
- [ ] Create proper TypeScript interfaces for all data structures
- [ ] Remove all `any` types
- [ ] Add proper type guards
- [ ] Create domain models for business entities

### Phase 5: Performance Optimization
- [ ] Implement React.memo for expensive components
- [ ] Use useMemo/useCallback appropriately
- [ ] Implement virtual scrolling for large lists
- [ ] Add proper loading skeletons as reusable components
- [ ] Optimize re-renders with proper dependency arrays

### Phase 6: API Layer
- [ ] Create API service layer with proper error handling
- [ ] Implement retry logic with exponential backoff
- [ ] Add request cancellation for unmounted components
- [ ] Create proper API response types

### Phase 7: Styling & Theming
- [ ] Extract inline styles to styled components or CSS modules
- [ ] Create theme constants for colors
- [ ] Implement proper dark/light mode support
- [ ] Create reusable style utilities

### Phase 8: Testing
- [ ] Add unit tests for custom hooks
- [ ] Add component tests with React Testing Library
- [ ] Add integration tests for data flows
- [ ] Add E2E tests for critical user journeys

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