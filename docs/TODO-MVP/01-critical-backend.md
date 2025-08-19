# Critical Backend Tasks - Calculation Consolidation

**Priority**: P0 - CRITICAL  
**Status**: 🔴 Not Started  
**Estimated**: 2 days  
**Blocking**: Frontend performance, data consistency

## 🎯 Objective

Move ALL calculation logic from frontend to backend to ensure:
- Single source of truth for calculations
- Consistent results across all clients
- Better performance (server-side computation)
- Easier testing and debugging

## 📋 Task Breakdown

### Phase 1: Create Calculation Service (4 hours)

#### Task 1.1: Basic Service Structure
**File**: `apps/api/app/services/calculations.py`

```python
# Implementation checklist:
- [ ] Create CalculationService class
- [ ] Add logging configuration
- [ ] Setup error handling
- [ ] Add input validation
```

**Methods to implement**:
- [ ] `calculate_returns()` - Daily, total, annualized
- [ ] `calculate_volatility()` - Standard deviation
- [ ] `calculate_sharpe_ratio()` - Risk-adjusted returns
- [ ] `calculate_max_drawdown()` - Maximum loss from peak
- [ ] `calculate_correlation_matrix()` - Asset correlations

#### Task 1.2: Technical Indicators
**Add to**: `apps/api/app/services/calculations.py`

```python
# Technical analysis methods:
- [ ] calculate_moving_average(prices, window)
- [ ] calculate_exponential_moving_average(prices, span)
- [ ] calculate_bollinger_bands(prices, window, num_std)
- [ ] calculate_rsi(prices, period=14)
- [ ] calculate_macd(prices)
```

### Phase 2: Create API Endpoints (4 hours)

#### Task 2.1: Router Setup
**File**: `apps/api/app/routers/calculations.py`

```python
# Endpoints to create:
- [ ] GET /portfolio-metrics - Complete portfolio analysis
- [ ] GET /technical-indicators - Chart indicators
- [ ] GET /correlation-matrix - Risk analysis
- [ ] GET /performance-comparison - vs benchmark
- [ ] POST /backtest - Strategy backtesting
```

#### Task 2.2: Response Schemas
**File**: `apps/api/app/schemas/calculations.py`

```python
# Schemas to define:
- [ ] PortfolioMetricsResponse
- [ ] TechnicalIndicatorsResponse
- [ ] CorrelationMatrixResponse
- [ ] PerformanceComparisonResponse
- [ ] BacktestResultResponse
```

### Phase 3: Frontend Migration (8 hours)

#### Task 3.1: Remove Frontend Calculations
**Files to modify**:
```
- [ ] apps/web/app/lib/calculations/portfolio.ts - DELETE
- [ ] apps/web/app/lib/calculations/technical.ts - DELETE
- [ ] apps/web/app/lib/calculations/risk.ts - DELETE
```

#### Task 3.2: Create API Service Layer
**File**: `apps/web/app/services/api/calculations.ts`

```typescript
// Services to implement:
- [ ] getPortfolioMetrics(startDate, endDate)
- [ ] getTechnicalIndicators(symbol, indicators[])
- [ ] getCorrelationMatrix(assets[], period)
- [ ] getPerformanceComparison(benchmark)
- [ ] runBacktest(strategy, params)
```

#### Task 3.3: Update React Hooks
**File**: `apps/web/app/hooks/useCalculations.ts`

```typescript
// Hooks to create:
- [ ] usePortfolioMetrics()
- [ ] useTechnicalIndicators()
- [ ] useCorrelationMatrix()
- [ ] usePerformanceComparison()
- [ ] useBacktest()
```

#### Task 3.4: Update Components
**Components to update**:
```
- [ ] PerformanceChart.tsx - Use pre-calculated data
- [ ] PortfolioMetrics.tsx - Use API data
- [ ] RiskAnalysis.tsx - Use correlation API
- [ ] BacktestResults.tsx - Use backtest API
```

### Phase 4: Caching Layer (2 hours)

#### Task 4.1: Redis Integration
**File**: `apps/api/app/services/cache.py`

```python
# Caching strategy:
- [ ] Cache portfolio metrics (5 min TTL)
- [ ] Cache technical indicators (1 min TTL)
- [ ] Cache correlation matrix (15 min TTL)
- [ ] Invalidate on data updates
```

#### Task 4.2: Cache Decorators
```python
- [ ] @cache_result(ttl=300)
- [ ] @invalidate_cache(keys=[])
- [ ] @cache_key_generator()
```

### Phase 5: Testing (4 hours)

#### Task 5.1: Unit Tests
**File**: `apps/api/tests/test_calculations.py`

```python
# Tests to write:
- [ ] test_returns_calculation_accuracy()
- [ ] test_volatility_with_edge_cases()
- [ ] test_sharpe_ratio_zero_volatility()
- [ ] test_drawdown_detection()
- [ ] test_correlation_matrix_symmetry()
```

#### Task 5.2: Integration Tests
**File**: `apps/api/tests/test_calculation_endpoints.py`

```python
# Tests to write:
- [ ] test_portfolio_metrics_endpoint()
- [ ] test_technical_indicators_endpoint()
- [ ] test_calculation_caching()
- [ ] test_concurrent_calculations()
- [ ] test_large_dataset_performance()
```

#### Task 5.3: Frontend Tests
**File**: `apps/web/tests/calculations.test.ts`

```typescript
// Tests to write:
- [ ] test API service calls
- [ ] test hook data fetching
- [ ] test error handling
- [ ] test loading states
- [ ] test cache behavior
```

## 📊 Implementation Details

### Calculation Service Structure

