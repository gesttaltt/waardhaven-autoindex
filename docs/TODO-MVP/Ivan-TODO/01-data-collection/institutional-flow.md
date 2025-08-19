# 🐋 Institutional Flow & Whale Tracking

**Priority**: HIGH  
**Complexity**: High  
**Timeline**: 3-4 days  
**Value**: Track smart money movements and follow the whales

## 🎯 Objective

Monitor institutional investor activity to:
- Track 13F filings from hedge funds
- Monitor dark pool transactions
- Analyze options flow for unusual activity
- Follow whale wallet movements
- Detect accumulation/distribution patterns

## 📊 Data Sources

### 13F Filings
```python
FORM_13F_SOURCES = {
    'sec_edgar': {
        'url': 'https://www.sec.gov/edgar',
        'frequency': 'Quarterly (45 days after quarter end)',
        'data': 'Holdings >$100M AUM'
    },
    'whalewisdom': {
        'url': 'https://whalewisdom.com',
        'api': 'Available',
        'features': ['Historical tracking', 'Performance metrics']
    },
    'dataroma': {
        'url': 'https://www.dataroma.com',
        'coverage': 'Superinvestor portfolios',
        'free': True
    },
    'gurufocus': {
        'url': 'https://www.gurufocus.com',
        'features': ['Guru trades', 'Real-time alerts']
    }
}
```

### Dark Pool Data
```python
DARK_POOL_SOURCES = {
    'finra_adf': {
        'description': 'Alternative Display Facility',
        'delay': 'T+2 reporting',
        'free': True
    },
    'squeezemetrics': {
        'product': 'DIX (Dark Pool Index)',
        'cost': '$150/month',
        'signals': 'Dark pool positioning'
    },
    'unusualwhales': {
        'features': ['Flow data', 'Dark pool prints'],
        'cost': '$20-50/month'
    }
}
```

### Options Flow
```python
OPTIONS_FLOW_SOURCES = {
    'opra': {
        'description': 'Options Price Reporting Authority',
        'real_time': True,
        'cost': 'Professional fees'
    },
    'cboe': {
        'products': ['Options volume', 'Put/Call ratios'],
        'free_delay': '15 minutes'
    },
    'flowalgo': {
        'features': ['Smart money flow', 'Unusual activity'],
        'cost': '$37/month'
    },
    'optionmetrics': {
        'data': 'Institutional grade',
        'cost': 'Enterprise pricing'
    }
}
```

## 💾 Database Schema

