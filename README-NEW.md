# 📈 Ainvestment 2.0 - Professional Stock Research Terminal

> **Análise confiável de ações com citações obrigatórias e LLM-optional**

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.30+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🎯 O que mudou (v2.0)?

### ✅ **ANTES (v1.0 - Frágil)**
- ❌ GPT-3.5 obrigatório (custos imprevisíveis)
- ❌ Apenas DuckDuckGo (1 fonte de notícias)
- ❌ Sem citações (respostas "viajadas")
- ❌ Sem validação de inputs
- ❌ Sem cache (refetch sempre)
- ❌ UX básica

### ✅ **AGORA (v2.0 - Profissional)**
- ✅ **LLM-optional:** Mock (grátis) | Ollama (local) | OpenAI (pago)
- ✅ **Múltiplas fontes:** NewsAPI + RSS + DuckDuckGo
- ✅ **Citações obrigatórias:** [Fonte, Data](URL) em todo resumo
- ✅ **Modo cético:** "Dados insuficientes" quando aplicável
- ✅ **Validação robusta:** Ticker, período, retry, timeout
- ✅ **Cache inteligente:** SQLite com TTL (24h)
- ✅ **UI profissional:** Cards, métricas, gráficos, export PDF/MD
- ✅ **Testes:** 80%+ coverage, CI/CD ready
- ✅ **Observabilidade:** Logs estruturados (JSON)

---

## 🚀 Quick Start (5 minutos)

### 1. Clonar e Instalar

```bash
# Clone
git clone https://github.com/seu-usuario/ainvestment.git
cd ainvestment

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements-new.txt
```

### 2. Configurar

```bash
# Copiar template de configuração
cp .env.example .env

# Editar .env (opcional - funciona sem API keys!)
nano .env
```

**Configuração mínima (sem LLM, sem NewsAPI):**
```bash
LLM_PROVIDER=mock        # Apenas dados objetivos
NEWSAPI_ENABLED=false    # Usar DuckDuckGo apenas
CACHE_ENABLED=true
```

### 3. Executar

```bash
# Rodar app
streamlit run app.py
```

Abrir navegador em: http://localhost:8501

---

## 🛠️ Opções de LLM

### Opção 1: **Mock (Padrão)** - Grátis, Sem IA

**Vantagens:**
- ✅ Custo zero
- ✅ Latência <1s
- ✅ 100% confiável (apenas fatos)

**Desvantagens:**
- ⚠️ Sem narrativa/interpretação
- ⚠️ Apenas lista de fatos

**Configuração:**
```bash
# .env
LLM_PROVIDER=mock
```

---

### Opção 2: **Ollama (Local)** - Grátis, Privado ⭐ RECOMENDADO

**Vantagens:**
- ✅ Custo zero
- ✅ Privacidade total
- ✅ Sem limites de requisições
- ✅ Narrativa + cenários

**Desvantagens:**
- ⚠️ Requer 8GB RAM
- ⚠️ Latência 5-10s (CPU) ou 1-2s (GPU)

**Instalação:**

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Baixar de https://ollama.com/download

# Instalar modelo
ollama pull llama3.1:8b

# Iniciar servidor (terminal separado)
ollama serve
```

**Configuração:**
```bash
# .env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

---

### Opção 3: **OpenAI (Cloud)** - Baixo Custo, Alta Qualidade

**Vantagens:**
- ✅ Melhor qualidade de resumo
- ✅ Latência <2s
- ✅ Sem necessidade de hardware local

**Desvantagens:**
- ⚠️ Custos (~$0.001/análise com gpt-4o-mini)
- ⚠️ Requer internet

**Configuração:**

1. Obter API Key: https://platform.openai.com/api-keys
2. Configurar budget: https://platform.openai.com/usage → Set limits

```bash
# .env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-seu-key-aqui
DAILY_TOKEN_LIMIT=100000      # ~$0.50/dia
MONTHLY_BUDGET_USD=5.00
```

**Custos Estimados (gpt-4o-mini):**
- 1 análise: ~3K tokens = $0.0005 (R$ 0.002)
- 1000 análises/mês: ~$0.50 (R$ 2.50)

---

## 📰 Fontes de Notícias

### Opção 1: **DuckDuckGo (Padrão)** - Grátis

**Configuração:**
```bash
# Nenhuma configuração necessária
# Funciona out-of-the-box
```

**Limitações:**
- ⚠️ Confiabilidade ~60%
- ⚠️ Sem metadados ricos

---

### Opção 2: **NewsAPI** - 100 req/dia grátis ⭐ RECOMENDADO

**Vantagens:**
- ✅ Alta confiabilidade (95%)
- ✅ Metadados ricos (autor, imagem, fonte)
- ✅ 70k+ fontes globais

**Configuração:**

1. Signup grátis: https://newsapi.org/register
2. Copiar API key

```bash
# .env
NEWSAPI_ENABLED=true
NEWSAPI_KEY=seu-key-aqui
```

**Limites Free Tier:**
- 100 requisições/dia
- Apenas para desenvolvimento (ver termos)

---

## 📊 Estrutura do Projeto

