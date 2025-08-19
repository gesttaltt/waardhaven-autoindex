# News Router

## Overview
Handles financial news retrieval, sentiment analysis, and entity tracking for portfolio assets.

## Location
`apps/api/app/routers/news.py`

## Important Note
The news router is registered with prefix `/news`, so all endpoints are under `/api/v1/news/`.

## Endpoints

### GET /api/v1/news/search
Search for news articles with various filters.

**Query Parameters:**
- `symbols`: Comma-separated list of stock symbols
- `keywords`: Search keywords
- `sentiment_min`: Minimum sentiment score (-1 to 1)
- `sentiment_max`: Maximum sentiment score (-1 to 1)
- `published_after`: ISO date string
- `published_before`: ISO date string
- `limit`: Number of results (default: 50)
- `offset`: Pagination offset

**Response:**
```json
{
  "articles": [
    {
      "id": "uuid",
      "title": "string",
      "description": "string",
      "url": "string",
      "source": "string",
      "published_at": "2024-01-01T00:00:00Z",
      "sentiment_score": 0.5,
      "entities": ["AAPL", "MSFT"]
    }
  ],
  "total": 100
}
```

### GET /api/v1/news/article/{article_id}
Get a specific news article by ID.

**Response:**
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "content": "string",
  "url": "string",
  "source": "string",
  "published_at": "2024-01-01T00:00:00Z",
  "sentiment": {
    "score": 0.5,
    "label": "positive",
    "confidence": 0.85
  },
  "entities": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "type": "company",
      "sentiment_score": 0.6,
      "mention_count": 3
    }
  ]
}
```

### GET /api/v1/news/sentiment/{symbol}
Get sentiment analysis for a specific symbol.

**Response:**
```json
{
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "current_sentiment": 0.6,
  "sentiment_trend": "improving",
  "article_count_24h": 15,
  "article_count_7d": 120,
  "recent_articles": [...],
  "sentiment_history": [
    {
      "date": "2024-01-01",
      "sentiment_score": 0.5,
      "article_count": 10
    }
  ]
}
```

### GET /api/v1/news/trending
Get trending entities based on news volume and sentiment.

**Query Parameters:**
- `entity_type`: Filter by type (company, person, location, product)
- `limit`: Number of results (default: 20)

**Response:**
```json
{
  "trending": [
    {
      "symbol": "NVDA",
      "name": "NVIDIA Corporation",
      "type": "company",
      "mention_count_24h": 250,
      "sentiment_score": 0.7,
      "sentiment_change": 0.2,
      "top_headlines": [...]
    }
  ]
}
```

### POST /api/v1/news/refresh
Manually trigger news data refresh (requires authentication).

**Request Body:**
```json
{
  "symbols": ["AAPL", "MSFT"],
  "lookback_days": 7
}
```

**Response:**
```json
{
  "status": "success",
  "articles_fetched": 150,
  "new_articles": 45,
  "symbols_processed": ["AAPL", "MSFT"]
}
```

## Additional Endpoints

### GET /api/v1/news/similar/{article_id}
Get articles similar to a given article.

**Query Parameters:**
- `limit`: Number of results (default: 10, max: 50)

### GET /api/v1/news/stats
Get statistics about news data in the database.

## Data Flow

1. **News Fetching**
   - MarketAux provider fetches articles
   - Articles stored in NewsArticle model
   - Entities extracted and linked

2. **Sentiment Analysis**
   - Articles analyzed for sentiment
   - Per-entity sentiment calculated
   - Historical sentiment tracked

3. **Entity Tracking**
   - Companies, people, products identified
   - Relevance scores calculated
   - Trending entities determined

## Provider Integration

The news router uses the MarketAux provider:
- Rate limiting: 500 requests/day
- Automatic retry with backoff
- Circuit breaker for failures
- Response caching

## Database Models

- **NewsArticle**: Main article storage
- **NewsSentiment**: Sentiment analysis results
- **NewsEntity**: Extracted entities
- **NewsSource**: Article publishers
- **EntitySentimentHistory**: Historical tracking

## Caching Strategy

- Article searches: 5 minutes
- Individual articles: 1 hour
- Sentiment data: 15 minutes
- Trending entities: 5 minutes

## Error Handling

- Provider failures: Returns cached data if available
- Invalid symbols: Returns empty results
- Rate limiting: 429 status with retry-after header

## Security

- All endpoints require authentication
- Admin token required for manual refresh
- Rate limiting per user
- Input validation for all parameters

## Related Modules
- `providers/news/marketaux.py`: MarketAux integration
- `services/news.py`: Business logic
- `models/news.py`: Database models
- `schemas/news.py`: Request/response schemas