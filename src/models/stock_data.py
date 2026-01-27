"""Data models for stock analysis."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import pandas as pd


@dataclass
class StockData:
    """Historical stock price data with metadata."""
    
    ticker: str
    period: str
    data: pd.DataFrame  # OHLCV data
    fetched_at: datetime
    source: str = "yfinance"
    
    @property
    def latest_price(self) -> float:
        """Get the most recent close price."""
        if self.data.empty:
            return 0.0
        return float(self.data['Close'].iloc[-1])
    
    @property
    def price_change_pct(self) -> float:
        """Calculate percentage change from first to last price."""
        if self.data.empty or len(self.data) < 2:
            return 0.0
        first = float(self.data['Close'].iloc[0])
        last = float(self.data['Close'].iloc[-1])
        return ((last - first) / first) * 100
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "ticker": self.ticker,
            "period": self.period,
            "latest_price": self.latest_price,
            "price_change_pct": self.price_change_pct,
            "data_points": len(self.data),
            "fetched_at": self.fetched_at.isoformat(),
            "source": self.source,
        }


@dataclass
class TechnicalIndicators:
    """Technical analysis indicators for a stock."""
    
    ticker: str
    
    # Returns
    return_7d: float
    return_30d: float
    return_ytd: float
    
    # Volatility
    volatility_30d: float  # Standard deviation of daily returns
    volatility_90d: float
    
    # Moving averages
    sma_20: float
    sma_50: float
    sma_200: float
    current_price: float
    
    # Risk metrics
    max_drawdown: float  # Maximum peak-to-trough decline
    sharpe_ratio: Optional[float]  # Risk-adjusted return
    
    # Trend indicators
    above_sma_20: bool
    above_sma_50: bool
    above_sma_200: bool
    
    calculated_at: datetime
    
    @property
    def trend_signal(self) -> str:
        """
        Simple trend signal based on moving averages.
        
        Returns:
            'BULLISH' | 'BEARISH' | 'NEUTRAL'
        """
        if self.above_sma_20 and self.above_sma_50 and self.above_sma_200:
            return "BULLISH"
        elif not self.above_sma_20 and not self.above_sma_50 and not self.above_sma_200:
            return "BEARISH"
        else:
            return "NEUTRAL"
    
    @property
    def risk_level(self) -> str:
        """
        Risk assessment based on volatility and drawdown.
        
        Returns:
            'LOW' | 'MEDIUM' | 'HIGH' | 'VERY HIGH'
        """
        # Annualized volatility
        annualized_vol = self.volatility_30d * (252 ** 0.5)
        
        if annualized_vol < 0.15 and abs(self.max_drawdown) < 0.10:
            return "LOW"
        elif annualized_vol < 0.25 and abs(self.max_drawdown) < 0.20:
            return "MEDIUM"
        elif annualized_vol < 0.40 and abs(self.max_drawdown) < 0.30:
            return "HIGH"
        else:
            return "VERY HIGH"
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "ticker": self.ticker,
            "returns": {
                "7d": round(self.return_7d, 4),
                "30d": round(self.return_30d, 4),
                "ytd": round(self.return_ytd, 4),
            },
            "volatility": {
                "30d": round(self.volatility_30d, 4),
                "90d": round(self.volatility_90d, 4),
            },
            "moving_averages": {
                "sma_20": round(self.sma_20, 2),
                "sma_50": round(self.sma_50, 2),
                "sma_200": round(self.sma_200, 2),
                "current_price": round(self.current_price, 2),
            },
            "risk": {
                "max_drawdown": round(self.max_drawdown, 4),
                "sharpe_ratio": round(self.sharpe_ratio, 2) if self.sharpe_ratio else None,
                "risk_level": self.risk_level,
            },
            "trend": {
                "signal": self.trend_signal,
                "above_sma_20": self.above_sma_20,
                "above_sma_50": self.above_sma_50,
                "above_sma_200": self.above_sma_200,
            },
            "calculated_at": self.calculated_at.isoformat(),
        }
