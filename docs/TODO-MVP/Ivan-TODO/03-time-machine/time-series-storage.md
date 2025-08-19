# 🗄️ Time-Series Storage Architecture

**Priority**: CRITICAL  
**Complexity**: High  
**Timeline**: 3-4 days  
**Value**: Foundation for all time machine functionality

## 🎯 Objective

Build a robust time-series storage system that:
- Stores all data with precise timestamps
- Enables point-in-time queries
- Handles massive data volumes efficiently
- Provides fast historical reconstruction
- Supports real-time ingestion

## 📊 Database Architecture

### Primary Stack
```python
STORAGE_STACK = {
    'primary_db': 'PostgreSQL with TimescaleDB extension',
    'benefits': [
        'Native time-series optimization',
        'SQL compatibility',
        'Automatic partitioning',
        'Compression capabilities',
        'Continuous aggregates'
    ],
    'backup': 'InfluxDB for high-frequency data',
    'caching': 'Redis for frequent queries'
}
```

### Hypertable Structure
```sql
-- Market data time series
CREATE TABLE market_data_ts (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    
    -- OHLCV data
    open DECIMAL(12,4),
    high DECIMAL(12,4),
    low DECIMAL(12,4),
    close DECIMAL(12,4),
    volume BIGINT,
    
    -- Extended metrics
    vwap DECIMAL(12,4),
    trades INTEGER,
    market_cap DECIMAL(20,2),
    
    -- Data quality
    source VARCHAR(50),
    quality_score DECIMAL(3,2),
    
    PRIMARY KEY (time, symbol)
);

-- Convert to hypertable (TimescaleDB)
SELECT create_hypertable('market_data_ts', 'time', 'symbol', 4);

-- Enable compression
ALTER TABLE market_data_ts SET (timescaledb.compress);
SELECT add_compression_policy('market_data_ts', INTERVAL '7 days');
```

## 💾 Core Schema Design

### News Events Time Series
```sql
CREATE TABLE news_events_ts (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20),
    
    -- Content
    title TEXT,
    content TEXT,
    source VARCHAR(100),
    
    -- Analysis
    sentiment DECIMAL(5,4),
    impact_score DECIMAL(5,4),
    categories TEXT[],
    
    -- Metadata
    url TEXT,
    author VARCHAR(255),
    language VARCHAR(10),
    
    PRIMARY KEY (time, symbol)
);

SELECT create_hypertable('news_events_ts', 'time');
```

### Insider Trading Time Series
```sql
CREATE TABLE insider_trades_ts (
    time TIMESTAMPTZ NOT NULL, -- Transaction date
    symbol VARCHAR(20) NOT NULL,
    
    -- Trade details
    insider_name VARCHAR(255),
    title VARCHAR(255),
    transaction_type VARCHAR(20), -- buy/sell
    shares INTEGER,
    price DECIMAL(10,2),
    value DECIMAL(15,2),
    
    -- Filing details
    filing_date TIMESTAMPTZ,
    form_type VARCHAR(10), -- 4, 4/A, etc.
    
    -- Analysis
    is_cluster_trade BOOLEAN,
    political_connection BOOLEAN,
    
    PRIMARY KEY (time, symbol, insider_name)
);

SELECT create_hypertable('insider_trades_ts', 'time');
```

### Social Sentiment Time Series
```sql
CREATE TABLE social_sentiment_ts (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    
    -- Aggregated metrics per hour
    mention_count INTEGER,
    sentiment_avg DECIMAL(5,4),
    sentiment_std DECIMAL(5,4),
    
    -- Volume metrics
    unique_users INTEGER,
    total_engagement INTEGER,
    
    -- Trending metrics
    momentum_score DECIMAL(5,4),
    viral_score DECIMAL(5,4),
    
    PRIMARY KEY (time, symbol, platform)
);

SELECT create_hypertable('social_sentiment_ts', 'time');
```

### Government Data Time Series
```sql
CREATE TABLE government_events_ts (
    time TIMESTAMPTZ NOT NULL,
    
    -- Event details
    event_type VARCHAR(100), -- contract_award, policy_change, etc.
    amount DECIMAL(20,2),
    description TEXT,
    
    -- Affected entities
    primary_symbol VARCHAR(20),
    affected_symbols TEXT[],
    sectors TEXT[],
    
    -- Geographic
    country VARCHAR(3),
    state_province VARCHAR(100),
    
    -- Impact assessment
    market_impact VARCHAR(20),
    confidence DECIMAL(3,2),
    
    PRIMARY KEY (time, event_type, primary_symbol)
);

SELECT create_hypertable('government_events_ts', 'time');
```

## 🔄 Ingestion Pipeline

