"""
Prompts anti-alucinação para LLM summarization.

Principles:
1. Always cite sources with [Source, Date](URL)
2. Separate FACTS from INTERPRETATIONS  
3. When confidence is low, say "insufficient data"
4. No buy/sell recommendations, only scenarios
5. Explicit disclaimer
"""

SYSTEM_PROMPT = """You are a skeptical financial analyst assistant. Your role is to:

1. Summarize stock news with MANDATORY citations
2. Clearly separate objective facts from subjective interpretations
3. Never make buy/sell recommendations
4. When data is insufficient, explicitly state this
5. Present multiple scenarios (bullish/bearish/neutral) with probabilities

CRITICAL RULES:
- Every factual claim MUST have a citation: [Source Name, DD/MM/YYYY](URL)
- If you cannot find supporting evidence, say "No data available for X"
- Use phrases like "According to [Source]...", "Based on data from..."
- Never use phrases like "The stock will...", "I recommend...", "You should..."
- Instead use: "Possible scenarios include...", "Historical data suggests...", "One interpretation is..."

OUTPUT FORMAT:
## 📊 OBJECTIVE FACTS
(Data points with citations - price, volume, etc.)

## 📰 NEWS SUMMARY  
(Key events with citations and dates)

## 🔮 POSSIBLE SCENARIOS
(Multiple interpretations with confidence levels)

## ⚠️ LIMITATIONS
(What data is missing or uncertain)
"""


def create_summarization_prompt(
    ticker: str,
    technical_data: dict,
    news_articles: list,
    confidence_threshold: float = 0.6
) -> str:
    """
    Create a prompt for summarizing stock analysis.
    
    Args:
        ticker: Stock symbol
        technical_data: Dictionary with technical indicators
        news_articles: List of NewsArticle objects
        confidence_threshold: Minimum confidence to provide interpretation
        
    Returns:
        Formatted prompt string
    """
    
    # Format technical data
    tech_summary = f"""
**Technical Data for {ticker}:**
- Current Price: ${technical_data.get('current_price', 'N/A')}
- 7-day Return: {technical_data.get('return_7d', 0) * 100:.2f}%
- 30-day Return: {technical_data.get('return_30d', 0) * 100:.2f}%
- Volatility (30d): {technical_data.get('volatility_30d', 0) * 100:.2f}%
- Trend Signal: {technical_data.get('trend_signal', 'N/A')}
- Risk Level: {technical_data.get('risk_level', 'N/A')}
"""
    
    # Format news articles
    if not news_articles or len(news_articles) < 3:
        news_summary = f"""
**WARNING:** Only {len(news_articles)} news articles found for {ticker}.
This is insufficient for reliable analysis. 

Articles:
"""
    else:
        news_summary = f"**News Articles ({len(news_articles)} found):**\n\n"
    
    for i, article in enumerate(news_articles[:15], 1):
        date_str = article.published_at.strftime("%d/%m/%Y")
        news_summary += f"""
{i}. **{article.title}**
   - Source: {article.source}
   - Date: {date_str}
   - URL: {article.url}
   - Snippet: {article.snippet}
"""
    
    # Create full prompt
    prompt = f"""{tech_summary}

{news_summary}

---

**TASK:** Analyze {ticker} following these strict rules:

1. **Cite Every Claim:** Use format [Source Name, DD/MM/YYYY](URL) for all facts
2. **Separate Sections:**
   - Objective Facts (price, volume, dates)
   - News Summary (what happened, with citations)
   - Possible Scenarios (interpretations, clearly marked as subjective)
   - Limitations (what data is missing)

3. **Confidence Check:**
   - If <3 news articles: Start with "⚠️ INSUFFICIENT DATA"
   - If <5 news articles: Add "⚠️ LIMITED INFORMATION" warning
   - State your confidence level (0-100%)

4. **No Recommendations:** 
   - ❌ Do NOT say: "buy", "sell", "invest", "I recommend"
   - ✅ Instead say: "possible scenario", "one interpretation", "historical patterns suggest"

5. **Multiple Scenarios:**
   - Bullish case (with probability)
   - Bearish case (with probability)
   - Neutral case (with probability)

6. **Explicit Uncertainty:**
   - If unsure, say "Insufficient evidence for X"
   - If conflicting data, present both views with citations

**OUTPUT LENGTH:** 3-4 paragraphs maximum. Be concise and factual.

**CONFIDENCE THRESHOLD:** If total confidence <{confidence_threshold * 100}%, add prominent warning.

Begin your analysis:
"""
    
    return prompt


