"""
News providers module.
"""

from .interface import (
    NewsProvider,
    NewsArticle,
    NewsSentiment,
    NewsEntity,
    NewsSearchParams,
    SentimentLabel,
)
from .marketaux import MarketauxProvider

__all__ = [
    "NewsProvider",
    "NewsArticle",
    "NewsSentiment",
    "NewsEntity",
    "NewsSearchParams",
    "SentimentLabel",
    "MarketauxProvider",
]
