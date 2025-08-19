# 📱 Social Signals & Crowd Sentiment Tracking

**Priority**: HIGH  
**Complexity**: High  
**Timeline**: 4-5 days  
**Value**: Real-time retail sentiment and viral stock detection

## 🎯 Objective

Track social media sentiment and crowd behavior to:
- Detect viral stocks before mainstream media
- Monitor retail investor sentiment
- Track influencer stock mentions
- Identify pump & dump schemes
- Measure social momentum

## 📊 Social Data Sources

### Reddit 🟠
```python
REDDIT_SOURCES = {
    'wallstreetbets': {
        'subscribers': '15M+',
        'importance': 'CRITICAL',
        'signals': ['meme stocks', 'retail momentum', 'squeeze plays']
    },
    'stocks': {
        'subscribers': '3M+',
        'importance': 'HIGH',
        'signals': ['general sentiment', 'DD posts']
    },
    'investing': {
        'subscribers': '2M+',
        'importance': 'MEDIUM',
        'signals': ['long-term sentiment']
    },
    'stockmarket': {
        'subscribers': '3M+',
        'importance': 'HIGH',
        'signals': ['market sentiment']
    },
    'options': {
        'subscribers': '1M+',
        'importance': 'HIGH',
        'signals': ['options flow', 'volatility plays']
    },
    'superstonk': {
        'subscribers': '1M+',
        'importance': 'MEDIUM',
        'signals': ['GME ecosystem']
    },
    'pennystocks': {
        'subscribers': '2M+',
        'importance': 'MEDIUM',
        'signals': ['small cap momentum']
    },
    'spacs': {
        'subscribers': '500K+',
        'importance': 'LOW',
        'signals': ['SPAC sentiment']
    }
}
```

### Twitter/X 🐦
```python
TWITTER_TRACKING = {
    'influencers': [
        {'handle': '@jimcramer', 'followers': '2M+', 'impact': 'HIGH'},
        {'handle': '@elonmusk', 'followers': '150M+', 'impact': 'EXTREME'},
        {'handle': '@chamath', 'followers': '1.5M+', 'impact': 'HIGH'},
        {'handle': '@icahn_carl', 'followers': '500K+', 'impact': 'HIGH'},
        {'handle': '@michael_burry', 'followers': '1M+', 'impact': 'HIGH'}
    ],
    'hashtags': [
        '#stocks', '#trading', '#investing', '#options',
        '#wallstreetbets', '#diamond  hands', '#tothemoon'
    ],
    'cashtags': [
        '$SPY', '$QQQ', '$TSLA', '$AAPL', '$GME', '$AMC'
    ]
}
```

### StockTwits 📈
```python
STOCKTWITS_CONFIG = {
    'api': 'StockTwits API',
    'streams': ['trending', 'most-active', 'watchers'],
    'metrics': ['sentiment', 'volume', 'momentum']
}
```

### Discord Servers 💬
```python
DISCORD_SERVERS = {
    'investment_servers': [
        'InvestorsUnderground',
        'Stonks',
        'TradingCommunity',
        'OptionsMillionaire'
    ],
    'monitoring_method': 'Bot integration',
    'signals': ['real-time alerts', 'group sentiment']
}
```

### TikTok Finance 🎵
```python
TIKTOK_FINANCE = {
    'hashtags': [
        '#fintok', '#stocktok', '#investingtips',
        '#tradingforbeginners', '#wealthbuilding'
    ],
    'influencers': [
        'Financial influencers with 100K+ followers'
    ],
    'risk': 'HIGH - many pump schemes'
}
```

## 💾 Database Schema

