# Plano de Refatoração Ainvestment

## 🎯 OVERVIEW

Transformar Ainvestment de protótipo frágil para produto profissional em **3 iterações**.

**Meta:** Sistema confiável, citações obrigatórias, LLM-optional, custo controlado.

---

## 📅 SEMANA 1: Fundação + Pipeline Determinístico

### Dia 1-2: Setup e Estrutura

**Objetivos:**
- ✅ Nova estrutura de pastas modular
- ✅ Configuração com Pydantic (sem hardcoded secrets)
- ✅ Sistema de logging estruturado

**Tarefas:**

1. **Criar nova estrutura de pastas** (1h)
   ```bash
   ainvestment/
   ├── src/
   │   ├── services/
   │   │   ├── data_sources.py
   │   │   ├── analytics.py
   │   │   ├── news.py
   │   │   ├── summarizer.py
   │   │   └── orchestrator.py
   │   ├── ui/
   │   │   ├── pages/
   │   │   │   ├── 1_🏠_Home.py
   │   │   │   ├── 2_📊_Analysis.py
   │   │   │   └── 3_⚙️_Settings.py
   │   │   └── components/
   │   │       ├── metrics_card.py
   │   │       ├── chart.py
   │   │       └── sources_table.py
   │   ├── utils/
   │   │   ├── config.py
   │   │   ├── logger.py
   │   │   ├── cache.py
   │   │   └── validators.py
   │   └── models/
   │       ├── stock_data.py
   │       ├── news_article.py
   │       └── analysis_result.py
   ├── tests/
   │   ├── unit/
   │   ├── integration/
   │   └── fixtures/
   ├── app.py  # Entry point
   ├── .env.example
   ├── pyproject.toml
   └── README.md
   ```

2. **Configuração com Pydantic** (2h)
   ```python
   # src/utils/config.py
   from pydantic_settings import BaseSettings
   
   class Settings(BaseSettings):
       # LLM
       llm_provider: str = "ollama"  # ollama | openai | none
       openai_api_key: Optional[str] = None
       ollama_base_url: str = "http://localhost:11434"
       
       # NewsAPI
       newsapi_key: Optional[str] = None
       
       # Cache
       cache_ttl_hours: int = 24
       cache_db_path: str = ".cache/ainvestment.db"
       
       # Budgets
       daily_token_limit: int = 100_000
       monthly_budget_usd: float = 5.0
       
       class Config:
           env_file = ".env"
   ```

3. **Logger estruturado** (1h)
   ```python
   # src/utils/logger.py
   import structlog
   
   logger = structlog.get_logger()
   
   # Uso:
   logger.info("fetched_stock_data", ticker="AAPL", rows=252)
   ```

**Entregável:** ✅ Estrutura de pastas + config + logger funcionando

**Métrica de sucesso:** `pytest tests/` passa sem erros

---

### Dia 3-4: Camada de Dados (Robusta)

**Objetivos:**
- ✅ yfinance com validação, retry, timeout
- ✅ Cache SQLite (evitar refetch)
- ✅ Cálculo de indicadores técnicos objetivos

**Tarefas:**

4. **Implementar `data_sources.py`** (4h)
   ```python
   class YFinanceProvider:
       def fetch_price_history(ticker: str, period: str) -> pd.DataFrame:
           # Validação
           # Retry com exponential backoff
           # Cache hit/miss
           # Timeout 10s
   ```

5. **Implementar `analytics.py`** (3h)
   ```python
   class IndicatorCalculator:
       @staticmethod
       def calculate_all(df: pd.DataFrame) -> dict:
           return {
               "returns_7d": ...,
               "returns_30d": ...,
               "volatility_30d": ...,
               "sma_20": ...,
               "sma_50": ...,
               "max_drawdown": ...,
               "sharpe_ratio": ...
           }
   ```

6. **Cache SQLite** (2h)
   ```python
   # src/utils/cache.py
   class CacheManager:
       def get(key: str) -> Optional[Any]:
           # Check TTL
       def set(key: str, value: Any, ttl_hours: int):
           # Store serialized
   ```

