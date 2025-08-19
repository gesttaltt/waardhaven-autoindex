# 📊 Sentiment Aggregation & Analysis

**Priority**: HIGH  
**Complexity**: High  
**Timeline**: 3-4 days  
**Value**: Unified sentiment signal from multiple sources

## 🎯 Objective

Build a comprehensive sentiment aggregation system that:
- Combines sentiment from news, social media, analysts
- Weights sources by credibility and accuracy
- Detects sentiment shifts and anomalies
- Provides real-time sentiment scores
- Tracks sentiment momentum

## 📡 Sentiment Sources

### Source Hierarchy
```python
SENTIMENT_SOURCES = {
    'tier_1_professional': {
        'sources': ['Bloomberg', 'Reuters', 'WSJ', 'FT'],
        'weight': 0.35,
        'latency': 'Minutes',
        'credibility': 0.95
    },
    'tier_2_analysts': {
        'sources': ['Analyst reports', 'Earnings calls', 'Guidance'],
        'weight': 0.25,
        'latency': 'Hours',
        'credibility': 0.85
    },
    'tier_3_social': {
        'sources': ['Twitter', 'Reddit', 'StockTwits'],
        'weight': 0.20,
        'latency': 'Real-time',
        'credibility': 0.60
    },
    'tier_4_alternative': {
        'sources': ['Blogs', 'Forums', 'YouTube'],
        'weight': 0.15,
        'latency': 'Hours',
        'credibility': 0.50
    },
    'tier_5_insider': {
        'sources': ['Employee reviews', 'Glassdoor', 'LinkedIn'],
        'weight': 0.05,
        'latency': 'Days',
        'credibility': 0.70
    }
}
```

## 💾 Database Schema

```sql
-- Aggregated sentiment scores
CREATE TABLE sentiment_aggregate (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    
    -- Overall sentiment
    overall_sentiment DECIMAL(5,4), -- -1 to 1
    sentiment_label VARCHAR(20), -- very_negative to very_positive
    confidence DECIMAL(5,4),
    
    -- Source breakdown
    news_sentiment DECIMAL(5,4),
    social_sentiment DECIMAL(5,4),
    analyst_sentiment DECIMAL(5,4),
    insider_sentiment DECIMAL(5,4),
    
    -- Momentum metrics
    sentiment_momentum DECIMAL(5,4), -- Rate of change
    sentiment_acceleration DECIMAL(5,4),
    
    -- Volume metrics
    total_mentions INTEGER,
    unique_sources INTEGER,
    
    -- Disagreement metrics
    sentiment_dispersion DECIMAL(5,4),
    source_agreement DECIMAL(5,4),
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(symbol, timestamp)
);

-- Sentiment events
CREATE TABLE sentiment_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    symbol VARCHAR(20) NOT NULL,
    event_time TIMESTAMP NOT NULL,
    
    -- Event details
    event_type VARCHAR(100), -- sentiment_shift, anomaly, divergence
    severity VARCHAR(20),
    
    -- Before/After
    sentiment_before DECIMAL(5,4),
    sentiment_after DECIMAL(5,4),
    change_magnitude DECIMAL(5,4),
    
    -- Trigger
    trigger_source VARCHAR(100),
    trigger_content TEXT,
    
    -- Impact
    price_impact DECIMAL(8,4),
    volume_impact DECIMAL(8,4),
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Source credibility tracking
CREATE TABLE source_credibility (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    source_name VARCHAR(255) UNIQUE NOT NULL,
    source_type VARCHAR(50),
    
    -- Accuracy metrics
    predictions_made INTEGER DEFAULT 0,
    predictions_correct INTEGER DEFAULT 0,
    accuracy_rate DECIMAL(5,4),
    
    -- Timing metrics
    avg_lead_time_hours DECIMAL(8,2),
    false_positive_rate DECIMAL(5,4),
    
    -- Current weight
    credibility_score DECIMAL(5,4),
    weight_multiplier DECIMAL(5,4) DEFAULT 1.0,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    last_evaluated TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Sentiment disagreement tracking
CREATE TABLE sentiment_disagreement (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    
    -- Disagreement metrics
    news_vs_social DECIMAL(5,4),
    analyst_vs_crowd DECIMAL(5,4),
    professional_vs_retail DECIMAL(5,4),
    
    -- Extreme positions
    most_bullish_source VARCHAR(100),
    most_bullish_score DECIMAL(5,4),
    most_bearish_source VARCHAR(100),
    most_bearish_score DECIMAL(5,4),
    
    -- Resolution
    eventual_direction VARCHAR(20), -- Which side was right
    resolution_time_hours DECIMAL(8,2),
    
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🧠 Sentiment Aggregation Engine

```python
# app/services/sentiment_aggregator.py

