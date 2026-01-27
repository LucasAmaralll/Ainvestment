# Ainvestment - Arquitetura e Decisões Técnicas

## 1. DECISÃO: **MANTER PYTHON** (com melhorias)

### Justificativa

**Por que NÃO migrar para TypeScript/Next.js agora:**
- ✅ Ecosistema Python é superior para análise financeira (pandas, numpy, yfinance)
- ✅ Time-to-market: refatoração Python leva 1-2 semanas vs 4-6 semanas reescrevendo
- ✅ Bibliotecas de ML/AI melhor integradas (scikit-learn, statsmodels)
- ✅ Streamlit Cloud deploy gratuito e simples
- ✅ Menor curva de aprendizado para manutenção

**Quando reconsiderar TypeScript:**
- Se precisar de múltiplos usuários simultâneos (>1000/dia)
- Se precisar de autenticação/pagamentos complexos
- Se quiser marketplace/SaaS completo
- Prazo: 6+ meses após estabilizar versão Python

### Stack Recomendada (Python Modernizado)

```
Frontend:    Streamlit (multipage, st.cache, theming)
Backend:     Python 3.11+ (type hints, dataclasses)
Data:        yfinance + pandas + caching local (SQLite)
News:        NewsAPI, RSS feeds, DuckDuckGo (fallback)
LLM:         Ollama (local/gratuito) OU OpenAI (com limites)
Analytics:   pandas-ta, numpy
Charts:      Plotly (interativo)
Export:      Markdown, PDF (weasyprint)
Testing:     pytest, pytest-cov
CI/CD:       GitHub Actions → Streamlit Cloud
```

---

## 2. ARQUITETURA PROPOSTA

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT UI (app.py)                    │
│  ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌──────────────┐ │
│  │ Home    │  │ Analysis │  │ Compare │  │ Settings     │ │
│  │ Page    │  │ Page     │  │ Page    │  │ Page         │ │
│  └─────────┘  └──────────┘  └─────────┘  └──────────────┘ │
└───────────────────┬─────────────────────────────────────────┘
                    │
        ┌───────────┴────────────┐
        │   ORCHESTRATOR         │
        │   (services/orchestrator.py)
        │   - Pipeline determinístico
        │   - Error handling
        │   - Progress tracking
        └───────────┬────────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
┌───▼────┐    ┌────▼─────┐    ┌───▼──────┐
│ DATA   │    │  NEWS    │    │ LLM      │
│ LAYER  │    │  LAYER   │    │ LAYER    │
└────────┘    └──────────┘    └──────────┘

DATA LAYER (services/data_sources.py)
├── YFinanceProvider
│   ├── fetch_price_history(ticker, period)
│   ├── validate_ticker(ticker)
│   └── retry + caching
├── IndicatorCalculator (services/analytics.py)
│   ├── calculate_returns(df)
│   ├── calculate_volatility(df)
│   ├── calculate_moving_averages(df)
│   ├── calculate_drawdown(df)
│   └── calculate_sharpe_ratio(df)

NEWS LAYER (services/news.py)
├── NewsAggregator
│   ├── NewsAPIProvider (primary)
│   ├── RSSFeedProvider (fallback)
│   └── DuckDuckGoProvider (fallback)
├── NewsDeduplicator
│   └── cosine_similarity + url matching
├── NewsValidator
│   └── check_date, source, title

LLM LAYER (services/summarizer.py)
├── SummarizerInterface (ABC)
├── MockSummarizer (no LLM needed)
│   └── generate_bullet_points(data)
├── OllamaLocalSummarizer (gratuito)
│   └── llama3.1:8b local
└── OpenAISummarizer (pago, opcional)
    └── gpt-4o-mini com limites

