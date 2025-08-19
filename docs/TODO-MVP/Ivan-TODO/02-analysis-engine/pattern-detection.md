# 🔍 Pattern Detection Engine

**Priority**: CRITICAL  
**Complexity**: Very High  
**Timeline**: 5-7 days  
**Value**: Identify market-moving patterns before they become obvious

## 🎯 Objective

Build a comprehensive pattern detection system that identifies:
- Insider trading clusters
- Accumulation/distribution patterns  
- Pump & dump schemes
- Government contract winners
- Social momentum shifts
- Technical breakouts
- Unusual market behavior

## 📊 Pattern Categories

### 1. Insider Trading Patterns
```python
INSIDER_PATTERNS = {
    'cluster_buying': {
        'description': 'Multiple insiders buying within short timeframe',
        'threshold': '3+ insiders in 7 days',
        'historical_accuracy': 0.72,
        'avg_return_30d': 0.08
    },
    'pre_earnings_accumulation': {
        'description': 'Insider buying before earnings',
        'threshold': '30 days before earnings',
        'historical_accuracy': 0.68,
        'avg_return_30d': 0.06
    },
    'political_coordination': {
        'description': 'Multiple politicians buying same sector',
        'threshold': '5+ politicians, same week',
        'historical_accuracy': 0.75,
        'avg_return_30d': 0.12
    },
    'ceo_confidence': {
        'description': 'CEO making large personal investment',
        'threshold': '>$1M or >10% of net worth',
        'historical_accuracy': 0.70,
        'avg_return_90d': 0.15
    }
}
```

### 2. Market Manipulation Patterns
```python
MANIPULATION_PATTERNS = {
    'pump_and_dump': {
        'signals': [
            'Sudden social media spike',
            'New account promotion',
            'Unrealistic price targets',
            'Low float stock'
        ],
        'detection_window': '24-48 hours'
    },
    'wash_trading': {
        'signals': [
            'Repetitive trades same price',
            'No real volume change',
            'Artificial price support'
        ]
    },
    'spoofing': {
        'signals': [
            'Large orders cancelled',
            'Price manipulation attempts',
            'False market depth'
        ]
    }
}
```

### 3. Institutional Patterns
```python
INSTITUTIONAL_PATTERNS = {
    'stealth_accumulation': {
        'signals': [
            'Dark pool accumulation',
            'Small consistent buys',
            'Price suppression during accumulation'
        ]
    },
    'distribution_top': {
        'signals': [
            'Insider selling',
            'Decreasing institutional ownership',
            'Weak price on high volume'
        ]
    },
    'short_squeeze_setup': {
        'signals': [
            'High short interest',
            'Increasing borrow rate',
            'Positive catalyst approaching'
        ]
    }
}
```

## 💾 Pattern Detection Schema

```sql
-- Pattern definitions
CREATE TABLE pattern_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    pattern_name VARCHAR(100) UNIQUE NOT NULL,
    pattern_category VARCHAR(50),
    
    -- Detection rules
    detection_rules JSONB NOT NULL,
    confidence_threshold DECIMAL(3,2),
    
    -- Historical performance
    historical_accuracy DECIMAL(3,2),
    avg_return_7d DECIMAL(8,4),
    avg_return_30d DECIMAL(8,4),
    false_positive_rate DECIMAL(3,2),
    
    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Detected patterns
CREATE TABLE detected_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    pattern_id UUID REFERENCES pattern_definitions(id),
    pattern_name VARCHAR(100),
    
    -- Detection details
    symbol VARCHAR(20),
    detection_time TIMESTAMP NOT NULL,
    confidence_score DECIMAL(3,2),
    
    -- Supporting data
    trigger_events JSONB,
    supporting_indicators JSONB,
    
    -- Entities involved
    involved_entities TEXT[], -- insider names, institutions, etc
    
    -- Impact assessment
    expected_move DECIMAL(8,4),
    expected_timeframe VARCHAR(50),
    risk_level VARCHAR(20),
    
    -- Outcome tracking
    actual_move DECIMAL(8,4),
    pattern_successful BOOLEAN,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Pattern correlations
CREATE TABLE pattern_correlations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    pattern_a VARCHAR(100),
    pattern_b VARCHAR(100),
    
    -- Correlation metrics
    correlation_coefficient DECIMAL(5,4),
    co_occurrence_rate DECIMAL(3,2),
    
    -- When they occur together
    combined_accuracy DECIMAL(3,2),
    combined_avg_return DECIMAL(8,4),
    
    UNIQUE(pattern_a, pattern_b)
);

-- Pattern alerts
CREATE TABLE pattern_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    pattern_id UUID REFERENCES detected_patterns(id),
    
    -- Alert details
    alert_type VARCHAR(50),
    severity VARCHAR(20),
    
    -- Notification
    message TEXT,
    sent_at TIMESTAMP,
    acknowledged BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🔄 Pattern Detection Pipeline

```python
# app/services/pattern_detector.py

