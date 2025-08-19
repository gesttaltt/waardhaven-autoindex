# 🏗️ Historical Reconstruction Engine

**Priority**: HIGH  
**Complexity**: Very High  
**Timeline**: 4-5 days  
**Value**: Accurate recreation of past market conditions

## 🎯 Objective

Build a sophisticated engine that can accurately reconstruct:
- Complete market state at any historical date
- Information availability as it was known then
- Decision context without hindsight bias
- Data quality and completeness metrics
- Timeline of information flow

## 🧠 Reconstruction Principles

### Core Rules
```python
RECONSTRUCTION_RULES = {
    'information_availability': {
        'market_data': 'Available with exchange delays (0-20 minutes)',
        'earnings': 'Available only after official release time',
        'insider_trades': 'Available only after SEC filing (T+2 to T+10)',
        'news': 'Available after publication timestamp',
        '13f_filings': 'Available 45 days after quarter end',
        'analyst_reports': 'Available after distribution to clients'
    },
    'data_revisions': {
        'earnings_restatements': 'Use original reported numbers',
        'splits_adjustments': 'Apply only known splits at time',
        'index_changes': 'Use index composition as of date',
        'delisted_stocks': 'Include if trading at time'
    },
    'survivorship_bias': {
        'universe': 'Include all stocks trading at time',
        'bankruptcies': 'Include stocks that later failed',
        'mergers': 'Include targets before announcement'
    }
}
```

## 💾 Reconstruction Database

```sql
-- Historical universe snapshots
CREATE TABLE historical_universe (
    snapshot_date DATE NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    
    -- Company info as of date
    company_name VARCHAR(255),
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap DECIMAL(20,2),
    
    -- Index memberships as of date
    sp500_member BOOLEAN,
    nasdaq100_member BOOLEAN,
    russell2000_member BOOLEAN,
    
    -- Trading status
    is_actively_trading BOOLEAN,
    exchange VARCHAR(10),
    shares_outstanding BIGINT,
    
    -- Future events (for validation)
    delisted_date DATE,
    merger_date DATE,
    bankruptcy_date DATE,
    
    PRIMARY KEY (snapshot_date, symbol)
);

-- Information availability tracking
CREATE TABLE information_timeline (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    symbol VARCHAR(20) NOT NULL,
    information_type VARCHAR(100), -- earnings, insider_trade, news, etc.
    
    -- Event timing
    event_date TIMESTAMP, -- When event actually occurred
    known_date TIMESTAMP, -- When it became public knowledge
    filing_date TIMESTAMP, -- When it was officially filed
    
    -- Content
    information_content JSONB,
    source VARCHAR(100),
    
    -- Impact
    market_moving BOOLEAN,
    price_impact_24h DECIMAL(8,4),
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Reconstructed market states
CREATE TABLE reconstructed_states (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    reconstruction_date DATE NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    
    -- Market data as known then
    last_price DECIMAL(10,2),
    last_price_timestamp TIMESTAMP,
    volume_20d_avg BIGINT,
    volatility_30d DECIMAL(8,4),
    
    -- Fundamental data as known then
    last_earnings_date DATE,
    last_eps DECIMAL(8,2),
    next_earnings_date DATE,
    pe_ratio DECIMAL(8,2),
    
    -- Sentiment as known then
    news_sentiment_7d DECIMAL(5,4),
    analyst_rating DECIMAL(3,1),
    price_target_avg DECIMAL(10,2),
    
    -- Insider activity as known then
    insider_trades_30d INTEGER,
    insider_net_value_30d DECIMAL(15,2),
    congress_trades_90d INTEGER,
    
    -- Technical indicators as calculable then
    rsi_14 DECIMAL(5,2),
    macd_signal DECIMAL(8,4),
    sma_50 DECIMAL(10,2),
    sma_200 DECIMAL(10,2),
    
    -- Data quality metrics
    completeness_score DECIMAL(3,2),
    staleness_score DECIMAL(3,2),
    reliability_score DECIMAL(3,2),
    
    -- Reconstruction metadata
    reconstruction_timestamp TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(reconstruction_date, symbol)
);
```

## 🔧 Reconstruction Engine

