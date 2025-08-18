"""
News provider interface and data models.
"""

from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

from ..base import BaseProvider


class SentimentLabel(Enum):
    """Sentiment classification labels."""

    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


@dataclass
class NewsEntity:
    """Entity mentioned in news article."""

    symbol: str
    name: str
    type: str  # company, person, location, etc.
    exchange: Optional[str] = None
    country: Optional[str] = None
    industry: Optional[str] = None
    match_score: Optional[float] = None
    sentiment_score: Optional[float] = None


@dataclass
class NewsSentiment:
    """Sentiment analysis result."""

    score: float  # -1 to 1
    label: SentimentLabel
    confidence: float  # 0 to 1

    @classmethod
    def from_score(cls, score: float, confidence: float = 0.8):
        """Create sentiment from score."""
        if score <= -0.6:
            label = SentimentLabel.VERY_NEGATIVE
        elif score <= -0.2:
            label = SentimentLabel.NEGATIVE
        elif score <= 0.2:
            label = SentimentLabel.NEUTRAL
        elif score <= 0.6:
            label = SentimentLabel.POSITIVE
        else:
            label = SentimentLabel.VERY_POSITIVE

        return cls(score=score, label=label, confidence=confidence)


@dataclass
class NewsArticle:
    """News article data model."""

    uuid: str
    title: str
    description: str
    url: str
    source: str
    published_at: datetime
    content: Optional[str] = None
    image_url: Optional[str] = None
    language: str = "en"
    country: Optional[str] = None
    entities: List[NewsEntity] = field(default_factory=list)
    sentiment: Optional[NewsSentiment] = None
    keywords: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "uuid": self.uuid,
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "source": self.source,
            "published_at": self.published_at.isoformat(),
            "content": self.content,
            "image_url": self.image_url,
            "language": self.language,
            "country": self.country,
            "entities": [
                {
                    "symbol": e.symbol,
                    "name": e.name,
                    "type": e.type,
                    "exchange": e.exchange,
                    "sentiment_score": e.sentiment_score,
                }
                for e in self.entities
            ],
            "sentiment": (
                {
                    "score": self.sentiment.score,
                    "label": self.sentiment.label.value,
                    "confidence": self.sentiment.confidence,
                }
                if self.sentiment
                else None
            ),
            "keywords": self.keywords,
            "categories": self.categories,
        }


@dataclass
class NewsSearchParams:
    """Parameters for news search."""

    symbols: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    sources: Optional[List[str]] = None
    countries: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    industries: Optional[List[str]] = None
    sentiment_min: Optional[float] = None
    sentiment_max: Optional[float] = None
    published_after: Optional[datetime] = None
    published_before: Optional[datetime] = None
    limit: int = 50
    offset: int = 0


class NewsProvider(BaseProvider):
    """
    Abstract interface for news providers.
    All news providers must implement this interface.
    """

    @abstractmethod
    def search_news(self, params: NewsSearchParams) -> List[NewsArticle]:
        """
        Search for news articles based on parameters.

        Args:
            params: Search parameters

        Returns:
            List of NewsArticle objects
        """
        pass

    @abstractmethod
    def get_article(self, article_id: str) -> Optional[NewsArticle]:
        """
        Get a specific article by ID.

        Args:
            article_id: Article UUID or ID

        Returns:
            NewsArticle or None if not found
        """
        pass

    @abstractmethod
    def get_similar_articles(
        self, article_id: str, limit: int = 10
    ) -> List[NewsArticle]:
        """
        Get articles similar to a given article.

        Args:
            article_id: Reference article ID
            limit: Maximum number of results

        Returns:
            List of similar NewsArticle objects
        """
        pass

    @abstractmethod
    def get_trending_entities(
        self, entity_type: Optional[str] = None, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get trending entities in news.

        Args:
            entity_type: Filter by entity type (e.g., 'company')
            limit: Maximum number of results

        Returns:
            List of trending entity data
        """
        pass

    @abstractmethod
    def get_entity_sentiment(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get sentiment analysis for a specific entity over time.

        Args:
            symbol: Entity symbol (e.g., stock ticker)
            start_date: Start of time range
            end_date: End of time range

        Returns:
            Sentiment data including scores and trends
        """
        pass

    def analyze_sentiment(self, text: str) -> NewsSentiment:
        """
        Analyze sentiment of text (if provider supports it).

        Args:
            text: Text to analyze

        Returns:
            NewsSentiment object
        """
        # Default implementation - can be overridden
        return NewsSentiment(score=0.0, label=SentimentLabel.NEUTRAL, confidence=0.5)

    def extract_entities(self, text: str) -> List[NewsEntity]:
        """
        Extract entities from text (if provider supports it).

        Args:
            text: Text to analyze

        Returns:
            List of NewsEntity objects
        """
        # Default implementation - can be overridden
        return []
