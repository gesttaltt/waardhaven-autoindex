"""
Marketaux news provider implementation.
Provides financial news with sentiment analysis and entity extraction.
"""

import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode

from .interface import (
    NewsProvider,
    NewsArticle,
    NewsSentiment,
    NewsEntity,
    NewsSearchParams,
    SentimentLabel
)
from ..base import ProviderStatus, APIError, RateLimitError
from ...core.config import settings
from ...core.redis_client import get_redis_client

logger = logging.getLogger(__name__)


class MarketauxProvider(NewsProvider):
    """
    Marketaux API provider implementation.
    Provides financial news, sentiment analysis, and entity extraction.
    """
    
    BASE_URL = "https://api.marketaux.com/v1"
    
    def __init__(self, api_key: Optional[str] = None, cache_enabled: bool = True):
        super().__init__(api_key or settings.MARKETAUX_API_KEY, cache_enabled)
        
        if not self.api_key:
            raise ValueError("Marketaux API key not configured")
        
        self.redis_client = get_redis_client()
        
        # Cache TTL settings
        self.news_cache_ttl = 900     # 15 minutes
        self.sentiment_cache_ttl = 3600  # 1 hour
        self.entity_cache_ttl = 1800  # 30 minutes
    
    def get_provider_name(self) -> str:
        return "Marketaux"
    
    def validate_config(self) -> bool:
        """Validate API key configuration."""
        return bool(self.api_key)
    
    def health_check(self) -> ProviderStatus:
        """Check Marketaux API health."""
        try:
            # Try a simple API call with minimal parameters
            response = self._make_api_request(
                "/news/all",
                params={"limit": 1}
            )
            
            if response and 'data' in response:
                return ProviderStatus.HEALTHY
            else:
                return ProviderStatus.DEGRADED
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return ProviderStatus.UNHEALTHY
    
    def _make_api_request(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        method: str = "GET"
    ) -> Dict[str, Any]:
        """Make API request to Marketaux."""
        if params is None:
            params = {}
        
        # Add API key
        params['api_token'] = self.api_key
        
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, params=params, timeout=30)
            else:
                response = requests.post(url, json=params, timeout=30)
            
            # Check for rate limiting
            if response.status_code == 429:
                retry_after = response.headers.get('Retry-After', 60)
                raise RateLimitError(
                    "Marketaux rate limit exceeded",
                    retry_after=int(retry_after)
                )
            
            # Check for errors
            if response.status_code != 200:
                raise APIError(
                    f"Marketaux API error: {response.text}",
                    status_code=response.status_code
                )
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise APIError(f"Failed to connect to Marketaux: {e}")
    
    def _execute_request(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Execute API request (called by base class retry logic)."""
        return self._make_api_request(endpoint, params)
    
    def _get_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key."""
        parts = [f"marketaux:{prefix}"]
        for k, v in sorted(kwargs.items()):
            if v is not None:
                if isinstance(v, list):
                    v = ",".join(str(x) for x in v)
                parts.append(f"{k}:{v}")
        return ":".join(parts)
    
    def search_news(self, params: NewsSearchParams) -> List[NewsArticle]:
        """Search for news articles."""
        # Build API parameters
        api_params = {
            "limit": params.limit,
            "page": params.offset // params.limit + 1 if params.offset else 1
        }
        
        # Add optional filters
        if params.symbols:
            api_params["symbols"] = ",".join(params.symbols)
        
        if params.keywords:
            api_params["search"] = " ".join(params.keywords)
        
        if params.sources:
            api_params["domains"] = ",".join(params.sources)
        
        if params.countries:
            api_params["countries"] = ",".join(params.countries)
        
        if params.languages:
            api_params["languages"] = ",".join(params.languages)
        
        if params.industries:
            api_params["industries"] = ",".join(params.industries)
        
        if params.sentiment_min is not None:
            api_params["sentiment_gte"] = params.sentiment_min
        
        if params.sentiment_max is not None:
            api_params["sentiment_lte"] = params.sentiment_max
        
        if params.published_after:
            api_params["published_after"] = params.published_after.isoformat()
        
        if params.published_before:
            api_params["published_before"] = params.published_before.isoformat()
        
        # Check cache
        cache_key = self._get_cache_key("search", **api_params)
        if self.cache_enabled and self.redis_client.is_connected:
            try:
                import json
                cached = self.redis_client.get(cache_key)
                if cached:
                    logger.debug(f"Cache hit: {cache_key}")
                    articles_data = json.loads(cached)
                    return [self._parse_article(a) for a in articles_data]
            except Exception as e:
                logger.debug(f"Cache get failed: {e}")
        
        # Make API request
        response = self.make_request("/news/all", api_params)
        
        if not response or 'data' not in response:
            return []
        
        articles = [self._parse_article(article) for article in response['data']]
        
        # Cache results
        if self.cache_enabled and self.redis_client.is_connected and articles:
            try:
                import json
                articles_data = [a.to_dict() for a in articles]
                self.redis_client.set(
                    cache_key,
                    json.dumps(articles_data),
                    expire=self.news_cache_ttl
                )
                logger.debug(f"Cached: {cache_key}")
            except Exception as e:
                logger.debug(f"Cache set failed: {e}")
        
        return articles
    
    def _parse_article(self, data: Dict) -> NewsArticle:
        """Parse API response into NewsArticle."""
        # Parse entities
        entities = []
        if 'entities' in data:
            for entity in data['entities']:
                entities.append(NewsEntity(
                    symbol=entity.get('symbol', ''),
                    name=entity.get('name', ''),
                    type=entity.get('type', 'unknown'),
                    exchange=entity.get('exchange'),
                    country=entity.get('country'),
                    industry=entity.get('industry'),
                    match_score=entity.get('match_score'),
                    sentiment_score=entity.get('sentiment_score')
                ))
        
        # Parse sentiment
        sentiment = None
        if 'sentiment' in data:
            sentiment = NewsSentiment.from_score(
                score=data['sentiment'].get('score', 0),
                confidence=data['sentiment'].get('confidence', 0.5)
            )
        
        # Parse datetime
        published_at = datetime.fromisoformat(
            data['published_at'].replace('Z', '+00:00')
        ) if 'published_at' in data else datetime.now()
        
        return NewsArticle(
            uuid=data.get('uuid', ''),
            title=data.get('title', ''),
            description=data.get('description', ''),
            url=data.get('url', ''),
            source=data.get('source', ''),
            published_at=published_at,
            content=data.get('snippet'),  # Marketaux uses 'snippet' for content
            image_url=data.get('image_url'),
            language=data.get('language', 'en'),
            country=data.get('country'),
            entities=entities,
            sentiment=sentiment,
            keywords=data.get('keywords', []),
            categories=data.get('categories', [])
        )
    
    def get_article(self, article_id: str) -> Optional[NewsArticle]:
        """Get specific article by UUID."""
        # Check cache
        cache_key = self._get_cache_key("article", uuid=article_id)
        if self.cache_enabled and self.redis_client.is_connected:
            try:
                import json
                cached = self.redis_client.get(cache_key)
                if cached:
                    logger.debug(f"Cache hit: {cache_key}")
                    return self._parse_article(json.loads(cached))
            except Exception as e:
                logger.debug(f"Cache get failed: {e}")
        
        # Make API request
        response = self.make_request(f"/news/{article_id}")
        
        if not response or 'data' not in response:
            return None
        
        article = self._parse_article(response['data'])
        
        # Cache result
        if self.cache_enabled and self.redis_client.is_connected:
            try:
                import json
                self.redis_client.set(
                    cache_key,
                    json.dumps(response['data']),
                    expire=self.news_cache_ttl
                )
            except Exception as e:
                logger.debug(f"Cache set failed: {e}")
        
        return article
    
    def get_similar_articles(
        self,
        article_id: str,
        limit: int = 10
    ) -> List[NewsArticle]:
        """Get similar articles."""
        response = self.make_request(
            f"/news/similar/{article_id}",
            params={"limit": limit}
        )
        
        if not response or 'data' not in response:
            return []
        
        return [self._parse_article(article) for article in response['data']]
    
    def get_trending_entities(
        self,
        entity_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get trending entities."""
        params = {"limit": limit}
        if entity_type:
            params["entity_type"] = entity_type
        
        response = self.make_request("/entity/trending", params)
        
        if not response or 'data' not in response:
            return []
        
        return response['data']
    
    def get_entity_sentiment(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get entity sentiment over time."""
        params = {"symbol": symbol}
        
        if start_date:
            params["from"] = start_date.isoformat()
        
        if end_date:
            params["to"] = end_date.isoformat()
        
        # Check cache
        cache_key = self._get_cache_key("sentiment", **params)
        if self.cache_enabled and self.redis_client.is_connected:
            try:
                import json
                cached = self.redis_client.get(cache_key)
                if cached:
                    logger.debug(f"Cache hit: {cache_key}")
                    return json.loads(cached)
            except Exception as e:
                logger.debug(f"Cache get failed: {e}")
        
        response = self.make_request("/entity/stats/time", params)
        
        if not response or 'data' not in response:
            return {}
        
        result = response['data']
        
        # Cache result
        if self.cache_enabled and self.redis_client.is_connected:
            try:
                import json
                self.redis_client.set(
                    cache_key,
                    json.dumps(result),
                    expire=self.sentiment_cache_ttl
                )
            except Exception as e:
                logger.debug(f"Cache set failed: {e}")
        
        return result