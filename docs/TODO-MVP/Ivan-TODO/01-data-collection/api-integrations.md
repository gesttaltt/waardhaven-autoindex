# 🔌 API Integrations & Setup Guide

**Priority**: CRITICAL  
**Complexity**: Medium  
**Timeline**: 2-3 days  
**Value**: Foundation for all data collection

## 🎯 Objective

Set up and configure all API integrations for:
- Market data providers
- News aggregators
- Government data sources
- Social media platforms
- Alternative data providers

## 📊 API Priority Tiers

### Tier 1 - Essential (Must Have)
```python
ESSENTIAL_APIS = {
    'polygon': {
        'purpose': 'Real-time & historical market data',
        'cost': '$199/month',
        'rate_limit': '100,000 requests/day',
        'endpoints': [
            '/v2/aggs/ticker/{ticker}/range',
            '/v2/reference/news',
            '/v1/meta/conditions'
        ]
    },
    'alpha_vantage': {
        'purpose': 'Backup market data',
        'cost': 'Free tier available',
        'rate_limit': '5 requests/minute',
        'key_features': ['Technical indicators', 'Fundamental data']
    },
    'marketaux': {
        'purpose': 'News aggregation',
        'cost': 'Existing',
        'coverage': '3000+ sources globally'
    },
    'sec_edgar': {
        'purpose': 'Filings and insider trading',
        'cost': 'Free',
        'rate_limit': '10 requests/second'
    }
}
```

### Tier 2 - Important (Should Have)
```python
IMPORTANT_APIS = {
    'quiver_quant': {
        'purpose': 'Congressional trading data',
        'cost': '$10/month',
        'unique_data': ['Congress trades', 'Lobbying', 'Gov contracts']
    },
    'finnhub': {
        'purpose': 'Global market data',
        'cost': '$50/month',
        'features': ['Earnings calendar', 'IPO calendar', 'Splits']
    },
    'newsapi': {
        'purpose': 'General news',
        'cost': '$449/month for production',
        'sources': '80,000+ publishers'
    },
    'reddit_api': {
        'purpose': 'Social sentiment',
        'cost': 'Free',
        'rate_limit': '60 requests/minute'
    }
}
```

### Tier 3 - Advanced (Nice to Have)
```python
ADVANCED_APIS = {
    'bloomberg': {
        'purpose': 'Professional data',
        'cost': '$2000/month',
        'benefits': 'Institutional quality data'
    },
    'refinitiv': {
        'purpose': 'Alternative data',
        'cost': 'Enterprise pricing',
        'data': ['ESG scores', 'Supply chain']
    },
    'satellite_data': {
        'providers': ['Orbital Insight', 'SpaceKnow'],
        'purpose': 'Physical world insights',
        'cost': '$5000+/month'
    }
}
```

## 🔑 API Configuration