UTILITIES (services/utils/)
├── cache_manager.py (SQLite caching)
├── config.py (pydantic settings)
├── logger.py (structured logging)
└── validators.py (input validation)
```

### Fluxo de Dados (Pipeline Determinístico)

```
USER INPUT (ticker, period, include_btc)
  │
  ├─► [1] VALIDAÇÃO
  │    └─► Ticker existe? Período válido?
  │
  ├─► [2] COLETA DE DADOS
  │    ├─► yfinance: preços históricos
  │    └─► Cache hit/miss (SQLite)
  │
  ├─► [3] CÁLCULO DE INDICADORES
  │    ├─► Retornos diários/mensais
  │    ├─► Volatilidade (std)
  │    ├─► Médias móveis (20d, 50d, 200d)
  │    ├─► Max drawdown
  │    └─► Sharpe ratio
  │
  ├─► [4] COLETA DE NOTÍCIAS
  │    ├─► NewsAPI (primary, 100 req/dia free)
  │    ├─► RSS feeds (sem limite)
  │    └─► DuckDuckGo (fallback)
  │    └─► Deduplicação (90% similarity)
  │
  ├─► [5] SUMARIZAÇÃO (LLM-OPTIONAL)
  │    ├─► Se LLM disponível:
  │    │    ├─► Prompt com citações obrigatórias
  │    │    ├─► Modo cético (confidence < 60% = "insuficiente")
  │    │    └─► Output: { summary, citations[], confidence }
  │    └─► Se LLM indisponível:
  │         └─► Mock: lista de fatos objetivos
  │
  └─► [6] GERAÇÃO DE RELATÓRIO
       ├─► Seção 1: Métricas Quantitativas (sempre)
       ├─► Seção 2: Notícias com Fontes (sempre)
       ├─► Seção 3: Análise Narrativa (se LLM disponível)
       └─► Export: Markdown/PDF
```

---

## 3. FONTES DE NOTÍCIAS CONFIÁVEIS

### Hierarquia de Fontes (prioridade)

```python
PRIMARY_SOURCES = {
    "newsapi": {
        "free_tier": "100 requests/day",
        "latency": "< 2s",
        "reliability": "95%",
        "metadata": ["title", "url", "publishedAt", "source", "author"]
    }
}

FALLBACK_SOURCES = {
    "rss_feeds": [
        "https://feeds.finance.yahoo.com/rss/2.0/headline",
        "https://www.reuters.com/finance/markets",
        # Sem limite de requisições
    ],
    "duckduckgo": {
        "use_case": "Último recurso",
        "reliability": "60%"
    }
}
```

### Estratégia de Rate Limiting

```python
# Exponential backoff + circuit breaker
retry_strategy = {
    "max_attempts": 3,
    "backoff": [1s, 5s, 15s],
    "circuit_breaker": {
        "threshold": 5,  # 5 falhas consecutivas
        "timeout": 60    # 60s antes de tentar novamente
    }
}
```

---

## 4. ESTRATÉGIA LLM (Custo Zero → Baixo Custo)

### Opção 1: **Ollama (Local, Gratuito)** ⭐ RECOMENDADO

```bash
# Instalar Ollama localmente
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:8b  # Modelo de 8B, bom para resumos

# Vantagens:
✅ Custo zero (roda local)
✅ Privacidade total
✅ Sem limite de requisições
✅ Bom para sumarização básica

# Desvantagens:
⚠️ Requer 8GB RAM
⚠️ Qualidade menor que GPT-4
⚠️ Latência 5-10s (CPU) ou 1-2s (GPU)
```

### Opção 2: **OpenAI GPT-4o-mini (Baixo Custo)**

```python
# Preços (Jan 2025):
# Input:  $0.150 / 1M tokens
# Output: $0.600 / 1M tokens

# Exemplo de custo:
# 1 análise = ~2K tokens input + 1K output
# Custo = (2000 * 0.15 + 1000 * 0.60) / 1M = $0.0009 (~R$ 0.005)
# 1000 análises/mês = $0.90 (R$ 4.50)

SAFETY_LIMITS = {
    "max_tokens_per_request": 2000,
    "daily_budget": 100_000,  # tokens/dia
    "monthly_budget_usd": 5.00,
    "fallback": "ollama_local"
}
```

### Opção 3: **Groq (Cloud, Gratuito)** 🚀 ALTERNATIVA

```python
# Free tier: 30 req/min, 14,400/dia
# Modelos: llama-3.1-8b, mixtral-8x7b
# Latência: <1s (muito rápido!)

# Limitação: apenas inglês funciona bem
```

### Implementação LLM-Optional

```python
class SummarizerFactory:
    @staticmethod
    def create(config: Config) -> SummarizerInterface:
        if config.llm_provider == "none":
            return MockSummarizer()  # Sem LLM, apenas fatos
        elif config.llm_provider == "ollama":
            return OllamaLocalSummarizer()  # Gratuito
        elif config.llm_provider == "openai":
            return OpenAISummarizer(
                budget_manager=BudgetManager(daily_limit=config.daily_budget)
            )
        else:
            logger.warning("LLM indisponível, usando mock")
            return MockSummarizer()
