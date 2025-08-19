# 🔍 Point-in-Time Query Engine

**Priority**: HIGH  
**Complexity**: High  
**Timeline**: 3-4 days  
**Value**: Fast, accurate historical data queries

## 🎯 Objective

Build an optimized query engine that:
- Retrieves data exactly as it was available at any historical moment
- Handles massive time-series datasets efficiently
- Provides sub-second query response times
- Supports complex multi-dimensional queries
- Maintains perfect historical accuracy

## 🔄 Query Architecture

### Query Types
```python
QUERY_TYPES = {
    'point_in_time': {
        'description': 'Get latest data as of specific timestamp',
        'use_case': 'What was AAPL price at market close on 2023-03-15?',
        'complexity': 'Low',
        'cache_strategy': 'Aggressive'
    },
    'range_queries': {
        'description': 'Get data within time range',
        'use_case': 'All insider trades between Jan-Mar 2023',
        'complexity': 'Medium',
        'cache_strategy': 'Selective'
    },
    'as_of_snapshots': {
        'description': 'Complete market snapshot at moment',
        'use_case': 'Full portfolio view as of earnings date',
        'complexity': 'High',
        'cache_strategy': 'Limited'
    },
    'temporal_joins': {
        'description': 'Join data from different time points',
        'use_case': 'Price vs insider trades with lag analysis',
        'complexity': 'Very High',
        'cache_strategy': 'None'
    }
}
```

## 💾 Optimized Schema Design

### Temporal Tables with Versioning
```sql
-- Temporal table for price data
CREATE TABLE price_history (
    symbol VARCHAR(20) NOT NULL,
    valid_from TIMESTAMPTZ NOT NULL,
    valid_to TIMESTAMPTZ NOT NULL DEFAULT 'infinity',
    
    -- Price data
    open DECIMAL(12,4),
    high DECIMAL(12,4),
    low DECIMAL(12,4),
    close DECIMAL(12,4),
    volume BIGINT,
    
    -- Metadata
    data_version INTEGER,
    source VARCHAR(50),
    
    PRIMARY KEY (symbol, valid_from),
    
    -- Temporal constraints
    CONSTRAINT valid_time_range CHECK (valid_from < valid_to),
    EXCLUDE USING GIST (
        symbol WITH =,
        tstzrange(valid_from, valid_to) WITH &&
    )
);

-- Hypertable for time-series optimization
SELECT create_hypertable('price_history', 'valid_from', 'symbol', 4);

-- Indexes for point-in-time queries
CREATE INDEX idx_price_symbol_time_range 
ON price_history USING GIST (symbol, tstzrange(valid_from, valid_to));

CREATE INDEX idx_price_valid_from 
ON price_history (valid_from DESC);
```

### Materialized Views for Common Queries
```sql
-- Daily snapshots for fast access
CREATE MATERIALIZED VIEW daily_market_snapshots AS
SELECT 
    DATE(valid_from) as snapshot_date,
    symbol,
    LAST(close, valid_from) as last_price,
    LAST(volume, valid_from) as last_volume,
    LAST(valid_from, valid_from) as as_of_time
FROM price_history
WHERE valid_from >= CURRENT_DATE - INTERVAL '5 years'
GROUP BY DATE(valid_from), symbol
ORDER BY snapshot_date DESC, symbol;

-- Create refresh schedule
CREATE INDEX ON daily_market_snapshots (snapshot_date DESC, symbol);
```

## 🚀 Query Engine Implementation

