"""
Unit tests for news service.
"""

import pytest
from unittest.mock import patch, MagicMock, create_autospec
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.news import NewsService
from app.models.news import (
    EntitySentimentHistory
)
from app.models.asset import Asset
from app.providers.news import NewsArticle, NewsSentiment, NewsEntity


@pytest.fixture
def mock_db():
    """Mock database session."""
    db = create_autospec(Session)
    db.query.return_value = db
    db.filter.return_value = db
    db.join.return_value = db
    db.order_by.return_value = db
    db.offset.return_value = db
    db.limit.return_value = db
    db.group_by.return_value = db
    db.all.return_value = []
    db.first.return_value = None
    db.count.return_value = 0
    db.scalar.return_value = 0
    return db


@pytest.fixture
def mock_provider():
    """Mock Marketaux provider."""
    with patch('app.services.news.MarketauxProvider') as mock_provider_class:
        provider = MagicMock()
        mock_provider_class.return_value = provider
        yield provider


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    with patch('app.services.news.get_redis_client') as mock_redis:
        redis_instance = MagicMock()
        redis_instance.is_connected = True
        mock_redis.return_value = redis_instance
        yield redis_instance


@pytest.fixture
def news_service(mock_db, mock_provider, mock_redis):
    """Create news service with mocked dependencies."""
    service = NewsService(mock_db)
    service.provider = mock_provider
    return service


