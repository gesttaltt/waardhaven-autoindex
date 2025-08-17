# Critical Implementations - Backend Calculation Consolidation

**Generated**: 2025-08-17  
**Priority**: IMMEDIATE  
**Focus**: Move all calculations to backend, update TwelveData integration, fix database integration

## Current State Analysis

### ✅ What's Working Well
- **Backend is most consolidated**: FastAPI structure solid, services well-organized
- **Redis & Celery configured**: Infrastructure ready for caching and async tasks
- **Test infrastructure exists**: 4 test files with comprehensive fixtures
- **TwelveData service implemented**: Modern SDK integration with error handling

### 🚨 Critical Issues

1. **Calculations Split Between Frontend/Backend**
   - Frontend doing heavy calculations in `apps/web/app/lib/calculations/portfolio.ts`
   - Charts calculating moving averages and volatility bands client-side
   - This causes performance issues and inconsistency

2. **Database Integration Gaps**
   - No Alembic migrations (only manual SQL scripts)
   - Missing composite indexes for performance queries
   - No automatic migration on startup despite documentation claims

3. **TwelveData API Updates Needed**
   - Need to verify current API endpoints against latest documentation
   - Rate limiting for free tier (8 requests/minute) not properly managed
   - Missing batch request optimization

## Implementation Plan

### Phase 1: Move All Calculations to Backend (Priority: CRITICAL)

#### 1.1 Create New Backend Calculation Service
**File**: `apps/api/app/services/calculations.py`

```python
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from app.models.index import Price, IndexValue
from app.models.strategy import RiskMetrics

class CalculationService:
    """Centralized calculation service for all portfolio metrics"""
    
    @staticmethod
    def calculate_returns(prices: List[float]) -> Dict[str, float]:
        """Calculate daily, total, and annualized returns"""
        # Move from frontend portfolio.ts
        
    @staticmethod
    def calculate_volatility(returns: List[float], annualized: bool = True) -> float:
        """Calculate volatility (standard deviation of returns)"""
        # Move from frontend portfolio.ts
        
    @staticmethod
    def calculate_sharpe_ratio(
        returns: List[float], 
        risk_free_rate: float = 0.02
    ) -> float:
        """Calculate Sharpe ratio"""
        # Move from frontend portfolio.ts
        
    @staticmethod
    def calculate_max_drawdown(values: List[float]) -> Tuple[float, float]:
        """Calculate maximum and current drawdown"""
        # Move from frontend portfolio.ts
        
    @staticmethod
    def calculate_moving_average(
        prices: List[float], 
        window: int = 50
    ) -> List[Optional[float]]:
        """Calculate moving average"""
        # Move from frontend PerformanceChart.tsx
        
    @staticmethod
    def calculate_volatility_bands(
        prices: List[float], 
        window: int = 20,
        num_std: float = 2
    ) -> Dict[str, List[float]]:
        """Calculate Bollinger bands"""
        # Move from frontend PerformanceChart.tsx
        
    @staticmethod
    def calculate_correlation_matrix(
        asset_prices: Dict[str, List[float]]
    ) -> np.ndarray:
        """Calculate correlation between assets"""
        # New calculation for risk management
```

#### 1.2 Create New API Endpoints for Calculations
**File**: `apps/api/app/routers/calculations.py`

```python
from fastapi import APIRouter, Depends, Query
from typing import Optional, List, Dict
from datetime import date
from app.schemas.calculations import (
    PortfolioMetricsResponse,
    TechnicalIndicatorsResponse,
    CorrelationMatrixResponse
)

router = APIRouter(prefix="/api/v1/calculations", tags=["calculations"])

@router.get("/portfolio-metrics")
async def get_portfolio_metrics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    include_risk_metrics: bool = Query(True),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> PortfolioMetricsResponse:
    """Get all portfolio metrics calculated server-side"""
    
@router.get("/technical-indicators")
async def get_technical_indicators(
    symbol: Optional[str] = Query(None),
    indicators: List[str] = Query(["ma50", "volatility_bands"]),
    db: Session = Depends(get_db)
) -> TechnicalIndicatorsResponse:
    """Get technical indicators for charting"""
    
@router.get("/correlation-matrix")
async def get_correlation_matrix(
    assets: List[str] = Query(...),
    period_days: int = Query(252),
    db: Session = Depends(get_db)
) -> CorrelationMatrixResponse:
    """Get correlation matrix for risk analysis"""
```

### Phase 2: Update TwelveData Integration (Priority: HIGH)

#### 2.1 Review Latest API Documentation
**Action Items**:
1. Check TwelveData API docs for deprecated endpoints
2. Implement batch request optimization
3. Add proper rate limiting with exponential backoff
4. Update error handling for new error codes

#### 2.2 Enhance TwelveData Service
**File**: `apps/api/app/services/twelvedata.py` (enhance existing)

```python
class EnhancedTwelveDataService:
    def __init__(self):
        self.rate_limiter = RateLimiter(
            max_requests=8,  # Free tier limit
            time_window=60   # Per minute
        )
        
    async def fetch_batch_quotes(
        self, 
        symbols: List[str],
        use_cache: bool = True
    ) -> Dict[str, Quote]:
        """Fetch multiple quotes in single API call"""
        
    async def fetch_historical_batch(
        self,
        symbols: List[str],
        start_date: date,
        end_date: date,
        interval: str = "1day"
    ) -> Dict[str, pd.DataFrame]:
        """Fetch historical data for multiple symbols efficiently"""
        
    def validate_api_response(self, response: Dict) -> bool:
        """Validate response against latest API schema"""
```