```python
# app/time_machine/reconstruction_engine.py

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

class HistoricalReconstructionEngine:
    """Accurately reconstruct historical market states"""
    
    def __init__(self):
        self.data_sources = self.initialize_data_sources()
        self.availability_rules = self.load_availability_rules()
        self.universe_tracker = UniverseTracker()
        
    async def reconstruct_market_state(self, target_date: datetime, symbols: List[str] = None) -> Dict:
        """Reconstruct complete market state as of target date"""
        
        print(f"Reconstructing market state for {target_date.date()}")
        
        # Get trading universe as of that date
        if symbols is None:
            symbols = await self.universe_tracker.get_universe_at_date(target_date)
        
        # Reconstruct state for each symbol
        reconstruction_tasks = [
            self.reconstruct_symbol_state(target_date, symbol)
            for symbol in symbols
        ]
        
        symbol_states = await asyncio.gather(*reconstruction_tasks, return_exceptions=True)
        
        # Combine into market state
        market_state = {
            'reconstruction_date': target_date,
            'universe_size': len(symbols),
            'symbols': {},
            'market_metrics': await self.calculate_market_metrics(target_date, symbol_states),
            'data_quality': self.assess_data_quality(symbol_states)
        }
        
        # Add successful reconstructions
        for symbol, state in zip(symbols, symbol_states):
            if not isinstance(state, Exception):
                market_state['symbols'][symbol] = state
        
        return market_state
    
    async def reconstruct_symbol_state(self, target_date: datetime, symbol: str) -> Dict:
        """Reconstruct complete state for single symbol"""
        
        # Collect all data types in parallel
        tasks = {
            'market_data': self.get_market_data_as_of(target_date, symbol),
            'fundamental_data': self.get_fundamental_data_as_of(target_date, symbol),
            'news_sentiment': self.get_news_sentiment_as_of(target_date, symbol),
            'insider_activity': self.get_insider_activity_as_of(target_date, symbol),
            'analyst_coverage': self.get_analyst_coverage_as_of(target_date, symbol),
            'social_sentiment': self.get_social_sentiment_as_of(target_date, symbol),
            'technical_indicators': self.calculate_technical_indicators_as_of(target_date, symbol)
        }
        
        results = await asyncio.gather(
            *tasks.values(),
            return_exceptions=True
        )
        
        # Combine results
        state = {}
        for key, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                state[key] = {'error': str(result), 'available': False}
            else:
                state[key] = result
        
        # Add metadata
        state['symbol'] = symbol
        state['reconstruction_date'] = target_date
        state['completeness'] = self.calculate_completeness(state)
        state['information_edge'] = await self.calculate_information_edge(target_date, symbol)
        
        return state
    
    async def get_market_data_as_of(self, target_date: datetime, symbol: str) -> Dict:
        """Get market data available as of target date"""
        
        # Account for market delays
        if target_date.time() < datetime.strptime('16:00', '%H:%M').time():
            # During trading hours, use delayed data
            cutoff_time = target_date - timedelta(minutes=20)
        else:
            # After hours, use end-of-day data
            cutoff_time = target_date.replace(hour=16, minute=0)
        
        query = """
            SELECT 
                time,
                open, high, low, close, volume,
                vwap, market_cap
            FROM market_data_ts
            WHERE symbol = $1 
                AND time <= $2
            ORDER BY time DESC
            LIMIT 1;
        """
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, symbol, cutoff_time)
        
        if not row:
            return {'available': False}
        
        # Calculate additional metrics using only available data
        price_history = await self.get_price_history_before(cutoff_time, symbol, days=252)
        
        return {
            'available': True,
            'as_of_time': row['time'],
            'price': float(row['close']),
            'volume': int(row['volume']),
            'market_cap': float(row['market_cap']) if row['market_cap'] else None,
            'volatility_30d': self.calculate_volatility(price_history, 30),
            'returns_ytd': self.calculate_ytd_return(price_history, target_date),
            'volume_avg_20d': self.calculate_avg_volume(price_history, 20),
            'price_trend_30d': self.calculate_trend(price_history, 30)
        }
    
    async def get_insider_activity_as_of(self, target_date: datetime, symbol: str) -> Dict:
        """Get insider activity known as of target date"""
        
        # Use filing_date for availability, not transaction_date
        query = """
            SELECT 
                transaction_date,
                filing_date,
                insider_name,
                transaction_type,
                shares,
                value,
                is_cluster_trade
            FROM insider_trades_ts
            WHERE symbol = $1 
                AND filing_date <= $2
                AND filing_date >= $3  -- Last 90 days
            ORDER BY filing_date DESC;
        """
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                query, 
                symbol, 
                target_date, 
                target_date - timedelta(days=90)
            )
        
        if not rows:
            return {'available': False, 'trades': []}
        
        trades = [dict(row) for row in rows]
        
        # Analyze patterns
        analysis = {
            'available': True,
            'trades': trades,
            'total_trades': len(trades),
            'buy_trades': len([t for t in trades if t['transaction_type'] == 'buy']),
            'sell_trades': len([t for t in trades if t['transaction_type'] == 'sell']),
            'net_value': sum(t['value'] if t['transaction_type'] == 'buy' else -t['value'] for t in trades),
            'cluster_trades': len([t for t in trades if t['is_cluster_trade']]),
            'unique_insiders': len(set(t['insider_name'] for t in trades)),
            'sentiment': self.calculate_insider_sentiment(trades)
        }
        
        return analysis
    
    async def get_news_sentiment_as_of(self, target_date: datetime, symbol: str) -> Dict:
        """Get news sentiment available as of target date"""
        
        query = """
            SELECT 
                time,
                title,
                sentiment,
                impact_score,
                source
            FROM news_events_ts
            WHERE symbol = $1 
                AND time <= $2
                AND time >= $3  -- Last 30 days
            ORDER BY time DESC, impact_score DESC
            LIMIT 100;
        """
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                query, 
                symbol, 
                target_date, 
                target_date - timedelta(days=30)
            )
        
        if not rows:
            return {'available': False, 'articles': []}
        
        articles = [dict(row) for row in rows]
        
        # Calculate aggregated sentiment
        sentiments = [a['sentiment'] for a in articles if a['sentiment'] is not None]
        impact_scores = [a['impact_score'] for a in articles if a['impact_score'] is not None]
        
        return {
            'available': True,
            'articles': articles[:10],  # Top 10 by impact
            'total_articles': len(articles),
            'avg_sentiment': np.mean(sentiments) if sentiments else 0,
            'sentiment_std': np.std(sentiments) if sentiments else 0,
            'avg_impact': np.mean(impact_scores) if impact_scores else 0,
            'recent_trend': self.calculate_sentiment_trend(articles)
        }
```

