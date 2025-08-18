# News Providers Documentation

## Overview
News providers supply financial news articles, sentiment analysis, and entity extraction. Currently implemented: Marketaux.

## Marketaux Provider

### Location
`app/providers/news/marketaux.py`

### Features
- Financial news aggregation (5,000+ sources)
- Sentiment analysis (-1 to +1 scale)
- Entity extraction and identification
- Similar articles discovery
- Trending entities tracking
- Multi-language support (30+ languages)
- Global market coverage (80+ markets)

### Configuration
```env
MARKETAUX_API_KEY=your_api_key_here
MARKETAUX_RATE_LIMIT=100  # Requests per minute
ENABLE_NEWS_CACHE=true
NEWS_REFRESH_INTERVAL=900  # 15 minutes
```

### API Documentation
https://www.marketaux.com/documentation

## Interface Definition

### NewsProvider Interface
```python
class NewsProvider(BaseProvider):
    @abstractmethod
    def search_news(params: NewsSearchParams) -> List[NewsArticle]
    
    @abstractmethod
    def get_article(article_id: str) -> Optional[NewsArticle]
    
    @abstractmethod
    def get_similar_articles(
        article_id: str, 
        limit: int = 10
    ) -> List[NewsArticle]
    
    @abstractmethod
    def get_trending_entities(
        entity_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]
    
    @abstractmethod
    def get_entity_sentiment(
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]
```

## Data Models

### NewsArticle
```python
@dataclass
class NewsArticle:
    uuid: str                      # Unique identifier
    title: str                     # Article headline
    description: str               # Brief summary
    url: str                       # Original article URL
    source: str                    # Publisher name
    published_at: datetime         # Publication time
    content: Optional[str]         # Full article text
    image_url: Optional[str]       # Featured image
    language: str = "en"           # Language code
    country: Optional[str]         # Country code
    entities: List[NewsEntity]     # Mentioned entities
    sentiment: Optional[NewsSentiment]  # Sentiment analysis
    keywords: List[str]            # Article keywords
    categories: List[str]          # News categories
```

### NewsSentiment
```python
@dataclass
class NewsSentiment:
    score: float           # -1 (negative) to +1 (positive)
    label: SentimentLabel  # Classification label
    confidence: float      # 0 to 1 confidence score
```

### SentimentLabel
```python
class SentimentLabel(Enum):
    VERY_NEGATIVE = "very_negative"  # <= -0.6
    NEGATIVE = "negative"            # -0.6 to -0.2
    NEUTRAL = "neutral"              # -0.2 to 0.2
    POSITIVE = "positive"            # 0.2 to 0.6
    VERY_POSITIVE = "very_positive"  # >= 0.6
```

### NewsEntity
```python
@dataclass
class NewsEntity:
    symbol: str              # Stock ticker/identifier
    name: str                # Entity name
    type: str                # Entity type (company, person, etc.)
    exchange: Optional[str]  # Stock exchange
    country: Optional[str]   # Country code
    industry: Optional[str]  # Industry classification
    match_score: Optional[float]     # Relevance score
    sentiment_score: Optional[float]  # Entity-specific sentiment
```

### NewsSearchParams
```python
@dataclass
class NewsSearchParams:
    symbols: Optional[List[str]]          # Stock symbols
    keywords: Optional[List[str]]         # Search keywords
    sources: Optional[List[str]]          # News sources
    countries: Optional[List[str]]        # Country filters
    languages: Optional[List[str]]        # Language filters
    categories: Optional[List[str]]       # Category filters
    industries: Optional[List[str]]       # Industry filters
    sentiment_min: Optional[float]        # Min sentiment (-1 to 1)
    sentiment_max: Optional[float]        # Max sentiment (-1 to 1)
    published_after: Optional[datetime]   # Start date
    published_before: Optional[datetime]  # End date
    limit: int = 50                      # Results per page
    offset: int = 0                      # Pagination offset
```

## Marketaux Implementation Details

### Caching Strategy
```yaml
News Articles:
  TTL: 900 seconds (15 minutes)
  Key: "marketaux:search:{params_hash}"
  Rationale: News updates frequently

Sentiment Data:
  TTL: 3600 seconds (1 hour)
  Key: "marketaux:sentiment:{symbol}:{date_range}"
  Rationale: Sentiment changes slowly

Trending Entities:
  TTL: 1800 seconds (30 minutes)
  Key: "marketaux:trending:{entity_type}"
  Rationale: Trends evolve moderately
```

### Rate Limiting
Marketaux uses standard rate limiting:
- Requests tracked per minute
- 429 status code when exceeded
- Retry-After header provided
- Automatic backoff implemented

## Usage Examples