```python
# app/time_machine/query_engine.py

import asyncio
import asyncpg
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from functools import lru_cache
import pandas as pd

class PointInTimeQueryEngine:
    """High-performance point-in-time query engine"""
    
    def __init__(self):
        self.pool = None
        self.cache = QueryCache()
        self.query_optimizer = QueryOptimizer()
        self.metrics = QueryMetrics()
        
    async def initialize(self):
        """Initialize connection pool and cache"""
        self.pool = await asyncpg.create_pool(
            host=settings.TIMESERIES_DB_HOST,
            database=settings.TIMESERIES_DB_NAME,
            user=settings.TIMESERIES_DB_USER,
            password=settings.TIMESERIES_DB_PASSWORD,
            min_size=20,
            max_size=50,
            command_timeout=30
        )
        
        await self.cache.initialize()
        await self.preload_common_queries()
    
    async def get_as_of(self, 
                       table: str, 
                       as_of_time: datetime, 
                       symbol: str = None,
                       fields: List[str] = None) -> Union[Dict, List[Dict]]:
        """Get data as it was at specific point in time"""
        
        start_time = datetime.now()
        
        # Check cache first
        cache_key = self.cache.generate_key(table, as_of_time, symbol, fields)
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            await self.metrics.record_cache_hit(table)
            return cached_result
        
        # Build optimized query
        query, params = self.query_optimizer.build_as_of_query(
            table, as_of_time, symbol, fields
        )
        
        # Execute query
        async with self.pool.acquire() as conn:
            if symbol:
                # Single symbol query
                row = await conn.fetchrow(query, *params)
                result = dict(row) if row else None
            else:
                # Multi-symbol query
                rows = await conn.fetch(query, *params)
                result = [dict(row) for row in rows]
        
        # Cache result
        await self.cache.set(cache_key, result, ttl=3600)  # 1 hour TTL
        
        # Record metrics
        query_time = (datetime.now() - start_time).total_seconds()
        await self.metrics.record_query(table, query_time, len(result) if isinstance(result, list) else 1)
        
        return result
    
    async def get_price_as_of(self, symbol: str, as_of_time: datetime) -> Optional[Dict]:
        """Optimized price query with caching"""
        
        # Use materialized view for daily snapshots
        if as_of_time.time() >= datetime.strptime('16:00', '%H:%M').time():
            # End of day query - use daily snapshots
            query = """
                SELECT 
                    snapshot_date,
                    symbol,
                    last_price as close,
                    last_volume as volume,
                    as_of_time
                FROM daily_market_snapshots
                WHERE symbol = $1 
                    AND snapshot_date <= $2
                ORDER BY snapshot_date DESC
                LIMIT 1;
            """
            params = [symbol, as_of_time.date()]
        else:
            # Intraday query - use full time series
            query = """
                SELECT 
                    symbol,
                    close,
                    volume,
                    valid_from as as_of_time
                FROM price_history
                WHERE symbol = $1 
                    AND valid_from <= $2
                    AND valid_to > $2
                ORDER BY valid_from DESC
                LIMIT 1;
            """
            params = [symbol, as_of_time]
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *params)
            return dict(row) if row else None
    
    async def get_insider_trades_as_of(self, 
                                      symbol: str, 
                                      as_of_time: datetime,
                                      days_back: int = 90) -> List[Dict]:
        """Get insider trades known as of specific time"""
        
        # Use filing_date for information availability
        query = """
            WITH trade_windows AS (
                SELECT 
                    transaction_date,
                    filing_date,
                    insider_name,
                    transaction_type,
                    shares,
                    value,
                    -- Calculate days between transaction and filing
                    EXTRACT(EPOCH FROM (filing_date - transaction_date))/86400 as filing_delay_days
                FROM insider_trades_ts
                WHERE symbol = $1
                    AND filing_date <= $2  -- Known by this date
                    AND filing_date >= $3  -- Within lookback period
            )
            SELECT 
                *,
                -- Add clustering analysis
                COUNT(*) OVER (
                    PARTITION BY DATE_TRUNC('week', transaction_date)
                ) as same_week_trades
            FROM trade_windows
            ORDER BY filing_date DESC, value DESC;
        """
        
        lookback_date = as_of_time - timedelta(days=days_back)
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, symbol, as_of_time, lookback_date)
            return [dict(row) for row in rows]
    
    async def get_news_sentiment_as_of(self, 
                                      symbol: str, 
                                      as_of_time: datetime,
                                      hours_back: int = 168) -> Dict:  # 1 week default
        """Get news sentiment aggregated as of specific time"""
        
        query = """
            WITH news_window AS (
                SELECT 
                    time,
                    title,
                    sentiment,
                    impact_score,
                    source,
                    -- Weight by recency and impact
                    impact_score * EXP(-EXTRACT(EPOCH FROM ($2 - time))/86400.0) as weighted_impact
                FROM news_events_ts
                WHERE symbol = $1
                    AND time <= $2
                    AND time >= $3
                    AND sentiment IS NOT NULL
            )
            SELECT 
                COUNT(*) as article_count,
                AVG(sentiment) as avg_sentiment,
                STDDEV(sentiment) as sentiment_volatility,
                SUM(weighted_impact) as total_weighted_impact,
                ARRAY_AGG(
                    JSON_BUILD_OBJECT(
                        'time', time,
                        'title', title,
                        'sentiment', sentiment,
                        'impact', impact_score
                    ) ORDER BY weighted_impact DESC
                )[1:5] as top_articles
            FROM news_window;
        """
        
        lookback_time = as_of_time - timedelta(hours=hours_back)
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, symbol, as_of_time, lookback_time)
            return dict(row) if row else {
                'article_count': 0,
                'avg_sentiment': 0,
                'sentiment_volatility': 0,
                'total_weighted_impact': 0,
                'top_articles': []
            }
```