```sql
-- 13F Holdings
CREATE TABLE institutional_holdings_13f (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Filing info
    cik VARCHAR(20) NOT NULL,
    filer_name VARCHAR(255) NOT NULL,
    report_period DATE NOT NULL,
    filing_date DATE NOT NULL,
    
    -- Holdings
    symbol VARCHAR(20) NOT NULL,
    company_name VARCHAR(255),
    shares BIGINT NOT NULL,
    market_value DECIMAL(20,2),
    
    -- Changes from previous quarter
    shares_change BIGINT,
    shares_change_pct DECIMAL(8,4),
    
    -- Position details
    pct_of_portfolio DECIMAL(8,4),
    pct_of_shares_outstanding DECIMAL(8,4),
    
    -- Metadata
    is_new_position BOOLEAN DEFAULT FALSE,
    is_closed_position BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(cik, symbol, report_period)
);

-- Dark Pool Transactions
CREATE TABLE dark_pool_trades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    symbol VARCHAR(20) NOT NULL,
    
    -- Trade details
    trade_date DATE NOT NULL,
    trade_time TIME,
    
    -- Volume and price
    shares BIGINT NOT NULL,
    price DECIMAL(10,2),
    total_value DECIMAL(20,2),
    
    -- Dark pool specifics
    dark_pool_venue VARCHAR(100),
    dix_value DECIMAL(5,4), -- Dark pool index
    
    -- Analysis
    is_block_trade BOOLEAN DEFAULT FALSE,
    pct_of_daily_volume DECIMAL(8,4),
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Options Flow
CREATE TABLE options_flow (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    symbol VARCHAR(20) NOT NULL,
    
    -- Option details
    strike_price DECIMAL(10,2) NOT NULL,
    expiration_date DATE NOT NULL,
    option_type VARCHAR(4) NOT NULL, -- CALL/PUT
    
    -- Trade info
    trade_date DATE NOT NULL,
    trade_time TIME,
    
    -- Volume and premium
    contracts INTEGER NOT NULL,
    premium_per_contract DECIMAL(10,2),
    total_premium DECIMAL(20,2),
    
    -- Greeks
    delta DECIMAL(5,4),
    gamma DECIMAL(5,4),
    theta DECIMAL(5,4),
    vega DECIMAL(5,4),
    
    -- Flow analysis
    is_sweep BOOLEAN DEFAULT FALSE,
    is_block BOOLEAN DEFAULT FALSE,
    is_unusual BOOLEAN DEFAULT FALSE,
    
    -- Sentiment
    sentiment VARCHAR(20), -- bullish/bearish/neutral
    aggressiveness_score DECIMAL(3,2),
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Whale Wallets (for tracking large holders)
CREATE TABLE whale_wallets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Wallet identification
    wallet_identifier VARCHAR(255) UNIQUE,
    wallet_type VARCHAR(50), -- hedge_fund, family_office, pension, etc
    estimated_aum DECIMAL(20,2),
    
    -- Tracking
    first_seen DATE,
    last_activity DATE,
    
    -- Performance
    total_trades INTEGER DEFAULT 0,
    win_rate DECIMAL(5,2),
    avg_return DECIMAL(8,4),
    
    -- Holdings summary
    current_holdings JSONB,
    top_positions TEXT[],
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Accumulation/Distribution Patterns
CREATE TABLE accumulation_distribution (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    symbol VARCHAR(20) NOT NULL,
    detection_date DATE NOT NULL,
    
    -- Pattern details
    pattern_type VARCHAR(50), -- accumulation/distribution
    confidence DECIMAL(3,2),
    
    -- Metrics
    institutional_ownership_change DECIMAL(8,4),
    smart_money_flow DECIMAL(20,2),
    
    -- Supporting indicators
    obv_trend VARCHAR(20), -- On-Balance Volume
    money_flow_index DECIMAL(5,2),
    accumulation_line_slope DECIMAL(8,4),
    
    -- Entities involved
    major_buyers TEXT[],
    major_sellers TEXT[],
    
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🔄 Collection Pipeline

```python
# app/services/institutional_flow_collector.py

import asyncio
from typing import List, Dict
from datetime import datetime, timedelta
import pandas as pd

