# Performance Optimization Tasks

**Priority**: P2 - MEDIUM  
**Status**: 🔴 Not Optimized  
**Estimated**: 2 days  
**Target**: <200ms response time, <1s page load

## 🎯 Objective

Optimize system performance for:
- Fast API response times
- Quick page loads
- Efficient database queries
- Reduced memory usage
- Better scalability

## 📋 Current Performance Issues

### Backend
- 🔴 No query optimization
- 🔴 Missing database indexes
- 🔴 Synchronous operations
- 🔴 No connection pooling optimization
- 🔴 Cache underutilized

### Frontend
- 🔴 Large bundle size (>2MB)
- 🔴 No code splitting
- 🔴 Images not optimized
- 🔴 No lazy loading
- 🔴 Render blocking resources

## 📋 Task Breakdown

### Phase 1: Database Optimization (4 hours)

#### Task 1.1: Query Optimization
```sql
-- Queries to optimize:
- [ ] Portfolio value calculation
- [ ] Historical data fetching
- [ ] Asset price lookups
- [ ] Allocation calculations
- [ ] Performance metrics
```

#### Task 1.2: Database Indexes
```sql
-- Critical indexes:
- [ ] CREATE INDEX idx_prices_asset_date ON prices(asset_id, date DESC);
- [ ] CREATE INDEX idx_allocations_user_date ON allocations(user_id, date);
- [ ] CREATE INDEX idx_transactions_user ON transactions(user_id, created_at DESC);
- [ ] CREATE INDEX idx_index_values_date ON index_values(date DESC);
```

#### Task 1.3: Query Batching
```python
# Implement:
- [ ] Bulk inserts for price updates
- [ ] Batch fetching for multiple assets
- [ ] Aggregated queries for metrics
- [ ] Prepared statements
```

#### Task 1.4: Connection Pool Tuning
```python
# Optimize:
- [ ] Pool size based on load
- [ ] Connection timeout settings
- [ ] Idle connection cleanup
- [ ] Connection retry logic
```

### Phase 2: Caching Strategy (3 hours)

#### Task 2.1: Redis Caching
```python
# Cache layers:
- [ ] API response caching
- [ ] Database query caching
- [ ] Calculation results caching
- [ ] Session caching
```

#### Task 2.2: Cache Warming
```python
# Pre-load:
- [ ] Popular portfolios
- [ ] Recent market data
- [ ] Common calculations
- [ ] Static resources
```

#### Task 2.3: Cache Invalidation
```python
# Strategies:
- [ ] TTL-based expiration
- [ ] Event-based invalidation
- [ ] Partial cache updates
- [ ] Cache versioning
```

### Phase 3: Async Operations (3 hours)

#### Task 3.1: Background Tasks
```python
# Move to background:
- [ ] Data refresh operations
- [ ] Report generation
- [ ] Email notifications
- [ ] Heavy calculations
```

#### Task 3.2: Async Endpoints
```python
# Convert to async:
- [ ] Database queries
- [ ] External API calls
- [ ] File operations
- [ ] Cache operations
```

#### Task 3.3: Task Queue Optimization
```python
# Celery optimization:
- [ ] Task prioritization
- [ ] Worker scaling
- [ ] Result backend optimization
- [ ] Task routing
```

### Phase 4: Frontend Optimization (4 hours)

#### Task 4.1: Bundle Size Reduction
```javascript
// Implement:
- [ ] Tree shaking
- [ ] Code splitting
- [ ] Dynamic imports
- [ ] Library optimization
```

#### Task 4.2: Asset Optimization
```javascript
// Optimize:
- [ ] Image compression
- [ ] WebP format
- [ ] Lazy loading
- [ ] CDN integration
```

#### Task 4.3: Rendering Performance
```javascript
// Improve:
- [ ] Virtual scrolling
- [ ] React.memo usage
- [ ] useMemo/useCallback
- [ ] Suspense boundaries
```

#### Task 4.4: Network Optimization
```javascript
// Implement:
- [ ] Request batching
- [ ] GraphQL (optional)
- [ ] HTTP/2 push
- [ ] Prefetching
```

### Phase 5: API Optimization (2 hours)

#### Task 5.1: Response Compression
```python
# Enable:
- [ ] Gzip compression
- [ ] Brotli compression
- [ ] JSON minification
```

#### Task 5.2: Pagination
```python
# Implement:
- [ ] Cursor-based pagination
- [ ] Limit/offset optimization
- [ ] Response size limits
```

