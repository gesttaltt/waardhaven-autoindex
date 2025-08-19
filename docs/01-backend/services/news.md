# News Service

## Overview
Service for managing news data, sentiment analysis, and entity tracking.

## Location
`apps/api/app/services/news.py`

## Purpose
Provides business logic for news operations including search, sentiment analysis, entity extraction, and trending topic identification.

## Class: NewsService

### Initialization
```python
NewsService(db: Session)
```
- Initializes with database session
- Creates MarketauxProvider instance for external data
- Sets up Redis client for caching

## Main Methods

### search_news()
Search for news articles in database and fetch new ones if needed.

**Parameters:**
- `symbols`: List of stock symbols to filter
- `keywords`: Search keywords for title/description
- `sentiment_min`: Minimum sentiment score filter
- `sentiment_max`: Maximum sentiment score filter
- `published_after`: Date filter for newer articles
- `published_before`: Date filter for older articles
- `limit`: Number of results to return
- `offset`: Pagination offset

**Features:**
- Searches database first
- Fetches from provider if insufficient results
- Filters by symbols via entity relationships
- Full-text search on title and description
- Sentiment score filtering
- Date range filtering
- Pagination support

**Returns:** List of article dictionaries

### get_article(article_id: str)
Get a specific article by its external ID.

**Returns:** Article dictionary or None

### get_similar_articles(article_id: str, limit: int)
Find articles similar to a given article.

**Features:**
- Matches by entities mentioned
- Considers sentiment similarity
- Returns related articles

**Returns:** List of similar article dictionaries

### get_entity_sentiment(symbol: str, start_date: datetime, end_date: datetime)
Get sentiment analysis for a specific entity over time.

**Features:**
- Aggregates sentiment scores by date
- Tracks positive/negative/neutral counts
- Calculates sentiment trends
- Returns historical sentiment data

**Returns:** Entity sentiment analysis dictionary

### get_trending_entities(entity_type: Optional[str], limit: int)
Identify trending entities based on mention frequency and sentiment.

**Features:**
- Counts entity mentions in recent period
- Calculates sentiment changes
- Filters by entity type if specified
- Orders by mention count

**Returns:** List of trending entity dictionaries

### refresh_news(symbols: Optional[List[str]])
Refresh news data for specified symbols or all assets.

**Process:**
1. Gets symbols from database if not provided
2. Fetches news from provider
3. Stores articles in database
4. Extracts entities
5. Calculates sentiment scores

**Returns:** Dictionary with refresh statistics

### get_stats()
Get statistics about news data in the database.

**Returns:** Dictionary with counts and date ranges

## Helper Methods

### _fetch_and_store_news(symbols: List[str], limit: int)
Internal method to fetch news from provider and store in database.

**Process:**
1. Calls provider API
2. Creates/updates source records
3. Stores articles
4. Links to assets
5. Extracts entities

### _article_to_dict(article: NewsArticleModel)
Converts SQLAlchemy model to dictionary response.

**Includes:**
- Article metadata
- Sentiment information
- Related entities
- Source information

### _extract_entities(article: NewsArticleModel)
Extract entities mentioned in an article.

**Note:** Currently returns empty list (not implemented)

### _calculate_sentiment(article: NewsArticleModel)
Calculate sentiment score for an article.

**Note:** Currently returns neutral (0.0) - not implemented

## Data Flow

1. **Search Request** → Check DB → Fetch if needed → Return results
2. **Refresh Request** → Fetch from provider → Store → Extract entities → Calculate sentiment
3. **Sentiment Query** → Aggregate DB data → Calculate trends → Return analysis
4. **Trending Query** → Count mentions → Calculate changes → Sort by relevance

## Caching Strategy
- Uses Redis for caching when available
- Cache keys based on query parameters
- Automatic cache invalidation on refresh

## Error Handling
- Graceful fallback on provider failures
- Logs errors for debugging
- Returns partial results when possible
- Validates input parameters

## Dependencies
- `models.news`: News database models
- `models.asset`: Asset model for linking
- `providers.news.MarketauxProvider`: External news data
- `core.redis_client`: Caching layer
- SQLAlchemy for database operations

## Usage Example

```python
from app.services.news import NewsService
from app.core.database import get_db

db = next(get_db())
service = NewsService(db)

# Search for news
articles = service.search_news(
    symbols=["AAPL", "MSFT"],
    sentiment_min=0.5,
    limit=10
)

# Get trending entities
trending = service.get_trending_entities(
    entity_type="company",
    limit=5
)

# Refresh news data
result = service.refresh_news(["AAPL"])
```

## Note on Implementation
While the service structure is in place, some features are not fully implemented:
- Entity extraction returns empty list
- Sentiment calculation returns neutral (0.0)
- These features are planned for future implementation