**Entregável:** ✅ Módulos `data_sources` + `analytics` + `cache` com testes

**Métrica de sucesso:**
- ✅ 100% tickers válidos processados sem erro
- ✅ Cache hit rate > 60% em testes

---

### Dia 5: Camada de Notícias (Múltiplas Fontes)

**Objetivos:**
- ✅ Agregador de notícias com fallback
- ✅ Deduplicação por similaridade
- ✅ Metadados (fonte, data, url) sempre presentes

**Tarefas:**

7. **Implementar `news.py`** (5h)
   ```python
   class NewsAggregator:
       def fetch_news(ticker: str, days: int = 7) -> list[NewsArticle]:
           # Prioridade: NewsAPI → RSS → DuckDuckGo
           # Circuit breaker
           # Deduplicação (cosine similarity > 0.9)
   
   @dataclass
   class NewsArticle:
       title: str
       url: str
       published_at: datetime
       source: str
       snippet: str
   ```

8. **Deduplicação** (2h)
   ```python
   from sklearn.feature_extraction.text import TfidfVectorizer
   from sklearn.metrics.pairwise import cosine_similarity
   
   def deduplicate_news(articles: list) -> list:
       # TF-IDF + cosine similarity
   ```

**Entregável:** ✅ Módulo `news` com testes de deduplicação

**Métrica de sucesso:**
- ✅ Ao menos 5 notícias únicas por ticker
- ✅ 100% dos artigos têm (title, url, date, source)

---

### Dia 6-7: LLM-Optional + Mock Summarizer

**Objetivos:**
- ✅ Interface abstrata para summarizers
- ✅ Mock summarizer (sem LLM, apenas fatos)
- ✅ Ollama local summarizer (gratuito)

**Tarefas:**

9. **Implementar `summarizer.py`** (4h)
   ```python
   class SummarizerInterface(ABC):
       @abstractmethod
       def summarize(data: dict, news: list) -> SummaryResult:
           pass
   
   class MockSummarizer(SummarizerInterface):
       def summarize(...) -> SummaryResult:
           # Gera bullet points objetivos sem interpretação
   
   class OllamaLocalSummarizer(SummarizerInterface):
       def summarize(...) -> SummaryResult:
           # Chama Ollama local
           # Valida citações no output
   ```

10. **Prompts anti-alucinação** (2h)
    - Ver arquivo separado `PROMPTS.md`

**Entregável:** ✅ Módulo `summarizer` com 2 implementações (mock + ollama)

**Métrica de sucesso:**
- ✅ Mock gera relatório em <1s
- ✅ Ollama gera resumo com >80% citações válidas

---

## 📅 SEMANA 2: UI Profissional + Testes + Deploy

### Dia 8-9: Streamlit Multipage

**Objetivos:**
- ✅ UI profissional com cards e gráficos
- ✅ Export PDF/Markdown
- ✅ Theming sem CSS inline

**Tarefas:**

11. **Página Home** (3h)
    - Logo, descrição, disclaimers
    - Quick start guide

12. **Página Analysis** (5h)
    - Input: ticker, período, checkbox BTC
    - Progress bar durante análise
    - Cards: métricas-chave (retorno, volatilidade, drawdown)
    - Gráfico Plotly interativo (preço + SMA)
    - Seção "Notícias" com tabela (título, fonte, data, link)
    - Seção "Análise IA" (se LLM disponível)
    - Botões: Export Markdown, Export PDF

13. **Página Settings** (2h)
    - Seletor LLM: None | Ollama | OpenAI
    - Configuração de API keys
    - Budget tracking

**Entregável:** ✅ App Streamlit completo e funcional

**Métrica de sucesso:**
- ✅ Análise de AAPL gera relatório completo em <30s
- ✅ Export PDF funciona

---

### Dia 10-11: Testes + CI/CD

**Objetivos:**
- ✅ Coverage >80%
- ✅ GitHub Actions para CI
- ✅ Deploy no Streamlit Cloud

**Tarefas:**

14. **Testes unitários** (4h)
    ```bash
    pytest tests/unit/test_analytics.py
    pytest tests/unit/test_news.py
    pytest tests/unit/test_summarizer.py
    ```