#### Task 5.3: Field Selection
```python
# Add:
- [ ] Sparse fieldsets
- [ ] Include/exclude fields
- [ ] Nested resource control
```

### Phase 6: Monitoring & Profiling (2 hours)

#### Task 6.1: Performance Monitoring
```python
# Track:
- [ ] Response times
- [ ] Database query times
- [ ] Cache hit rates
- [ ] Memory usage
```

#### Task 6.2: Profiling Tools
```python
# Setup:
- [ ] Python profiler
- [ ] React DevTools Profiler
- [ ] Chrome Lighthouse
- [ ] Database query analyzer
```

## 📊 Implementation Examples

### Optimized Database Queries

```python
# apps/api/app/services/portfolio_optimized.py

from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Dict
import asyncio

class OptimizedPortfolioService:
    
    async def get_portfolio_value_batch(
        self,
        user_id: int,
        dates: List[date]
    ) -> Dict[date, float]:
        """Batch fetch portfolio values for multiple dates"""
        
        # Single query with window function
        query = select(
            Allocation.date,
            func.sum(
                Allocation.quantity * Price.close_price
            ).label('total_value')
        ).select_from(
            Allocation
        ).join(
            Price,
            and_(
                Price.asset_id == Allocation.asset_id,
                Price.date == Allocation.date
            )
        ).where(
            and_(
                Allocation.user_id == user_id,
                Allocation.date.in_(dates)
            )
        ).group_by(
            Allocation.date
        )
        
        results = await self.db.execute(query)
        return {row.date: row.total_value for row in results}
    
    async def get_portfolio_with_prices(self, user_id: int):
        """Fetch portfolio with prices in single query"""
        
        # Use joinedload to prevent N+1 queries
        query = select(Portfolio).options(
            joinedload(Portfolio.allocations).joinedload(Allocation.asset),
            joinedload(Portfolio.allocations).joinedload(Allocation.latest_price)
        ).where(
            Portfolio.user_id == user_id
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def bulk_update_prices(self, price_updates: List[Dict]):
        """Bulk update prices efficiently"""
        
        # Use bulk_insert_mappings for speed
        await self.db.bulk_insert_mappings(
            Price,
            price_updates,
            render_nulls=True
        )
        
        # Single commit for all updates
        await self.db.commit()
```

### Advanced Caching

```python
# apps/api/app/core/cache_advanced.py

import hashlib
import json
from typing import Any, Optional, Callable
from functools import wraps
import asyncio
import redis.asyncio as redis

class AdvancedCache:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.local_cache = {}  # L1 cache
    
    def cache_key(self, prefix: str, **kwargs) -> str:
        """Generate consistent cache key"""
        key_data = json.dumps(kwargs, sort_keys=True)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    async def get_or_set(
        self,
        key: str,
        factory: Callable,
        ttl: int = 300
    ) -> Any:
        """Get from cache or compute and set"""
        
        # Check L1 cache first
        if key in self.local_cache:
            return self.local_cache[key]
        
        # Check Redis
        value = await self.redis.get(key)
        if value:
            result = json.loads(value)
            self.local_cache[key] = result
            return result
        
        # Compute value
        result = await factory()
        
        # Store in both caches
        await self.redis.setex(
            key,
            ttl,
            json.dumps(result)
        )
        self.local_cache[key] = result
        
        return result
    
    def cached(
        self,
        prefix: str,
        ttl: int = 300,
        key_func: Optional[Callable] = None
    ):
        """Decorator for caching function results"""
        
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = self.cache_key(
                        prefix,
                        args=str(args),
                        kwargs=str(kwargs)
                    )
                
                # Get or compute
                return await self.get_or_set(
                    cache_key,
                    lambda: func(*args, **kwargs),
                    ttl
                )
            
            return wrapper
        return decorator
    
    async def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern"""
        
        # Clear from Redis
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(
                cursor,
                match=pattern,
                count=100
            )
            
            if keys:
                await self.redis.delete(*keys)
            
            if cursor == 0:
                break
        
        # Clear from local cache
        keys_to_remove = [
            k for k in self.local_cache 
            if k.startswith(pattern.replace('*', ''))
        ]
        for key in keys_to_remove:
            del self.local_cache[key]
```

### Frontend Bundle Optimization

