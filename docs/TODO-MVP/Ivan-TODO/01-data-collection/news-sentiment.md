# 📰 News & Sentiment Aggregation System

**Priority**: HIGH  
**Complexity**: Medium  
**Timeline**: 3-4 days  
**Value**: Comprehensive sentiment analysis from global news sources

## 🎯 Objective

Build a multi-source news aggregation system that:
- Collects news from 20+ global sources
- Performs sentiment analysis in multiple languages
- Detects breaking news and market-moving events
- Tracks sentiment trends over time
- Correlates news with price movements

## 📊 News Data Sources

### Tier 1 - Professional Financial News
```python
PROFESSIONAL_SOURCES = {
    'bloomberg': {
        'api': 'Bloomberg API',
        'cost': '$2000/month',
        'coverage': 'Global financial news',
        'languages': ['en', 'zh', 'ja', 'de']
    },
    'reuters': {
        'api': 'Reuters News API',
        'cost': '$500/month',
        'coverage': 'Global news',
        'real_time': True
    },
    'marketaux': {
        'api': 'Marketaux API',
        'cost': 'Existing',
        'coverage': 'Financial news aggregation'
    },
    'benzinga': {
        'api': 'Benzinga API',
        'cost': '$199/month',
        'coverage': 'US market news, analyst ratings'
    },
    'dow_jones': {
        'api': 'Dow Jones DNA',
        'cost': '$1000/month',
        'coverage': 'WSJ, Barrons, MarketWatch'
    }
}
```

### Tier 2 - Free/Affordable Sources
```python
FREE_SOURCES = {
    'google_news': {
        'method': 'RSS/Web scraping',
        'coverage': 'Global aggregation',
        'languages': 'All'
    },
    'yahoo_finance': {
        'method': 'API/Scraping',
        'coverage': 'Financial news',
        'real_time': True
    },
    'seeking_alpha': {
        'method': 'Web scraping',
        'coverage': 'Analysis and news',
        'quality': 'High'
    },
    'cnbc': {
        'method': 'RSS feeds',
        'coverage': 'US market news'
    },
    'financial_times': {
        'method': 'RSS/API',
        'coverage': 'Global financial'
    }
}
```

### Tier 3 - Regional Sources
```python
REGIONAL_SOURCES = {
    'asia': {
        'nikkei': 'Japanese markets',
        'scmp': 'China/HK markets',
        'economic_times': 'Indian markets',
        'korea_herald': 'Korean markets'
    },
    'europe': {
        'ft': 'UK/Europe',
        'handelsblatt': 'German markets',
        'les_echos': 'French markets',
        'il_sole': 'Italian markets'
    },
    'americas': {
        'globe_mail': 'Canadian markets',
        'valor': 'Brazilian markets',
        'el_economista': 'Mexican markets'
    }
}
```

## 💾 Database Schema