```python
# app/storage/timeseries_ingester.py

import asyncio
import asyncpg
from datetime import datetime, timezone
from typing import Dict, List, Any
import pandas as pd

class TimeSeriesIngester:
    """High-performance time series data ingestion"""
    
    def __init__(self):
        self.pool = None
        self.buffer = {
            'market_data': [],
            'news_events': [],
            'insider_trades': [],
            'social_sentiment': [],
            'government_events': []
        }
        self.buffer_size = 1000
        
    async def initialize(self):
        """Initialize connection pool"""
        self.pool = await asyncpg.create_pool(
            host=settings.TIMESERIES_DB_HOST,
            port=settings.TIMESERIES_DB_PORT,
            user=settings.TIMESERIES_DB_USER,
            password=settings.TIMESERIES_DB_PASSWORD,
            database=settings.TIMESERIES_DB_NAME,
            min_size=10,
            max_size=20
        )
    
    async def ingest_market_data(self, data: List[Dict]):
        """Ingest market data with deduplication"""
        
        # Add to buffer
        self.buffer['market_data'].extend(data)
        
        # Flush if buffer is full
        if len(self.buffer['market_data']) >= self.buffer_size:
            await self.flush_market_data()
    
    async def flush_market_data(self):
        """Flush market data buffer to database"""
        
        if not self.buffer['market_data']:
            return
            
        async with self.pool.acquire() as conn:
            # Prepare data
            records = [
                (
                    item['timestamp'],
                    item['symbol'],
                    item['open'],
                    item['high'],
                    item['low'],
                    item['close'],
                    item['volume'],
                    item.get('vwap'),
                    item.get('trades'),
                    item.get('market_cap'),
                    item.get('source', 'unknown'),
                    item.get('quality_score', 1.0)
                ) for item in self.buffer['market_data']
            ]
            
            # Use COPY for bulk insert performance
            await conn.copy_records_to_table(
                'market_data_ts',
                records=records,
                columns=[
                    'time', 'symbol', 'open', 'high', 'low', 
                    'close', 'volume', 'vwap', 'trades', 
                    'market_cap', 'source', 'quality_score'
                ]
            )
            
        # Clear buffer
        self.buffer['market_data'].clear()
        logger.info(f"Flushed {len(records)} market data records")
    
    async def ingest_with_deduplication(self, table: str, data: List[Dict]):
        """Generic ingestion with deduplication"""
        
        async with self.pool.acquire() as conn:
            # Create temp table
            temp_table = f"temp_{table}_{int(datetime.now().timestamp())}"
            
            # Insert into temp table
            await self.bulk_insert_temp(conn, temp_table, table, data)
            
            # Merge with deduplication
            await self.merge_deduplicated(conn, temp_table, table)
            
            # Drop temp table
            await conn.execute(f"DROP TABLE {temp_table}")
    
    async def bulk_insert_temp(self, conn, temp_table: str, main_table: str, data: List[Dict]):
        """Bulk insert into temporary table"""
        
        # Create temp table with same structure
        await conn.execute(f"""
            CREATE TEMP TABLE {temp_table} 
            (LIKE {main_table} INCLUDING ALL)
        """)
        
        # Bulk insert
        await conn.copy_records_to_table(
            temp_table,
            records=self.dict_to_records(data, main_table)
        )
    
    async def setup_continuous_aggregates(self):
        """Set up continuous aggregates for common queries"""
        
        async with self.pool.acquire() as conn:
            # Daily OHLCV aggregates
            await conn.execute("""
                CREATE MATERIALIZED VIEW daily_ohlcv
                WITH (timescaledb.continuous) AS
                SELECT 
                    time_bucket('1 day', time) AS day,
                    symbol,
                    FIRST(open, time) AS open,
                    MAX(high) AS high,
                    MIN(low) AS low,
                    LAST(close, time) AS close,
                    SUM(volume) AS volume,
                    AVG(vwap) AS vwap
                FROM market_data_ts
                GROUP BY day, symbol
                ORDER BY day DESC, symbol;
            """)
            
            # Hourly sentiment aggregates
            await conn.execute("""
                CREATE MATERIALIZED VIEW hourly_sentiment
                WITH (timescaledb.continuous) AS
                SELECT 
                    time_bucket('1 hour', time) AS hour,
                    symbol,
                    AVG(sentiment_avg) AS sentiment,
                    SUM(mention_count) AS mentions,
                    COUNT(DISTINCT platform) AS platforms
                FROM social_sentiment_ts
                GROUP BY hour, symbol
                ORDER BY hour DESC, symbol;
            """)
```

## 🔍 Point-in-Time Queries

