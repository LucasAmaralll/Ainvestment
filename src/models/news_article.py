"""Data models for news articles."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class NewsArticle:
    """Represents a news article with metadata."""
    
    title: str
    url: str
    published_at: datetime
    source: str
    snippet: str
    author: Optional[str] = None
    image_url: Optional[str] = None
    
    # Internal metadata
    fetched_at: datetime = None  # type: ignore
    relevance_score: Optional[float] = None
    
    def __post_init__(self):
        """Set fetched_at if not provided."""
        if self.fetched_at is None:
            self.fetched_at = datetime.now(timezone.utc)
    
    @property
    def age_hours(self) -> float:
        """Calculate how old the article is in hours."""
        now = datetime.now(timezone.utc)
        # Make published_at timezone-aware if it isn't
        pub_at = self.published_at
        if pub_at.tzinfo is None:
            pub_at = pub_at.replace(tzinfo=timezone.utc)
        delta = now - pub_at
        return delta.total_seconds() / 3600
    
    @property
    def is_recent(self, max_hours: int = 48) -> bool:
        """Check if article is recent (within max_hours)."""
        return self.age_hours <= max_hours
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "title": self.title,
            "url": self.url,
            "published_at": self.published_at.isoformat(),
            "source": self.source,
            "snippet": self.snippet,
            "author": self.author,
            "image_url": self.image_url,
            "age_hours": round(self.age_hours, 1),
            "relevance_score": self.relevance_score,
        }
    
    def to_markdown(self) -> str:
        """Format as markdown for display."""
        date_str = self.published_at.strftime("%d/%m/%Y %H:%M")
        return f"**[{self.title}]({self.url})**  \n*{self.source}* • {date_str}  \n{self.snippet}"


@dataclass
class NewsCollection:
    """Collection of news articles for a ticker."""
    
    ticker: str
    articles: list[NewsArticle]
    fetched_at: datetime
    sources_used: list[str]
    
    @property
    def article_count(self) -> int:
        """Total number of articles."""
        return len(self.articles)
    
    @property
    def unique_sources(self) -> list[str]:
        """Get list of unique news sources."""
        return list(set(article.source for article in self.articles))
    
    @property
    def average_age_hours(self) -> float:
        """Average age of articles in hours."""
        if not self.articles:
            return 0.0
        return sum(article.age_hours for article in self.articles) / len(self.articles)
    
    def get_recent(self, max_hours: int = 48) -> list[NewsArticle]:
        """Get only recent articles."""
        return [a for a in self.articles if a.is_recent(max_hours)]
    
    def sort_by_date(self, descending: bool = True) -> None:
        """Sort articles by publication date."""
        self.articles.sort(
            key=lambda x: x.published_at,
            reverse=descending
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "ticker": self.ticker,
            "article_count": self.article_count,
            "unique_sources": self.unique_sources,
            "average_age_hours": round(self.average_age_hours, 1),
            "sources_used": self.sources_used,
            "fetched_at": self.fetched_at.isoformat(),
            "articles": [article.to_dict() for article in self.articles],
        }