```sql
-- Social posts storage
CREATE TABLE social_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Post identification
    platform VARCHAR(50) NOT NULL, -- reddit, twitter, stocktwits, discord
    platform_id VARCHAR(255) UNIQUE, -- Original post ID
    url TEXT,
    
    -- Content
    title TEXT, -- For Reddit
    content TEXT NOT NULL,
    
    -- Author
    author_username VARCHAR(255),
    author_followers INTEGER,
    author_reputation INTEGER,
    is_influencer BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    posted_at TIMESTAMP NOT NULL,
    
    -- Engagement metrics
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    
    -- Extracted entities
    mentioned_tickers TEXT[],
    mentioned_cryptos TEXT[],
    
    -- Sentiment analysis
    sentiment_score DECIMAL(3,2),
    bullish_bearish VARCHAR(20),
    confidence DECIMAL(3,2),
    
    -- Virality metrics
    virality_score DECIMAL(3,2),
    is_trending BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Reddit specific data
CREATE TABLE reddit_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID REFERENCES social_posts(id),
    
    subreddit VARCHAR(100) NOT NULL,
    flair VARCHAR(100),
    
    -- Reddit specific metrics
    score INTEGER, -- upvotes - downvotes
    upvote_ratio DECIMAL(3,2),
    num_awards INTEGER,
    is_dd BOOLEAN DEFAULT FALSE, -- Due Diligence post
    is_yolo BOOLEAN DEFAULT FALSE,
    is_gain_loss BOOLEAN DEFAULT FALSE,
    
    -- Content analysis
    dd_quality_score DECIMAL(3,2), -- For DD posts
    has_positions BOOLEAN,
    position_details JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Social momentum tracking
CREATE TABLE social_momentum (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    symbol VARCHAR(20) NOT NULL,
    platform VARCHAR(50),
    
    -- Time window
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    
    -- Volume metrics
    mention_count INTEGER,
    unique_users INTEGER,
    
    -- Sentiment metrics
    avg_sentiment DECIMAL(3,2),
    bullish_count INTEGER,
    bearish_count INTEGER,
    
    -- Engagement metrics
    total_upvotes INTEGER,
    total_comments INTEGER,
    total_shares INTEGER,
    
    -- Momentum indicators
    momentum_score DECIMAL(3,2), -- Rate of change
    is_accelerating BOOLEAN,
    
    -- Top posts
    top_post_ids UUID[],
    
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(symbol, platform, period_start, period_end)
);

-- Influencer tracking
CREATE TABLE social_influencers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    platform VARCHAR(50) NOT NULL,
    username VARCHAR(255) NOT NULL,
    
    -- Metrics
    followers INTEGER,
    engagement_rate DECIMAL(5,2),
    
    -- Track record
    total_calls INTEGER DEFAULT 0,
    successful_calls INTEGER DEFAULT 0,
    success_rate DECIMAL(3,2),
    avg_return DECIMAL(8,4),
    
    -- Categories
    categories TEXT[], -- ['crypto', 'options', 'pennystocks']
    credibility_score DECIMAL(3,2),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(platform, username)
);
```

## 🔄 Social Collection Pipeline