### Phase 3: Fix Database Integration (Priority: HIGH)

#### 3.1 Implement Alembic Migrations
```bash
# Initialize Alembic
cd apps/api
alembic init alembic

# Create first migration
alembic revision --autogenerate -m "Initial schema with indexes"
```

#### 3.2 Add Composite Indexes
**File**: `apps/api/alembic/versions/001_add_performance_indexes.py`

```python
def upgrade():
    # Add composite indexes for performance
    op.create_index('ix_prices_asset_date', 'prices', ['asset_id', 'date'])
    op.create_index('ix_allocations_date_asset', 'allocations', ['date', 'asset_id'])
    op.create_index('ix_index_values_date', 'index_values', ['date'])
    
def downgrade():
    # Remove indexes
    op.drop_index('ix_prices_asset_date')
    op.drop_index('ix_allocations_date_asset')
    op.drop_index('ix_index_values_date')
```

#### 3.3 Auto-migration on Startup
**File**: `apps/api/app/main.py` (update existing)

```python
from alembic.config import Config
from alembic import command

@app.on_event("startup")
async def startup_event():
    """Run migrations and create indexes on startup"""
    try:
        # Run Alembic migrations
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        
        # Verify indexes exist
        verify_database_indexes()
        
        # Optional: Run data refresh if configured
        if not settings.SKIP_STARTUP_REFRESH:
            await initial_data_refresh()
            
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        # Don't crash, allow app to start
```

### Phase 4: Frontend Simplification (Priority: MEDIUM)

#### 4.1 Remove Calculation Logic from Frontend
**Files to Update**:
- `apps/web/app/lib/calculations/portfolio.ts` - Remove, replace with API calls
- `apps/web/app/components/dashboard/PerformanceChart.tsx` - Use pre-calculated data

#### 4.2 Create New API Hooks
**File**: `apps/web/app/hooks/useCalculations.ts`

```typescript
import { useQuery } from '@tanstack/react-query';
import { calculationsApi } from '@/services/api/calculations';

export const usePortfolioMetrics = (startDate?: Date, endDate?: Date) => {
  return useQuery({
    queryKey: ['portfolio-metrics', startDate, endDate],
    queryFn: () => calculationsApi.getPortfolioMetrics({ startDate, endDate }),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useTechnicalIndicators = (symbol?: string, indicators?: string[]) => {
  return useQuery({
    queryKey: ['technical-indicators', symbol, indicators],
    queryFn: () => calculationsApi.getTechnicalIndicators({ symbol, indicators }),
    staleTime: 60 * 1000, // 1 minute for real-time feel
  });
};
```

## Implementation Timeline

### Week 1 (Immediate)
- [ ] Day 1-2: Move all calculations to backend service
- [ ] Day 3: Create calculation API endpoints
- [ ] Day 4: Update frontend to use new endpoints
- [ ] Day 5: Test and verify consistency

### Week 2 (High Priority)
- [ ] Day 1-2: Review and update TwelveData integration
- [ ] Day 3: Implement Alembic migrations
- [ ] Day 4: Add database indexes
- [ ] Day 5: Performance testing

## Success Metrics

1. **Performance**: 50%+ reduction in frontend calculation time
2. **Consistency**: All users see same calculated values
3. **Scalability**: Backend can handle 100+ concurrent calculation requests
4. **Database**: Query performance improved by 10x with indexes
5. **API Efficiency**: Reduced TwelveData API calls by 30% with batching

## Testing Requirements

### Backend Tests
```python
# apps/api/tests/test_calculations.py
def test_portfolio_returns_calculation():
    """Verify returns match expected values"""
    
def test_volatility_calculation():
    """Verify volatility calculation accuracy"""
    
def test_sharpe_ratio_edge_cases():
    """Test Sharpe ratio with zero volatility"""
    
def test_drawdown_calculation():
    """Verify max drawdown detection"""
```

### Integration Tests
```python
# apps/api/tests/test_calculation_endpoints.py
def test_portfolio_metrics_endpoint():
    """Test full portfolio metrics API"""
    
def test_calculation_caching():
    """Verify Redis caching works"""
    
def test_calculation_performance():
    """Ensure calculations complete in <1 second"""
```

## Dependencies to Add

### Backend (apps/api/requirements.txt)
```txt
# Calculation libraries
numpy>=1.24.0
pandas>=2.0.0
scipy>=1.11.0

# Database migrations
alembic>=1.12.0
```

### Frontend (apps/web/package.json)
```json
{
  "dependencies": {
    "@tanstack/react-query": "^5.0.0",
    "@tanstack/react-query-devtools": "^5.0.0"
  }
}
```

## Environment Variables Update

### apps/api/.env.example
```env
# Add these missing variables
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# TwelveData optimization
TWELVEDATA_BATCH_SIZE=5
TWELVEDATA_RATE_LIMIT=8
```

## Notes

1. **Backend is the source of truth** for all calculations
2. **Frontend only displays** pre-calculated data
3. **Cache aggressively** but invalidate on data updates
4. **Monitor performance** with logging and metrics
5. **Test thoroughly** before deploying calculation changes

---

**Next Steps**: 
1. Start with Phase 1 - Move calculations to backend
2. Update TwelveData API integration based on latest docs
3. Implement proper database migrations with Alembic