class InstitutionalFlowCollector:
    def __init__(self):
        self.sec_client = SECEdgarClient()
        self.options_client = OptionsFlowClient()
        self.darkpool_client = DarkPoolClient()
        
    async def collect_13f_filings(self):
        """Collect latest 13F filings"""
        
        # Get recent filings
        filings = await self.sec_client.get_recent_13f()
        
        processed = []
        for filing in filings:
            # Parse holding data
            holdings = self.parse_13f_holdings(filing)
            
            # Compare with previous quarter
            changes = await self.calculate_position_changes(
                filing['cik'],
                holdings
            )
            
            # Identify significant moves
            significant = self.identify_significant_positions(changes)
            
            processed.append({
                'filer': filing['filer_name'],
                'cik': filing['cik'],
                'holdings': holdings,
                'changes': changes,
                'significant_moves': significant
            })
            
        return processed
    
    def identify_significant_positions(self, changes: Dict) -> List[Dict]:
        """Identify significant position changes"""
        
        significant = []
        
        for symbol, change in changes.items():
            # New large position
            if change['is_new'] and change['value'] > 10_000_000:
                significant.append({
                    'type': 'new_position',
                    'symbol': symbol,
                    'value': change['value'],
                    'signal': 'bullish'
                })
                
            # Large increase
            elif change['pct_change'] > 50 and change['value'] > 5_000_000:
                significant.append({
                    'type': 'increased_position',
                    'symbol': symbol,
                    'increase': change['pct_change'],
                    'signal': 'bullish'
                })
                
            # Complete exit
            elif change['is_closed']:
                significant.append({
                    'type': 'closed_position',
                    'symbol': symbol,
                    'signal': 'bearish'
                })
                
        return significant
    
    async def track_dark_pools(self, symbol: str):
        """Track dark pool activity for a symbol"""
        
        # Get dark pool data
        dark_pool_data = await self.darkpool_client.get_activity(symbol)
        
        # Calculate DIX (Dark Pool Index)
        dix = self.calculate_dix(dark_pool_data)
        
        # Detect large blocks
        large_blocks = self.detect_block_trades(dark_pool_data)
        
        # Analyze positioning
        positioning = self.analyze_dark_pool_positioning(
            symbol,
            dark_pool_data,
            dix
        )
        
        return {
            'symbol': symbol,
            'dix': dix,
            'large_blocks': large_blocks,
            'positioning': positioning,
            'signal': self.interpret_dark_pool_signal(dix, large_blocks)
        }
    
    async def analyze_options_flow(self, symbol: str):
        """Analyze options flow for unusual activity"""
        
        # Get options flow data
        flow_data = await self.options_client.get_flow(symbol)
        
        # Identify unusual activity
        unusual = self.detect_unusual_options(flow_data)
        
        # Calculate put/call ratio
        pc_ratio = self.calculate_put_call_ratio(flow_data)
        
        # Identify sweeps
        sweeps = self.detect_option_sweeps(flow_data)
        
        # Smart money analysis
        smart_money = self.analyze_smart_money_options(flow_data)
        
        return {
            'symbol': symbol,
            'unusual_activity': unusual,
            'put_call_ratio': pc_ratio,
            'sweeps': sweeps,
            'smart_money': smart_money,
            'signal': self.interpret_options_signal(unusual, pc_ratio, sweeps)
        }
```

## 🚨 Smart Money Detection

```python
class SmartMoneyDetector:
    """Detect and follow smart money movements"""
    
    def detect_smart_money_accumulation(self, symbol: str) -> Dict:
        """Detect institutional accumulation patterns"""
        
        signals = {
            'is_accumulating': False,
            'confidence': 0,
            'indicators': []
        }
        
        # Check 13F increases
        institutional_changes = self.get_institutional_changes(symbol)
        if institutional_changes['net_buyers'] > institutional_changes['net_sellers']:
            signals['indicators'].append('institutional_buying')
            signals['confidence'] += 0.3
            
        # Check dark pool positioning
        dark_pool_dix = self.get_dark_pool_dix(symbol)
        if dark_pool_dix > 0.45:  # Above 45% is bullish
            signals['indicators'].append('dark_pool_accumulation')
            signals['confidence'] += 0.25
            
        # Check options flow
        options_sentiment = self.get_options_sentiment(symbol)
        if options_sentiment['smart_money_bullish']:
            signals['indicators'].append('bullish_options_flow')
            signals['confidence'] += 0.25
            
        # Check price/volume relationship
        if self.check_accumulation_pattern(symbol):
            signals['indicators'].append('accumulation_pattern')
            signals['confidence'] += 0.2
            
        # Determine if accumulating
        if signals['confidence'] >= 0.6:
            signals['is_accumulating'] = True
            
        return signals
    
    def identify_whale_trades(self, min_value: float = 1_000_000):
        """Identify large institutional trades"""
        
        whale_trades = []
        
        # Check 13F for large new positions
        new_positions = self.get_new_13f_positions(min_value)
        whale_trades.extend(new_positions)
        
        # Check dark pool blocks
        dark_blocks = self.get_dark_pool_blocks(min_value)
        whale_trades.extend(dark_blocks)
        
        # Check options blocks
        option_blocks = self.get_option_blocks(min_value)
        whale_trades.extend(option_blocks)
        
        return sorted(whale_trades, key=lambda x: x['value'], reverse=True)
