# 🕵️ Insider Trading Data Collection

**Priority**: HIGH  
**Complexity**: Medium  
**Timeline**: 3-4 days  
**Value**: Track what politicians and corporate insiders are buying/selling

## 🎯 Objective

Build a comprehensive insider trading tracker that monitors:
- Congressional trades (Senate & House)
- Corporate insider transactions
- Institutional movements (13F)
- Pattern detection for unusual activity

## 📊 Data Sources

### Primary Sources

#### 1. Quiver Quant API ($50/month)
```python
ENDPOINTS = {
    'congress_trading': '/beta/live/congresstrading',
    'senate': '/beta/historical/senatetrading',
    'house': '/beta/historical/housetrading',
    'insider': '/beta/live/insidertrading',
    'lobbying': '/beta/historical/lobbying'
}

# Example response
{
    "Representative": "Nancy Pelosi",
    "Transaction": "Purchase",
    "Ticker": "NVDA",
    "Range": "$1,000,001 - $5,000,000",
    "TransactionDate": "2024-01-15",
    "ReportDate": "2024-02-14"
}
```

#### 2. SEC EDGAR (Free)
```python
# Form 4 - Insider trading reports
SEC_FORMS = {
    'form_4': 'Statement of changes in beneficial ownership',
    'form_13f': 'Quarterly institutional holdings',
    'form_13d': '5%+ ownership stake',
    'form_13g': 'Passive investment >5%'
}
```

#### 3. Senate/House Disclosure Sites (Free)
```python
GOVERNMENT_SOURCES = {
    'senate': 'https://efdsearch.senate.gov/search/',
    'house': 'https://disclosures-clerk.house.gov/PublicDisclosure/FinancialDisclosure',
    'executive': 'https://www.oge.gov/web/oge.nsf/Public%20Financial%20Disclosure'
}
```

### Secondary Sources

#### OpenInsider (Web Scraping)
```python
# Notable insider trades with performance metrics
OPENINSIDER_FILTERS = {
    'min_value': 100000,
    'rating': ['Top Officers', 'Large Shareholders'],
    'trade_type': ['P-Purchase', 'S-Sale']
}
```

#### WhaleWisdom (13F Tracking)
```python
# Track institutional movements
WHALE_METRICS = {
    'new_positions': True,
    'increased_positions': True,
    'closed_positions': True,
    'min_value': 1000000
}
```

## 💾 Database Schema

```sql
-- Main insider transactions table
CREATE TABLE insider_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Trader info
    trader_name VARCHAR(255) NOT NULL,
    trader_title VARCHAR(255),
    trader_type VARCHAR(50), -- 'politician', 'executive', 'institutional'
    organization VARCHAR(255),
    
    -- Transaction details
    symbol VARCHAR(20) NOT NULL,
    transaction_type VARCHAR(20), -- 'buy', 'sell', 'option'
    shares INTEGER,
    price_range VARCHAR(100), -- For political disclosures
    estimated_value DECIMAL(15,2),
    
    -- Dates
    transaction_date DATE NOT NULL,
    filing_date DATE NOT NULL,
    
    -- Analysis fields
    days_before_earnings INTEGER,
    subsequent_return_7d DECIMAL(8,4),
    subsequent_return_30d DECIMAL(8,4),
    is_unusual BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    source VARCHAR(50),
    source_url TEXT,
    raw_data JSONB,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for fast queries
CREATE INDEX idx_insider_symbol ON insider_transactions(symbol);
CREATE INDEX idx_insider_trader ON insider_transactions(trader_name);
CREATE INDEX idx_insider_date ON insider_transactions(transaction_date DESC);
CREATE INDEX idx_insider_unusual ON insider_transactions(is_unusual) WHERE is_unusual = TRUE;

-- Trader profiles for tracking performance
CREATE TABLE insider_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(255) UNIQUE NOT NULL,
    trader_type VARCHAR(50),
    title VARCHAR(255),
    organization VARCHAR(255),
    
    -- Performance metrics
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    average_return DECIMAL(8,4),
    best_trade_return DECIMAL(8,4),
    
    -- Activity
    last_trade_date DATE,
    most_traded_stocks TEXT[],
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 🔄 Collection Pipeline

```python
# app/services/insider_collector.py