## 📊 Information Edge Analysis

```python
class InformationEdgeCalculator:
    """Calculate information advantages at specific points in time"""
    
    async def calculate_information_edge(self, target_date: datetime, symbol: str) -> Dict:
        """Calculate how much 'edge' information was available"""
        
        # Get information timeline
        timeline = await self.get_information_timeline(target_date, symbol)
        
        edge_factors = {
            'insider_edge': self.calculate_insider_edge(timeline),
            'earnings_edge': self.calculate_earnings_edge(timeline, target_date),
            'news_edge': self.calculate_news_edge(timeline),
            'technical_edge': self.calculate_technical_edge(timeline),
            'social_edge': self.calculate_social_edge(timeline)
        }
        
        # Combine into overall edge score
        overall_edge = self.combine_edge_factors(edge_factors)
        
        return {
            'overall_edge': overall_edge,
            'edge_factors': edge_factors,
            'information_timeline': timeline[:10],  # Most recent 10 events
            'edge_interpretation': self.interpret_edge_score(overall_edge)
        }
    
    def calculate_insider_edge(self, timeline: List[Dict]) -> float:
        """Calculate edge from insider activity"""
        
        insider_events = [e for e in timeline if e['type'] == 'insider_trade']
        
        if not insider_events:
            return 0.0
        
        # Weight by recency and size
        edge_score = 0.0
        for event in insider_events[:5]:  # Top 5 recent
            days_ago = (datetime.now() - event['date']).days
            recency_weight = max(0, 1 - days_ago / 30)  # Decay over 30 days
            size_weight = min(event['value'] / 1_000_000, 1.0)  # Cap at $1M
            
            if event['transaction_type'] == 'buy':
                edge_score += recency_weight * size_weight * 0.3
            else:
                edge_score -= recency_weight * size_weight * 0.2
        
        return max(-1.0, min(1.0, edge_score))
    
    def calculate_earnings_edge(self, timeline: List[Dict], target_date: datetime) -> float:
        """Calculate edge from earnings proximity"""
        
        # Find next earnings date
        next_earnings = self.find_next_earnings_date(target_date, timeline)
        
        if not next_earnings:
            return 0.0
        
        days_to_earnings = (next_earnings - target_date).days
        
        # Higher edge closer to earnings
        if days_to_earnings <= 0:
            return 0.0  # After earnings, no edge
        elif days_to_earnings <= 7:
            return 0.8  # High edge within a week
        elif days_to_earnings <= 30:
            return 0.4  # Medium edge within a month
        else:
            return 0.1  # Low edge beyond a month
```

## 🔍 Data Quality Assessment

