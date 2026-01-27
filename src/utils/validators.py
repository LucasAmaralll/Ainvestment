"""
Input validation utilities.
Ensures data integrity before processing.
"""

import re
from datetime import datetime, timedelta
from typing import Literal

import yfinance as yf

from src.utils.logger import logger


PeriodType = Literal["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


def validate_ticker(ticker: str) -> str:
    """
    Validate and normalize a stock ticker.
    
    Args:
        ticker: Stock symbol (e.g., "AAPL", "BTC-USD")
        
    Returns:
        Normalized ticker (uppercase)
        
    Raises:
        ValidationError: If ticker is invalid
    """
    if not ticker:
        raise ValidationError("Ticker cannot be empty")
    
    # Normalize
    ticker = ticker.strip().upper()
    
    # Basic format check
    if not re.match(r'^[A-Z0-9\-\.]+$', ticker):
        raise ValidationError(
            f"Invalid ticker format: {ticker}. "
            "Use only letters, numbers, hyphens, and dots."
        )
    
    # Verify ticker exists (quick check)
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Check if we got valid data
        if not info or 'regularMarketPrice' not in info:
            # Try alternative check
            hist = stock.history(period="5d")
            if hist.empty:
                raise ValidationError(f"Ticker {ticker} not found or has no data")
                
    except Exception as e:
        logger.warning("ticker_validation_failed", ticker=ticker, error=str(e))
        raise ValidationError(f"Cannot validate ticker {ticker}: {str(e)}")
    
    return ticker


def validate_period(period: str) -> PeriodType:
    """
    Validate a time period string.
    
    Args:
        period: Period string (e.g., "1y", "6mo")
        
    Returns:
        Validated period
        
    Raises:
        ValidationError: If period is invalid
    """
    valid_periods: list[PeriodType] = [
        "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
    ]
    
    period = period.lower().strip()
    
    if period not in valid_periods:
        raise ValidationError(
            f"Invalid period: {period}. "
            f"Must be one of: {', '.join(valid_periods)}"
        )
    
    return period  # type: ignore


def validate_date_range(start_date: str, end_date: str) -> tuple[datetime, datetime]:
    """
    Validate and parse date range.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        Tuple of (start_datetime, end_datetime)
        
    Raises:
        ValidationError: If dates are invalid
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError as e:
        raise ValidationError(f"Invalid date format. Use YYYY-MM-DD: {e}")
    
    if start >= end:
        raise ValidationError("Start date must be before end date")
    
    if end > datetime.now():
        raise ValidationError("End date cannot be in the future")
    
    if (end - start).days < 7:
        raise ValidationError("Date range must be at least 7 days")
    
    return start, end


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename for safe file system operations.
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename
    """
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename
