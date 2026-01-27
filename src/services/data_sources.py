"""
Robust data fetching from Yahoo Finance with caching, retry, and validation.
"""

import time
from datetime import datetime
from typing import Optional

import yfinance as yf
import pandas as pd
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from src.models.stock_data import StockData
from src.utils.cache import cache
from src.utils.config import settings
from src.utils.logger import logger
from src.utils.validators import validate_ticker, validate_period


class YFinanceProvider:
    """
    Yahoo Finance data provider with robustness features.
    
    Features:
    - Input validation
    - Exponential backoff retry
    - Caching (24h TTL)
    - Timeout handling
    - Error logging
    """
    
    def __init__(self):
        self.timeout = settings.timeout_seconds
        self.max_retries = settings.max_retries
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    )
    def _fetch_with_retry(self, ticker: str, period: str) -> pd.DataFrame:
        """
        Fetch data with retry logic.
        
        Args:
            ticker: Stock symbol
            period: Time period
            
        Returns:
            DataFrame with OHLCV data
            
        Raises:
            Exception: If all retries fail
        """
        stock = yf.Ticker(ticker)
        data = stock.history(period=period, timeout=self.timeout)
        
        if data.empty:
            raise ValueError(f"No data returned for {ticker}")
        
        return data
    
    def fetch_price_history(
        self,
        ticker: str,
        period: str = "1y",
        use_cache: bool = True
    ) -> StockData:
        """
        Fetch historical price data for a ticker.
        
        Args:
            ticker: Stock symbol (e.g., "AAPL", "BTC-USD")
            period: Time period (e.g., "1y", "6mo", "3mo")
            use_cache: Whether to use cache
            
        Returns:
            StockData object with price history
            
        Raises:
            ValidationError: If ticker or period is invalid
            Exception: If data fetching fails
        """
        start_time = time.time()
        
        # Validate inputs
        ticker = validate_ticker(ticker)
        period = validate_period(period)
        
        # Check cache
        cache_key = f"stock_{ticker}_{period}"
        if use_cache:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                logger.info(
                    "data_fetched_from_cache",
                    ticker=ticker,
                    period=period,
                    duration_ms=int((time.time() - start_time) * 1000)
                )
                return cached_data
        
        # Fetch from Yahoo Finance
        try:
            logger.info("fetching_stock_data", ticker=ticker, period=period)
            
            df = self._fetch_with_retry(ticker, period)
            
            # Create StockData object
            stock_data = StockData(
                ticker=ticker,
                period=period,
                data=df,
                fetched_at=datetime.now(),
                source="yfinance"
            )
            
            # Cache the result
            if use_cache:
                cache.set(cache_key, stock_data, ttl_hours=settings.cache_ttl_hours)
            
            duration_ms = int((time.time() - start_time) * 1000)
            logger.info(
                "data_fetched_successfully",
                ticker=ticker,
                period=period,
                rows=len(df),
                duration_ms=duration_ms
            )
            
            return stock_data
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(
                "data_fetch_failed",
                ticker=ticker,
                period=period,
                error=str(e),
                duration_ms=duration_ms
            )
            raise
    
    def get_current_price(self, ticker: str) -> Optional[float]:
        """
        Get current price for a ticker (uses cache if available).
        
        Args:
            ticker: Stock symbol
            
        Returns:
            Current price or None if unavailable
        """
        try:
            ticker = validate_ticker(ticker)
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Try different price fields
            price = (
                info.get('regularMarketPrice') or
                info.get('currentPrice') or
                info.get('previousClose')
            )
            
            if price:
                logger.debug("current_price_fetched", ticker=ticker, price=price)
                return float(price)
            
            return None
            
        except Exception as e:
            logger.warning("current_price_fetch_failed", ticker=ticker, error=str(e))
            return None
    
    def get_info(self, ticker: str) -> dict:
        """
        Get company information.
        
        Args:
            ticker: Stock symbol
            
        Returns:
            Dictionary of company info
        """
        try:
            ticker = validate_ticker(ticker)
            
            cache_key = f"info_{ticker}"
            cached = cache.get(cache_key)
            if cached:
                return cached
            
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Cache for 24 hours
            cache.set(cache_key, info, ttl_hours=24)
            
            return info
            
        except Exception as e:
            logger.warning("info_fetch_failed", ticker=ticker, error=str(e))
            return {}


# Global provider instance
provider = YFinanceProvider()