```python
class DataQualityAssessor:
    """Assess quality and completeness of reconstructed data"""
    
    def assess_reconstruction_quality(self, reconstructed_state: Dict) -> Dict:
        """Comprehensive quality assessment"""
        
        quality_metrics = {
            'completeness': self.calculate_completeness_score(reconstructed_state),
            'timeliness': self.calculate_timeliness_score(reconstructed_state),
            'accuracy': self.calculate_accuracy_score(reconstructed_state),
            'consistency': self.calculate_consistency_score(reconstructed_state)
        }
        
        # Overall quality score
        weights = {'completeness': 0.3, 'timeliness': 0.3, 'accuracy': 0.25, 'consistency': 0.15}
        overall_score = sum(quality_metrics[k] * weights[k] for k in weights)
        
        return {
            'overall_quality': overall_score,
            'metrics': quality_metrics,
            'recommendations': self.generate_quality_recommendations(quality_metrics),
            'confidence_level': self.calculate_confidence_level(overall_score)
        }
    
    def calculate_completeness_score(self, state: Dict) -> float:
        """Calculate data completeness score"""
        
        required_fields = [
            'market_data', 'fundamental_data', 'news_sentiment',
            'insider_activity', 'technical_indicators'
        ]
        
        available_count = 0
        total_fields = 0
        
        for field in required_fields:
            if field in state and state[field].get('available', False):
                # Count sub-fields
                sub_fields = self.get_expected_subfields(field)
                available_sub = sum(1 for sf in sub_fields if sf in state[field])
                available_count += available_sub
                total_fields += len(sub_fields)
            else:
                total_fields += len(self.get_expected_subfields(field))
        
        return available_count / total_fields if total_fields > 0 else 0.0
    
    def identify_data_gaps(self, state: Dict) -> List[Dict]:
        """Identify specific data gaps and their impact"""
        
        gaps = []
        
        # Check for missing critical data
        if not state.get('market_data', {}).get('available', False):
            gaps.append({
                'type': 'critical',
                'description': 'Market data not available',
                'impact': 'Cannot perform basic analysis',
                'recommendation': 'Check data source connectivity'
            })
        
        if not state.get('insider_activity', {}).get('available', False):
            gaps.append({
                'type': 'important',
                'description': 'No insider trading data',
                'impact': 'Missing key sentiment indicator',
                'recommendation': 'Increase SEC filing monitoring'
            })
        
        # Check data staleness
        market_data = state.get('market_data', {})
        if market_data.get('available') and 'as_of_time' in market_data:
            staleness = (datetime.now() - market_data['as_of_time']).total_seconds() / 3600
            if staleness > 24:
                gaps.append({
                    'type': 'warning',
                    'description': f'Market data is {staleness:.1f} hours old',
                    'impact': 'Analysis may not reflect current conditions',
                    'recommendation': 'Update data feeds'
                })
        
        return gaps
```

## 🎨 Visualization Components

```typescript
// HistoricalReconstructionDashboard.tsx

const HistoricalReconstructionDashboard = () => {
  return (
    <div className="historical-reconstruction">
      {/* Date Selection */}
      <Card>
        <CardHeader>
          <Title>📅 Historical Date Selection</Title>
        </CardHeader>
        <CardBody>
          <DatePicker 
            value={selectedDate}
            onChange={setSelectedDate}
            maxDate={new Date()}
            highlightedDates={significantMarketDates}
          />
          <ReconstructionProgress loading={isReconstruting} />
        </CardBody>
      </Card>
      
      {/* Market State Summary */}
      <Card>
        <CardHeader>
          <Title>📊 Market State as of {selectedDate}</Title>
        </CardHeader>
        <CardBody>
          <MarketStateSummary 
            state={reconstructedState}
            showDataQuality={true}
          />
          <DataCompletenessIndicator 
            completeness={dataQuality.completeness}
          />
        </CardBody>
      </Card>
      
      {/* Information Timeline */}
      <Card>
        <CardHeader>
          <Title>⏱️ Information Timeline</Title>
        </CardHeader>
        <CardBody>
          <InformationTimeline 
            events={informationEvents}
            highlightDate={selectedDate}
          />
        </CardBody>
      </Card>
      
      {/* Data Quality Assessment */}
      <Card>
        <CardHeader>
          <Title>🔍 Data Quality Assessment</Title>
        </CardHeader>
        <CardBody>
          <QualityMetrics metrics={dataQuality} />
          <DataGapsAlert gaps={dataGaps} />
        </CardBody>
      </Card>
      
      {/* Information Edge Analysis */}
      <Card>
        <CardHeader>
          <Title>🎯 Information Edge</Title>
        </CardHeader>
        <CardBody>
          <EdgeFactorsChart factors={informationEdge.factors} />
          <EdgeInterpretation score={informationEdge.overall} />
        </CardBody>
      </Card>
    </div>
  );
};
```

## 📊 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Reconstruction accuracy | >99% | - |
| Data completeness | >95% | - |
| Reconstruction time | <30s | - |
| Historical coverage | 10 years | - |
| Information edge accuracy | >80% | - |

---

**Next**: Continue with point-in-time query engine.