```sql
-- News articles storage
CREATE TABLE news_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Article identification
    external_id VARCHAR(255) UNIQUE,
    url TEXT UNIQUE NOT NULL,
    
    -- Content
    title TEXT NOT NULL,
    summary TEXT,
    content TEXT,
    
    -- Metadata
    source VARCHAR(100) NOT NULL,
    author VARCHAR(255),
    language VARCHAR(10) DEFAULT 'en',
    
    -- Timestamps
    published_at TIMESTAMP NOT NULL,
    scraped_at TIMESTAMP DEFAULT NOW(),
    
    -- Categories
    categories TEXT[],
    tags TEXT[],
    
    -- Entities mentioned
    mentioned_stocks TEXT[], -- Array of tickers
    mentioned_companies TEXT[],
    mentioned_people TEXT[],
    mentioned_countries TEXT[],
    
    -- Analysis results
    sentiment_score DECIMAL(3,2), -- -1 to 1
    sentiment_label VARCHAR(20), -- positive/negative/neutral
    credibility_score DECIMAL(3,2),
    virality_score DECIMAL(3,2),
    
    -- Impact metrics
    market_impact VARCHAR(20), -- high/medium/low
    affected_sectors TEXT[],
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Sentiment time series
CREATE TABLE sentiment_timeseries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(20) NOT NULL,
    
    -- Time window
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    granularity VARCHAR(20), -- hourly/daily/weekly
    
    -- Sentiment metrics
    avg_sentiment DECIMAL(3,2),
    sentiment_std_dev DECIMAL(3,2),
    
    -- Volume metrics
    article_count INTEGER,
    unique_sources INTEGER,
    
    -- Breakdown
    positive_count INTEGER,
    negative_count INTEGER,
    neutral_count INTEGER,
    
    -- Top factors
    top_positive_keywords TEXT[],
    top_negative_keywords TEXT[],
    
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(symbol, period_start, period_end, granularity)
);

-- Breaking news alerts
CREATE TABLE breaking_news (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    article_id UUID REFERENCES news_articles(id),
    
    -- Alert details
    alert_type VARCHAR(50), -- earnings, merger, scandal, etc.
    severity VARCHAR(20), -- critical/high/medium/low
    
    -- Affected entities
    primary_symbol VARCHAR(20),
    affected_symbols TEXT[],
    
    -- Impact assessment
    expected_impact VARCHAR(20), -- positive/negative
    confidence DECIMAL(3,2),
    
    -- Distribution
    sent_to_users BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🔄 News Collection Pipeline

```python
# app/services/news_collector.py

import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict
import feedparser
from newspaper import Article
import yfinance as yf

class NewsCollector:
    def __init__(self):
        self.sources = self.initialize_sources()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.entity_extractor = EntityExtractor()
        
    async def collect_all_news(self):
        """Main collection orchestrator"""
        tasks = []
        
        for source in self.sources:
            if source['type'] == 'api':
                tasks.append(self.collect_from_api(source))
            elif source['type'] == 'rss':
                tasks.append(self.collect_from_rss(source))
            elif source['type'] == 'scrape':
                tasks.append(self.scrape_website(source))
                
        articles = await asyncio.gather(*tasks)
        
        # Flatten and deduplicate
        all_articles = self.deduplicate_articles(articles)
        
        # Process each article
        processed = await self.process_articles(all_articles)
        
        return processed
    
    async def process_articles(self, articles: List[Dict]) -> List[Dict]:
        """Process articles for sentiment and entities"""
        
        processed = []
        for article in articles:
            # Extract entities (stocks, people, etc.)
            entities = await self.entity_extractor.extract(article['content'])
            
            # Analyze sentiment
            sentiment = await self.sentiment_analyzer.analyze(
                article['content'],
                article.get('language', 'en')
            )
            
            # Assess market impact
            impact = self.assess_market_impact(article, entities, sentiment)
            
            # Check if breaking news
            is_breaking = self.detect_breaking_news(article, impact)
            
            processed.append({
                **article,
                'entities': entities,
                'sentiment': sentiment,
                'impact': impact,
                'is_breaking': is_breaking
            })
            
        return processed
    
    def assess_market_impact(self, article: Dict, entities: Dict, sentiment: Dict) -> Dict:
        """Assess potential market impact of news"""
        
        impact_score = 0
        affected_stocks = []
        
        # Check for high-impact keywords
        high_impact_keywords = [
            'bankruptcy', 'merger', 'acquisition', 'earnings beat',
            'earnings miss', 'FDA approval', 'SEC investigation',
            'data breach', 'recall', 'lawsuit', 'guidance',
            'dividend', 'buyback', 'split'
        ]
        
        content_lower = article['content'].lower()
        for keyword in high_impact_keywords:
            if keyword in content_lower:
                impact_score += 0.3
                
        # Check credibility of source
        if article['source'] in ['bloomberg', 'reuters', 'wsj']:
            impact_score += 0.2
            
        # Check sentiment strength
        if abs(sentiment['score']) > 0.7:
            impact_score += 0.2
            
        # Check entity mentions
        if len(entities.get('stocks', [])) > 0:
            affected_stocks = entities['stocks']
            impact_score += 0.1 * min(len(affected_stocks), 3)
            
        return {
            'score': min(impact_score, 1.0),
            'level': self.categorize_impact(impact_score),
            'affected_stocks': affected_stocks,
            'reasoning': self.explain_impact(article, impact_score)
        }
