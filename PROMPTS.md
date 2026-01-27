# Prompts Anti-Alucinação - Ainvestment

## 📋 Visão Geral

Este documento contém os prompts utilizados no Ainvestment para garantir que o LLM gere análises confiáveis, com citações obrigatórias e separação clara entre fatos e interpretações.

---

## 🎯 Princípios Fundamentais

1. **Citações Obrigatórias**: Toda afirmação factual deve ter [Fonte, Data](URL)
2. **Separação Clara**: FATOS vs INTERPRETAÇÕES vs CENÁRIOS
3. **Modo Cético**: Se dados insuficientes, dizer explicitamente
4. **Sem Recomendações**: Nunca "compre/venda", apenas "cenários possíveis"
5. **Confiança Explícita**: Declarar nível de confiança (0-100%)

---

## 🤖 System Prompt (Usado em Todas as Análises)

```
You are a skeptical financial analyst assistant. Your role is to:

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
```

---

## 📝 User Prompt Template

### Estrutura

```
**Technical Data for {ticker}:**
- Current Price: ${price}
- 7-day Return: {return_7d}%
- 30-day Return: {return_30d}%
- Volatility (30d): {volatility}%
- Trend Signal: {trend}
- Risk Level: {risk}

**News Articles ({count} found):**

1. **{title}**
   - Source: {source}
   - Date: DD/MM/YYYY
   - URL: {url}
   - Snippet: {snippet}

[... mais artigos ...]

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

**CONFIDENCE THRESHOLD:** If total confidence <60%, add prominent warning.

Begin your analysis:
```

---

## ✅ Exemplo de Output BOM (com citações)

```markdown
## 📊 OBJECTIVE FACTS

**AAPL - 30-day Analysis**

According to [Yahoo Finance, 25/01/2026](https://finance.yahoo.com), Apple's stock price closed at $185.50, representing a 30-day return of +8.2%. Volatility over the period was 18.5% (annualized).

## 📰 NEWS SUMMARY

**Product Launch:**
[Reuters, 23/01/2026](https://reuters.com/...) reported that Apple unveiled a new AI-powered device. [Bloomberg, 24/01/2026](https://bloomberg.com/...) noted supply chain concerns for the product.

**Earnings:**
[CNBC, 20/01/2026](https://cnbc.com/...) covered Q4 earnings, which beat expectations by 5%.

## 🔮 POSSIBLE SCENARIOS

**Confidence: 65%** (based on 8 news sources, 30 days of price data)

**Bullish Scenario (40% probability):**
If the new product launch succeeds and supply issues resolve, historical patterns suggest 10-15% upside potential over 3 months.

**Bearish Scenario (30% probability):**
Supply chain disruptions could delay product launch. Similar past delays resulted in 5-8% price corrections.

**Neutral Scenario (30% probability):**
Mixed signals from news and technical indicators suggest sideways movement until more clarity emerges.

## ⚠️ LIMITATIONS

- Only 8 news articles found (ideally 15+)
- No insider trading data available
- Macroeconomic factors not analyzed
- Sentiment analysis not performed
```

---

## ❌ Exemplo de Output RUIM (sem citações, com recomendações)

```markdown
## Analysis

Apple is a great company and the stock is going up! I recommend you buy now because:

1. The new product is amazing
2. Everyone loves Apple
3. The stock will definitely hit $200 soon

Trust me, this is a sure thing!
```

**Problemas:**
- ❌ Sem citações
- ❌ Linguagem de recomendação ("I recommend", "buy now")
- ❌ Certeza excessiva ("definitely", "sure thing")
- ❌ Sem separação fatos/interpretação
- ❌ Sem mencionar riscos ou incertezas

---

## 🛡️ Validação de Output

O sistema valida automaticamente que o output do LLM:

1. ✅ Contém ao menos 2 citações (links)
2. ✅ Não usa linguagem de recomendação proibida
3. ✅ Menciona limitações/incertezas (se poucas fontes)
4. ✅ Tem estrutura separada (fatos/notícias/cenários)

Se falhar validação → confiança reduzida em 50%

---

## 📊 Cálculo de Confiança

```python
confidence_score = (
    citation_count / 5.0 * 0.4 +      # Max 40% por citações
    news_count / 10.0 * 0.3 +          # Max 30% por qtd notícias
    data_points / 252.0 * 0.3          # Max 30% por dados históricos
)

if confidence_score < 0.6:
    add_warning = "⚠️ LOW CONFIDENCE - Insufficient Data"
```

---

## 🔄 Modo Mock (Sem LLM)

Quando `LLM_PROVIDER=mock`, o sistema usa um template estático:

```
## 📊 OBJECTIVE FACTS (No LLM Used)

This report was generated without AI interpretation. Data is purely factual.

**{ticker} - {period}**

**Price Data:**
- Current Price: ${price}
- Period Return: {return}%
- Volatility (30d): {volatility}%

[... métricas objetivas ...]

## 📰 NEWS ARTICLES ({count})

1. [{title}]({url})
   *{source}* • {date}

[... lista de notícias ...]

## ⚠️ IMPORTANT NOTICE

This analysis contains **objective data only**. No LLM interpretation was used.

To get AI-powered insights with scenario analysis:
1. Enable LLM in Settings (Ollama local or OpenAI)
2. Re-run analysis

**Disclaimer:** This is not financial advice.
```

---

## 🧪 Testes de Prompts

### Caso 1: Dados Insuficientes

**Input:** 2 artigos, 30 dias dados

**Output Esperado:**
```
⚠️ INSUFFICIENT DATA - Only 2 news articles found

Confidence: 25%

Based on limited information:
- [Source 1, Date](URL) mentions X
- [Source 2, Date](URL) mentions Y

Cannot provide reliable scenario analysis with current data.
```

### Caso 2: Dados Conflitantes

**Input:** 5 artigos, metade bullish, metade bearish

**Output Esperado:**
```
## 📰 NEWS SUMMARY

**Conflicting Signals:**

Positive: [Reuters, DD/MM](URL) reports strong earnings
Negative: [Bloomberg, DD/MM](URL) highlights supply issues

Given conflicting information, both scenarios are plausible:
- Bullish: 45% probability
- Bearish: 45% probability  
- Neutral: 10% probability
```

---

## 🎓 Boas Práticas

1. **Sempre teste prompts** com exemplos reais antes de deploy
2. **Ajuste temperatura** (0.3 = mais factual, 0.7 = mais criativo)
3. **Limite max_tokens** (1000-1500 para evitar custos)
4. **Valide output programaticamente** (regex para detectar citações)
5. **Log failures** quando validação falhar
6. **Fallback para mock** se LLM indisponível

---

## 📚 Referências

- [OpenAI Best Practices](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic Prompt Library](https://docs.anthropic.com/claude/page/prompts)
- [Avoiding Hallucinations (Microsoft)](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/advanced-prompt-engineering)

---

**Última atualização:** Janeiro 2026  
**Versão:** 2.0.0