```python
# app/services/social_collector.py

import praw  # Reddit API
import tweepy  # Twitter API
import asyncio
from datetime import datetime, timedelta
import re

class SocialSignalsCollector:
    def __init__(self):
        self.reddit = self.init_reddit()
        self.twitter = self.init_twitter()
        self.stocktwits = self.init_stocktwits()
        
    def init_reddit(self):
        """Initialize Reddit API connection"""
        return praw.Reddit(
            client_id=settings.REDDIT_CLIENT_ID,
            client_secret=settings.REDDIT_CLIENT_SECRET,
            user_agent='StockIntelligence/1.0'
        )
    
    async def collect_reddit_wsb(self):
        """Collect from WallStreetBets"""
        
        subreddit = self.reddit.subreddit('wallstreetbets')
        
        # Get different post types
        hot_posts = list(subreddit.hot(limit=100))
        new_posts = list(subreddit.new(limit=100))
        top_daily = list(subreddit.top('day', limit=50))
        
        all_posts = hot_posts + new_posts + top_daily
        
        processed_posts = []
        for post in all_posts:
            # Extract tickers
            tickers = self.extract_tickers(post.title + ' ' + post.selftext)
            
            # Analyze sentiment
            sentiment = self.analyze_wsb_sentiment(post)
            
            # Check if DD post
            is_dd = self.is_due_diligence(post)
            
            # Calculate virality
            virality = self.calculate_virality(post)
            
            processed_posts.append({
                'id': post.id,
                'title': post.title,
                'content': post.selftext[:5000],  # Limit content size
                'author': str(post.author),
                'created': datetime.fromtimestamp(post.created_utc),
                'score': post.score,
                'comments': post.num_comments,
                'tickers': tickers,
                'sentiment': sentiment,
                'is_dd': is_dd,
                'virality': virality,
                'flair': post.link_flair_text
            })
            
        return processed_posts
    
    def extract_tickers(self, text: str) -> List[str]:
        """Extract stock tickers from text"""
        
        # Common patterns: $TICKER, TICKER, NYSE:TICKER
        patterns = [
            r'\$([A-Z]{1,5})\b',  # $TICKER
            r'\b([A-Z]{2,5})\b',   # TICKER (2-5 uppercase letters)
            r'NYSE:([A-Z]{1,5})',  # Exchange:TICKER
            r'NASDAQ:([A-Z]{1,5})'
        ]
        
        tickers = set()
        for pattern in patterns:
            matches = re.findall(pattern, text)
            tickers.update(matches)
            
        # Filter out common words that aren't tickers
        blacklist = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'NEW', 'WSB', 'USA']
        tickers = [t for t in tickers if t not in blacklist]
        
        # Validate against known tickers
        valid_tickers = self.validate_tickers(list(tickers))
        
        return valid_tickers
    
    def analyze_wsb_sentiment(self, post) -> Dict:
        """Analyze WSB-specific sentiment"""
        
        # WSB specific bullish terms
        bullish_terms = [
            '🚀', 'moon', 'tendies', 'diamond hands', '💎🙌',
            'YOLO', 'squeeze', 'gamma', 'calls', 'buy',
            'hold', 'hodl', 'apes', 'strong', 'breakout'
        ]
        
        # WSB specific bearish terms
        bearish_terms = [
            '🌈🐻', 'puts', 'drill', 'dump', 'crash',
            'sell', 'short', 'overvalued', 'bubble', 'rug pull',
            'bag holder', 'loss porn', 'GUH', 'rip'
        ]
        
        text = (post.title + ' ' + post.selftext).lower()
        
        bullish_score = sum(1 for term in bullish_terms if term in text)
        bearish_score = sum(1 for term in bearish_terms if term in text)
        
        # Calculate sentiment
        if bullish_score > bearish_score:
            sentiment = min(bullish_score / 10, 1.0)
            label = 'bullish'
        elif bearish_score > bullish_score:
            sentiment = -min(bearish_score / 10, 1.0)
            label = 'bearish'
        else:
            sentiment = 0
            label = 'neutral'
            
        return {
            'score': sentiment,
            'label': label,
            'bullish_signals': bullish_score,
            'bearish_signals': bearish_score
        }
    
    def calculate_virality(self, post) -> float:
        """Calculate virality score"""
        
        # Factors for virality
        score = 0
        
        # Upvotes (logarithmic scale)
        if post.score > 0:
            score += min(np.log10(post.score) / 5, 0.3)  # Max 0.3
            
        # Comments (engagement)
        if post.num_comments > 0:
            score += min(np.log10(post.num_comments) / 4, 0.2)  # Max 0.2
            
        # Awards
        if hasattr(post, 'total_awards_received'):
            score += min(post.total_awards_received / 10, 0.2)  # Max 0.2
            
        # Upvote ratio
        if hasattr(post, 'upvote_ratio'):
            score += post.upvote_ratio * 0.2  # Max 0.2
            
        # Time decay (newer is better)
        age_hours = (datetime.now() - datetime.fromtimestamp(post.created_utc)).seconds / 3600
        if age_hours < 24:
            score += 0.1
            
        return min(score, 1.0)
```

## 🚨 Pump & Dump Detection

```python
class PumpDumpDetector:
    """Detect potential pump and dump schemes"""
    
    def detect_pump_signals(self, symbol: str) -> Dict:
        """Detect pump and dump patterns"""
        
        signals = {
            'is_suspicious': False,
            'risk_level': 'low',
            'red_flags': [],
            'confidence': 0
        }
        
        # Check sudden mention spike
        mention_spike = self.check_mention_spike(symbol)
        if mention_spike['is_spike']:
            signals['red_flags'].append('sudden_mention_spike')
            signals['confidence'] += 0.3
            
        # Check coordinated posting
        coordinated = self.check_coordinated_posting(symbol)
        if coordinated['is_coordinated']:
            signals['red_flags'].append('coordinated_posting')
            signals['confidence'] += 0.4
            
        # Check new account activity
        new_accounts = self.check_new_account_activity(symbol)
        if new_accounts['suspicious']:
            signals['red_flags'].append('new_account_pumping')
            signals['confidence'] += 0.3
            
        # Check for typical pump language
        pump_language = self.check_pump_language(symbol)
        if pump_language['detected']:
            signals['red_flags'].append('pump_language')
            signals['confidence'] += 0.2
            
        # Determine risk level
        if signals['confidence'] >= 0.7:
            signals['risk_level'] = 'high'
            signals['is_suspicious'] = True
        elif signals['confidence'] >= 0.4:
            signals['risk_level'] = 'medium'
            signals['is_suspicious'] = True
            
        return signals
    
    def check_coordinated_posting(self, symbol: str) -> Dict:
        """Check for coordinated posting patterns"""
        
        # Get recent posts mentioning symbol
        recent_posts = self.get_recent_posts(symbol, hours=6)
        
        # Group by time windows (5 minute buckets)
        time_buckets = {}
        for post in recent_posts:
            bucket = post['created'].replace(minute=post['created'].minute // 5 * 5)
            if bucket not in time_buckets:
                time_buckets[bucket] = []
            time_buckets[bucket].append(post)
            
        # Check for suspicious clustering
        suspicious_buckets = []
        for bucket, posts in time_buckets.items():
            if len(posts) > 10:  # More than 10 posts in 5 minutes
                # Check if similar content
                similarity = self.check_content_similarity(posts)
                if similarity > 0.7:
                    suspicious_buckets.append(bucket)
                    
        return {
            'is_coordinated': len(suspicious_buckets) > 0,
            'suspicious_times': suspicious_buckets,
            'confidence': min(len(suspicious_buckets) / 3, 1.0)
        }
```