```

---

## 5. ANTI-ALUCINAÇÃO: GUARDRAILS

### Técnicas Implementadas

1. **Citações Obrigatórias**
   ```python
   # Prompt exige formato:
   # "Segundo [Fonte X](url), publicado em DD/MM/AAAA, ..."
   # Parser valida que cada afirmação tem [citation]
   ```

2. **Modo Cético**
   ```python
   if len(news_articles) < 3:
       return "⚠️ Dados insuficientes para análise confiável"
   
   if confidence_score < 0.6:
       return "⚠️ Baixa confiança: apenas {len(sources)} fontes encontradas"
   ```

3. **Separação Fatos vs Interpretação**
   ```markdown
   ## 📊 FATOS OBJETIVOS
   - Preço atual: $150.00 (fonte: Yahoo Finance)
   - Variação 7d: -5.2% (fonte: Yahoo Finance)
   
   ## 📰 NOTÍCIAS RECENTES
   - [Reuters, 25/01/2026]: "Empresa X anuncia..." [url]
   
   ## 🔮 CENÁRIOS POSSÍVEIS (baseado em IA)
   ⚠️ Aviso: Esta seção contém interpretações, não recomendações
   - Cenário otimista: ...
   - Cenário pessimista: ...
   ```

4. **Validação de Output**
   ```python
   def validate_summary(text: str, sources: list) -> bool:
       # Conta citações no texto
       citations = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', text)
       
       # Exige ao menos 1 citação por parágrafo
       paragraphs = text.split('\n\n')
       return len(citations) >= len(paragraphs) * 0.8
   ```

---

## 6. COMPARAÇÃO: ATUAL vs PROPOSTO

| Aspecto | Atual (Frágil) | Proposto (Robusto) |
|---------|----------------|-------------------|
| **LLM** | GPT-3.5 (obrigatório, $$) | Ollama local (grátis) + OpenAI opcional |
| **Fontes notícias** | DuckDuckGo (1 fonte) | NewsAPI + RSS + DDG (3 fontes) |
| **Citações** | ❌ Nenhuma | ✅ Obrigatórias com URL + data |
| **Validação** | ❌ Nenhuma | ✅ Ticker, datas, timeouts, retry |
| **Cache** | ❌ Refetch sempre | ✅ SQLite (evita API calls) |
| **Modo sem LLM** | ❌ Impossível | ✅ Gera relatório quantitativo |
| **UX** | Textarea simples | Cards, gráficos, export PDF |
| **Testes** | ❌ Nenhum | ✅ pytest (coverage >80%) |
| **Custos** | Imprevisível | Controlado (budget + fallback) |
| **Observabilidade** | ❌ Nenhuma | ✅ Logs estruturados (JSON) |

---

## 7. RISCOS E MITIGAÇÕES

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Yahoo Finance API falha | Alta | Alto | Cache + retry + fallback para Alpha Vantage |
| NewsAPI quota excedido | Média | Médio | RSS feeds automático |
| Ollama muito lento | Média | Baixo | Timeout 30s + fallback para mock |
| Ticker inválido | Alta | Baixo | Validação prévia com yfinance |
| Usuário espera muito | Alta | Alto | Progress bar + streaming UI |

---

## 8. MÉTRICAS DE SUCESSO

```python
KPIS = {
    "confiabilidade": {
        "error_rate": "< 5%",  # 95% das análises sem erro
        "citation_coverage": "> 80%",  # 80% das afirmações citadas
        "data_freshness": "< 24h"  # Notícias de até 24h
    },
    "performance": {
        "p95_latency": "< 30s",  # 95% das análises em <30s
        "cache_hit_rate": "> 60%",  # 60% usa cache
    },
    "custo": {
        "monthly_llm_cost": "< $5",
        "api_calls_per_analysis": "< 15"
    },
    "qualidade": {
        "test_coverage": "> 80%",
        "user_satisfaction": "> 4.0/5"
    }
}
```

---

## 9. ROADMAP DE EVOLUÇÃO (6 meses)

### Fase 1: Fundação (semanas 1-2) ✅ ESTE PLANO
- Arquitetura modular
- LLM-optional
- Citações obrigatórias

### Fase 2: Melhorias (semanas 3-4)
- Backtesting de estratégias
- Múltiplos tickers simultâneos
- Alertas por email

### Fase 3: Escala (mês 2)
- PostgreSQL (substituir SQLite)
- Celery (jobs assíncronos)
- Redis (cache distribuído)

### Fase 4: Avançado (mês 3-6)
- Sentiment analysis local (transformers)
- Integração com brokers (Alpha Vantage, IEX Cloud)
- Dashboard personalizado (salvar watchlists)
- **Considerar migração Next.js** (se >1000 users/dia)

---

**Decisão Final:** Refatorar em Python com arquitetura robusta. ROI imediato, mantendo caminho aberto para TypeScript no futuro.