## 📋 Query Optimization Strategies

```python
class QueryOptimizer:
    """Optimize queries for different scenarios"""
    
    def __init__(self):
        self.query_templates = self.load_query_templates()
        self.index_advisor = IndexAdvisor()
        
    def build_as_of_query(self, 
                         table: str, 
                         as_of_time: datetime, 
                         symbol: str = None,
                         fields: List[str] = None) -> tuple:
        """Build optimized AS OF query"""
        
        # Choose strategy based on query pattern
        if self.is_recent_query(as_of_time):
            return self.build_recent_query(table, as_of_time, symbol, fields)
        elif self.is_daily_boundary(as_of_time):
            return self.build_snapshot_query(table, as_of_time, symbol, fields)
        else:
            return self.build_temporal_query(table, as_of_time, symbol, fields)
    
    def build_recent_query(self, table: str, as_of_time: datetime, symbol: str, fields: List[str]) -> tuple:
        """Optimized query for recent data (last 7 days)"""
        
        # Use covering indexes and avoid full table scans
        base_fields = fields or ['*']
        field_list = ', '.join(base_fields)
        
        if symbol:
            query = f"""
                SELECT {field_list}
                FROM {table}
                WHERE symbol = $1 
                    AND valid_from <= $2
                    AND valid_to > $2
                ORDER BY valid_from DESC
                LIMIT 1;
            """
            params = [symbol, as_of_time]
        else:
            query = f"""
                SELECT DISTINCT ON (symbol) 
                    symbol, {field_list}
                FROM {table}
                WHERE valid_from <= $1
                    AND valid_to > $1
                    AND valid_from >= $2  -- Optimize with recency filter
                ORDER BY symbol, valid_from DESC;
            """
            params = [as_of_time, as_of_time - timedelta(days=7)]
        
        return query, params
    
    def build_bulk_as_of_query(self, symbols: List[str], as_of_time: datetime) -> str:
        """Optimized bulk query for multiple symbols"""
        
        # Use VALUES clause for efficient multi-symbol queries
        return """
            WITH symbols_list(symbol) AS (
                VALUES {symbol_values}
            ),
            latest_data AS (
                SELECT DISTINCT ON (p.symbol)
                    p.symbol,
                    p.close,
                    p.volume,
                    p.valid_from
                FROM price_history p
                INNER JOIN symbols_list s ON p.symbol = s.symbol
                WHERE p.valid_from <= $1
                    AND p.valid_to > $1
                ORDER BY p.symbol, p.valid_from DESC
            )
            SELECT * FROM latest_data
            ORDER BY symbol;
        """.format(
            symbol_values=','.join(f"('{symbol}')" for symbol in symbols)
        )
```

## 💾 Caching Strategy

