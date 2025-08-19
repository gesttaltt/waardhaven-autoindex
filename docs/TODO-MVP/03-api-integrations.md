# API Integration Updates - TwelveData & Marketaux

**Priority**: P1 - HIGH  
**Status**: 🟡 Basic Implementation  
**Estimated**: 1 day  
**APIs**: TwelveData (Technical), Marketaux (News/Fundamental)

## 🎯 Objective

Update and optimize external API integrations for:
- Latest API versions and endpoints
- Batch request optimization
- Proper rate limiting
- Error handling and retry logic
- Cost optimization

## 📋 Current State

### TwelveData (Technical Analysis)
- ✅ Basic integration exists
- ✅ Retry logic implemented
- 🔴 No batch optimization
- 🔴 Rate limiting not proper (8 req/min free tier)
- 🔴 Missing new endpoints

### Marketaux (News & Sentiment)
- 🔴 Not integrated
- 🔴 No service implementation
- 🔴 No schema definitions

## 📋 Task Breakdown

### Phase 1: TwelveData Optimization (4 hours)

#### Task 1.1: Update Service Implementation
**File**: `apps/api/app/services/twelvedata.py`

```python
# Enhancements needed:
- [ ] Add rate limiter (8 req/min for free tier)
- [ ] Implement batch requests
- [ ] Add request queuing
- [ ] Update to latest API endpoints
- [ ] Add WebSocket support for real-time
```

#### Task 1.2: Batch Request Implementation
```python
class TwelveDataService:
    # Methods to implement:
    - [ ] fetch_batch_quotes(symbols: List[str])
    - [ ] fetch_batch_time_series(symbols: List[str], interval: str)
    - [ ] fetch_batch_technical_indicators(symbols: List[str], indicators: List[str])
    - [ ] optimize_request_batching(requests: List[Dict])
```

#### Task 1.3: Rate Limiting
```python
# Implementation:
- [ ] Token bucket algorithm
- [ ] Request queue with priority
- [ ] Exponential backoff on 429
- [ ] Usage tracking and alerts
```

### Phase 2: Marketaux Integration (4 hours)

#### Task 2.1: Create Marketaux Service
**File**: `apps/api/app/services/marketaux.py`

```python
class MarketauxService:
    """News and sentiment analysis service"""
    
    # Methods to implement:
    - [ ] fetch_news(symbols: List[str], limit: int)
    - [ ] fetch_sentiment(symbol: str, period: str)
    - [ ] fetch_fundamental_data(symbol: str)
    - [ ] aggregate_news_sentiment(news_items: List[Dict])
```

#### Task 2.2: News Schema
**File**: `apps/api/app/schemas/news.py`

```python
# Schemas to create:
- [ ] NewsItem
- [ ] NewsSentiment
- [ ] NewsAggregation
- [ ] FundamentalData
```

#### Task 2.3: News Endpoints
**File**: `apps/api/app/routers/news.py`

```python
# Endpoints to create:
- [ ] GET /news/latest - Latest market news
- [ ] GET /news/symbol/{symbol} - Symbol-specific news
- [ ] GET /news/sentiment/{symbol} - Sentiment analysis
- [ ] GET /news/trending - Trending topics
```

### Phase 3: Caching Strategy (2 hours)

#### Task 3.1: Cache Configuration
```python
# Cache strategies:
- [ ] Quote cache: 1 minute TTL
- [ ] Historical data: 1 hour TTL
- [ ] News: 5 minutes TTL
- [ ] Fundamental data: 24 hours TTL
```

#### Task 3.2: Cache Invalidation
```python
# Invalidation triggers:
- [ ] Market open/close
- [ ] Data refresh request
- [ ] Error responses
- [ ] Stale data detection
```

### Phase 4: Cost Optimization (2 hours)

#### Task 4.1: Request Optimization
```python
# Strategies:
- [ ] Deduplicate requests
- [ ] Cache hit prioritization
- [ ] Off-hours pre-fetching
- [ ] Compression support
```

#### Task 4.2: Usage Monitoring
```python
# Monitoring:
- [ ] API call counter
- [ ] Cost calculator
- [ ] Usage alerts
- [ ] Monthly reports
```

## 📊 Implementation Examples

### Enhanced TwelveData Service