### Searching News
```python
from app.providers.news import MarketauxProvider, NewsSearchParams
from datetime import datetime, timedelta

provider = MarketauxProvider()

# Search for positive Apple news
params = NewsSearchParams(
    symbols=["AAPL"],
    sentiment_min=0.5,  # Positive sentiment only
    published_after=datetime.now() - timedelta(days=7),
    limit=20
)

articles = provider.search_news(params)

for article in articles:
    print(f"Title: {article.title}")
    print(f"Sentiment: {article.sentiment.score:.2f} ({article.sentiment.label.value})")
    print(f"Source: {article.source}")
    print(f"Published: {article.published_at}")
    print(f"URL: {article.url}\n")
```

### Getting Article Details
```python
# Get specific article
article = provider.get_article("article-uuid-123")

if article:
    print(f"Title: {article.title}")
    print(f"Content: {article.content[:500]}...")
    
    # Display entities
    print("\nMentioned Companies:")
    for entity in article.entities:
        if entity.type == "company":
            print(f"  - {entity.name} ({entity.symbol})")
            if entity.sentiment_score:
                print(f"    Sentiment: {entity.sentiment_score:.2f}")
```

### Finding Similar Articles
```python
# Get similar articles
similar = provider.get_similar_articles("article-uuid-123", limit=5)

print(f"Found {len(similar)} similar articles:")
for article in similar:
    print(f"  - {article.title}")
    print(f"    Similarity: {article.source}")
```

### Analyzing Entity Sentiment
```python
# Get sentiment history for Apple
sentiment_data = provider.get_entity_sentiment(
    "AAPL",
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now()
)

print(f"Symbol: {sentiment_data['symbol']}")
print(f"Average Sentiment: {sentiment_data['sentiment_avg']:.2f}")
print(f"Total Articles: {sentiment_data.get('article_count', 0)}")

# Plot sentiment trend
if 'sentiment_trend' in sentiment_data:
    for point in sentiment_data['sentiment_trend']:
        print(f"{point['date']}: {point['score']:.2f} ({point['count']} articles)")
```

### Getting Trending Entities
```python
# Get trending companies
trending = provider.get_trending_entities(entity_type="company", limit=10)

print("Top Trending Companies:")
for i, entity in enumerate(trending, 1):
    print(f"{i}. {entity['name']} ({entity['symbol']})")
    print(f"   Mentions: {entity['mention_count']}")
    print(f"   Sentiment: {entity.get('average_sentiment', 0):.2f}")
```

## Advanced Features

### Sentiment Filtering
```python
# Get only negative news
negative_params = NewsSearchParams(
    symbols=["TSLA", "RIVN", "NIO"],
    sentiment_max=-0.3,  # Only negative sentiment
    limit=50
)

negative_news = provider.search_news(negative_params)

# Categorize by sentiment
very_negative = [a for a in negative_news if a.sentiment.score <= -0.6]
moderate_negative = [a for a in negative_news if -0.6 < a.sentiment.score <= -0.3]
```

### Multi-Symbol Analysis
```python
# Compare sentiment across multiple stocks
symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
sentiment_comparison = {}

for symbol in symbols:
    params = NewsSearchParams(
        symbols=[symbol],
        published_after=datetime.now() - timedelta(days=7)
    )
    articles = provider.search_news(params)
    
    if articles:
        avg_sentiment = sum(a.sentiment.score for a in articles) / len(articles)
        sentiment_comparison[symbol] = {
            'score': avg_sentiment,
            'count': len(articles)
        }

# Sort by sentiment
sorted_sentiment = sorted(
    sentiment_comparison.items(), 
    key=lambda x: x[1]['score'], 
    reverse=True
)

print("Sentiment Ranking (7 days):")
for symbol, data in sorted_sentiment:
    print(f"{symbol}: {data['score']:+.3f} ({data['count']} articles)")
```

### Entity Extraction
```python
# Extract all mentioned entities from articles
all_entities = {}

params = NewsSearchParams(
    keywords=["artificial intelligence", "AI"],
    limit=100
)
articles = provider.search_news(params)

for article in articles:
    for entity in article.entities:
        if entity.type == "company" and entity.symbol:
            if entity.symbol not in all_entities:
                all_entities[entity.symbol] = {
                    'name': entity.name,
                    'count': 0,
                    'sentiment_sum': 0
                }
            all_entities[entity.symbol]['count'] += 1
            if entity.sentiment_score:
                all_entities[entity.symbol]['sentiment_sum'] += entity.sentiment_score

# Most mentioned companies in AI news
top_mentioned = sorted(
    all_entities.items(), 
    key=lambda x: x[1]['count'], 
    reverse=True
)[:10]

print("Top Companies in AI News:")
for symbol, data in top_mentioned:
    avg_sentiment = data['sentiment_sum'] / data['count'] if data['count'] > 0 else 0
    print(f"{symbol} ({data['name']}): {data['count']} mentions, sentiment: {avg_sentiment:.2f}")
```