```

## 📊 Flow Analysis

```python
class FlowAnalyzer:
    """Analyze institutional flow patterns"""
    
    def calculate_smart_money_flow(self, symbol: str, days: int = 20) -> float:
        """Calculate Smart Money Flow Index"""
        
        # Get intraday data
        intraday_data = self.get_intraday_data(symbol, days)
        
        smf_values = []
        for day_data in intraday_data:
            # First 30 minutes = retail trading
            retail_volume = day_data['volume_first_30min']
            retail_price = day_data['vwap_first_30min']
            
            # Rest of day = institutional trading
            inst_volume = day_data['volume_rest_of_day']
            inst_price = day_data['vwap_rest_of_day']
            
            # Calculate daily SMF
            daily_smf = (inst_price * inst_volume) - (retail_price * retail_volume)
            smf_values.append(daily_smf)
            
        # Return average SMF
        return np.mean(smf_values)
    
    def detect_accumulation_distribution(self, symbol: str) -> str:
        """Detect if stock is under accumulation or distribution"""
        
        # Get price and volume data
        data = self.get_price_volume_data(symbol, days=30)
        
        # Calculate Accumulation/Distribution Line
        ad_line = []
        for i, row in data.iterrows():
            mfm = ((row['close'] - row['low']) - (row['high'] - row['close'])) / (row['high'] - row['low'])
            mfv = mfm * row['volume']
            
            if i == 0:
                ad_line.append(mfv)
            else:
                ad_line.append(ad_line[-1] + mfv)
                
        # Check trend
        ad_slope = np.polyfit(range(len(ad_line)), ad_line, 1)[0]
        
        if ad_slope > 0 and data['close'].iloc[-1] > data['close'].iloc[0]:
            return 'accumulation'
        elif ad_slope < 0 and data['close'].iloc[-1] < data['close'].iloc[0]:
            return 'distribution'
        else:
            return 'neutral'
```

## 🎨 UI Components

```typescript
// InstitutionalFlowDashboard.tsx

const InstitutionalFlowDashboard = () => {
  return (
    <div className="institutional-flow">
      {/* 13F Tracker */}
      <Card>
        <CardHeader>
          <Title>🏦 Latest 13F Filings</Title>
          <Badge>Q4 2024</Badge>
        </CardHeader>
        <CardBody>
          <Table>
            <thead>
              <tr>
                <th>Institution</th>
                <th>Stock</th>
                <th>Action</th>
                <th>Shares</th>
                <th>Value</th>
              </tr>
            </thead>
            <tbody>
              {filings.map(filing => (
                <FilingRow key={filing.id} filing={filing} />
              ))}
            </tbody>
          </Table>
        </CardBody>
      </Card>
      
      {/* Dark Pool Activity */}
      <Card>
        <CardHeader>
          <Title>🌑 Dark Pool Activity</Title>
        </CardHeader>
        <CardBody>
          <DIXChart data={dixData} />
          <BlockTradesList trades={blockTrades} />
        </CardBody>
      </Card>
      
      {/* Options Flow */}
      <Card>
        <CardHeader>
          <Title>📊 Unusual Options Activity</Title>
        </CardHeader>
        <CardBody>
          <OptionsFlowTable flows={unusualOptions} />
          <PutCallRatioChart data={pcRatio} />
        </CardBody>
      </Card>
      
      {/* Smart Money Signals */}
      <Card>
        <SmartMoneySignals signals={smartMoneySignals} />
      </Card>
    </div>
  );
};
```

## 📊 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| 13F filings tracked | 500+ funds | 0 |
| Dark pool coverage | 40+ venues | 0 |
| Options flow accuracy | 85% | - |
| Whale detection | <1 hour | - |
| Smart money signals | 70% accuracy | - |

---

**Next**: Continue with more infrastructure documentation.