```python
# apps/api/app/services/twelvedata.py

import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import aiohttp
from app.core.config import settings
from app.core.cache import cache_result
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Token bucket rate limiter"""
    def __init__(self, rate: int, per: int):
        self.rate = rate
        self.per = per
        self.tokens = rate
        self.updated_at = datetime.now()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        async with self.lock:
            now = datetime.now()
            elapsed = (now - self.updated_at).total_seconds()
            self.tokens = min(self.rate, self.tokens + elapsed * (self.rate / self.per))
            self.updated_at = now
            
            if self.tokens < 1:
                sleep_time = (1 - self.tokens) * (self.per / self.rate)
                await asyncio.sleep(sleep_time)
                self.tokens = 1
            
            self.tokens -= 1

class TwelveDataService:
    """Enhanced TwelveData API service with batching and rate limiting"""
    
    BASE_URL = "https://api.twelvedata.com"
    
    def __init__(self):
        self.api_key = settings.TWELVEDATA_API_KEY
        self.rate_limiter = RateLimiter(rate=8, per=60)  # 8 requests per minute
        self.session = None
        self.request_queue = asyncio.Queue()
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @cache_result(ttl=60)
    async def fetch_batch_quotes(self, symbols: List[str]) -> Dict[str, Dict]:
        """Fetch multiple quotes in a single API call"""
        await self.rate_limiter.acquire()
        
        # Batch symbols (max 120 per request for free tier)
        batch_size = 120
        results = {}
        
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i + batch_size]
            symbol_str = ",".join(batch)
            
            params = {
                "symbol": symbol_str,
                "apikey": self.api_key
            }
            
            try:
                async with self.session.get(
                    f"{self.BASE_URL}/quote",
                    params=params
                ) as response:
                    data = await response.json()
                    
                    if response.status == 200:
                        # Handle both single and batch responses
                        if isinstance(data, dict) and "symbol" in data:
                            results[data["symbol"]] = data
                        else:
                            results.update(data)
                    else:
                        logger.error(f"API error: {data}")
                        
            except Exception as e:
                logger.error(f"Failed to fetch quotes: {e}")
        
        return results
    
    async def fetch_time_series_batch(
        self,
        symbols: List[str],
        interval: str = "1day",
        outputsize: int = 30
    ) -> Dict[str, List]:
        """Fetch historical data for multiple symbols"""
        await self.rate_limiter.acquire()
        
        results = {}
        
        # Time series must be fetched individually
        for symbol in symbols:
            params = {
                "symbol": symbol,
                "interval": interval,
                "outputsize": outputsize,
                "apikey": self.api_key
            }
            
            try:
                async with self.session.get(
                    f"{self.BASE_URL}/time_series",
                    params=params
                ) as response:
                    data = await response.json()
                    
                    if response.status == 200 and "values" in data:
                        results[symbol] = data["values"]
                    
            except Exception as e:
                logger.error(f"Failed to fetch time series for {symbol}: {e}")
        
        return results
    
    async def fetch_technical_indicators(
        self,
        symbol: str,
        indicators: List[str],
        interval: str = "1day"
    ) -> Dict[str, Dict]:
        """Fetch multiple technical indicators"""
        await self.rate_limiter.acquire()
        
        results = {}
        
        for indicator in indicators:
            params = {
                "symbol": symbol,
                "interval": interval,
                "apikey": self.api_key
            }
            
            # Add indicator-specific parameters
            if indicator == "sma":
                params["time_period"] = 50
            elif indicator == "rsi":
                params["time_period"] = 14
            elif indicator == "bbands":
                params["time_period"] = 20
                params["sd"] = 2
            
            try:
                async with self.session.get(
                    f"{self.BASE_URL}/{indicator}",
                    params=params
                ) as response:
                    data = await response.json()
                    
                    if response.status == 200:
                        results[indicator] = data
                        
            except Exception as e:
                logger.error(f"Failed to fetch {indicator} for {symbol}: {e}")
        
        return results
```

### Marketaux Service Implementation