import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import asyncio

class PatternDetectionEngine:
    def __init__(self):
        self.patterns = self.load_pattern_definitions()
        self.ml_models = self.load_ml_models()
        
    async def detect_all_patterns(self, symbol: str = None) -> List[Dict]:
        """Run all pattern detection algorithms"""
        
        detected_patterns = []
        
        # Run different pattern categories in parallel
        tasks = [
            self.detect_insider_patterns(symbol),
            self.detect_institutional_patterns(symbol),
            self.detect_manipulation_patterns(symbol),
            self.detect_technical_patterns(symbol),
            self.detect_sentiment_patterns(symbol),
            self.detect_correlation_patterns(symbol)
        ]
        
        results = await asyncio.gather(*tasks)
        
        for category_results in results:
            detected_patterns.extend(category_results)
            
        # Filter by confidence threshold
        high_confidence = [p for p in detected_patterns if p['confidence'] >= 0.7]
        
        # Check for pattern combinations
        combinations = self.check_pattern_combinations(high_confidence)
        
        return high_confidence + combinations
    
    async def detect_insider_patterns(self, symbol: str = None) -> List[Dict]:
        """Detect insider trading patterns"""
        
        patterns = []
        
        # Get insider data
        if symbol:
            insider_data = await self.get_insider_data(symbol)
        else:
            insider_data = await self.get_all_insider_data()
            
        # Check for cluster buying
        clusters = self.detect_cluster_buying(insider_data)
        patterns.extend(clusters)
        
        # Check for pre-announcement trading
        pre_announcement = self.detect_pre_announcement_trading(insider_data)
        patterns.extend(pre_announcement)
        
        # Check for political coordination
        political = self.detect_political_coordination(insider_data)
        patterns.extend(political)
        
        return patterns
    
    def detect_cluster_buying(self, insider_data: List[Dict]) -> List[Dict]:
        """Detect cluster buying patterns"""
        
        # Group by symbol and time window
        symbol_groups = {}
        for trade in insider_data:
            symbol = trade['symbol']
            if symbol not in symbol_groups:
                symbol_groups[symbol] = []
            symbol_groups[symbol].append(trade)
            
        detected = []
        for symbol, trades in symbol_groups.items():
            # Sort by date
            trades.sort(key=lambda x: x['transaction_date'])
            
            # Look for clusters (3+ buys in 7 days)
            for i in range(len(trades)):
                cluster = [trades[i]]
                cluster_end = trades[i]['transaction_date'] + timedelta(days=7)
                
                for j in range(i+1, len(trades)):
                    if trades[j]['transaction_date'] <= cluster_end:
                        if trades[j]['transaction_type'] == 'buy':
                            cluster.append(trades[j])
                            
                if len(cluster) >= 3:
                    # Calculate cluster strength
                    total_value = sum(t['value'] for t in cluster)
                    unique_insiders = len(set(t['trader_name'] for t in cluster))
                    
                    confidence = self.calculate_cluster_confidence(
                        cluster_size=len(cluster),
                        unique_insiders=unique_insiders,
                        total_value=total_value
                    )
                    
                    detected.append({
                        'pattern': 'insider_cluster_buying',
                        'symbol': symbol,
                        'confidence': confidence,
                        'cluster_size': len(cluster),
                        'total_value': total_value,
                        'insiders': [t['trader_name'] for t in cluster],
                        'start_date': cluster[0]['transaction_date'],
                        'end_date': cluster[-1]['transaction_date'],
                        'expected_return': 0.08,  # Historical average
                        'risk_level': 'medium'
                    })
                    
        return detected
