"""
LLM-optional summarizer with multiple implementations.

Supports:
- Mock (no LLM, template-based)
- Ollama (local, free)
- OpenAI (cloud, paid)
"""

import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

import requests

from src.models.analysis_result import Citation, SummaryResult
from src.utils.config import settings
from src.utils.logger import logger
from src.services.prompts import (
    SYSTEM_PROMPT,
    create_summarization_prompt,
    create_mock_summary
)


class SummarizerInterface(ABC):
    """Abstract base class for all summarizers."""
    
    @abstractmethod
    def summarize(
        self,
        ticker: str,
        technical_data: dict,
        news_articles: list
    ) -> SummaryResult:
        """
        Generate a summary of stock analysis.
        
        Args:
            ticker: Stock symbol
            technical_data: Dictionary with technical indicators
            news_articles: List of NewsArticle objects
            
        Returns:
            SummaryResult with text and citations
        """
        pass


class MockSummarizer(SummarizerInterface):
    """
    Template-based summarizer without LLM.
    
    Use this when:
    - No LLM configured
    - Want pure objective analysis
    - Testing/development
    """
    
    def summarize(
        self,
        ticker: str,
        technical_data: dict,
        news_articles: list
    ) -> SummaryResult:
        """Generate template-based summary."""
        
        logger.info("generating_mock_summary", ticker=ticker)
        
        period = technical_data.get('period', '1y')
        summary_text = create_mock_summary(
            ticker=ticker,
            period=period,
            technical_data=technical_data,
            news_articles=news_articles
        )
        
        # Extract citations from news
        citations = []
        for article in news_articles[:5]:
            citation = Citation(
                source=article.source,
                url=article.url,
                published_at=article.published_at,
                snippet=article.title
            )
            citations.append(citation)
        
        return SummaryResult(
            ticker=ticker,
            summary_text=summary_text,
            citations=citations,
            confidence_score=1.0,  # Mock is always "confident" in its data
            generated_at=datetime.now(),
            llm_provider="mock",
            tokens_used=0
        )


