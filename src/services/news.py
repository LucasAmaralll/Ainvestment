"""
News aggregation from multiple sources with deduplication.
"""

import time
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import quote

import requests
from duckduckgo_search import DDGS

from src.models.news_article import NewsArticle, NewsCollection
from src.utils.cache import cache
from src.utils.config import settings
from src.utils.logger import logger


class NewsAPIProvider:
    """
    NewsAPI.org provider (100 requests/day free).
    
    Signup: https://newsapi.org/
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.newsapi_key
        self.base_url = "https://newsapi.org/v2/everything"
        self.enabled = bool(self.api_key) and settings.newsapi_enabled
    
    def fetch(self, ticker: str, days_back: int = 7) -> list[NewsArticle]:
        """Fetch news from NewsAPI."""
        if not self.enabled:
            logger.debug("newsapi_disabled", ticker=ticker)
            return []
        
        try:
            # Build query
            query = f"{ticker} stock OR {ticker} shares"
            from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            
            params = {
                "q": query,
                "from": from_date,
                "language": "en",
                "sortBy": "publishedAt",
                "apiKey": self.api_key,
                "pageSize": 20
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                timeout=settings.timeout_seconds
            )
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for item in data.get("articles", []):
                try:
                    article = NewsArticle(
                        title=item["title"],
                        url=item["url"],
                        published_at=datetime.fromisoformat(
                            item["publishedAt"].replace("Z", "+00:00")
                        ),
                        source=item["source"]["name"],
                        snippet=item.get("description", "")[:300],
                        author=item.get("author"),
                        image_url=item.get("urlToImage")
                    )
                    articles.append(article)
                except Exception as e:
                    logger.warning("newsapi_article_parse_error", error=str(e))
                    continue
            
            logger.info(
                "newsapi_fetched",
                ticker=ticker,
                count=len(articles)
            )
            
            return articles
            
        except Exception as e:
            logger.warning("newsapi_fetch_failed", ticker=ticker, error=str(e))
            return []


class DuckDuckGoProvider:
    """DuckDuckGo news search (no API key needed, free)."""
    
    def fetch(self, ticker: str, days_back: int = 7, max_results: int = 10) -> list[NewsArticle]:
        """Fetch news from DuckDuckGo."""
        try:
            query = f"{ticker} stock news"
            
            with DDGS() as ddgs:
                results = list(ddgs.news(
                    keywords=query,
                    max_results=max_results,
                    timelimit=f"{days_back}d"
                ))
            
            articles = []
            for item in results:
                try:
                    # Parse date
                    published_at = datetime.fromisoformat(
                        item.get("date", datetime.now().isoformat())
                    )
                    
                    article = NewsArticle(
                        title=item["title"],
                        url=item["url"],
                        published_at=published_at,
                        source=item.get("source", "DuckDuckGo"),
                        snippet=item.get("body", "")[:300]
                    )
                    articles.append(article)
                except Exception as e:
                    logger.warning("ddg_article_parse_error", error=str(e))
                    continue
            
            logger.info(
                "duckduckgo_fetched",
                ticker=ticker,
                count=len(articles)
            )
            
            return articles
            
        except Exception as e:
            logger.warning("duckduckgo_fetch_failed", ticker=ticker, error=str(e))
            return []


class NewsDeduplicator:
    """
    Remove duplicate news articles based on title similarity.
    
    Uses simple string matching (can be upgraded to TF-IDF if needed).
    """
    
    @staticmethod
    def deduplicate(articles: list[NewsArticle], threshold: float = 0.85) -> list[NewsArticle]:
        """
        Remove duplicate articles.
        
        Args:
            articles: List of news articles
            threshold: Similarity threshold (0.0 to 1.0)
            
        Returns:
            Deduplicated list
        """
        if not articles:
            return []
        
        unique = []
        seen_titles = []
        
        for article in articles:
            # Normalize title
            title_lower = article.title.lower().strip()
            
            # Check similarity with existing titles
            is_duplicate = False
            for seen_title in seen_titles:
                similarity = NewsDeduplicator._simple_similarity(title_lower, seen_title)
                if similarity >= threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique.append(article)
                seen_titles.append(title_lower)
        
        removed_count = len(articles) - len(unique)
        if removed_count > 0:
            logger.debug(
                "news_deduplicated",
                original=len(articles),
                unique=len(unique),
                removed=removed_count
            )
        
        return unique
    
    @staticmethod
    def _simple_similarity(s1: str, s2: str) -> float:
        """
        Calculate simple word-based similarity.
        
        Returns:
            Similarity score (0.0 to 1.0)
        """
        words1 = set(s1.split())
        words2 = set(s2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)


class NewsAggregator:
    """
    Aggregates news from multiple sources with fallback strategy.
    
    Priority:
    1. NewsAPI (if available)
    2. DuckDuckGo (fallback)
    
    Features:
    - Deduplication
    - Caching
    - Metadata validation
    """
    
    def __init__(self):
        self.newsapi = NewsAPIProvider()
        self.ddg = DuckDuckGoProvider()
        self.deduplicator = NewsDeduplicator()
    
    def fetch_news(
        self,
        ticker: str,
        days_back: int = 7,
        use_cache: bool = True
    ) -> NewsCollection:
        """
        Fetch and aggregate news from all sources.
        
        Args:
            ticker: Stock symbol
            days_back: How many days back to search
            use_cache: Whether to use cache
            
        Returns:
            NewsCollection with deduplicated articles
        """
        start_time = time.time()
        
        # Check cache
        cache_key = f"news_{ticker}_{days_back}d"
        if use_cache:
            cached = cache.get(cache_key)
            if cached:
                logger.info(
                    "news_fetched_from_cache",
                    ticker=ticker,
                    count=cached.article_count
                )
                return cached
        
        # Fetch from sources
        all_articles = []
        sources_used = []
        
        # Try NewsAPI first
        if self.newsapi.enabled:
            newsapi_articles = self.newsapi.fetch(ticker, days_back)
            all_articles.extend(newsapi_articles)
            if newsapi_articles:
                sources_used.append("NewsAPI")
        
        # Always fetch from DuckDuckGo
        ddg_articles = self.ddg.fetch(ticker, days_back)
        all_articles.extend(ddg_articles)
        if ddg_articles:
            sources_used.append("DuckDuckGo")
        
        # Deduplicate
        unique_articles = self.deduplicator.deduplicate(all_articles)
        
        # Sort by date (most recent first)
        unique_articles.sort(key=lambda x: x.published_at, reverse=True)
        
        # Limit to max articles
        unique_articles = unique_articles[:settings.news_max_articles]
        
        # Create collection
        collection = NewsCollection(
            ticker=ticker,
            articles=unique_articles,
            fetched_at=datetime.now(),
            sources_used=sources_used
        )
        
        # Cache
        if use_cache:
            cache.set(cache_key, collection, ttl_hours=settings.cache_ttl_hours)
        
        duration_ms = int((time.time() - start_time) * 1000)
        logger.info(
            "news_aggregated",
            ticker=ticker,
            total_fetched=len(all_articles),
            unique_count=len(unique_articles),
            sources=sources_used,
            duration_ms=duration_ms
        )
        
        return collection


# Global aggregator instance
aggregator = NewsAggregator()