```

## 🧠 Machine Learning Pattern Detection

```python
class MLPatternDetector:
    """Machine learning based pattern detection"""
    
    def __init__(self):
        self.models = {
            'insider_pattern': self.load_model('insider_pattern_xgb.pkl'),
            'manipulation_detector': self.load_model('manipulation_lstm.pkl'),
            'breakout_predictor': self.load_model('breakout_cnn.pkl'),
            'sentiment_shift': self.load_model('sentiment_transformer.pkl')
        }
        
    def detect_complex_patterns(self, symbol: str) -> List[Dict]:
        """Use ML to detect complex patterns"""
        
        # Extract features
        features = self.extract_features(symbol)
        
        patterns = []
        
        # Insider pattern detection
        insider_prob = self.models['insider_pattern'].predict_proba(features['insider'])
        if insider_prob > 0.7:
            patterns.append({
                'pattern': 'ml_insider_opportunity',
                'confidence': insider_prob,
                'features': self.explain_prediction('insider_pattern', features['insider'])
            })
            
        # Manipulation detection
        manip_prob = self.models['manipulation_detector'].predict(features['time_series'])
        if manip_prob > 0.8:
            patterns.append({
                'pattern': 'ml_manipulation_detected',
                'confidence': manip_prob,
                'type': self.classify_manipulation(features)
            })
            
        return patterns
    
    def extract_features(self, symbol: str) -> Dict:
        """Extract features for ML models"""
        
        features = {}
        
        # Insider features
        features['insider'] = [
            self.get_insider_buy_ratio(symbol, 30),
            self.get_insider_cluster_score(symbol),
            self.get_political_activity(symbol),
            self.get_insider_timing_score(symbol)
        ]
        
        # Time series features
        features['time_series'] = self.get_price_volume_features(symbol)
        
        # Sentiment features
        features['sentiment'] = self.get_sentiment_features(symbol)
        
        return features
```

## 🚨 Real-time Pattern Detection

```python
class RealTimePatternDetector:
    """Real-time pattern detection system"""
    
    def __init__(self):
        self.active_monitors = {}
        self.alert_queue = asyncio.Queue()
        
    async def start_monitoring(self, symbols: List[str]):
        """Start real-time monitoring for patterns"""
        
        for symbol in symbols:
            self.active_monitors[symbol] = asyncio.create_task(
                self.monitor_symbol(symbol)
            )
            
    async def monitor_symbol(self, symbol: str):
        """Monitor a symbol for patterns"""
        
        while True:
            try:
                # Check for patterns every minute
                patterns = await self.quick_pattern_check(symbol)
                
                if patterns:
                    for pattern in patterns:
                        await self.alert_queue.put({
                            'symbol': symbol,
                            'pattern': pattern,
                            'timestamp': datetime.now()
                        })
                        
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error monitoring {symbol}: {e}")
                
    async def quick_pattern_check(self, symbol: str) -> List[Dict]:
        """Quick pattern check for real-time monitoring"""
        
        patterns = []
        
        # Check for sudden changes
        if await self.check_volume_spike(symbol):
            patterns.append({'type': 'volume_spike', 'confidence': 0.8})
            
        if await self.check_social_surge(symbol):
            patterns.append({'type': 'social_surge', 'confidence': 0.7})
            
        if await self.check_unusual_options(symbol):
            patterns.append({'type': 'unusual_options', 'confidence': 0.75})
            
        return patterns