class OllamaLocalSummarizer(SummarizerInterface):
    """
    Ollama local LLM summarizer (free, runs on your machine).
    
    Setup:
        1. Install Ollama: https://ollama.com/download
        2. Run: ollama pull llama3.1:8b
        3. Start: ollama serve (runs on localhost:11434)
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 30
    ):
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model
        self.timeout = timeout
    
    def _is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=2
            )
            return response.status_code == 200
        except:
            return False
    
    def summarize(
        self,
        ticker: str,
        technical_data: dict,
        news_articles: list
    ) -> SummaryResult:
        """Generate summary using Ollama."""
        
        # Check availability
        if not self._is_available():
            logger.warning(
                "ollama_unavailable",
                ticker=ticker,
                base_url=self.base_url
            )
            # Fallback to mock
            return MockSummarizer().summarize(ticker, technical_data, news_articles)
        
        logger.info("generating_ollama_summary", ticker=ticker, model=self.model)
        
        # Create prompt
        user_prompt = create_summarization_prompt(
            ticker=ticker,
            technical_data=technical_data,
            news_articles=news_articles
        )
        
        try:
            # Call Ollama API
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"{SYSTEM_PROMPT}\n\n{user_prompt}",
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # Low temperature for factual output
                        "top_p": 0.9,
                    }
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            summary_text = result["response"]
            
            # Extract citations
            citations = self._extract_citations(summary_text, news_articles)
            
            # Calculate confidence based on citation count
            confidence = min(len(citations) / 5, 1.0) if citations else 0.3
            
            # Validate summary quality
            if not self._validate_summary(summary_text, citations):
                logger.warning(
                    "ollama_summary_failed_validation",
                    ticker=ticker,
                    citation_count=len(citations)
                )
                # Lower confidence if validation fails
                confidence *= 0.5
            
            logger.info(
                "ollama_summary_generated",
                ticker=ticker,
                confidence=confidence,
                citations=len(citations)
            )
            
            return SummaryResult(
                ticker=ticker,
                summary_text=summary_text,
                citations=citations,
                confidence_score=confidence,
                generated_at=datetime.now(),
                llm_provider="ollama",
                tokens_used=None  # Ollama doesn't report tokens
            )
            
        except Exception as e:
            logger.error(
                "ollama_summary_failed",
                ticker=ticker,
                error=str(e)
            )
            # Fallback to mock
            return MockSummarizer().summarize(ticker, technical_data, news_articles)
    
    def _extract_citations(self, text: str, news_articles: list) -> list[Citation]:
        """Extract citations from LLM output."""
        citations = []
        
        # Find all markdown links: [text](url)
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(pattern, text)
        
        for match_text, url in matches:
            # Try to match with news articles
            for article in news_articles:
                if article.url in url or url in article.url:
                    citation = Citation(
                        source=article.source,
                        url=article.url,
                        published_at=article.published_at,
                        snippet=article.title
                    )
                    citations.append(citation)
                    break
        
        return citations
    
    def _validate_summary(self, text: str, citations: list) -> bool:
        """
        Validate that summary follows anti-hallucination rules.
        
        Checks:
        - Has citations
        - No buy/sell language
        - Acknowledges uncertainty
        """
        # Check for citations
        if len(citations) < 2:
            return False
        
        # Check for prohibited language
        prohibited = ["i recommend", "you should buy", "you should sell", "invest now"]
        text_lower = text.lower()
        if any(phrase in text_lower for phrase in prohibited):
            return False
        
        # Check for uncertainty acknowledgment (if few sources)
        if len(citations) < 3:
            uncertainty_markers = ["insufficient", "limited", "uncertain", "unclear"]
            if not any(marker in text_lower for marker in uncertainty_markers):
                return False
        
        return True


class OpenAISummarizer(SummarizerInterface):
    """
    OpenAI summarizer with cost controls.
    
    Uses gpt-4o-mini for cost efficiency.
    Implements budget tracking and daily limits.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        self.model = "gpt-4o-mini"
        self.base_url = "https://api.openai.com/v1/chat/completions"
        
        # Budget tracking (simple in-memory, could be persisted)
        self.daily_tokens = 0
        self.daily_limit = settings.daily_token_limit
    
    def summarize(
        self,
        ticker: str,
        technical_data: dict,
        news_articles: list
    ) -> SummaryResult:
        """Generate summary using OpenAI."""
        
        if not self.api_key:
            logger.warning("openai_api_key_missing", ticker=ticker)
            return MockSummarizer().summarize(ticker, technical_data, news_articles)
        
        # Check budget
        if self.daily_tokens >= self.daily_limit:
            logger.warning(
                "openai_daily_limit_reached",
                ticker=ticker,
                tokens=self.daily_tokens,
                limit=self.daily_limit
            )
            return MockSummarizer().summarize(ticker, technical_data, news_articles)
        
        logger.info("generating_openai_summary", ticker=ticker)
        
        user_prompt = create_summarization_prompt(
            ticker=ticker,
            technical_data=technical_data,
            news_articles=news_articles
        )
        
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            summary_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            # Update budget tracking
            self.daily_tokens += tokens_used
            
            # Extract citations
            citations = OllamaLocalSummarizer()._extract_citations(
                summary_text, news_articles
            )
            
            confidence = min(len(citations) / 5, 1.0) if citations else 0.3
            
            logger.info(
                "openai_summary_generated",
                ticker=ticker,
                tokens=tokens_used,
                daily_total=self.daily_tokens,
                confidence=confidence
            )
            
            return SummaryResult(
                ticker=ticker,
                summary_text=summary_text,
                citations=citations,
                confidence_score=confidence,
                generated_at=datetime.now(),
                llm_provider="openai",
                tokens_used=tokens_used
            )
            
        except Exception as e:
            logger.error("openai_summary_failed", ticker=ticker, error=str(e))
            return MockSummarizer().summarize(ticker, technical_data, news_articles)


class SummarizerFactory:
    """Factory to create the appropriate summarizer based on config."""
    
    @staticmethod
    def create() -> SummarizerInterface:
        """
        Create summarizer based on settings.
        
        Returns:
            Appropriate summarizer instance
        """
        provider = settings.llm_provider.lower()
        
        if provider == "mock" or provider == "none":
            logger.info("using_mock_summarizer")
            return MockSummarizer()
        
        elif provider == "ollama":
            logger.info("using_ollama_summarizer")
            return OllamaLocalSummarizer()
        
        elif provider == "openai":
            logger.info("using_openai_summarizer")
            return OpenAISummarizer()
        
        else:
            logger.warning(
                "unknown_llm_provider",
                provider=provider,
                fallback="mock"
            )
            return MockSummarizer()


# Global summarizer instance
summarizer = SummarizerFactory.create()