import numpy as np
import pandas as pd
from typing import Dict, List
from datetime import datetime, timedelta
import asyncio

class SentimentAggregator:
    """Multi-source sentiment aggregation engine"""
    
    def __init__(self):
        self.source_weights = self.initialize_weights()
        self.nlp_models = self.load_nlp_models()
        self.credibility_tracker = CredibilityTracker()
        
    async def calculate_aggregate_sentiment(self, symbol: str) -> Dict:
        """Calculate weighted aggregate sentiment"""
        
        # Collect sentiment from all sources
        sentiments = await self.collect_all_sentiments(symbol)
        
        # Apply credibility weights
        weighted_sentiments = self.apply_credibility_weights(sentiments)
        
        # Calculate aggregate
        aggregate = self.calculate_weighted_average(weighted_sentiments)
        
        # Calculate momentum
        momentum = await self.calculate_sentiment_momentum(symbol)
        
        # Detect anomalies
        anomalies = self.detect_sentiment_anomalies(sentiments)
        
        # Check for disagreement
        disagreement = self.analyze_disagreement(sentiments)
        
        return {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'overall_sentiment': aggregate['score'],
            'confidence': aggregate['confidence'],
            'sentiment_label': self.score_to_label(aggregate['score']),
            'momentum': momentum,
            'source_breakdown': self.get_source_breakdown(sentiments),
            'anomalies': anomalies,
            'disagreement': disagreement,
            'recommendation': self.generate_recommendation(aggregate, momentum)
        }
    
    async def collect_all_sentiments(self, symbol: str) -> Dict:
        """Collect sentiment from all sources"""
        
        tasks = [
            self.collect_news_sentiment(symbol),
            self.collect_social_sentiment(symbol),
            self.collect_analyst_sentiment(symbol),
            self.collect_insider_sentiment(symbol),
            self.collect_alternative_sentiment(symbol)
        ]
        
        results = await asyncio.gather(*tasks)
        
        return {
            'news': results[0],
            'social': results[1],
            'analyst': results[2],
            'insider': results[3],
            'alternative': results[4]
        }
    
    async def collect_news_sentiment(self, symbol: str) -> Dict:
        """Aggregate news sentiment"""
        
        # Get recent news articles
        articles = await self.get_news_articles(symbol, hours=24)
        
        if not articles:
            return {'score': 0, 'confidence': 0, 'volume': 0}
        
        sentiments = []
        weights = []
        
        for article in articles:
            # Analyze sentiment
            sentiment = await self.analyze_article_sentiment(article)
            
            # Weight by source credibility and recency
            weight = self.calculate_article_weight(article)
            
            sentiments.append(sentiment)
            weights.append(weight)
        
        # Weighted average
        weighted_sentiment = np.average(sentiments, weights=weights)
        
        return {
            'score': weighted_sentiment,
            'confidence': self.calculate_confidence(sentiments, weights),
            'volume': len(articles),
            'sources': list(set(a['source'] for a in articles)),
            'top_headlines': self.get_top_headlines(articles, 3)
        }
    
    async def collect_social_sentiment(self, symbol: str) -> Dict:
        """Aggregate social media sentiment"""
        
        # Collect from multiple platforms
        reddit = await self.get_reddit_sentiment(symbol)
        twitter = await self.get_twitter_sentiment(symbol)
        stocktwits = await self.get_stocktwits_sentiment(symbol)
        
        # Weight by platform importance and volume
        weights = {
            'reddit': 0.4,
            'twitter': 0.35,
            'stocktwits': 0.25
        }
        
        # Adjust weights by volume
        total_volume = reddit['volume'] + twitter['volume'] + stocktwits['volume']
        
        if total_volume > 0:
            volume_adjusted_weights = {
                'reddit': weights['reddit'] * (reddit['volume'] / total_volume),
                'twitter': weights['twitter'] * (twitter['volume'] / total_volume),
                'stocktwits': weights['stocktwits'] * (stocktwits['volume'] / total_volume)
            }
        else:
            volume_adjusted_weights = weights
        
        # Calculate weighted average
        social_sentiment = (
            reddit['sentiment'] * volume_adjusted_weights['reddit'] +
            twitter['sentiment'] * volume_adjusted_weights['twitter'] +
            stocktwits['sentiment'] * volume_adjusted_weights['stocktwits']
        )
        
        return {
            'score': social_sentiment,
            'confidence': np.mean([reddit['confidence'], twitter['confidence'], stocktwits['confidence']]),
            'volume': total_volume,
            'momentum': self.calculate_social_momentum(reddit, twitter, stocktwits),
            'platforms': {
                'reddit': reddit,
                'twitter': twitter,
                'stocktwits': stocktwits
            }
        }