```python
class PointInTimeQuerier:
    """Query engine for historical data reconstruction"""
    
    async def get_market_state_at(self, timestamp: datetime, symbols: List[str] = None) -> Dict:
        """Get complete market state at specific time"""
        
        query = """
            WITH latest_prices AS (
                SELECT DISTINCT ON (symbol)
                    symbol,
                    time,
                    close as price,
                    volume,
                    market_cap
                FROM market_data_ts
                WHERE time <= $1
                    AND ($2::text[] IS NULL OR symbol = ANY($2))
                ORDER BY symbol, time DESC
            )
            SELECT * FROM latest_prices
            ORDER BY symbol;
        """
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, timestamp, symbols)
            
        return {
            row['symbol']: {
                'price': float(row['price']),
                'volume': int(row['volume']),
                'market_cap': float(row['market_cap']) if row['market_cap'] else None,
                'as_of': row['time']
            } for row in rows
        }
    
    async def get_news_before(self, timestamp: datetime, symbols: List[str] = None) -> List[Dict]:
        """Get all news available before timestamp"""
        
        query = """
            SELECT 
                time,
                symbol,
                title,
                sentiment,
                impact_score,
                source
            FROM news_events_ts
            WHERE time <= $1
                AND ($2::text[] IS NULL OR symbol = ANY($2))
            ORDER BY time DESC, impact_score DESC
            LIMIT 1000;
        """
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, timestamp, symbols)
            
        return [dict(row) for row in rows]
    
    async def get_insider_activity_before(self, timestamp: datetime, symbols: List[str] = None) -> List[Dict]:
        """Get insider trades disclosed before timestamp"""
        
        # Important: Use filing_date, not transaction_date
        # for point-in-time accuracy
        query = """
            SELECT 
                time as transaction_date,
                filing_date,
                symbol,
                insider_name,
                transaction_type,
                shares,
                value,
                is_cluster_trade
            FROM insider_trades_ts
            WHERE filing_date <= $1  -- Key: when it was known
                AND ($2::text[] IS NULL OR symbol = ANY($2))
            ORDER BY filing_date DESC, value DESC
            LIMIT 500;
        """
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, timestamp, symbols)
            
        return [dict(row) for row in rows]
    
    async def reconstruct_full_state(self, timestamp: datetime, symbol: str) -> Dict:
        """Reconstruct complete market state for a symbol at timestamp"""
        
        # Run queries in parallel
        market_task = self.get_market_state_at(timestamp, [symbol])
        news_task = self.get_news_before(timestamp, [symbol])
        insider_task = self.get_insider_activity_before(timestamp, [symbol])
        sentiment_task = self.get_sentiment_before(timestamp, [symbol])
        
        market_data, news, insider_trades, sentiment = await asyncio.gather(
            market_task, news_task, insider_task, sentiment_task
        )
        
        return {
            'timestamp': timestamp,
            'symbol': symbol,
            'market_data': market_data.get(symbol, {}),
            'recent_news': news[:10],  # Top 10 by impact
            'insider_activity': self.analyze_insider_activity(insider_trades),
            'sentiment': sentiment,
            'technical_indicators': await self.calculate_indicators_at(timestamp, symbol)
        }
```

## ⚡ Performance Optimization

### Indexing Strategy
```sql
-- Compound indexes for common queries
CREATE INDEX CONCURRENTLY idx_market_data_symbol_time 
ON market_data_ts (symbol, time DESC);

CREATE INDEX CONCURRENTLY idx_news_time_impact 
ON news_events_ts (time DESC, impact_score DESC);

CREATE INDEX CONCURRENTLY idx_insider_filing_symbol 
ON insider_trades_ts (filing_date DESC, symbol, value DESC);

-- Partial indexes for common filters
CREATE INDEX CONCURRENTLY idx_high_impact_news 
ON news_events_ts (time DESC, symbol) 
WHERE impact_score > 0.7;
```

### Compression and Retention
```sql
-- Compression policies
SELECT add_compression_policy('market_data_ts', INTERVAL '7 days');
SELECT add_compression_policy('news_events_ts', INTERVAL '30 days');
SELECT add_compression_policy('social_sentiment_ts', INTERVAL '3 days');

-- Retention policies
SELECT add_retention_policy('social_sentiment_ts', INTERVAL '2 years');
SELECT add_retention_policy('news_events_ts', INTERVAL '10 years');
```

### Query Optimization
```python
class QueryOptimizer:
    """Optimize time-series queries"""
    
    @functools.lru_cache(maxsize=1000)
    async def cached_market_state(self, timestamp: datetime, symbol: str) -> Dict:
        """Cache frequently accessed market states"""
        return await self.get_market_state_at(timestamp, [symbol])
    
    def batch_queries(self, queries: List[Tuple]) -> List[Dict]:
        """Batch multiple point-in-time queries"""
        
        # Group by timestamp to minimize queries
        timestamp_groups = {}
        for timestamp, symbol in queries:
            if timestamp not in timestamp_groups:
                timestamp_groups[timestamp] = []
            timestamp_groups[timestamp].append(symbol)
        
        # Execute batched queries
        results = []
        for timestamp, symbols in timestamp_groups.items():
            batch_result = await self.get_market_state_at(timestamp, symbols)
            results.extend(batch_result.items())
            
        return results
```

## 📊 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Query response time | <100ms | - |
| Ingestion throughput | 100k points/sec | - |
| Storage efficiency | 10:1 compression | - |
| Data retention | 10 years | - |
| Point-in-time accuracy | 99.99% | - |

---

**Next**: Continue with historical reconstruction capabilities.