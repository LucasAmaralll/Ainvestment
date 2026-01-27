"""
Main orchestrator: coordinates the entire analysis pipeline.

Pipeline:
1. Validate inputs
2. Fetch price data
3. Calculate indicators
4. Fetch news
5. Generate summary (optional)
6. Return result
"""

import time
from datetime import datetime

from src.models.analysis_result import AnalysisResult
from src.services.data_sources import provider as data_provider
from src.services.analytics import calculator
from src.services.news import aggregator as news_aggregator
from src.services.summarizer import summarizer
from src.utils.logger import logger
from src.utils.validators import validate_ticker, validate_period, ValidationError


class AnalysisOrchestrator:
    """
    Coordinates the full stock analysis pipeline.
    
    Handles:
    - Error recovery
    - Progress tracking
    - Timing metrics
    - Graceful degradation
    """
    
    def analyze(
        self,
        ticker: str,
        period: str = "1y",
        include_llm: bool = True,
        progress_callback=None
    ) -> AnalysisResult:
        """
        Run complete stock analysis.
        
        Args:
            ticker: Stock symbol
            period: Time period
            include_llm: Whether to use LLM for summary
            progress_callback: Optional callback(message, percent)
            
        Returns:
            AnalysisResult with all data
            
        Raises:
            ValidationError: If inputs are invalid
            Exception: If critical step fails
        """
        start_time = time.time()
        
        def update_progress(message: str, percent: int):
            """Update progress if callback provided."""
            if progress_callback:
                progress_callback(message, percent)
            logger.debug("analysis_progress", message=message, percent=percent)
        
        try:
            # Step 1: Validate
            update_progress("Validating inputs...", 5)
            ticker = validate_ticker(ticker)
            period = validate_period(period)
            
            logger.info("analysis_started", ticker=ticker, period=period)
            
            # Step 2: Fetch price data
            update_progress(f"Fetching price data for {ticker}...", 15)
            stock_data = data_provider.fetch_price_history(ticker, period)
            
            if stock_data.data.empty:
                raise ValueError(f"No price data available for {ticker}")
            
            # Step 3: Calculate indicators
            update_progress("Calculating technical indicators...", 35)
            indicators = calculator.calculate_all(stock_data.data, ticker)
            
            # Step 4: Fetch news
            update_progress("Fetching news articles...", 55)
            news = news_aggregator.fetch_news(ticker, days_back=7)
            
            if news.article_count == 0:
                logger.warning("no_news_found", ticker=ticker)
            
            # Step 5: Generate summary (optional)
            summary_result = None
            if include_llm:
                update_progress("Generating AI summary...", 75)
                
                # Prepare data for summarizer
                tech_data = indicators.to_dict()
                tech_data['period'] = period
                
                try:
                    summary_result = summarizer.summarize(
                        ticker=ticker,
                        technical_data=tech_data,
                        news_articles=news.articles
                    )
                except Exception as e:
                    logger.error(
                        "summary_generation_failed",
                        ticker=ticker,
                        error=str(e)
                    )
                    # Continue without summary
                    summary_result = None
            else:
                logger.info("llm_summary_skipped", ticker=ticker)
            
            # Step 6: Create result
            update_progress("Finalizing report...", 95)
            
            processing_time = time.time() - start_time
            
            result = AnalysisResult(
                ticker=ticker,
                period=period,
                stock_data=stock_data,
                indicators=indicators,
                news=news,
                summary=summary_result,
                generated_at=datetime.now(),
                processing_time_seconds=processing_time
            )
            
            update_progress("Complete!", 100)
            
            logger.info(
                "analysis_completed",
                ticker=ticker,
                period=period,
                processing_time_seconds=round(processing_time, 2),
                news_count=news.article_count,
                has_summary=summary_result is not None,
                data_quality=result.data_quality_score
            )
            
            return result
            
        except ValidationError as e:
            logger.error("analysis_validation_error", ticker=ticker, error=str(e))
            raise
        
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(
                "analysis_failed",
                ticker=ticker,
                period=period,
                error=str(e),
                processing_time_seconds=round(processing_time, 2)
            )
            raise
    
    def analyze_multiple(
        self,
        tickers: list[str],
        period: str = "1y",
        include_llm: bool = True
    ) -> dict[str, AnalysisResult]:
        """
        Analyze multiple tickers.
        
        Args:
            tickers: List of stock symbols
            period: Time period
            include_llm: Whether to use LLM
            
        Returns:
            Dictionary mapping ticker to AnalysisResult
        """
        results = {}
        
        for i, ticker in enumerate(tickers, 1):
            logger.info(
                "analyzing_multiple",
                ticker=ticker,
                position=i,
                total=len(tickers)
            )
            
            try:
                result = self.analyze(ticker, period, include_llm)
                results[ticker] = result
            except Exception as e:
                logger.error(
                    "multiple_analysis_item_failed",
                    ticker=ticker,
                    error=str(e)
                )
                # Continue with next ticker
                continue
        
        logger.info(
            "multiple_analysis_completed",
            requested=len(tickers),
            successful=len(results),
            failed=len(tickers) - len(results)
        )
        
        return results


# Global orchestrator instance
orchestrator = AnalysisOrchestrator()
