"""
Configuration management using Pydantic.
Loads from .env file and provides type-safe access to settings.
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # LLM Configuration
    llm_provider: str = "mock"  # mock | ollama | openai
    openai_api_key: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    
    # News API Configuration
    newsapi_key: Optional[str] = None
    newsapi_enabled: bool = False
    
    # Cache Configuration
    cache_ttl_hours: int = 24
    cache_db_path: str = ".cache/ainvestment.db"
    cache_enabled: bool = True
    
    # Budget Limits (prevent runaway costs)
    daily_token_limit: int = 100_000
    monthly_budget_usd: float = 5.0
    max_requests_per_hour: int = 100
    
    # Data Source Configuration
    default_period: str = "1y"  # 3mo, 6mo, 1y, 2y, 5y
    timeout_seconds: int = 10
    max_retries: int = 3
    
    # News Configuration
    news_days_back: int = 7
    news_min_articles: int = 3
    news_max_articles: int = 20
    
    # UI Configuration
    app_title: str = "Ainvestment - Stock Research Terminal"
    app_icon: str = "📈"
    theme: str = "dark"  # dark | light
    
    # Logging
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    log_format: str = "json"  # json | text
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def is_llm_enabled(self) -> bool:
        """Check if LLM is available and configured."""
        if self.llm_provider == "mock":
            return False
        if self.llm_provider == "openai" and not self.openai_api_key:
            return False
        return True


# Global settings instance
settings = Settings()
