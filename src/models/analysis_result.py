"""Data models for analysis results."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.models.stock_data import StockData, TechnicalIndicators
from src.models.news_article import NewsCollection


@dataclass
class Citation:
    """Reference to a news source."""
    
    source: str
    url: str
    published_at: datetime
    snippet: str
    
    def to_markdown(self) -> str:
        """Format citation as markdown."""
        date_str = self.published_at.strftime("%d/%m/%Y")
        return f"[{self.source}, {date_str}]({self.url})"


@dataclass
class SummaryResult:
    """LLM-generated summary with citations."""
    
    ticker: str
    summary_text: str
    citations: list[Citation]
    confidence_score: float  # 0.0 to 1.0
    generated_at: datetime
    llm_provider: str
    tokens_used: Optional[int] = None
    
    @property
    def is_confident(self) -> bool:
        """Check if summary has high confidence."""
        return self.confidence_score >= 0.6
    
    @property
    def citation_count(self) -> int:
        """Number of citations."""
        return len(self.citations)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "ticker": self.ticker,
            "summary_text": self.summary_text,
            "citation_count": self.citation_count,
            "confidence_score": round(self.confidence_score, 2),
            "is_confident": self.is_confident,
            "generated_at": self.generated_at.isoformat(),
            "llm_provider": self.llm_provider,
            "tokens_used": self.tokens_used,
        }


@dataclass
class AnalysisResult:
    """Complete analysis result for a stock."""
    
    ticker: str
    period: str
    
    # Data components
    stock_data: StockData
    indicators: TechnicalIndicators
    news: NewsCollection
    
    # AI-generated (optional)
    summary: Optional[SummaryResult]
    
    # Metadata
    generated_at: datetime
    processing_time_seconds: float
    
    @property
    def has_llm_summary(self) -> bool:
        """Check if LLM summary is available."""
        return self.summary is not None
    
    @property
    def recommendation(self) -> str:
        """
        Gera recomendação baseada em indicadores técnicos.
        
        Returns:
            str: COMPRA FORTE, COMPRA, NEUTRO, VENDA, VENDA FORTE
        """
        score = 0
        
        # Tendência (peso 3)
        if self.indicators.trend_signal == "BULLISH":
            score += 3
        elif self.indicators.trend_signal == "BEARISH":
            score -= 3
        
        # Retorno 30 dias (peso 2)
        if self.indicators.return_30d > 0.10:  # +10%
            score += 2
        elif self.indicators.return_30d > 0.05:  # +5%
            score += 1
        elif self.indicators.return_30d < -0.10:  # -10%
            score -= 2
        elif self.indicators.return_30d < -0.05:  # -5%
            score -= 1
        
        # Risco (peso 2)
        if self.indicators.risk_level == "LOW":
            score += 2
        elif self.indicators.risk_level == "HIGH":
            score -= 2
        
        # Médias móveis (peso 2)
        ma_above = sum([self.indicators.above_sma_20, self.indicators.above_sma_50, self.indicators.above_sma_200])
        if ma_above == 3:
            score += 2
        elif ma_above == 0:
            score -= 2
        elif ma_above == 2:
            score += 1
        elif ma_above == 1:
            score -= 1
        
        # Sharpe ratio (peso 1)
        if self.indicators.sharpe_ratio:
            if self.indicators.sharpe_ratio > 1.5:
                score += 1
            elif self.indicators.sharpe_ratio < 0.5:
                score -= 1
        
        # Traduzir score para recomendação
        if score >= 6:
            return "COMPRA FORTE"
        elif score >= 3:
            return "COMPRA"
        elif score >= -2:
            return "NEUTRO"
        elif score >= -5:
            return "VENDA"
        else:
            return "VENDA FORTE"
    
    @property
    def recommendation_color(self) -> str:
        """Retorna cor para a recomendação."""
        rec = self.recommendation
        if "COMPRA" in rec:
            return "success" if "FORTE" in rec else "normal"
        elif "VENDA" in rec:
            return "inverse" if "FORTE" in rec else "normal"
        else:
            return "off"
    
    @property
    def data_quality_score(self) -> float:
        """
        Assess quality of data collected (0.0 to 1.0).
        
        Factors:
        - News article count
        - Data points available
        - Citation count (if LLM used)
        """
        score = 0.0
        
        # News quality (max 0.4)
        news_score = min(self.news.article_count / 10, 1.0) * 0.4
        score += news_score
        
        # Price data quality (max 0.3)
        data_points = len(self.stock_data.data)
        data_score = min(data_points / 252, 1.0) * 0.3  # 252 = trading days/year
        score += data_score
        
        # Citation quality (max 0.3)
        if self.summary:
            citation_score = min(self.summary.citation_count / 5, 1.0) * 0.3
            score += citation_score
        else:
            score += 0.15  # Partial credit for no LLM
        
        return round(score, 2)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "ticker": self.ticker,
            "period": self.period,
            "stock_data": self.stock_data.to_dict(),
            "indicators": self.indicators.to_dict(),
            "news": self.news.to_dict(),
            "summary": self.summary.to_dict() if self.summary else None,
            "generated_at": self.generated_at.isoformat(),
            "processing_time_seconds": round(self.processing_time_seconds, 2),
            "data_quality_score": self.data_quality_score,
            "has_llm_summary": self.has_llm_summary,
        }
    
    def to_markdown(self) -> str:
        """
        Generate a comprehensive markdown report.
        
        Returns:
            Formatted markdown document
        """
        md = f"# 📊 Análise: {self.ticker}\n\n"
        md += f"**Período:** {self.period} | **Gerado em:** {self.generated_at.strftime('%d/%m/%Y %H:%M')}\n\n"
        md += "---\n\n"
        
        # Executive Summary
        md += "## 📈 Resumo Executivo\n\n"
        md += f"- **Preço Atual:** ${self.stock_data.latest_price:.2f}\n"
        md += f"- **Variação no Período:** {self.stock_data.price_change_pct:+.2f}%\n"
        md += f"- **Tendência:** {self.indicators.trend_signal}\n"
        md += f"- **Nível de Risco:** {self.indicators.risk_level}\n"
        md += f"- **Qualidade dos Dados:** {self.data_quality_score * 100:.0f}%\n\n"
        
        # Metrics
        md += "---\n\n## 📊 Métricas Quantitativas\n\n"
        md += "### Retornos\n\n"
        md += f"- **7 dias:** {self.indicators.return_7d * 100:+.2f}%\n"
        md += f"- **30 dias:** {self.indicators.return_30d * 100:+.2f}%\n"
        md += f"- **YTD:** {self.indicators.return_ytd * 100:+.2f}%\n\n"
        
        md += "### Volatilidade & Risco\n\n"
        md += f"- **Volatilidade (30d):** {self.indicators.volatility_30d * 100:.2f}%\n"
        md += f"- **Max Drawdown:** {self.indicators.max_drawdown * 100:.2f}%\n"
        if self.indicators.sharpe_ratio:
            md += f"- **Sharpe Ratio:** {self.indicators.sharpe_ratio:.2f}\n"
        md += "\n"
        
        # News
        md += "---\n\n## 📰 Notícias Recentes\n\n"
        md += f"**{self.news.article_count} artigos** de {len(self.news.unique_sources)} fontes\n\n"
        
        for i, article in enumerate(self.news.articles[:10], 1):
            md += f"### {i}. {article.title}\n\n"
            md += f"**Fonte:** {article.source} | **Data:** {article.published_at.strftime('%d/%m/%Y %H:%M')}\n\n"
            md += f"{article.snippet}\n\n"
            md += f"🔗 [Ler mais]({article.url})\n\n"
        
        # AI Summary
        if self.summary:
            md += "---\n\n## 🤖 Análise com IA\n\n"
            md += f"**Confiança:** {self.summary.confidence_score * 100:.0f}% | "
            md += f"**Citações:** {self.summary.citation_count}\n\n"
            
            if not self.summary.is_confident:
                md += "⚠️ **Aviso:** Dados insuficientes para alta confiança.\n\n"
            
            md += self.summary.summary_text + "\n\n"
            
            if self.summary.citations:
                md += "### Fontes Citadas\n\n"
                for citation in self.summary.citations:
                    md += f"- {citation.to_markdown()}\n"
                md += "\n"
        
        # Disclaimer
        md += "---\n\n## ⚠️ Aviso Legal\n\n"
        md += "Este relatório é apenas para fins informativos e educacionais. "
        md += "Não constitui recomendação de compra ou venda. "
        md += "Investimentos envolvem risco de perda. "
        md += "Consulte um profissional qualificado antes de tomar decisões financeiras.\n\n"
        
        return md