```

## 🧠 Sentiment Analysis Engine

```python
class SentimentAnalyzer:
    """Multi-language sentiment analysis"""
    
    def __init__(self):
        self.models = {
            'en': FinBERT(),  # Financial BERT for English
            'zh': ChineseBERT(),
            'ja': JapaneseBERT(),
            'es': SpanishBERT(),
            'multi': XLMRoberta()  # Multilingual fallback
        }
        
    async def analyze(self, text: str, language: str = 'en') -> Dict:
        """Analyze sentiment with financial context"""
        
        # Select appropriate model
        model = self.models.get(language, self.models['multi'])
        
        # Get base sentiment
        base_sentiment = await model.predict(text)
        
        # Apply financial context adjustments
        adjusted = self.apply_financial_context(text, base_sentiment)
        
        # Extract aspect-based sentiment
        aspects = self.extract_aspect_sentiment(text)
        
        return {
            'score': adjusted['score'],  # -1 to 1
            'label': self.score_to_label(adjusted['score']),
            'confidence': adjusted['confidence'],
            'aspects': aspects,  # Sentiment per aspect (earnings, management, etc.)
            'explanation': self.explain_sentiment(text, adjusted)
        }
    
    def apply_financial_context(self, text: str, base_sentiment: Dict) -> Dict:
        """Adjust sentiment for financial context"""
        
        # Financial positive indicators
        positive_financial = [
            'beat expectations', 'record revenue', 'strong guidance',
            'share buyback', 'dividend increase', 'upgraded'
        ]
        
        # Financial negative indicators
        negative_financial = [
            'missed expectations', 'lowered guidance', 'layoffs',
            'investigation', 'downgraded', 'bankruptcy'
        ]
        
        text_lower = text.lower()
        
        # Adjust based on financial indicators
        adjustment = 0
        for phrase in positive_financial:
            if phrase in text_lower:
                adjustment += 0.2
                
        for phrase in negative_financial:
            if phrase in text_lower:
                adjustment -= 0.2
                
        # Apply adjustment
        adjusted_score = max(-1, min(1, base_sentiment['score'] + adjustment))
        
        return {
            'score': adjusted_score,
            'confidence': base_sentiment['confidence'],
            'adjustment': adjustment
        }
```

## 🚨 Breaking News Detection

```python
class BreakingNewsDetector:
    """Detect market-moving news in real-time"""
    
    def __init__(self):
        self.alert_patterns = {
            'merger': {
                'keywords': ['merger', 'acquisition', 'takeover', 'buyout'],
                'severity': 'high',
                'typical_impact': 0.05  # 5% move expected
            },
            'earnings': {
                'keywords': ['earnings', 'revenue', 'EPS', 'guidance'],
                'severity': 'medium',
                'typical_impact': 0.03
            },
            'regulatory': {
                'keywords': ['FDA', 'SEC', 'investigation', 'approval', 'recall'],
                'severity': 'high',
                'typical_impact': 0.07
            },
            'bankruptcy': {
                'keywords': ['bankruptcy', 'chapter 11', 'insolvency'],
                'severity': 'critical',
                'typical_impact': 0.20
            }
        }
        
    async def detect(self, article: Dict) -> Dict:
        """Detect if article is breaking news"""
        
        # Check recency (less than 1 hour old)
        age_minutes = (datetime.now() - article['published_at']).seconds / 60
        if age_minutes > 60:
            return {'is_breaking': False}
            
        # Check for alert patterns
        detected_patterns = []
        for pattern_name, pattern in self.alert_patterns.items():
            if self.matches_pattern(article, pattern):
                detected_patterns.append(pattern_name)
                
        if not detected_patterns:
            return {'is_breaking': False}
            
        # Get affected stocks
        affected_stocks = article.get('entities', {}).get('stocks', [])
        
        # Check if first to report
        is_first = await self.is_first_to_report(article['title'], affected_stocks)
        
        return {
            'is_breaking': True,
            'patterns': detected_patterns,
            'severity': self.get_max_severity(detected_patterns),
            'affected_stocks': affected_stocks,
            'is_first': is_first,
            'expected_impact': self.estimate_impact(detected_patterns),
            'alert_message': self.create_alert_message(article, detected_patterns)
        }