import asyncio
from typing import List, Dict
import aiohttp
from datetime import datetime, timedelta

class InsiderCollector:
    def __init__(self):
        self.quiver_api_key = settings.QUIVERQUANT_API_KEY
        self.sources = ['quiver', 'edgar', 'senate', 'house']
        
    async def collect_all(self):
        """Main collection orchestrator"""
        tasks = [
            self.collect_congress_trades(),
            self.collect_insider_trades(),
            self.collect_institutional(),
            self.collect_unusual_activity()
        ]
        
        results = await asyncio.gather(*tasks)
        await self.process_and_store(results)
        
    async def collect_congress_trades(self):
        """Fetch congressional trading data"""
        async with aiohttp.ClientSession() as session:
            headers = {'Authorization': f'Bearer {self.quiver_api_key}'}
            
            # Get recent trades
            async with session.get(
                'https://api.quiverquant.com/beta/live/congresstrading',
                headers=headers
            ) as response:
                data = await response.json()
                
        return self.normalize_congress_data(data)
    
    def detect_unusual_patterns(self, transactions: List[Dict]):
        """Identify suspicious trading patterns"""
        patterns = {
            'cluster_buying': self.detect_clusters(transactions),
            'pre_announcement': self.check_timing(transactions),
            'unusual_size': self.check_sizes(transactions),
            'first_time_buyer': self.check_history(transactions)
        }
        
        return patterns
    
    def calculate_performance(self, transaction: Dict):
        """Track how well the trade performed"""
        # Get price at transaction date
        # Get current price
        # Calculate returns for different periods
        pass
```

## 🚨 Pattern Detection

### Suspicious Patterns to Track

#### 1. Cluster Trading
```python
def detect_cluster_trading(transactions, window_days=7):
    """Multiple insiders buying same stock"""
    clusters = {}
    
    for symbol in unique_symbols:
        buyers = get_buyers_in_window(symbol, window_days)
        if len(buyers) >= 3:
            clusters[symbol] = {
                'buyers': buyers,
                'total_value': sum_values(buyers),
                'confidence': calculate_confidence(buyers)
            }
    
    return clusters
```

#### 2. Pre-Announcement Trading
```python
def check_pre_announcement_trading(transaction):
    """Trading before major news/earnings"""
    upcoming_events = get_upcoming_events(
        transaction['symbol'],
        transaction['transaction_date']
    )
    
    flags = []
    for event in upcoming_events:
        days_before = (event['date'] - transaction['date']).days
        if days_before <= 30:
            flags.append({
                'event': event['type'],
                'days_before': days_before,
                'suspicious': days_before <= 7
            })
    
    return flags
```

#### 3. Unusual Size Detection
```python
def detect_unusual_size(transaction, trader_profile):
    """Trades significantly larger than usual"""
    avg_trade_size = trader_profile['average_trade_size']
    current_size = transaction['estimated_value']
    
    if current_size > avg_trade_size * 3:
        return {
            'unusual': True,
            'factor': current_size / avg_trade_size,
            'confidence': 'high' if current_size > avg_trade_size * 5 else 'medium'
        }
```

## 📊 Alert System

### Alert Triggers

```python
ALERT_RULES = {
    'political_cluster': {
        'condition': 'multiple_politicians_same_stock',
        'threshold': 3,
        'window': '7_days',
        'severity': 'high'
    },
    'pre_earnings_trading': {
        'condition': 'trade_before_earnings',
        'threshold': '14_days',
        'severity': 'medium'
    },
    'unusual_option_activity': {
        'condition': 'large_option_purchase',
        'threshold': '$1_million',
        'severity': 'high'
    },
    'first_time_buyer': {
        'condition': 'never_bought_before',
        'severity': 'medium'
    }
}
```

### Alert Implementation
```python
async def check_alerts(transaction):
    alerts = []
    
    for rule_name, rule in ALERT_RULES.items():
        if evaluate_rule(transaction, rule):
            alerts.append({
                'type': rule_name,
                'severity': rule['severity'],
                'transaction': transaction,
                'message': generate_alert_message(rule_name, transaction)
            })
    
    if alerts:
        await send_alerts(alerts)
    
    return alerts