```

## 📊 Pattern Combination Analysis

```python
class PatternCombinationAnalyzer:
    """Analyze combinations of patterns for stronger signals"""
    
    def analyze_combinations(self, patterns: List[Dict]) -> List[Dict]:
        """Find powerful pattern combinations"""
        
        combinations = []
        
        # Group patterns by symbol
        symbol_patterns = {}
        for pattern in patterns:
            symbol = pattern['symbol']
            if symbol not in symbol_patterns:
                symbol_patterns[symbol] = []
            symbol_patterns[symbol].append(pattern)
            
        # Check for powerful combinations
        for symbol, symbol_pats in symbol_patterns.items():
            # Insider + Government contract
            if self.has_pattern(symbol_pats, 'insider_cluster_buying') and \
               self.has_pattern(symbol_pats, 'gov_contract_win'):
                combinations.append({
                    'symbol': symbol,
                    'combination': 'insider_plus_gov_contract',
                    'confidence': 0.9,
                    'expected_return': 0.15
                })
                
            # Social momentum + unusual options
            if self.has_pattern(symbol_pats, 'social_momentum') and \
               self.has_pattern(symbol_pats, 'unusual_options'):
                combinations.append({
                    'symbol': symbol,
                    'combination': 'retail_institutional_alignment',
                    'confidence': 0.85,
                    'expected_return': 0.10
                })
                
        return combinations
```

## 🎨 Pattern Visualization

```typescript
// PatternDetectionDashboard.tsx

const PatternDetectionDashboard = () => {
  return (
    <div className="pattern-detection">
      {/* Active Patterns */}
      <Card>
        <CardHeader>
          <Title>🎯 Active Patterns Detected</Title>
          <Badge>{activePatterns.length} Patterns</Badge>
        </CardHeader>
        <CardBody>
          {activePatterns.map(pattern => (
            <PatternCard key={pattern.id}>
              <PatternIcon type={pattern.type} />
              <PatternDetails>
                <Symbol>{pattern.symbol}</Symbol>
                <PatternName>{pattern.name}</PatternName>
                <Confidence level={pattern.confidence}>
                  {pattern.confidence * 100}% Confidence
                </Confidence>
              </PatternDetails>
              <ExpectedReturn>
                +{pattern.expectedReturn}% Expected
              </ExpectedReturn>
            </PatternCard>
          ))}
        </CardBody>
      </Card>
      
      {/* Pattern Timeline */}
      <Card>
        <PatternTimeline patterns={historicalPatterns} />
      </Card>
      
      {/* Pattern Combinations */}
      <Card>
        <CardHeader>
          <Title>🔗 Pattern Combinations</Title>
        </CardHeader>
        <CardBody>
          <CombinationMatrix combinations={patternCombinations} />
        </CardBody>
      </Card>
      
      {/* Success Rate Tracking */}
      <Card>
        <PatternSuccessRates patterns={patternDefinitions} />
      </Card>
    </div>
  );
};
```

## 📈 Pattern Library

### Technical Patterns
- Head and Shoulders
- Cup and Handle
- Ascending Triangle
- Bull/Bear Flag
- Double Bottom/Top
- Wedge Patterns

### Volume Patterns
- Volume Climax
- Volume Dry Up
- Accumulation Days
- Distribution Days

### Sentiment Patterns
- Sentiment Divergence
- Capitulation
- Euphoria Peak
- Fear Bottom

### Flow Patterns
- Smart Money Accumulation
- Retail FOMO
- Institutional Distribution
- Short Covering

## 📊 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Patterns tracked | 50+ | 0 |
| Detection accuracy | 75% | - |
| False positive rate | <20% | - |
| Detection latency | <1 min | - |
| Combination detection | 80% | - |

---

**Next**: Continue building comprehensive documentation for all components.