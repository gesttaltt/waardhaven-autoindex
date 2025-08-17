# Backend Modularization Migration Guide

## Overview

This guide documents the migration from monolithic `models.py` and `schemas.py` files to a modular, domain-driven structure.

## Changes Made

### 1. Models Refactoring

#### Before (Monolithic)
```python
# app/models.py - All models in one file
class User(Base): ...
class Asset(Base): ...
class Price(Base): ...
class IndexValue(Base): ...
# ... all other models
```

#### After (Modular)
```python
# app/models/__init__.py - Central export
from .user import User
from .asset import Asset, Price
from .index import IndexValue, Allocation
from .trading import Order
from .strategy import StrategyConfig, RiskMetrics, MarketCapData
```

Models are now organized by domain:
- `models/user.py` - Authentication models
- `models/asset.py` - Asset and pricing models
- `models/index.py` - Index composition models
- `models/trading.py` - Trading models
- `models/strategy.py` - Strategy and risk models

### 2. Schemas Refactoring

#### Before (Monolithic)
```python
# app/schemas.py - All schemas in one file
class RegisterRequest(BaseModel): ...
class AllocationItem(BaseModel): ...
# ... all other schemas
```

#### After (Modular)
```python
# app/schemas/__init__.py - Central export
from .auth import RegisterRequest, LoginRequest, TokenResponse
from .index import AllocationItem, IndexCurrentResponse, ...
from .benchmark import BenchmarkResponse
from .broker import OrderRequest, OrderResponse
from .strategy import StrategyConfigRequest, RiskMetricsResponse
```

Schemas are now organized by domain:
- `schemas/auth.py` - Authentication schemas
- `schemas/index.py` - Index management schemas
- `schemas/benchmark.py` - Benchmark schemas
- `schemas/broker.py` - Trading schemas
- `schemas/strategy.py` - Strategy schemas

## Migration Steps

### Step 1: Update Imports in Routers

All router files need to update their imports:

```python
# OLD
from ..models import User, Asset, Price
from ..schemas import RegisterRequest, TokenResponse

# NEW
from ..models import User, Asset, Price  # Works the same due to __init__.py
from ..schemas import RegisterRequest, TokenResponse  # Works the same
```

### Step 2: Update Service Imports

Services should import from the new structure:

```python
# OLD
from ..models import Asset, Price, IndexValue, Allocation

# NEW
from ..models import Asset, Price, IndexValue, Allocation  # Works the same
```

### Step 3: Database Migrations

No database changes are required as the table structures remain the same.

### Step 4: Testing

Run all tests to ensure imports work correctly:

```bash
# Run unit tests
pytest tests/

# Test API endpoints
python test_api.py
```

## Benefits of New Structure

### 1. **Better Organization**
- Models and schemas grouped by business domain
- Easier to find and modify related code
- Clear separation of concerns

### 2. **Improved Maintainability**
- Smaller, focused files
- Less merge conflicts
- Easier code reviews

### 3. **Enhanced Scalability**
- Easy to add new domains
- Can split into microservices if needed
- Better for team collaboration

### 4. **Type Safety**
- Better IDE support with smaller files
- Clearer import paths
- Easier to track dependencies

## Backward Compatibility

The refactoring maintains backward compatibility:

1. **Import Compatibility**: All models and schemas are re-exported from `__init__.py` files
2. **No Breaking Changes**: Existing code continues to work
3. **Database Compatibility**: No schema changes required

## Common Issues and Solutions

### Issue 1: Circular Import Errors

**Solution**: Use string references for relationships:
```python
# Instead of
from .user import User
class Order(Base):
    user = relationship(User)

# Use
class Order(Base):
    user = relationship("User")
```

### Issue 2: Missing Imports

**Solution**: Check the `__init__.py` files ensure all models/schemas are exported:
```python
# app/models/__init__.py
__all__ = ["User", "Asset", "Price", ...]  # Ensure all models listed
```

### Issue 3: IDE Not Recognizing Imports

**Solution**: Restart IDE or invalidate caches after restructuring.

## Testing Checklist

- [ ] All API endpoints respond correctly
- [ ] Database operations work (CRUD)
- [ ] Authentication flows work
- [ ] Data refresh pipeline works
- [ ] Strategy calculations work
- [ ] Risk metrics are calculated
- [ ] Frontend can connect and display data

## Rollback Plan

If issues arise, rollback is simple:

1. Keep old `models.py` and `schemas.py` as backup
2. Revert imports in routers and services
3. Remove new directories
4. Restart application

## Future Improvements

### Phase 2: Service Layer Refactoring
- Create service interfaces/protocols
- Implement dependency injection
- Add service layer tests

### Phase 3: Repository Pattern
- Add repository layer for data access
- Separate business logic from data access
- Implement unit of work pattern

### Phase 4: Event-Driven Architecture
- Add domain events
- Implement event bus
- Decouple components further

## Documentation Updates

The following documentation has been updated:
- `/docs/01-backend/API_ARCHITECTURE.md` - New architecture overview
- `/docs/01-backend/models/` - Model documentation
- `/docs/01-backend/schemas/` - Schema documentation

## Support

For questions or issues related to this migration:
1. Check the migration guide
2. Review the API architecture documentation
3. Check error logs for import issues
4. Test with the provided test scripts