```

## 📊 Sentiment Aggregation

```python
class SentimentAggregator:
    """Aggregate sentiment across multiple sources"""
    
    def calculate_weighted_sentiment(self, symbol: str, hours: int = 24) -> Dict:
        """Calculate weighted sentiment for a symbol"""
        
        # Get all articles mentioning symbol
        articles = self.get_articles_for_symbol(symbol, hours)
        
        if not articles:
            return {'sentiment': 0, 'confidence': 0}
            
        # Weight factors
        weights = {
            'source_credibility': 0.3,
            'recency': 0.25,
            'relevance': 0.25,
            'virality': 0.2
        }
        
        total_weighted_sentiment = 0
        total_weight = 0
        
        for article in articles:
            # Calculate individual weights
            source_weight = self.get_source_credibility(article['source'])
            recency_weight = self.get_recency_weight(article['published_at'])
            relevance_weight = self.get_relevance_weight(article, symbol)
            virality_weight = self.get_virality_weight(article)
            
            # Combined weight
            article_weight = (
                source_weight * weights['source_credibility'] +
                recency_weight * weights['recency'] +
                relevance_weight * weights['relevance'] +
                virality_weight * weights['virality']
            )
            
            # Add to total
            total_weighted_sentiment += article['sentiment_score'] * article_weight
            total_weight += article_weight
            
        # Calculate final sentiment
        if total_weight > 0:
            final_sentiment = total_weighted_sentiment / total_weight
        else:
            final_sentiment = 0
            
        return {
            'sentiment': final_sentiment,
            'confidence': min(total_weight / len(articles), 1.0),
            'article_count': len(articles),
            'sources': list(set(a['source'] for a in articles)),
            'trend': self.calculate_trend(symbol, hours)
        }
```

## 🎨 UI Components

```typescript
// NewsSentimentDashboard.tsx

interface NewsArticle {
  id: string;
  title: string;
  source: string;
  sentiment: number;
  impact: 'high' | 'medium' | 'low';
  stocks: string[];
  publishedAt: Date;
}

const NewsSentimentDashboard = () => {
  return (
    <div className="grid grid-cols-12 gap-4">
      {/* Breaking News Alert Banner */}
      <BreakingNewsAlert className="col-span-12" />
      
      {/* Sentiment Overview */}
      <Card className="col-span-8">
        <CardHeader>
          <Title>Market Sentiment Overview</Title>
        </CardHeader>
        <CardBody>
          <SentimentHeatmap symbols={watchlist} />
          <SentimentTrendChart timeframe="24h" />
        </CardBody>
      </Card>
      
      {/* Top News */}
      <Card className="col-span-4">
        <CardHeader>
          <Title>Top Market Moving News</Title>
        </CardHeader>
        <CardBody>
          <NewsFeed 
            articles={topArticles}
            showSentiment={true}
            showImpact={true}
          />
        </CardBody>
      </Card>
      
      {/* Sentiment by Source */}
      <Card className="col-span-6">
        <SourceSentimentComparison sources={newsSources} />
      </Card>
      
      {/* Word Cloud */}
      <Card className="col-span-6">
        <TrendingTopicsCloud topics={trendingTopics} />
      </Card>
    </div>
  );
};
```

## 📊 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Articles collected/day | 5000+ | 0 |
| Sources active | 20+ | 0 |
| Sentiment accuracy | 85% | - |
| Breaking news detection | <5 min | - |
| Language coverage | 10+ | - |

---

**Next**: Implement [social-signals.md](social-signals.md) for social media tracking.