```

## 📈 Sentiment Momentum Tracking

```python
class SentimentMomentumTracker:
    """Track sentiment momentum and acceleration"""
    
    async def calculate_sentiment_momentum(self, symbol: str) -> Dict:
        """Calculate sentiment momentum indicators"""
        
        # Get historical sentiment
        sentiment_history = await self.get_sentiment_history(symbol, days=30)
        
        if len(sentiment_history) < 7:
            return {'momentum': 0, 'acceleration': 0, 'trend': 'neutral'}
        
        # Convert to time series
        ts = pd.Series(
            [s['sentiment'] for s in sentiment_history],
            index=[s['timestamp'] for s in sentiment_history]
        )
        
        # Calculate momentum (rate of change)
        momentum_1d = ts.iloc[-1] - ts.iloc[-2] if len(ts) > 1 else 0
        momentum_7d = (ts.iloc[-1] - ts.iloc[-8]) / 7 if len(ts) > 7 else 0
        momentum_30d = (ts.iloc[-1] - ts.iloc[0]) / len(ts) if len(ts) > 0 else 0
        
        # Calculate acceleration
        if len(ts) > 14:
            recent_momentum = (ts.iloc[-1] - ts.iloc[-8]) / 7
            previous_momentum = (ts.iloc[-8] - ts.iloc[-15]) / 7
            acceleration = recent_momentum - previous_momentum
        else:
            acceleration = 0
        
        # Determine trend
        trend = self.determine_trend(ts)
        
        # Identify inflection points
        inflection_points = self.find_inflection_points(ts)
        
        return {
            'momentum_1d': momentum_1d,
            'momentum_7d': momentum_7d,
            'momentum_30d': momentum_30d,
            'acceleration': acceleration,
            'trend': trend,
            'trend_strength': self.calculate_trend_strength(ts),
            'inflection_points': inflection_points,
            'momentum_percentile': self.calculate_momentum_percentile(momentum_7d, symbol)
        }
    
    def determine_trend(self, ts: pd.Series) -> str:
        """Determine sentiment trend"""
        
        if len(ts) < 7:
            return 'insufficient_data'
        
        # Simple moving averages
        sma_7 = ts.iloc[-7:].mean()
        sma_14 = ts.iloc[-14:].mean() if len(ts) >= 14 else sma_7
        
        # Current vs averages
        current = ts.iloc[-1]
        
        if current > sma_7 > sma_14:
            return 'strong_uptrend'
        elif current > sma_7:
            return 'uptrend'
        elif current < sma_7 < sma_14:
            return 'strong_downtrend'
        elif current < sma_7:
            return 'downtrend'
        else:
            return 'sideways'
```

## 🔍 Anomaly Detection

```python
class SentimentAnomalyDetector:
    """Detect sentiment anomalies and divergences"""
    
    def detect_anomalies(self, sentiments: Dict) -> List[Dict]:
        """Detect various types of sentiment anomalies"""
        
        anomalies = []
        
        # Check for extreme sentiment
        extreme = self.check_extreme_sentiment(sentiments)
        if extreme:
            anomalies.append(extreme)
        
        # Check for sentiment divergence
        divergence = self.check_sentiment_divergence(sentiments)
        if divergence:
            anomalies.append(divergence)
        
        # Check for sudden shifts
        shift = self.check_sudden_shift(sentiments)
        if shift:
            anomalies.append(shift)
        
        # Check for source disagreement
        disagreement = self.check_source_disagreement(sentiments)
        if disagreement:
            anomalies.append(disagreement)
        
        return anomalies
    
    def check_sentiment_divergence(self, sentiments: Dict) -> Dict:
        """Check for divergence between price and sentiment"""
        
        # Get recent price trend
        price_trend = self.get_price_trend(sentiments['symbol'])
        
        # Get sentiment trend
        sentiment_trend = sentiments['momentum']['trend']
        
        # Check for divergence
        if price_trend == 'up' and sentiment_trend in ['downtrend', 'strong_downtrend']:
            return {
                'type': 'bearish_divergence',
                'severity': 'high',
                'description': 'Price rising but sentiment falling',
                'action': 'Consider taking profits',
                'confidence': 0.75
            }
        elif price_trend == 'down' and sentiment_trend in ['uptrend', 'strong_uptrend']:
            return {
                'type': 'bullish_divergence',
                'severity': 'high',
                'description': 'Price falling but sentiment rising',
                'action': 'Potential buying opportunity',
                'confidence': 0.75
            }
        
        return None
    
    def check_source_disagreement(self, sentiments: Dict) -> Dict:
        """Check for disagreement between sources"""
        
        news = sentiments.get('news', {}).get('score', 0)
        social = sentiments.get('social', {}).get('score', 0)
        analyst = sentiments.get('analyst', {}).get('score', 0)
        
        # Calculate standard deviation
        scores = [news, social, analyst]
        std_dev = np.std(scores)
        
        # High disagreement threshold
        if std_dev > 0.3:
            # Identify extremes
            max_source = max([(news, 'news'), (social, 'social'), (analyst, 'analyst')])
            min_source = min([(news, 'news'), (social, 'social'), (analyst, 'analyst')])
            
            return {
                'type': 'source_disagreement',
                'severity': 'medium',
                'description': f'{max_source[1]} bullish ({max_source[0]:.2f}) vs {min_source[1]} bearish ({min_source[0]:.2f})',
                'disagreement_level': std_dev,
                'action': 'Wait for consensus or use as contrarian signal'
            }
        
        return None