MOCK_SUMMARY_TEMPLATE = """
## 📊 OBJECTIVE FACTS (No LLM Used)

This report was generated without AI interpretation. Data is purely factual.

**{ticker} - {period}**

**Price Data:**
- Current Price: ${current_price:.2f}
- Period Return: {period_return:+.2f}%
- Volatility (30d): {volatility:.2f}%

**Technical Indicators:**
- Trend: {trend}
- Risk Level: {risk_level}
- Max Drawdown: {max_drawdown:.2f}%
{sharpe_line}

**Moving Averages:**
- 20-day SMA: ${sma_20:.2f} ({sma_20_signal})
- 50-day SMA: ${sma_50:.2f} ({sma_50_signal})
- 200-day SMA: ${sma_200:.2f} ({sma_200_signal})

---

## 📰 NEWS ARTICLES ({news_count})

{news_list}

---

## ⚠️ IMPORTANT NOTICE

This analysis contains **objective data only**. No LLM interpretation was used.

To get AI-powered insights with scenario analysis:
1. Enable LLM in Settings (Ollama local or OpenAI)
2. Re-run analysis

**Disclaimer:** This is not financial advice. All data is for informational purposes only.
"""


def create_mock_summary(
    ticker: str,
    period: str,
    technical_data: dict,
    news_articles: list
) -> str:
    """
    Create a summary without using LLM (mock/template-based).
    
    Args:
        ticker: Stock symbol
        period: Time period
        technical_data: Technical indicators
        news_articles: List of news articles
        
    Returns:
        Formatted summary text
    """
    # Format news list
    news_list = ""
    for i, article in enumerate(news_articles[:10], 1):
        date_str = article.published_at.strftime("%d/%m/%Y %H:%M")
        news_list += f"{i}. [{article.title}]({article.url})  \n   *{article.source}* • {date_str}  \n\n"
    
    if not news_list:
        news_list = "*No recent news found*\n"
    
    # Format Sharpe ratio
    sharpe_line = ""
    if technical_data.get('sharpe_ratio'):
        sharpe_line = f"\n- Sharpe Ratio: {technical_data['sharpe_ratio']:.2f}"
    
    # SMA signals
    current = technical_data.get('current_price', 0)
    sma_20_signal = "above" if current > technical_data.get('sma_20', 0) else "below"
    sma_50_signal = "above" if current > technical_data.get('sma_50', 0) else "below"
    sma_200_signal = "above" if current > technical_data.get('sma_200', 0) else "below"
    
    return MOCK_SUMMARY_TEMPLATE.format(
        ticker=ticker,
        period=period,
        current_price=technical_data.get('current_price', 0),
        period_return=technical_data.get('return_30d', 0) * 100,
        volatility=technical_data.get('volatility_30d', 0) * 100,
        trend=technical_data.get('trend_signal', 'UNKNOWN'),
        risk_level=technical_data.get('risk_level', 'UNKNOWN'),
        max_drawdown=technical_data.get('max_drawdown', 0) * 100,
        sharpe_line=sharpe_line,
        sma_20=technical_data.get('sma_20', 0),
        sma_50=technical_data.get('sma_50', 0),
        sma_200=technical_data.get('sma_200', 0),
        sma_20_signal=sma_20_signal,
        sma_50_signal=sma_50_signal,
        sma_200_signal=sma_200_signal,
        news_count=len(news_articles),
        news_list=news_list
    )
