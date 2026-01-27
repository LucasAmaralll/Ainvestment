"""
Simple unit tests for Ainvestment v2.0
Run with: pytest tests/unit/test_validators.py
"""

import pytest
from datetime import datetime

from src.utils.validators import (
    validate_ticker,
    validate_period,
    validate_date_range,
    sanitize_filename,
    ValidationError
)


class TestValidateTicker:
    """Test ticker validation."""
    
    def test_valid_tickers(self):
        """Test valid ticker formats."""
        assert validate_ticker("AAPL") == "AAPL"
        assert validate_ticker("aapl") == "AAPL"  # Uppercase
        assert validate_ticker("BTC-USD") == "BTC-USD"
        assert validate_ticker("^GSPC") == "^GSPC"
    
    def test_invalid_ticker_empty(self):
        """Test empty ticker raises error."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_ticker("")
    
    def test_invalid_ticker_special_chars(self):
        """Test ticker with invalid characters."""
        with pytest.raises(ValidationError, match="Invalid ticker format"):
            validate_ticker("AAPL$")
        
        with pytest.raises(ValidationError):
            validate_ticker("AAP L")  # Space
    
    def test_ticker_normalization(self):
        """Test ticker is normalized to uppercase."""
        assert validate_ticker("  aapl  ") == "AAPL"


class TestValidatePeriod:
    """Test period validation."""
    
    def test_valid_periods(self):
        """Test valid period formats."""
        valid = ["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
        for period in valid:
            assert validate_period(period) == period
    
    def test_case_insensitive(self):
        """Test period is case-insensitive."""
        assert validate_period("1Y") == "1y"
        assert validate_period("YTD") == "ytd"
    
    def test_invalid_period(self):
        """Test invalid period raises error."""
        with pytest.raises(ValidationError, match="Invalid period"):
            validate_period("3w")
        
        with pytest.raises(ValidationError):
            validate_period("invalid")


class TestValidateDateRange:
    """Test date range validation."""
    
    def test_valid_date_range(self):
        """Test valid date range."""
        start, end = validate_date_range("2024-01-01", "2024-12-31")
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert start < end
    
    def test_invalid_date_format(self):
        """Test invalid date format."""
        with pytest.raises(ValidationError, match="Invalid date format"):
            validate_date_range("01-01-2024", "31-12-2024")
    
    def test_start_after_end(self):
        """Test start date after end date."""
        with pytest.raises(ValidationError, match="Start date must be before"):
            validate_date_range("2024-12-31", "2024-01-01")
    
    def test_date_range_too_short(self):
        """Test date range less than 7 days."""
        with pytest.raises(ValidationError, match="at least 7 days"):
            validate_date_range("2024-01-01", "2024-01-05")


class TestSanitizeFilename:
    """Test filename sanitization."""
    
    def test_safe_filename(self):
        """Test filename with safe characters."""
        assert sanitize_filename("AAPL_report.md") == "AAPL_report.md"
    
    def test_unsafe_characters(self):
        """Test filename with unsafe characters."""
        result = sanitize_filename("AAPL<>:report.md")
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
    
    def test_long_filename(self):
        """Test very long filename is truncated."""
        long_name = "A" * 300
        result = sanitize_filename(long_name)
        assert len(result) <= 200


class TestIntegration:
    """Integration tests (optional, can be slow)."""
    
    @pytest.mark.skipif(True, reason="Requires internet connection")
    def test_validate_ticker_existence(self):
        """Test ticker validation against Yahoo Finance (slow)."""
        # This test actually queries Yahoo Finance
        validate_ticker("AAPL")  # Should pass
        
        with pytest.raises(ValidationError):
            validate_ticker("INVALID_TICKER_XYZ123")


# Run with: pytest tests/unit/test_validators.py -v