```

## 🔮 Predictive Sentiment

```python
class PredictiveSentiment:
    """Use sentiment to predict price movements"""
    
    def predict_from_sentiment(self, symbol: str, sentiment_data: Dict) -> Dict:
        """Predict price movement from sentiment"""
        
        # Historical correlation
        correlation = self.get_sentiment_price_correlation(symbol)
        
        # Current sentiment strength
        sentiment_strength = abs(sentiment_data['overall_sentiment'])
        
        # Momentum factor
        momentum_factor = sentiment_data['momentum']['momentum_7d']
        
        # Calculate expected move
        base_move = sentiment_data['overall_sentiment'] * correlation * 0.05  # 5% max base move
        momentum_adjustment = momentum_factor * 0.02  # 2% max momentum adjustment
        
        expected_move = base_move + momentum_adjustment
        
        # Calculate confidence
        confidence = min(
            sentiment_data['confidence'] * 
            sentiment_strength * 
            (1 - sentiment_data['disagreement']['level']),
            0.95
        )
        
        # Time horizons
        predictions = {
            '1_day': expected_move * 0.2,
            '7_day': expected_move * 0.7,
            '30_day': expected_move * 1.5
        }
        
        return {
            'symbol': symbol,
            'predictions': predictions,
            'confidence': confidence,
            'key_driver': self.identify_key_driver(sentiment_data),
            'risk_factors': self.identify_risks(sentiment_data)
        }
```

## 🎨 Visualization Components

```typescript
// SentimentAggregationDashboard.tsx

const SentimentAggregationDashboard = () => {
  return (
    <div className="sentiment-aggregation">
      {/* Overall Sentiment Gauge */}
      <Card>
        <CardHeader>
          <Title>📈 Market Sentiment</Title>
        </CardHeader>
        <CardBody>
          <SentimentGauge 
            value={overallSentiment}
            min={-1}
            max={1}
            showZones={true}
          />
          <SentimentBreakdown sources={sentimentSources} />
        </CardBody>
      </Card>
      
      {/* Sentiment Momentum */}
      <Card>
        <CardHeader>
          <Title>🚀 Sentiment Momentum</Title>
        </CardHeader>
        <CardBody>
          <MomentumChart 
            data={momentumData}
            showAcceleration={true}
          />
          <TrendIndicator trend={currentTrend} />
        </CardBody>
      </Card>
      
      {/* Source Agreement */}
      <Card>
        <CardHeader>
          <Title>🤝 Source Agreement</Title>
        </CardHeader>
        <CardBody>
          <SourceAgreementMatrix sources={sources} />
          <DisagreementAlerts alerts={disagreementAlerts} />
        </CardBody>
      </Card>
      
      {/* Sentiment Heatmap */}
      <Card>
        <CardHeader>
          <Title>🔥 Sentiment Heatmap</Title>
        </CardHeader>
        <CardBody>
          <SentimentHeatmap 
            symbols={watchlist}
            timeframe="24h"
            colorScale="RdYlGn"
          />
        </CardBody>
      </Card>
      
      {/* Anomaly Detection */}
      <Card>
        <CardHeader>
          <Title>⚠️ Sentiment Anomalies</Title>
        </CardHeader>
        <CardBody>
          <AnomalyList anomalies={detectedAnomalies} />
        </CardBody>
      </Card>
    </div>
  );
};
```

## 📊 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Sentiment sources integrated | 20+ | 0 |
| Sentiment accuracy | >75% | - |
| Anomaly detection rate | >90% | - |
| Processing latency | <1s | - |
| Prediction correlation | >0.6 | - |

---

**Next**: Continue with backtesting framework.