```python
class QueryCache:
    """Multi-level caching for query results"""
    
    def __init__(self):
        self.redis_client = None
        self.local_cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
    
    async def initialize(self):
        """Initialize Redis connection"""
        self.redis_client = await aioredis.create_connection(
            f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}'
        )
    
    def generate_key(self, table: str, as_of_time: datetime, symbol: str, fields: List[str]) -> str:
        """Generate cache key"""
        
        # Round to nearest minute for better cache hit rates
        rounded_time = as_of_time.replace(second=0, microsecond=0)
        
        key_parts = [
            table,
            rounded_time.isoformat(),
            symbol or 'ALL',
            '_'.join(sorted(fields or ['ALL']))
        ]
        
        return ':'.join(key_parts)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get from cache with fallback"""
        
        # Try local cache first
        if key in self.local_cache:
            self.cache_stats['hits'] += 1
            return self.local_cache[key]
        
        # Try Redis
        if self.redis_client:
            try:
                cached_data = await self.redis_client.get(key)
                if cached_data:
                    result = json.loads(cached_data)
                    # Store in local cache
                    self.local_cache[key] = result
                    self.cache_stats['hits'] += 1
                    return result
            except Exception as e:
                logger.warning(f"Redis cache error: {e}")
        
        self.cache_stats['misses'] += 1
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Set in cache with TTL"""
        
        # Store in local cache
        self.local_cache[key] = value
        
        # Evict if local cache too large
        if len(self.local_cache) > 1000:
            # Remove oldest entries
            oldest_keys = list(self.local_cache.keys())[:100]
            for old_key in oldest_keys:
                del self.local_cache[old_key]
                self.cache_stats['evictions'] += 1
        
        # Store in Redis
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    key, 
                    ttl, 
                    json.dumps(value, default=str)
                )
            except Exception as e:
                logger.warning(f"Redis cache set error: {e}")
```

## 📈 Query Performance Monitoring

```python
class QueryMetrics:
    """Monitor query performance and optimize"""
    
    def __init__(self):
        self.metrics = {
            'queries_by_table': defaultdict(int),
            'avg_response_time': defaultdict(list),
            'cache_hit_rate': defaultdict(float),
            'slow_queries': []
        }
    
    async def record_query(self, table: str, response_time: float, result_count: int):
        """Record query metrics"""
        
        self.metrics['queries_by_table'][table] += 1
        self.metrics['avg_response_time'][table].append(response_time)
        
        # Track slow queries
        if response_time > 1.0:  # Slower than 1 second
            self.metrics['slow_queries'].append({
                'table': table,
                'response_time': response_time,
                'result_count': result_count,
                'timestamp': datetime.now()
            })
        
        # Keep only recent slow queries
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.metrics['slow_queries'] = [
            q for q in self.metrics['slow_queries']
            if q['timestamp'] > cutoff_time
        ]
    
    def get_performance_summary(self) -> Dict:
        """Get performance summary"""
        
        summary = {
            'total_queries': sum(self.metrics['queries_by_table'].values()),
            'tables_queried': len(self.metrics['queries_by_table']),
            'avg_response_times': {},
            'slow_query_count': len(self.metrics['slow_queries'])
        }
        
        # Calculate average response times
        for table, times in self.metrics['avg_response_time'].items():
            if times:
                summary['avg_response_times'][table] = {
                    'avg': np.mean(times),
                    'p95': np.percentile(times, 95),
                    'p99': np.percentile(times, 99)
                }
        
        return summary
```

## 🎨 Query Interface

```typescript
// PointInTimeQueryInterface.tsx

interface QueryParams {
  table: string;
  asOfTime: Date;
  symbol?: string;
  fields?: string[];
}

const PointInTimeQueryInterface = () => {
  const [queryParams, setQueryParams] = useState<QueryParams>();
  const [results, setResults] = useState<any[]>();
  const [isLoading, setIsLoading] = useState(false);
  const [queryMetrics, setQueryMetrics] = useState<any>();

  const executeQuery = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/time-machine/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(queryParams)
      });
      
      const data = await response.json();
      setResults(data.results);
      setQueryMetrics(data.metrics);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="query-interface">
      {/* Query Builder */}
      <Card>
        <CardHeader>
          <Title>🔍 Point-in-Time Query Builder</Title>
        </CardHeader>
        <CardBody>
          <QueryBuilder 
            params={queryParams}
            onChange={setQueryParams}
          />
          <Button 
            onClick={executeQuery}
            loading={isLoading}
            disabled={!queryParams}
          >
            Execute Query
          </Button>
        </CardBody>
      </Card>
      
      {/* Results */}
      {results && (
        <Card>
          <CardHeader>
            <Title>📈 Query Results</Title>
            <Badge>{results.length} records</Badge>
          </CardHeader>
          <CardBody>
            <ResultsTable data={results} />
            <QueryMetrics metrics={queryMetrics} />
          </CardBody>
        </Card>
      )}
    </div>
  );
};
```

## 📊 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Query response time | <100ms | - |
| Cache hit rate | >80% | - |
| Concurrent queries | 1000+ | - |
| Historical accuracy | 100% | - |
| Query throughput | 10k queries/sec | - |

---

**Next**: Continue with prediction validation system.