## Integration with Database

### Storing News Articles
```python
from app.models.news import NewsArticle as NewsArticleModel
from app.services.news import NewsService

# Fetch and store news
service = NewsService(db_session)
articles_fetched = service.refresh_news(symbols=["AAPL", "MSFT"])

print(f"Stored {articles_fetched} new articles")
```

### Querying Stored News
```python
# Search stored news with filters
stored_articles = service.search_news(
    symbols=["AAPL"],
    sentiment_min=0.5,
    published_after=datetime.now() - timedelta(days=30),
    limit=50
)
```

## Performance Optimization

### 1. Batch Symbol Processing
```python
# Process multiple symbols efficiently
symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]

# Single request with multiple symbols
params = NewsSearchParams(symbols=symbols, limit=100)
articles = provider.search_news(params)

# Group by symbol
articles_by_symbol = {}
for article in articles:
    for entity in article.entities:
        if entity.symbol in symbols:
            if entity.symbol not in articles_by_symbol:
                articles_by_symbol[entity.symbol] = []
            articles_by_symbol[entity.symbol].append(article)
```

### 2. Caching Strategy
```python
# Cache is automatic, but can be controlled
provider.cache_enabled = True  # Enable caching
provider.news_cache_ttl = 900  # 15 minutes

# Force cache refresh
provider.cache_enabled = False
fresh_articles = provider.search_news(params)
provider.cache_enabled = True
```

### 3. Parallel Requests
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def fetch_all_news_data(symbols: List[str]):
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Fetch different data types in parallel
        search_future = executor.submit(
            provider.search_news, 
            NewsSearchParams(symbols=symbols)
        )
        trending_future = executor.submit(
            provider.get_trending_entities
        )
        
        articles = search_future.result()
        trending = trending_future.result()
        
    return articles, trending
```

## Error Handling

### Common Errors and Solutions

#### 1. Rate Limit Exceeded
```python
try:
    articles = provider.search_news(params)
except RateLimitError as e:
    logger.warning(f"Rate limited, retry after {e.retry_after}s")
    time.sleep(e.retry_after)
    articles = provider.search_news(params)  # Retry
```

#### 2. Invalid Parameters
```python
try:
    # Invalid sentiment range
    params = NewsSearchParams(sentiment_min=2.0)  # Invalid: > 1
    articles = provider.search_news(params)
except ValueError as e:
    logger.error(f"Invalid parameters: {e}")
```

#### 3. Network Issues
```python
try:
    articles = provider.search_news(params)
except APIError as e:
    if e.status_code >= 500:
        # Server error, use cached data
        logger.error("Marketaux server error, using cache")
        articles = get_from_cache(params)
    else:
        raise
```

## Monitoring & Debugging

### Health Check
```python
status = provider.health_check()
print(f"Marketaux Status: {status.value}")

stats = provider.get_stats()
print(f"Requests: {stats['requests']}")
print(f"Error Rate: {stats['error_rate']:.2%}")
print(f"Circuit Breaker: {stats['circuit_breaker_state']}")
```

### Debug Logging
```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('app.providers.news')

# Logs will show:
# - API requests and responses
# - Cache operations
# - Rate limiting
# - Error details
```

## Best Practices

### 1. Filter at Source
```python
# Good: Filter at API level
params = NewsSearchParams(
    symbols=["AAPL"],
    sentiment_min=0.5,
    published_after=datetime.now() - timedelta(days=7)
)
articles = provider.search_news(params)

# Bad: Fetch all and filter locally
all_articles = provider.search_news(NewsSearchParams())
filtered = [a for a in all_articles if a.sentiment.score > 0.5]
```

### 2. Use Appropriate Limits
```python
# For real-time display
params = NewsSearchParams(limit=10)  # Quick response

# For analysis
params = NewsSearchParams(limit=100)  # More comprehensive

# For export/archive
params = NewsSearchParams(limit=500, offset=0)  # Paginate through all
```

### 3. Handle Missing Data
```python
article = provider.get_article("uuid")
if article:
    # Check for optional fields
    sentiment_score = article.sentiment.score if article.sentiment else 0
    image = article.image_url or "/default-image.png"
    content = article.content or article.description
```

## Future Enhancements

### Planned Features
1. **Real-time News Stream**
   - WebSocket connection
   - Push notifications
   - Event-driven updates

2. **Advanced Analytics**
   - Topic modeling
   - Trend prediction
   - Correlation analysis

3. **Custom Sentiment Models**
   - Financial-specific training
   - Entity-level sentiment
   - Aspect-based analysis

4. **Additional Providers**
   - Bloomberg News
   - Reuters
   - Financial Times
   - Yahoo Finance