15. **Testes de integração** (3h)
    ```python
    def test_full_pipeline_aapl():
        result = orchestrator.analyze("AAPL", period="1y")
        assert result.metrics["returns_30d"] is not None
        assert len(result.news) >= 3
        assert result.summary is not None
    ```

16. **GitHub Actions** (1h)
    ```yaml
    # .github/workflows/test.yml
    name: Tests
    on: [push]
    jobs:
      test:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v3
          - run: pip install -e .[dev]
          - run: pytest --cov=src tests/
    ```

17. **Deploy Streamlit Cloud** (1h)
    - Conectar GitHub repo
    - Adicionar secrets (NEWSAPI_KEY)
    - URL pública gerada

**Entregável:** ✅ Testes passando + deploy live

**Métrica de sucesso:**
- ✅ Coverage >80%
- ✅ App acessível em `https://ainvestment.streamlit.app`

---

### Dia 12-14: Polimento + Documentação

**Objetivos:**
- ✅ README completo
- ✅ Checklist de segurança
- ✅ Vídeo demo

**Tarefas:**

18. **README.md profissional** (2h)
    - Screenshots
    - Quickstart (5 minutos)
    - Configuração de LLM
    - Troubleshooting

19. **Checklist de segurança** (2h)
    - Ver arquivo `SECURITY.md`

20. **Vídeo demo** (1h)
    - Loom: 3 minutos mostrando análise AAPL

**Entregável:** ✅ Documentação completa

---

## 📅 MÊS 1 (Semanas 3-4): Melhorias Avançadas

### Semana 3: Múltiplos Tickers + Comparação

**Tarefas:**
21. Suporte para múltiplos tickers simultâneos (3d)
22. Página "Compare" para contrastar ações (2d)

**Entregável:** ✅ Análise comparativa (ex: AAPL vs MSFT vs BTC)

---

### Semana 4: Alertas + Backtesting Básico

**Tarefas:**
23. Sistema de alertas por email (SendGrid) (2d)
24. Backtesting de estratégia simples (SMA crossover) (3d)

**Entregável:** ✅ User pode salvar watchlist e receber alertas

---

## 🎯 CRITÉRIOS DE ACEITAÇÃO (Semana 2)

| # | Critério | Status |
|---|----------|--------|
| 1 | Análise de ticker válido completa em <30s | ⬜ |
| 2 | Ao menos 5 notícias com fonte+data+url | ⬜ |
| 3 | Resumo IA com >80% de citações válidas | ⬜ |
| 4 | Modo sem LLM funciona (mock summarizer) | ⬜ |
| 5 | Export PDF/Markdown funciona | ⬜ |
| 6 | Cache reduz latência em 60% | ⬜ |
| 7 | Custo LLM <$1/dia (se OpenAI) | ⬜ |
| 8 | Coverage testes >80% | ⬜ |
| 9 | Deploy no Streamlit Cloud OK | ⬜ |
| 10 | Zero erros para tickers válidos (AAPL, MSFT, BTC-USD) | ⬜ |

---

## 📊 TRACKING DE PROGRESSO

### Como usar este plano:

1. **Diariamente:** Check 2-3 tarefas concluídas
2. **Fim de semana:** Review e ajustar próxima semana
3. **Semana 2:** Demo interna + collect feedback
4. **Mês 1:** Release público beta

### Ferramentas:

- **Tasks:** GitHub Projects
- **Commits:** Conventional commits (`feat:`, `fix:`, `refactor:`)
- **Branches:** `main` (estável) | `develop` (trabalho)

---

## 🚀 PRÓXIMOS PASSOS (após Mês 1)

- **Mês 2:** PostgreSQL + Celery + Redis (escala)
- **Mês 3:** Sentiment analysis local (transformers)
- **Mês 4:** Integração com brokers (Alpha Vantage)
- **Mês 5:** Dashboard personalizado (watchlists)
- **Mês 6:** Avaliar migração Next.js (se >1000 users/dia)

---

**Nota:** Este plano é adaptável. Priorize sempre: **confiabilidade > features**.