```python
# apps/api/app/services/calculations.py

import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.cache import cache_result
import logging

logger = logging.getLogger(__name__)

class CalculationService:
    """Centralized calculation service for all portfolio metrics"""
    
    def __init__(self, db: Session):
        self.db = db
        
    @cache_result(ttl=300)
    def calculate_portfolio_metrics(
        self, 
        user_id: int, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """Calculate comprehensive portfolio metrics"""
        try:
            # Fetch data
            prices = self._fetch_portfolio_prices(user_id, start_date, end_date)
            
            # Calculate metrics
            returns = self.calculate_returns(prices)
            volatility = self.calculate_volatility(returns['daily'])
            sharpe = self.calculate_sharpe_ratio(returns['daily'])
            drawdown = self.calculate_max_drawdown(prices)
            
            return {
                'returns': returns,
                'volatility': volatility,
                'sharpe_ratio': sharpe,
                'max_drawdown': drawdown[0],
                'current_drawdown': drawdown[1],
                'calculated_at': datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Portfolio metrics calculation failed: {e}")
            raise
    
    def calculate_returns(self, prices: List[float]) -> Dict[str, float]:
        """Calculate various return metrics"""
        if len(prices) < 2:
            return {'daily': 0, 'total': 0, 'annualized': 0}
            
        prices_array = np.array(prices)
        daily_returns = np.diff(prices_array) / prices_array[:-1]
        
        total_return = (prices[-1] - prices[0]) / prices[0]
        
        # Annualized return (assuming 252 trading days)
        days = len(prices)
        years = days / 252
        annualized_return = (1 + total_return) ** (1/years) - 1 if years > 0 else 0
        
        return {
            'daily': daily_returns.tolist(),
            'total': total_return,
            'annualized': annualized_return,
            'average_daily': np.mean(daily_returns)
        }
```

### API Endpoint Structure

```python
# apps/api/app/routers/calculations.py

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.calculations import CalculationService
from app.schemas.calculations import (
    PortfolioMetricsResponse,
    TechnicalIndicatorsResponse
)
from app.core.auth import get_current_user

router = APIRouter(prefix="/api/v1/calculations", tags=["calculations"])

@router.get("/portfolio-metrics", response_model=PortfolioMetricsResponse)
async def get_portfolio_metrics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    include_risk_metrics: bool = Query(True),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get comprehensive portfolio metrics"""
    try:
        service = CalculationService(db)
        metrics = service.calculate_portfolio_metrics(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
        return PortfolioMetricsResponse(**metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Frontend Hook Structure

```typescript
// apps/web/app/hooks/useCalculations.ts

import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { calculationsApi } from '@/services/api/calculations';
import { PortfolioMetrics, TechnicalIndicators } from '@/types/calculations';

export const usePortfolioMetrics = (
  startDate?: Date, 
  endDate?: Date
): UseQueryResult<PortfolioMetrics> => {
  return useQuery({
    queryKey: ['portfolio-metrics', startDate, endDate],
    queryFn: () => calculationsApi.getPortfolioMetrics({ startDate, endDate }),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
  });
};

export const useTechnicalIndicators = (
  symbol: string,
  indicators: string[] = ['sma', 'ema', 'bollinger']
): UseQueryResult<TechnicalIndicators> => {
  return useQuery({
    queryKey: ['technical-indicators', symbol, indicators],
    queryFn: () => calculationsApi.getTechnicalIndicators({ symbol, indicators }),
    staleTime: 60 * 1000, // 1 minute for real-time feel
    refetchInterval: 60 * 1000, // Auto-refresh every minute
  });
};
```

## 🧪 Testing Checklist

### Backend Tests
- [ ] All calculation methods have unit tests
- [ ] Edge cases covered (empty data, single point, etc.)
- [ ] Performance tests for large datasets
- [ ] Cache invalidation tests
- [ ] Concurrent request handling

### Frontend Tests
- [ ] API service mocked properly
- [ ] Loading states tested
- [ ] Error states tested
- [ ] Data transformation tested
- [ ] Component integration tested

### Integration Tests
- [ ] End-to-end calculation flow
- [ ] Database to API to frontend
- [ ] Cache behavior under load
- [ ] Error propagation
- [ ] Performance benchmarks

## 📈 Success Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Frontend calculation time | >500ms | 0ms | 🔴 |
| Backend calculation time | N/A | <100ms | 🔴 |
| API response time | N/A | <200ms | 🔴 |
| Cache hit rate | 0% | >80% | 🔴 |
| Test coverage | 25% | >80% | 🔴 |

## 🚀 Migration Strategy

### Step 1: Parallel Implementation
1. Build backend service alongside frontend
2. Add feature flag for gradual rollout
3. Compare results for accuracy

### Step 2: Gradual Migration
1. Start with non-critical calculations
2. A/B test with subset of users
3. Monitor for discrepancies

### Step 3: Full Cutover
1. Remove feature flag
2. Delete frontend calculation code
3. Optimize backend performance

## ⚠️ Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Calculation differences | High | Extensive testing, gradual rollout |
| Performance regression | Medium | Caching, optimization, monitoring |
| API overload | Medium | Rate limiting, queueing |
| Cache inconsistency | Low | TTL strategy, invalidation |

## 📝 Notes

- Keep calculation methods pure (no side effects)
- Use NumPy/Pandas for performance
- Log all calculation errors with context
- Consider using Celery for long-running calculations
- Document all financial formulas used

## 🔄 Dependencies

### Python Packages to Add
```txt
numpy>=1.24.0
pandas>=2.0.0
scipy>=1.11.0
ta-lib>=0.4.25  # Technical analysis
```

### Frontend Packages to Add
```json
{
  "@tanstack/react-query": "^5.0.0",
  "@tanstack/react-query-devtools": "^5.0.0"
}
```

---

**Next**: After completing backend calculations, move to [02-database-migrations.md](./02-database-migrations.md)