```javascript
// next.config.js

const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

module.exports = withBundleAnalyzer({
  // Enable SWC minification
  swcMinify: true,
  
  // Optimize images
  images: {
    domains: ['cdn.example.com'],
    formats: ['image/avif', 'image/webp'],
  },
  
  // Webpack optimization
  webpack: (config, { isServer }) => {
    // Tree shaking
    config.optimization = {
      ...config.optimization,
      usedExports: true,
      sideEffects: false,
      
      // Code splitting
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          default: false,
          vendors: false,
          
          // Vendor code splitting
          vendor: {
            name: 'vendor',
            chunks: 'all',
            test: /node_modules/,
            priority: 20,
          },
          
          // Common components
          common: {
            name: 'common',
            minChunks: 2,
            chunks: 'all',
            priority: 10,
            reuseExistingChunk: true,
            enforce: true,
          },
        },
      },
    };
    
    // Ignore moment locales
    if (!isServer) {
      config.resolve.alias = {
        ...config.resolve.alias,
        'moment': 'moment/min/moment.min.js',
      };
    }
    
    return config;
  },
  
  // Compression
  compress: true,
  
  // Production optimizations
  productionBrowserSourceMaps: false,
  
  // Experimental features
  experimental: {
    optimizeFonts: true,
    optimizeImages: true,
    optimizeCss: true,
  },
});
```

### React Performance Optimization

```typescript
// apps/web/app/components/optimized/PortfolioTable.tsx

import React, { useMemo, useCallback, memo } from 'react';
import { FixedSizeList as List } from 'react-window';
import AutoSizer from 'react-virtualized-auto-sizer';

// Memoized row component
const Row = memo(({ index, style, data }) => {
  const item = data[index];
  
  return (
    <div style={style} className="flex items-center p-4 border-b">
      <div className="flex-1">{item.symbol}</div>
      <div className="flex-1">{item.quantity}</div>
      <div className="flex-1">${item.value.toFixed(2)}</div>
    </div>
  );
});

Row.displayName = 'Row';

export const OptimizedPortfolioTable = memo(({ assets }) => {
  // Memoize sorted data
  const sortedAssets = useMemo(() => {
    return [...assets].sort((a, b) => b.value - a.value);
  }, [assets]);
  
  // Memoize row renderer
  const rowRenderer = useCallback(
    (props) => <Row {...props} data={sortedAssets} />,
    [sortedAssets]
  );
  
  // Virtual scrolling for large lists
  if (sortedAssets.length > 50) {
    return (
      <AutoSizer>
        {({ height, width }) => (
          <List
            height={height}
            itemCount={sortedAssets.length}
            itemSize={60}
            width={width}
          >
            {rowRenderer}
          </List>
        )}
      </AutoSizer>
    );
  }
  
  // Regular rendering for small lists
  return (
    <div className="divide-y">
      {sortedAssets.map((asset, index) => (
        <Row
          key={asset.id}
          index={index}
          data={sortedAssets}
          style={{}}
        />
      ))}
    </div>
  );
});

OptimizedPortfolioTable.displayName = 'OptimizedPortfolioTable';
```

## 🧪 Performance Testing

```python
# tests/performance/test_load.py

from locust import HttpUser, task, between

class PortfolioUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password"
        })
    
    @task(3)
    def view_portfolio(self):
        self.client.get("/api/v1/portfolio")
    
    @task(2)
    def get_calculations(self):
        self.client.get("/api/v1/calculations/portfolio-metrics")
    
    @task(1)
    def update_allocation(self):
        self.client.put("/api/v1/allocations", json={
            "allocations": [
                {"asset_id": 1, "percentage": 50},
                {"asset_id": 2, "percentage": 50}
            ]
        })
```

## 📈 Performance Targets

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| API response time | >500ms | <100ms | 🔴 |
| Database query time | >200ms | <50ms | 🔴 |
| Frontend bundle size | >2MB | <500KB | 🔴 |
| First contentful paint | >3s | <1s | 🔴 |
| Time to interactive | >5s | <2s | 🔴 |
| Cache hit rate | <20% | >80% | 🔴 |
| Lighthouse score | 60 | 95+ | 🔴 |

## 🔄 Dependencies

### Backend
```txt
uvloop>=0.18.0
aioredis>=2.0.0
asyncpg>=0.28.0
orjson>=3.9.0
```

### Frontend
```json
{
  "dependencies": {
    "react-window": "^1.8.10",
    "react-virtualized-auto-sizer": "^1.0.20"
  },
  "devDependencies": {
    "@next/bundle-analyzer": "^14.0.0",
    "compression-webpack-plugin": "^10.0.0",
    "terser-webpack-plugin": "^5.3.0"
  }
}
```

---

**Next**: Complete with [PROJECT-STATUS.md](./PROJECT-STATUS.md)