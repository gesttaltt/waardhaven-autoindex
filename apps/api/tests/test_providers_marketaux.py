"""
Unit tests for Marketaux news provider.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import json

from app.providers.news import (
    MarketauxProvider,
    NewsSearchParams,
    SentimentLabel
)
from app.providers.base import APIError, RateLimitError, ProviderStatus


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    with patch('app.providers.news.marketaux.get_redis_client') as mock_redis:
        redis_instance = MagicMock()
        redis_instance.is_connected = True
        redis_instance.get.return_value = None
        redis_instance.set.return_value = True
        mock_redis.return_value = redis_instance
        yield redis_instance


@pytest.fixture
def mock_requests():
    """Mock requests library."""
    with patch('app.providers.news.marketaux.requests') as mock_req:
        yield mock_req


@pytest.fixture
def provider(mock_redis, mock_requests):
    """Create Marketaux provider with mocked dependencies."""
    with patch('app.providers.news.marketaux.settings') as mock_settings:
        mock_settings.MARKETAUX_API_KEY = "test_api_key"
        
        provider = MarketauxProvider(api_key="test_api_key")
        return provider


class TestMarketauxProvider:
    """Test Marketaux provider functionality."""
    
    def test_provider_initialization(self, provider):
        """Test provider initializes correctly."""
        assert provider.get_provider_name() == "Marketaux"
        assert provider.validate_config() is True
        assert provider.api_key == "test_api_key"
    
    def test_provider_without_api_key(self, mock_redis):
        """Test provider raises error without API key."""
        with patch('app.providers.news.marketaux.settings') as mock_settings:
            mock_settings.MARKETAUX_API_KEY = ""
            
            with pytest.raises(ValueError, match="API key not configured"):
                MarketauxProvider()
    
    def test_search_news_success(self, provider, mock_requests):
        """Test successful news search."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {
                    'uuid': 'article-1',
                    'title': 'Apple Reports Strong Earnings',
                    'description': 'Apple beats expectations',
                    'url': 'https://example.com/article-1',
                    'source': 'TechNews',
                    'published_at': '2024-01-15T10:00:00Z',
                    'snippet': 'Apple Inc. reported...',
                    'entities': [
                        {
                            'symbol': 'AAPL',
                            'name': 'Apple Inc.',
                            'type': 'company',
                            'sentiment_score': 0.8
                        }
                    ],
                    'sentiment': {
                        'score': 0.75,
                        'confidence': 0.9
                    },
                    'keywords': ['earnings', 'technology'],
                    'categories': ['Technology', 'Finance']
                }
            ]
        }
        mock_requests.get.return_value = mock_response
        
        # Search news
        params = NewsSearchParams(
            symbols=['AAPL'],
            limit=10
        )
        articles = provider.search_news(params)
        
        assert len(articles) == 1
        assert articles[0].title == 'Apple Reports Strong Earnings'
        assert articles[0].uuid == 'article-1'
        assert len(articles[0].entities) == 1
        assert articles[0].entities[0].symbol == 'AAPL'
        assert articles[0].sentiment.score == 0.75
    
    def test_search_news_with_filters(self, provider, mock_requests):
        """Test news search with various filters."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': []}
        mock_requests.get.return_value = mock_response
        
        # Search with filters
        params = NewsSearchParams(
            symbols=['AAPL', 'MSFT'],
            keywords=['earnings', 'revenue'],
            sentiment_min=0.5,
            sentiment_max=1.0,
            published_after=datetime(2024, 1, 1),
            published_before=datetime(2024, 1, 31),
            limit=50,
            offset=10
        )
        
        provider.search_news(params)
        
        # Verify API call parameters
        call_args = mock_requests.get.call_args
        params_sent = call_args[1]['params']
        
        assert params_sent['symbols'] == 'AAPL,MSFT'
        assert params_sent['search'] == 'earnings revenue'
        assert params_sent['sentiment_gte'] == 0.5
        assert params_sent['sentiment_lte'] == 1.0
        assert params_sent['limit'] == 50
        assert params_sent['page'] == 2  # offset 10 with limit 50 = page 2
    
    def test_get_article_success(self, provider, mock_requests):
        """Test getting specific article."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'uuid': 'article-123',
                'title': 'Market Update',
                'description': 'Latest market news',
                'url': 'https://example.com/article-123',
                'source': 'MarketWatch',
                'published_at': '2024-01-15T14:00:00Z'
            }
        }
        mock_requests.get.return_value = mock_response
        
        # Get article
        article = provider.get_article('article-123')
        
        assert article is not None
        assert article.uuid == 'article-123'
        assert article.title == 'Market Update'
        
        # Verify API endpoint
        call_args = mock_requests.get.call_args
        assert '/news/article-123' in call_args[0][0]
    
    def test_get_similar_articles(self, provider, mock_requests):
        """Test getting similar articles."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {
                    'uuid': 'similar-1',
                    'title': 'Related Article',
                    'description': 'Similar content',
                    'url': 'https://example.com/similar-1',
                    'source': 'NewsSource',
                    'published_at': '2024-01-15T15:00:00Z'
                }
            ]
        }
        mock_requests.get.return_value = mock_response
        
        # Get similar articles
        similar = provider.get_similar_articles('article-123', limit=5)
        
        assert len(similar) == 1
        assert similar[0].uuid == 'similar-1'
        
        # Verify API endpoint
        call_args = mock_requests.get.call_args
        assert '/news/similar/article-123' in call_args[0][0]
    
    def test_get_trending_entities(self, provider, mock_requests):
        """Test getting trending entities."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {
                    'symbol': 'AAPL',
                    'name': 'Apple Inc.',
                    'type': 'company',
                    'mention_count': 150,
                    'sentiment_avg': 0.65
                },
                {
                    'symbol': 'MSFT',
                    'name': 'Microsoft Corp.',
                    'type': 'company',
                    'mention_count': 120,
                    'sentiment_avg': 0.72
                }
            ]
        }
        mock_requests.get.return_value = mock_response
        
        # Get trending
        trending = provider.get_trending_entities(entity_type='company', limit=10)
        
        assert len(trending) == 2
        assert trending[0]['symbol'] == 'AAPL'
        assert trending[0]['mention_count'] == 150
    
    def test_get_entity_sentiment(self, provider, mock_requests):
        """Test getting entity sentiment over time."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'symbol': 'AAPL',
                'sentiment_avg': 0.68,
                'sentiment_data': [
                    {'date': '2024-01-01', 'score': 0.65, 'count': 10},
                    {'date': '2024-01-02', 'score': 0.70, 'count': 15}
                ]
            }
        }
        mock_requests.get.return_value = mock_response
        
        # Get sentiment
        sentiment = provider.get_entity_sentiment(
            'AAPL',
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31)
        )
        
        assert sentiment['symbol'] == 'AAPL'
        assert sentiment['sentiment_avg'] == 0.68
        assert len(sentiment['sentiment_data']) == 2
    
    def test_rate_limit_handling(self, provider, mock_requests):
        """Test rate limit error handling."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '60'}
        mock_requests.get.return_value = mock_response
        
        # Should raise RateLimitError
        with pytest.raises(RateLimitError) as exc_info:
            provider._make_api_request('/news/all', {})
        
        assert exc_info.value.retry_after == 60
    
    def test_api_error_handling(self, provider, mock_requests):
        """Test API error handling."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_requests.get.return_value = mock_response
        
        # Should raise APIError
        with pytest.raises(APIError) as exc_info:
            provider._make_api_request('/news/all', {})
        
        assert exc_info.value.status_code == 500
        assert "Internal Server Error" in str(exc_info.value)
    
    def test_health_check(self, provider, mock_requests):
        """Test health check functionality."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': []}
        mock_requests.get.return_value = mock_response
        
        # Check health
        status = provider.health_check()
        
        assert status == ProviderStatus.HEALTHY
    
    def test_parse_article_sentiment(self, provider):
        """Test article parsing with sentiment."""
        data = {
            'uuid': 'test-123',
            'title': 'Test Article',
            'description': 'Test description',
            'url': 'https://test.com',
            'source': 'TestSource',
            'published_at': '2024-01-15T10:00:00Z',
            'sentiment': {
                'score': -0.8,
                'confidence': 0.95
            }
        }
        
        article = provider._parse_article(data)
        
        assert article.sentiment is not None
        assert article.sentiment.score == -0.8
        assert article.sentiment.label == SentimentLabel.VERY_NEGATIVE
        assert article.sentiment.confidence == 0.95
    
    def test_parse_article_entities(self, provider):
        """Test article parsing with entities."""
        data = {
            'uuid': 'test-123',
            'title': 'Test Article',
            'description': 'Test description',
            'url': 'https://test.com',
            'source': 'TestSource',
            'published_at': '2024-01-15T10:00:00Z',
            'entities': [
                {
                    'symbol': 'AAPL',
                    'name': 'Apple Inc.',
                    'type': 'company',
                    'exchange': 'NASDAQ',
                    'country': 'US',
                    'industry': 'Technology',
                    'match_score': 0.95,
                    'sentiment_score': 0.7
                },
                {
                    'symbol': 'MSFT',
                    'name': 'Microsoft Corp.',
                    'type': 'company',
                    'sentiment_score': 0.6
                }
            ]
        }
        
        article = provider._parse_article(data)
        
        assert len(article.entities) == 2
        assert article.entities[0].symbol == 'AAPL'
        assert article.entities[0].exchange == 'NASDAQ'
        assert article.entities[0].sentiment_score == 0.7
        assert article.entities[1].symbol == 'MSFT'
    
    def test_cache_functionality(self, provider, mock_redis, mock_requests):
        """Test caching of news data."""
        # First call - cache miss
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [{
                'uuid': 'cached-1',
                'title': 'Cached Article',
                'description': 'Test',
                'url': 'https://test.com',
                'source': 'Test',
                'published_at': '2024-01-15T10:00:00Z'
            }]
        }
        mock_requests.get.return_value = mock_response
        
        # Search news
        params = NewsSearchParams(symbols=['AAPL'])
        articles1 = provider.search_news(params)
        
        # Verify cache was set
        mock_redis.set.assert_called()
        
        # Second call - cache hit
        mock_redis.get.return_value = json.dumps([a.to_dict() for a in articles1])
        mock_requests.get.reset_mock()
        
        articles2 = provider.search_news(params)
        
        # API should not be called (cache hit)
        mock_requests.get.assert_not_called()
        
        # Results should be the same
        assert len(articles2) == len(articles1)
        assert articles2[0].uuid == articles1[0].uuid
    
    def test_request_timeout(self, provider, mock_requests):
        """Test request timeout handling."""
        import requests
        mock_requests.get.side_effect = requests.RequestException("Connection timeout")
        
        # Should raise APIError
        with pytest.raises(APIError, match="Failed to connect"):
            provider._make_api_request('/news/all', {})
    
    def test_empty_response_handling(self, provider, mock_requests):
        """Test handling of empty API responses."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': []}
        mock_requests.get.return_value = mock_response
        
        # Search should return empty list
        params = NewsSearchParams(symbols=['UNKNOWN'])
        articles = provider.search_news(params)
        
        assert articles == []
        
        # Get article should return None
        mock_response.json.return_value = {}
        article = provider.get_article('unknown-id')
        
        assert article is None