```

## 📈 Performance Tracking

### Success Metrics
```python
def track_insider_performance(trader_name: str, lookback_days: int = 90):
    """Track how well insider's trades performed"""
    
    trades = get_trader_history(trader_name, lookback_days)
    
    metrics = {
        'total_trades': len(trades),
        'winning_trades': count_winning_trades(trades),
        'average_return': calculate_average_return(trades),
        'best_trade': get_best_trade(trades),
        'worst_trade': get_worst_trade(trades),
        'win_rate': calculate_win_rate(trades),
        'avg_holding_period': calculate_avg_holding(trades)
    }
    
    return metrics
```

### Leaderboard
```python
def generate_insider_leaderboard():
    """Rank insiders by performance"""
    
    insiders = get_all_active_insiders()
    
    rankings = []
    for insider in insiders:
        performance = track_insider_performance(insider['name'])
        rankings.append({
            'name': insider['name'],
            'title': insider['title'],
            'win_rate': performance['win_rate'],
            'avg_return': performance['average_return'],
            'total_trades': performance['total_trades']
        })
    
    return sorted(rankings, key=lambda x: x['avg_return'], reverse=True)
```

## 🎨 UI Components

### Dashboard Widget
```typescript
// InsiderActivityWidget.tsx
interface InsiderActivity {
  trader: string;
  position: string;
  symbol: string;
  action: 'buy' | 'sell';
  value: number;
  date: Date;
  pattern?: 'cluster' | 'unusual' | 'pre-news';
}

const InsiderActivityWidget = () => {
  return (
    <Card>
      <CardHeader>
        <Title>🕵️ Latest Insider Activity</Title>
        <Badge>{alertCount} Unusual Patterns Detected</Badge>
      </CardHeader>
      <CardBody>
        <ActivityFeed activities={latestActivities} />
        <PatternAlerts patterns={detectedPatterns} />
        <TopTraders traders={topPerformers} />
      </CardBody>
    </Card>
  );
};
```

## ⚙️ Configuration

```yaml
# config/insider_tracking.yaml

sources:
  quiver_quant:
    enabled: true
    api_key: ${QUIVERQUANT_API_KEY}
    rate_limit: 100/hour
    
  sec_edgar:
    enabled: true
    rate_limit: 10/second
    
  congress:
    senate: true
    house: true
    check_interval: 3600  # seconds

alerts:
  cluster_threshold: 3
  timing_window: 14  # days before event
  min_trade_value: 100000
  
  channels:
    - email
    - slack
    - dashboard

performance:
  track_returns: [1, 7, 30, 90]  # days
  min_history: 30  # days
  confidence_threshold: 0.7
```

## 🚀 Implementation Steps

### Week 1
1. ✅ Set up Quiver Quant API
2. ✅ Create database tables
3. ✅ Build basic collector
4. ✅ Test data ingestion

### Week 2
1. ⬜ Add SEC EDGAR integration
2. ⬜ Implement pattern detection
3. ⬜ Create alert system
4. ⬜ Build performance tracking

### Week 3
1. ⬜ Add UI components
2. ⬜ Create leaderboard
3. ⬜ Implement backtesting
4. ⬜ Launch beta version

## 📊 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Daily trades collected | 100+ | 0 |
| Pattern detection accuracy | 70% | - |
| Alert relevance | 80% | - |
| Performance tracking | 90 days | - |

---

**Next**: Implement [government-spending.md](government-spending.md) for contract tracking.