```python
# app/core/api_config.py

from typing import Dict, Optional
import os
from dataclasses import dataclass
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

@dataclass
class APIConfig:
    """Configuration for each API"""
    name: str
    base_url: str
    api_key: Optional[str]
    rate_limit: int  # requests per second
    timeout: int = 30
    retry_count: int = 3
    
class APIManager:
    """Centralized API management"""
    
    def __init__(self):
        self.configs = self.load_api_configs()
        self.clients = {}
        self.rate_limiters = {}
        
    def load_api_configs(self) -> Dict[str, APIConfig]:
        """Load all API configurations"""
        
        return {
            'polygon': APIConfig(
                name='Polygon',
                base_url='https://api.polygon.io',
                api_key=os.getenv('POLYGON_API_KEY'),
                rate_limit=100  # per second
            ),
            'alpha_vantage': APIConfig(
                name='Alpha Vantage',
                base_url='https://www.alphavantage.co',
                api_key=os.getenv('ALPHA_VANTAGE_API_KEY'),
                rate_limit=0.08  # 5 per minute
            ),
            'marketaux': APIConfig(
                name='Marketaux',
                base_url='https://api.marketaux.com/v1',
                api_key=os.getenv('MARKETAUX_API_KEY'),
                rate_limit=10
            ),
            'sec_edgar': APIConfig(
                name='SEC EDGAR',
                base_url='https://data.sec.gov',
                api_key=None,  # No API key required
                rate_limit=10
            ),
            'quiver': APIConfig(
                name='Quiver Quantitative',
                base_url='https://api.quiverquant.com/beta',
                api_key=os.getenv('QUIVER_API_KEY'),
                rate_limit=5
            ),
            'reddit': APIConfig(
                name='Reddit',
                base_url='https://oauth.reddit.com',
                api_key=os.getenv('REDDIT_CLIENT_ID'),
                rate_limit=1
            ),
            'twitter': APIConfig(
                name='Twitter/X',
                base_url='https://api.twitter.com/2',
                api_key=os.getenv('TWITTER_BEARER_TOKEN'),
                rate_limit=15
            ),
            'finnhub': APIConfig(
                name='Finnhub',
                base_url='https://finnhub.io/api/v1',
                api_key=os.getenv('FINNHUB_API_KEY'),
                rate_limit=30
            )
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def make_request(
        self,
        api_name: str,
        endpoint: str,
        params: Dict = None,
        method: str = 'GET'
    ) -> Dict:
        """Make rate-limited API request with retries"""
        
        config = self.configs[api_name]
        
        # Get or create client
        if api_name not in self.clients:
            self.clients[api_name] = httpx.AsyncClient(
                base_url=config.base_url,
                timeout=config.timeout
            )
        
        client = self.clients[api_name]
        
        # Apply rate limiting
        await self.rate_limit(api_name)
        
        # Prepare headers
        headers = self.get_headers(config)
        
        # Make request
        try:
            response = await client.request(
                method=method,
                url=endpoint,
                params=params,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"API request failed: {api_name} - {endpoint} - {e}")
            raise
```

## 🔄 Data Pipeline Architecture

```python
# app/services/data_pipeline.py

class DataPipeline:
    """Main data collection orchestrator"""
    
    def __init__(self):
        self.api_manager = APIManager()
        self.collectors = self.initialize_collectors()
        self.scheduler = AsyncIOScheduler()
        
    def initialize_collectors(self) -> Dict:
        """Initialize all data collectors"""
        
        return {
            'market': MarketDataCollector(self.api_manager),
            'news': NewsCollector(self.api_manager),
            'insider': InsiderTradingCollector(self.api_manager),
            'government': GovernmentDataCollector(self.api_manager),
            'social': SocialMediaCollector(self.api_manager),
            'alternative': AlternativeDataCollector(self.api_manager)
        }
    
    async def run_collection_cycle(self):
        """Run complete data collection cycle"""
        
        tasks = []
        
        # Real-time collections (every minute)
        tasks.append(self.collectors['market'].collect_realtime())
        tasks.append(self.collectors['social'].collect_trending())
        
        # Frequent collections (every 15 minutes)
        if self.should_run('frequent'):
            tasks.append(self.collectors['news'].collect_latest())
            tasks.append(self.collectors['market'].collect_options_flow())
        
        # Hourly collections
        if self.should_run('hourly'):
            tasks.append(self.collectors['insider'].collect_recent())
            tasks.append(self.collectors['government'].check_contracts())
        
        # Daily collections
        if self.should_run('daily'):
            tasks.append(self.collectors['alternative'].collect_all())
            tasks.append(self.collectors['market'].collect_fundamentals())
        
        # Run all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        await self.process_results(results)
        
        return results
```

## 📊 API Health Monitoring

```python
class APIHealthMonitor:
    """Monitor API health and usage"""
    
    def __init__(self):
        self.metrics = defaultdict(lambda: {
            'requests': 0,
            'errors': 0,
            'latency': [],
            'last_error': None,
            'status': 'healthy'
        })
    
    async def check_all_apis(self) -> Dict:
        """Health check all configured APIs"""
        
        health_status = {}
        
        for api_name, config in self.api_manager.configs.items():
            try:
                # Make test request
                start = time.time()
                result = await self.test_api(api_name)
                latency = time.time() - start
                
                health_status[api_name] = {
                    'status': 'healthy',
                    'latency': latency,
                    'rate_limit_remaining': result.get('rate_limit'),
                    'last_checked': datetime.now()
                }
                
            except Exception as e:
                health_status[api_name] = {
                    'status': 'unhealthy',
                    'error': str(e),
                    'last_checked': datetime.now()
                }
        
        return health_status
```