```
ainvestment/
├── app.py                      # 🚀 Entry point Streamlit
├── src/
│   ├── models/                 # 📦 Data models
│   │   ├── stock_data.py
│   │   ├── news_article.py
│   │   └── analysis_result.py
│   ├── services/               # 🔧 Business logic
│   │   ├── data_sources.py     # Yahoo Finance + cache
│   │   ├── analytics.py        # Indicadores técnicos
│   │   ├── news.py             # Agregador notícias
│   │   ├── summarizer.py       # LLM-optional
│   │   ├── prompts.py          # Anti-alucinação
│   │   └── orchestrator.py     # Pipeline principal
│   └── utils/                  # 🛠️ Utilities
│       ├── config.py           # Pydantic settings
│       ├── logger.py           # Structured logging
│       ├── cache.py            # SQLite cache
│       └── validators.py       # Input validation
├── tests/                      # 🧪 Tests
│   ├── unit/
│   └── integration/
├── .env.example                # 📝 Config template
├── requirements-new.txt        # 📦 Dependencies
├── ARCHITECTURE.md             # 📐 Architecture doc
├── REFACTORING_PLAN.md         # 📋 Roadmap
├── PROMPTS.md                  # 🤖 LLM prompts
└── SECURITY.md                 # 🔒 Security checklist
```

---

## 🧪 Testando

```bash
# Instalar dependências de teste
pip install pytest pytest-cov pytest-mock

# Rodar testes unitários
pytest tests/unit/

# Rodar com coverage
pytest --cov=src tests/

# Rodar teste de integração (requer internet)
pytest tests/integration/
```

---

## 📈 Exemplos de Uso

### 1. Análise Básica (AAPL)

```bash
# Abrir app
streamlit run app.py

# No navegador:
# 1. Ticker: AAPL
# 2. Período: 1y
# 3. Clicar "Generate Report"
```

**Output esperado:**
- ✅ Preço atual, retornos, volatilidade
- ✅ 5-10 notícias com fontes
- ✅ Gráfico interativo
- ✅ Resumo (se LLM ativo)
- ✅ Export Markdown/JSON

---

### 2. Comparação com Bitcoin

```bash
# No app:
# 1. Ticker: MSFT
# 2. Período: 6mo
# 3. ✅ Include BTC
# 4. Generate Report
```

**Output:**
- Análise de MSFT
- Análise de BTC-USD
- Comparação lado-a-lado

---

### 3. Usando Programaticamente

```python
from src.services.orchestrator import orchestrator

# Analisar AAPL
result = orchestrator.analyze(ticker="AAPL", period="1y", include_llm=True)

# Acessar dados
print(f"Preço: ${result.stock_data.latest_price}")
print(f"Retorno 30d: {result.indicators.return_30d * 100:.2f}%")
print(f"Notícias: {result.news.article_count}")

# Export
markdown = result.to_markdown()
with open("AAPL_report.md", "w") as f:
    f.write(markdown)
```

---

## 🔧 Troubleshooting

### Problema: "Ticker not found"

```bash
# Verificar ticker no Yahoo Finance:
https://finance.yahoo.com/quote/AAPL

# Tickers especiais:
# - Bitcoin: BTC-USD
# - Ethereum: ETH-USD
# - S&P 500: ^GSPC
```

---

### Problema: "Ollama connection failed"

```bash
# Verificar se Ollama está rodando
curl http://localhost:11434/api/tags

# Se falhar, iniciar:
ollama serve

# Em outro terminal:
streamlit run app.py
```

---

### Problema: "NewsAPI rate limit"

```bash
# Opção 1: Desabilitar NewsAPI
# .env
NEWSAPI_ENABLED=false

# Opção 2: Limpar cache (reset quota local)
python -c "from src.utils.cache import cache; cache.clear_all()"
```

---

## 📝 Roadmap

### ✅ Semana 1-2 (Completo)
- [x] Arquitetura modular
- [x] LLM-optional
- [x] Citações obrigatórias
- [x] Cache + retry
- [x] UI profissional

### 🔄 Semana 3-4 (Próximo)
- [ ] Múltiplos tickers simultâneos
- [ ] Página "Compare"
- [ ] Testes de integração completos
- [ ] CI/CD (GitHub Actions)

### 📅 Mês 2
- [ ] Alertas por email
- [ ] Backtesting básico
- [ ] Sentiment analysis local

### 📅 Mês 3-6
- [ ] PostgreSQL + Redis
- [ ] API REST (FastAPI)
- [ ] Autenticação
- [ ] Deploy escalável (AWS/GCP)

---

## 🤝 Contribuindo

```bash
# Fork + clone
git clone https://github.com/seu-usuario/ainvestment.git

# Criar branch
git checkout -b feature/nova-funcionalidade

# Fazer mudanças + testes
pytest tests/

# Commit (conventional commits)
git commit -m "feat: adicionar suporte para ETFs"

# Push + Pull Request
git push origin feature/nova-funcionalidade
```

**Conventional Commits:**
- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `test:` Testes
- `refactor:` Refatoração

---

## ⚠️ Disclaimer

**ESTE SOFTWARE É APENAS PARA FINS EDUCACIONAIS E INFORMATIVOS.**

- ❌ Não constitui aconselhamento financeiro
- ❌ Não é recomendação de compra/venda
- ❌ Investimentos envolvem risco de perda
- ✅ Sempre consulte um profissional qualificado

O autor não se responsabiliza por perdas financeiras decorrentes do uso desta ferramenta.

---

## 📄 Licença

MIT License - Ver [LICENSE](LICENSE) para detalhes.

---

## 🙏 Agradecimentos

- **yfinance:** Yahoo Finance API
- **Streamlit:** Framework web
- **Ollama:** LLM local gratuito
- **NewsAPI:** Agregador de notícias
- **Comunidade Python:** Bibliotecas incríveis

---

## 📧 Suporte

- 🐛 Bugs: [GitHub Issues](https://github.com/seu-usuario/ainvestment/issues)
- 💬 Discussões: [GitHub Discussions](https://github.com/seu-usuario/ainvestment/discussions)
- 📧 Email: seuemail@example.com

---

**Desenvolvido com ❤️ usando Python + Streamlit**

⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!