## 📊 Momentum Tracking

```python
class SocialMomentumTracker:
    """Track social momentum for stocks"""
    
    def calculate_momentum(self, symbol: str) -> Dict:
        """Calculate comprehensive social momentum"""
        
        # Get mention data for different time periods
        mentions_1h = self.get_mentions(symbol, hours=1)
        mentions_6h = self.get_mentions(symbol, hours=6)
        mentions_24h = self.get_mentions(symbol, hours=24)
        mentions_7d = self.get_mentions(symbol, days=7)
        
        # Calculate momentum scores
        hourly_momentum = self.calculate_rate_of_change(mentions_1h, mentions_6h)
        daily_momentum = self.calculate_rate_of_change(mentions_24h, mentions_7d)
        
        # Get sentiment momentum
        sentiment_trend = self.calculate_sentiment_trend(symbol)
        
        # Calculate composite score
        momentum_score = (
            hourly_momentum * 0.4 +  # Recent momentum weighted higher
            daily_momentum * 0.3 +
            sentiment_trend * 0.3
        )
        
        # Determine if accelerating
        is_accelerating = hourly_momentum > daily_momentum
        
        return {
            'symbol': symbol,
            'momentum_score': momentum_score,
            'hourly_momentum': hourly_momentum,
            'daily_momentum': daily_momentum,
            'sentiment_trend': sentiment_trend,
            'is_accelerating': is_accelerating,
            'mention_count_24h': len(mentions_24h),
            'unique_users_24h': self.count_unique_users(mentions_24h),
            'top_posts': self.get_top_posts(mentions_24h, limit=5),
            'platforms': self.get_platform_breakdown(mentions_24h)
        }
```

## 🎨 UI Components

```typescript
// SocialSignalsDashboard.tsx

const SocialSignalsDashboard = () => {
  return (
    <div className="social-dashboard">
      {/* Trending Stocks */}
      <Card>
        <CardHeader>
          <Title>🔥 Trending on Social Media</Title>
          <Badge>Last Hour</Badge>
        </CardHeader>
        <CardBody>
          <TrendingStocksList 
            stocks={trendingStocks}
            showMomentum={true}
            showPlatforms={true}
          />
        </CardBody>
      </Card>
      
      {/* Reddit WSB Monitor */}
      <Card>
        <CardHeader>
          <Title>🦍 WallStreetBets Activity</Title>
        </CardHeader>
        <CardBody>
          <WSBFeed 
            posts={wsbPosts}
            showDD={true}
            showYOLO={true}
          />
        </CardBody>
      </Card>
      
      {/* Pump & Dump Warnings */}
      <AlertCard severity="warning">
        <Title>⚠️ Potential Pump & Dump Detected</Title>
        <PumpDumpWarnings warnings={pumpWarnings} />
      </AlertCard>
      
      {/* Social Momentum Chart */}
      <Card>
        <MomentumChart 
          data={momentumData}
          platforms={['reddit', 'twitter', 'stocktwits']}
        />
      </Card>
      
      {/* Influencer Mentions */}
      <Card>
        <InfluencerActivity 
          mentions={influencerMentions}
          showImpact={true}
        />
      </Card>
    </div>
  );
};
```

## 📊 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Posts analyzed/day | 50,000+ | 0 |
| Platforms monitored | 5+ | 0 |
| Pump detection accuracy | 80% | - |
| Viral stock detection | <1 hour | - |
| Influencer tracking | 100+ | 0 |

---

**Next**: Create analysis engine documentation for pattern detection and ML scoring.