## 🔐 Authentication Setup

```yaml
# .env.example

# Market Data
POLYGON_API_KEY=your_polygon_key
ALPHA_VANTAGE_API_KEY=your_av_key
FINNHUB_API_KEY=your_finnhub_key

# News
MARKETAUX_API_KEY=existing_key
NEWSAPI_KEY=your_newsapi_key

# Government/Insider
QUIVER_API_KEY=your_quiver_key
# SEC EDGAR doesn't need key

# Social Media
REDDIT_CLIENT_ID=your_reddit_id
REDDIT_CLIENT_SECRET=your_reddit_secret
TWITTER_BEARER_TOKEN=your_twitter_token
STOCKTWITS_TOKEN=your_stocktwits_token

# Alternative Data (Optional)
SATELLITE_API_KEY=your_satellite_key
WEATHER_API_KEY=your_weather_key
```

## 🚀 Quick Start Guide

### 1. Obtain API Keys
```bash
# Essential APIs (start here)
- Polygon.io: https://polygon.io/pricing
- Marketaux: Already have
- SEC EDGAR: No key needed
- Reddit: https://www.reddit.com/prefs/apps

# Important APIs (add next)
- Quiver Quant: https://www.quiverquant.com/pricing
- Finnhub: https://finnhub.io/pricing
- NewsAPI: https://newsapi.org/pricing
```

### 2. Test Connections
```python
# scripts/test_apis.py

async def test_all_connections():
    """Test all API connections"""
    
    api_manager = APIManager()
    results = {}
    
    # Test each API
    for api_name in api_manager.configs.keys():
        try:
            print(f"Testing {api_name}...")
            result = await api_manager.test_connection(api_name)
            results[api_name] = "✅ Success"
        except Exception as e:
            results[api_name] = f"❌ Failed: {e}"
    
    # Print results
    print("\n" + "="*50)
    print("API Connection Test Results:")
    print("="*50)
    for api, status in results.items():
        print(f"{api:20} {status}")

if __name__ == "__main__":
    asyncio.run(test_all_connections())
```

### 3. Initialize Database
```sql
-- Create API usage tracking table
CREATE TABLE api_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_name VARCHAR(50) NOT NULL,
    endpoint VARCHAR(255),
    
    -- Usage metrics
    request_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    
    -- Rate limiting
    rate_limit_remaining INTEGER,
    rate_limit_reset TIMESTAMP,
    
    -- Billing
    cost_per_request DECIMAL(10,6),
    total_cost DECIMAL(10,2),
    
    -- Time window
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(api_name, period_start, period_end)
);
```

## 📊 Cost Optimization

```python
class APICostOptimizer:
    """Optimize API usage to minimize costs"""
    
    def __init__(self):
        self.cost_per_request = {
            'polygon': 0.0002,  # $199/mo ÷ 1M requests
            'bloomberg': 0.02,   # Expensive per request
            'sec_edgar': 0,      # Free
            'reddit': 0,         # Free
        }
    
    def select_optimal_source(self, data_type: str) -> str:
        """Select cheapest reliable source for data type"""
        
        sources_by_type = {
            'market_data': ['sec_edgar', 'alpha_vantage', 'polygon'],
            'news': ['reddit', 'marketaux', 'newsapi'],
            'insider': ['sec_edgar', 'quiver'],
        }
        
        # Get available sources for data type
        available = sources_by_type.get(data_type, [])
        
        # Sort by cost and reliability
        return self.rank_sources(available)[0]
```

## 🎯 Implementation Checklist

- [ ] Set up essential API keys
- [ ] Configure rate limiting
- [ ] Implement retry logic
- [ ] Set up health monitoring
- [ ] Create cost tracking
- [ ] Test all endpoints
- [ ] Set up error alerting
- [ ] Document API limits
- [ ] Create fallback sources
- [ ] Optimize request batching

## 📊 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| APIs integrated | 10+ | 0 |
| Uptime | 99.9% | - |
| Error rate | <1% | - |
| Cost per million requests | <$50 | - |
| Average latency | <500ms | - |

---

**Next**: Continue with alternative data sources documentation.