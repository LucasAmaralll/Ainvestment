"""
Technical indicators calculator.
Provides objective, quantitative analysis without speculation.
"""

from datetime import datetime
from typing import Optional

import pandas as pd
import numpy as np

from src.models.stock_data import TechnicalIndicators
from src.utils.logger import logger


class IndicatorCalculator:
    """
    Calculate technical indicators from price data.
    
    All calculations are deterministic and objective.
    No predictive modeling or speculation.
    """
    
    @staticmethod
    def calculate_returns(df: pd.DataFrame) -> dict[str, float]:
        """
        Calculate returns over various periods.
        
        Args:
            df: DataFrame with 'Close' column
            
        Returns:
            Dictionary with return percentages
        """
        if df.empty or 'Close' not in df.columns:
            return {"7d": 0.0, "30d": 0.0, "ytd": 0.0}
        
        current_price = df['Close'].iloc[-1]
        
        # Calculate returns
        returns = {}
        
        # 7-day return
        if len(df) >= 7:
            price_7d_ago = df['Close'].iloc[-7]
            returns["7d"] = (current_price - price_7d_ago) / price_7d_ago
        else:
            returns["7d"] = 0.0
        
        # 30-day return
        if len(df) >= 30:
            price_30d_ago = df['Close'].iloc[-30]
            returns["30d"] = (current_price - price_30d_ago) / price_30d_ago
        else:
            returns["30d"] = 0.0
        
        # Year-to-date return
        current_year = datetime.now().year
        ytd_data = df[df.index.year == current_year]
        if not ytd_data.empty:
            ytd_start_price = ytd_data['Close'].iloc[0]
            returns["ytd"] = (current_price - ytd_start_price) / ytd_start_price
        else:
            returns["ytd"] = 0.0
        
        return returns
    
    @staticmethod
    def calculate_volatility(df: pd.DataFrame) -> dict[str, float]:
        """
        Calculate volatility (standard deviation of daily returns).
        
        Args:
            df: DataFrame with 'Close' column
            
        Returns:
            Dictionary with volatility metrics
        """
        if df.empty or 'Close' not in df.columns:
            return {"30d": 0.0, "90d": 0.0}
        
        # Calculate daily returns
        df = df.copy()
        df['returns'] = df['Close'].pct_change()
        
        volatility = {}
        
        # 30-day volatility
        if len(df) >= 30:
            vol_30d = df['returns'].iloc[-30:].std()
            volatility["30d"] = float(vol_30d)
        else:
            volatility["30d"] = 0.0
        
        # 90-day volatility
        if len(df) >= 90:
            vol_90d = df['returns'].iloc[-90:].std()
            volatility["90d"] = float(vol_90d)
        else:
            volatility["90d"] = 0.0
        
        return volatility
    
    @staticmethod
    def calculate_moving_averages(df: pd.DataFrame) -> dict[str, float]:
        """
        Calculate simple moving averages.
        
        Args:
            df: DataFrame with 'Close' column
            
        Returns:
            Dictionary with SMA values
        """
        if df.empty or 'Close' not in df.columns:
            return {"sma_20": 0.0, "sma_50": 0.0, "sma_200": 0.0}
        
        ma = {}
        
        # 20-day SMA
        if len(df) >= 20:
            ma["sma_20"] = float(df['Close'].iloc[-20:].mean())
        else:
            ma["sma_20"] = float(df['Close'].mean())
        
        # 50-day SMA
        if len(df) >= 50:
            ma["sma_50"] = float(df['Close'].iloc[-50:].mean())
        else:
            ma["sma_50"] = float(df['Close'].mean())
        
        # 200-day SMA
        if len(df) >= 200:
            ma["sma_200"] = float(df['Close'].iloc[-200:].mean())
        else:
            ma["sma_200"] = float(df['Close'].mean())
        
        return ma
    
    @staticmethod
    def calculate_max_drawdown(df: pd.DataFrame) -> float:
        """
        Calculate maximum drawdown (largest peak-to-trough decline).
        
        Args:
            df: DataFrame with 'Close' column
            
        Returns:
            Maximum drawdown as decimal (negative value)
        """
        if df.empty or 'Close' not in df.columns:
            return 0.0
        
        # Calculate cumulative maximum
        cum_max = df['Close'].cummax()
        
        # Calculate drawdown
        drawdown = (df['Close'] - cum_max) / cum_max
        
        # Return maximum drawdown (most negative)
        max_dd = float(drawdown.min())
        
        return max_dd
    
    @staticmethod
    def calculate_sharpe_ratio(
        df: pd.DataFrame,
        risk_free_rate: float = 0.04
    ) -> Optional[float]:
        """
        Calculate Sharpe Ratio (risk-adjusted return).
        
        Args:
            df: DataFrame with 'Close' column
            risk_free_rate: Annual risk-free rate (default 4%)
            
        Returns:
            Sharpe ratio or None if insufficient data
        """
        if df.empty or 'Close' not in df.columns or len(df) < 30:
            return None
        
        # Calculate daily returns
        df = df.copy()
        df['returns'] = df['Close'].pct_change()
        
        # Annualize returns and volatility
        avg_return = df['returns'].mean() * 252  # 252 trading days
        volatility = df['returns'].std() * np.sqrt(252)
        
        if volatility == 0:
            return None
        
        # Calculate Sharpe
        sharpe = (avg_return - risk_free_rate) / volatility
        
        return float(sharpe)
    
    def calculate_all(self, df: pd.DataFrame, ticker: str) -> TechnicalIndicators:
        """
        Calculate all technical indicators for a stock.
        
        Args:
            df: DataFrame with OHLCV data
            ticker: Stock symbol
            
        Returns:
            TechnicalIndicators object
        """
        logger.info("calculating_indicators", ticker=ticker, rows=len(df))
        
        # Calculate each component
        returns = self.calculate_returns(df)
        volatility = self.calculate_volatility(df)
        ma = self.calculate_moving_averages(df)
        max_dd = self.calculate_max_drawdown(df)
        sharpe = self.calculate_sharpe_ratio(df)
        
        current_price = float(df['Close'].iloc[-1]) if not df.empty else 0.0
        
        # Create indicators object
        indicators = TechnicalIndicators(
            ticker=ticker,
            return_7d=returns["7d"],
            return_30d=returns["30d"],
            return_ytd=returns["ytd"],
            volatility_30d=volatility["30d"],
            volatility_90d=volatility["90d"],
            sma_20=ma["sma_20"],
            sma_50=ma["sma_50"],
            sma_200=ma["sma_200"],
            current_price=current_price,
            max_drawdown=max_dd,
            sharpe_ratio=sharpe,
            above_sma_20=current_price > ma["sma_20"] if ma["sma_20"] > 0 else False,
            above_sma_50=current_price > ma["sma_50"] if ma["sma_50"] > 0 else False,
            above_sma_200=current_price > ma["sma_200"] if ma["sma_200"] > 0 else False,
            calculated_at=datetime.now()
        )
        
        logger.info(
            "indicators_calculated",
            ticker=ticker,
            trend=indicators.trend_signal,
            risk=indicators.risk_level
        )
        
        return indicators


# Global calculator instance
calculator = IndicatorCalculator()