```python
# apps/api/app/services/marketaux.py

import aiohttp
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app.core.config import settings
from app.core.cache import cache_result
import logging

logger = logging.getLogger(__name__)

class MarketauxService:
    """Marketaux news and sentiment analysis service"""
    
    BASE_URL = "https://api.marketaux.com/v1"
    
    def __init__(self):
        self.api_key = settings.MARKETAUX_API_KEY
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @cache_result(ttl=300)  # 5 minute cache
    async def fetch_news(
        self,
        symbols: Optional[List[str]] = None,
        limit: int = 10,
        languages: str = "en"
    ) -> List[Dict]:
        """Fetch latest financial news"""
        params = {
            "api_token": self.api_key,
            "limit": limit,
            "languages": languages,
            "filter_entities": "true",
            "sort": "published_at",
            "sort_order": "desc"
        }
        
        if symbols:
            params["symbols"] = ",".join(symbols)
        
        try:
            async with self.session.get(
                f"{self.BASE_URL}/news/all",
                params=params
            ) as response:
                data = await response.json()
                
                if response.status == 200:
                    return data.get("data", [])
                else:
                    logger.error(f"Marketaux API error: {data}")
                    return []
                    
        except Exception as e:
            logger.error(f"Failed to fetch news: {e}")
            return []
    
    async def fetch_sentiment(
        self,
        symbol: str,
        days: int = 7
    ) -> Dict:
        """Analyze sentiment for a symbol"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        params = {
            "api_token": self.api_key,
            "symbols": symbol,
            "published_after": start_date.isoformat(),
            "published_before": end_date.isoformat(),
            "filter_entities": "true",
            "group_by": "symbol"
        }
        
        try:
            async with self.session.get(
                f"{self.BASE_URL}/news/all",
                params=params
            ) as response:
                data = await response.json()
                
                if response.status == 200:
                    news_items = data.get("data", [])
                    return self._calculate_sentiment(news_items)
                    
        except Exception as e:
            logger.error(f"Failed to fetch sentiment: {e}")
            return {}
    
    def _calculate_sentiment(self, news_items: List[Dict]) -> Dict:
        """Calculate aggregate sentiment from news items"""
        if not news_items:
            return {"sentiment": "neutral", "score": 0, "count": 0}
        
        positive = 0
        negative = 0
        neutral = 0
        
        for item in news_items:
            sentiment = item.get("sentiment", {})
            score = sentiment.get("score", 0)
            
            if score > 0.2:
                positive += 1
            elif score < -0.2:
                negative += 1
            else:
                neutral += 1
        
        total = len(news_items)
        
        # Calculate weighted sentiment
        sentiment_score = (positive - negative) / total if total > 0 else 0
        
        if sentiment_score > 0.2:
            sentiment_label = "positive"
        elif sentiment_score < -0.2:
            sentiment_label = "negative"
        else:
            sentiment_label = "neutral"
        
        return {
            "sentiment": sentiment_label,
            "score": sentiment_score,
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "total": total
        }
```

## 🧪 Testing Checklist

### TwelveData Tests
- [ ] Rate limiter respects limits
- [ ] Batch requests work correctly
- [ ] Error handling for API failures
- [ ] Cache behavior
- [ ] Concurrent request handling

### Marketaux Tests
- [ ] News fetching
- [ ] Sentiment calculation
- [ ] Symbol filtering
- [ ] Date range queries
- [ ] Error scenarios

### Integration Tests
- [ ] End-to-end data flow
- [ ] Multiple API coordination
- [ ] Cache invalidation
- [ ] Rate limit compliance

## 📈 Success Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| API calls/day | >1000 | <500 | 🔴 |
| Batch efficiency | 0% | >80% | 🔴 |
| Cache hit rate | <20% | >60% | 🔴 |
| Error rate | Unknown | <1% | 🔴 |
| Response time | >2s | <500ms | 🔴 |

## 🔄 Environment Variables

```env
# TwelveData
TWELVEDATA_API_KEY=your_api_key_here
TWELVEDATA_RATE_LIMIT=8
TWELVEDATA_BATCH_SIZE=120
TWELVEDATA_WEBSOCKET_ENABLED=false

# Marketaux
MARKETAUX_API_KEY=your_api_key_here
MARKETAUX_RATE_LIMIT=100
NEWS_FETCH_INTERVAL=300
```

## 📝 API Documentation Links

- [TwelveData Docs](https://twelvedata.com/docs)
- [TwelveData Python SDK](https://github.com/twelvedata/twelvedata-python)
- [Marketaux Docs](https://www.marketaux.com/documentation)

---

**Next**: Continue with [04-frontend-refactoring.md](./04-frontend-refactoring.md)