class TestNewsService:
    """Test news service functionality."""
    
    def test_search_news_from_database(self, news_service, mock_db):
        """Test searching news from database."""
        # Mock database articles
        mock_articles = [
            MagicMock(
                external_id='art-1',
                title='Article 1',
                description='Description 1',
                url='https://example.com/1',
                source_name='Source1',
                published_at=datetime.now(),
                entities=[],
                sentiment=MagicMock(
                    sentiment_score=0.5,
                    sentiment_label='positive',
                    confidence=0.8
                )
            )
        ]
        mock_db.all.return_value = mock_articles
        mock_db.count.return_value = 1
        
        # Search news
        results = news_service.search_news(
            symbols=['AAPL'],
            limit=10
        )
        
        assert len(results) == 1
        assert results[0]['title'] == 'Article 1'
        assert results[0]['sentiment']['score'] == 0.5
    
    def test_search_news_fetches_fresh_data(self, news_service, mock_db, mock_provider):
        """Test fetching fresh news when database is empty."""
        # Database returns empty
        mock_db.all.return_value = []
        mock_db.count.return_value = 0
        
        # Provider returns articles
        mock_provider.search_news.return_value = [
            NewsArticle(
                uuid='fresh-1',
                title='Fresh Article',
                description='New content',
                url='https://example.com/fresh',
                source='FreshSource',
                published_at=datetime.now(),
                sentiment=NewsSentiment.from_score(0.7)
            )
        ]
        
        # Search news
        news_service.search_news(
            symbols=['AAPL'],
            limit=10
        )
        
        # Should fetch from provider
        mock_provider.search_news.assert_called_once()
        
        # Should store in database
        mock_db.add.assert_called()
        mock_db.flush.assert_called()
    
    def test_search_news_with_filters(self, news_service, mock_db):
        """Test news search with various filters."""
        # Search with filters
        news_service.search_news(
            symbols=['AAPL', 'MSFT'],
            keywords='earnings',
            sentiment_min=0.5,
            sentiment_max=1.0,
            published_after=datetime(2024, 1, 1),
            published_before=datetime(2024, 1, 31)
        )
        
        # Verify database query filters
        mock_db.filter.assert_called()
        mock_db.join.assert_called()
    
    def test_get_article_from_database(self, news_service, mock_db):
        """Test getting article from database."""
        # Mock article in database
        mock_article = MagicMock(
            external_id='art-123',
            title='Test Article',
            entities=[],
            sentiment=None
        )
        mock_db.first.return_value = mock_article
        
        # Get article
        result = news_service.get_article('art-123')
        
        assert result is not None
        assert result['id'] == 'art-123'
        assert result['title'] == 'Test Article'
    
    def test_get_article_from_provider(self, news_service, mock_db, mock_provider):
        """Test fetching article from provider when not in database."""
        # Database returns None
        mock_db.first.return_value = None
        
        # Provider returns article
        mock_provider.get_article.return_value = NewsArticle(
            uuid='provider-123',
            title='Provider Article',
            description='From provider',
            url='https://example.com/provider',
            source='Provider',
            published_at=datetime.now()
        )
        
        # Get article
        news_service.get_article('provider-123')
        
        # Should fetch from provider
        mock_provider.get_article.assert_called_once_with('provider-123')
        
        # Should store in database
        mock_db.add.assert_called()
    
    def test_get_similar_articles(self, news_service, mock_db, mock_provider):
        """Test getting similar articles."""
        # Provider returns similar articles
        mock_provider.get_similar_articles.return_value = [
            NewsArticle(
                uuid='similar-1',
                title='Similar Article',
                description='Similar content',
                url='https://example.com/similar',
                source='Source',
                published_at=datetime.now()
            )
        ]
        
        # Get similar articles
        results = news_service.get_similar_articles('art-123', limit=5)
        
        assert len(results) == 1
        assert results[0]['title'] == 'Similar Article'
        
        # Should call provider
        mock_provider.get_similar_articles.assert_called_once_with('art-123', 5)
    
    def test_get_entity_sentiment_with_history(self, news_service, mock_db):
        """Test getting entity sentiment with existing history."""
        # Mock sentiment history
        mock_history = [
            MagicMock(
                date=datetime(2024, 1, 1),
                sentiment_score=0.6,
                article_count=10,
                positive_count=6,
                negative_count=2,
                neutral_count=2
            ),
            MagicMock(
                date=datetime(2024, 1, 2),
                sentiment_score=0.7,
                article_count=15,
                positive_count=10,
                negative_count=3,
                neutral_count=2
            )
        ]
        
        # Configure mock returns
        def query_side_effect(model):
            if model == EntitySentimentHistory:
                mock_query = MagicMock()
                mock_query.filter.return_value = mock_query
                mock_query.order_by.return_value = mock_query
                mock_query.all.return_value = mock_history
                return mock_query
            return mock_db
        
        mock_db.query.side_effect = query_side_effect
        
        # Get sentiment
        result = news_service.get_entity_sentiment(
            'AAPL',
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31)
        )
        
        assert result['symbol'] == 'AAPL'
        assert result['total_articles'] == 25  # 10 + 15
        assert len(result['sentiment_trend']) == 2
        assert result['sentiment_trend'][0]['sentiment_score'] == 0.6
    
    def test_get_trending_entities_from_provider(self, news_service, mock_provider):
        """Test getting trending entities from provider."""
        # Provider returns trending data
        mock_provider.get_trending_entities.return_value = [
            {
                'symbol': 'AAPL',
                'name': 'Apple Inc.',
                'type': 'company',
                'mention_count': 100,
                'average_sentiment': 0.7
            }
        ]
        
        # Get trending
        results = news_service.get_trending_entities(entity_type='company')
        
        assert len(results) == 1
        assert results[0]['symbol'] == 'AAPL'
        assert results[0]['mention_count'] == 100
    
    def test_refresh_news(self, news_service, mock_db, mock_provider):
        """Test refreshing news for symbols."""
        # Mock assets in database
        mock_assets = [
            MagicMock(symbol='AAPL'),
            MagicMock(symbol='MSFT')
        ]
        
        def query_side_effect(model):
            if model == Asset:
                mock_query = MagicMock()
                mock_query.all.return_value = mock_assets
                return mock_query
            return mock_db
        
        mock_db.query.side_effect = query_side_effect
        
        # Provider returns articles
        mock_provider.search_news.return_value = [
            NewsArticle(
                uuid='refresh-1',
                title='Refreshed Article',
                description='Fresh content',
                url='https://example.com/refresh',
                source='Source',
                published_at=datetime.now()
            )
        ]
        
        # Refresh news
        result = news_service.refresh_news()
        
        assert result['symbols_processed'] == 2
        assert result['articles_fetched'] >= 0
        
        # Should call provider for each symbol
        assert mock_provider.search_news.call_count == 2
    
    def test_get_stats(self, news_service, mock_db):
        """Test getting news statistics."""
        # Mock database counts
        mock_db.scalar.side_effect = [100, 10, 25]  # articles, sources, recent
        
        # Mock sentiment distribution
        sentiment_stats = [
            MagicMock(sentiment_label='positive', count=40),
            MagicMock(sentiment_label='negative', count=30),
            MagicMock(sentiment_label='neutral', count=30)
        ]
        
        def query_side_effect(model):
            query = MagicMock()
            query.scalar.return_value = 100
            query.filter.return_value = query
            query.group_by.return_value = query
            query.all.return_value = sentiment_stats
            return query
        
        mock_db.query.side_effect = query_side_effect
        
        # Get stats
        stats = news_service.get_stats()
        
        assert stats['total_articles'] == 100
        assert 'sentiment_distribution' in stats
        assert stats['sentiment_distribution']['positive'] == 40
    
    def test_store_article_with_entities(self, news_service, mock_db):
        """Test storing article with entities and sentiment."""
        # Create article data
        article_data = NewsArticle(
            uuid='store-1',
            title='Test Store',
            description='Test',
            url='https://example.com/store',
            source='TestSource',
            published_at=datetime.now(),
            entities=[
                NewsEntity(
                    symbol='AAPL',
                    name='Apple Inc.',
                    type='company',
                    sentiment_score=0.8
                )
            ],
            sentiment=NewsSentiment.from_score(0.75)
        )
        
        # Mock asset exists
        mock_asset = MagicMock(id=1, symbol='AAPL')
        
        def query_side_effect(model):
            query = MagicMock()
            if model == Asset:
                query.filter.return_value = query
                query.first.return_value = mock_asset
            else:
                query.filter.return_value = query
                query.first.return_value = None
            return query
        
        mock_db.query.side_effect = query_side_effect
        
        # Store article
        news_service._store_article(article_data)
        
        # Should create article
        assert mock_db.add.called
        assert mock_db.flush.called
        
        # Should link to asset
        mock_db.execute.assert_called()
    
    def test_calculate_sentiment_history(self, news_service, mock_db):
        """Test calculating sentiment history from articles."""
        # Mock articles with sentiment
        mock_articles = [
            MagicMock(
                published_at=datetime(2024, 1, 1, 10, 0),
                sentiment=MagicMock(sentiment_score=0.5)
            ),
            MagicMock(
                published_at=datetime(2024, 1, 1, 14, 0),
                sentiment=MagicMock(sentiment_score=0.7)
            ),
            MagicMock(
                published_at=datetime(2024, 1, 2, 9, 0),
                sentiment=MagicMock(sentiment_score=-0.3)
            )
        ]
        
        def query_side_effect(model):
            query = MagicMock()
            query.join.return_value = query
            query.filter.return_value = query
            query.all.return_value = mock_articles
            return query
        
        mock_db.query.side_effect = query_side_effect
        
        # Calculate history
        news_service._calculate_sentiment_history(
            'AAPL',
            datetime(2024, 1, 1),
            datetime(2024, 1, 2)
        )
        
        # Should create history records
        assert mock_db.add.called
        assert mock_db.commit.called
    
    def test_error_handling_in_store_article(self, news_service, mock_db):
        """Test error handling when storing article fails."""
        # Create article data
        article_data = NewsArticle(
            uuid='error-1',
            title='Error Test',
            description='Test',
            url='https://example.com/error',
            source='ErrorSource',
            published_at=datetime.now()
        )
        
        # Make database operations fail
        mock_db.add.side_effect = Exception("Database error")
        
        # Store article should handle error
        result = news_service._store_article(article_data)
        
        assert result is None
        mock_db.rollback.assert_called()