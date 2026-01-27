# 🏗️ ARQUITETURA PARA PRODUÇÃO - Multi-Usuário com Custo Zero

**Data:** 27/01/2026  
**Requisitos Atualizados:**
- ✅ Custo **zero** (não pode gastar)
- ✅ Suportar **múltiplos usuários** simultâneos
- ✅ Pronto para **demonstração pública/empresarial**
- ✅ Escalável e profissional

---

## 🎯 Decisão Arquitetural

**Stack Recomendada:**

```
Frontend: Next.js 14 + TypeScript + Tailwind CSS
Backend: FastAPI (Python) como Vercel Serverless Functions
Dados: yfinance (serverless) + Upstash Redis (cache gratuito)
LLM: Ollama local via API OU Groq (grátis, 14,400 req/day)
Deploy: Vercel (frontend + backend = 100% grátis)
```

### Por que NÃO Streamlit para produção?

| Critério | Streamlit Cloud Free | Next.js + Vercel Free |
|----------|---------------------|----------------------|
| **Usuários simultâneos** | ~10-20 (limite baixo) | Milhares (serverless) |
| **Bandwidth** | 1GB/mês | 100GB/mês |
| **Execuções** | Ilimitadas mas lentas | 100GB-hours/mês |
| **Custom domain** | ❌ Não | ✅ Sim |
| **Edge caching** | ❌ Não | ✅ Sim (CDN global) |
| **Cold start** | 30-60s | 1-3s |
| **Profissionalismo** | 6/10 (parece app interno) | 10/10 (indistinguível de produto pago) |

**Veredito:** Streamlit é excelente para **demos locais** (o que fizemos até agora está perfeito para você testar), mas para **produção pública** com múltiplos usuários, Next.js + Vercel é superior e igualmente gratuito.

---

## 🏛️ Arquitetura Proposta

```
┌─────────────────────────────────────────────────────────────┐
│                        USUÁRIO                              │
│                     (Browser/Mobile)                        │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  VERCEL EDGE NETWORK                        │
│             (CDN Global - Custo Zero)                       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         NEXT.JS 14 FRONTEND                         │   │
│  │  - TypeScript + React Server Components            │   │
│  │  - Tailwind CSS + shadcn/ui                         │   │
│  │  - Chart.js/Recharts (gráficos)                     │   │
│  │  - Streaming UI (exibir análise em tempo real)     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │    VERCEL SERVERLESS FUNCTIONS (FastAPI)            │   │
│  │  /api/stock/[ticker]   - Dados de preço            │   │
│  │  /api/news/[ticker]    - Agregação de notícias     │   │
│  │  /api/analyze/[ticker] - Análise completa          │   │
│  │  /api/compare          - Comparar múltiplos ativos │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │
                ┌────────────┼────────────┐
                ▼            ▼            ▼
       ┌─────────────┐ ┌──────────┐ ┌─────────────┐
       │  yfinance   │ │ NewsAPI  │ │ Groq LLM    │
       │   (grátis)  │ │(100/dia) │ │(14,400/dia) │
       └─────────────┘ └──────────┘ └─────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Upstash Redis   │
                    │ (Cache 10k/dia) │
                    │   Custo Zero    │
                    └─────────────────┘
```

---

## 💰 Análise de Custos

### Tier Gratuito Vercel (Free Plan)

| Recurso | Limite Grátis | Suficiente Para |
|---------|--------------|-----------------|
| Bandwidth | 100 GB/mês | ~100k pageviews/mês |
| Execuções Serverless | 100 GB-hours/mês | ~500k requests API |
| Build Minutes | 6,000 min/mês | ~200 deploys |
| Usuários Simultâneos | Ilimitado | Centenas/milhares |
| Custom Domains | 1 | exemplo.com |
| Edge Functions | 100k requests/day | Suficiente |

**Conclusão:** Para um app de análise de ações com ~1000 usuários/mês, você NÃO ultrapassará os limites gratuitos.

### Alternativas se Vercel ficar caro (improvável)

1. **Cloudflare Pages + Workers** (grátis, bandwidth ilimitado)
2. **Netlify** (100GB/mês, serverless functions)
3. **AWS Amplify Free Tier** (12 meses grátis, depois ~$5/mês)

---

## 🔧 Stack Detalhada

### Frontend: Next.js 14 + TypeScript

**Por que Next.js?**
- ✅ Server Components = carrega dados no servidor (mais rápido)
- ✅ Streaming UI = exibe análise enquanto carrega (UX superior)
- ✅ SEO nativo (Google indexa suas análises)
- ✅ TypeScript = type safety, menos bugs
- ✅ Tailwind CSS + shadcn/ui = UI profissional em horas

**Estrutura:**
```
app/
├── page.tsx                    # Home: pesquisa de ticker
├── stock/[ticker]/page.tsx     # Página de análise individual
├── compare/page.tsx            # Comparar múltiplos ativos
├── api/
│   ├── stock/[ticker]/route.ts       # Proxy para FastAPI
│   ├── news/[ticker]/route.ts
│   └── analyze/[ticker]/route.ts
├── components/
│   ├── StockChart.tsx          # Gráfico candlestick
│   ├── MetricsCard.tsx         # Cards de métricas
│   ├── NewsCard.tsx            # Cartão de notícia
│   └── AnalysisStream.tsx      # Streaming de análise LLM
└── lib/
    ├── api-client.ts           # Chamadas para backend
    └── types.ts                # TypeScript types
```

**Dependências:**
```json
{
  "dependencies": {
    "next": "14.1.0",
    "react": "18.2.0",
    "recharts": "2.10.0",        // Gráficos React
    "tailwindcss": "3.4.0",      // Estilo
    "shadcn-ui": "latest",       // Componentes UI
    "date-fns": "3.0.0",         // Manipulação de datas
    "swr": "2.2.0"               // Cache de dados client-side
  }
}
```

---

### Backend: FastAPI como Vercel Serverless

**Por que FastAPI + Serverless?**
- ✅ Python (reutiliza todo código de analytics.py, news.py, etc.)
- ✅ Serverless = escala automaticamente (0 → 1000 usuários sem configuração)
- ✅ Custo zero quando não está em uso (paga apenas por execução)
- ✅ FastAPI é rápido (Starlette + Pydantic)

**Estrutura:**
```
api/
├── stock.py         # GET /api/stock/AAPL?period=1y
├── news.py          # GET /api/news/AAPL
├── analyze.py       # POST /api/analyze { ticker, period, llm_enabled }
├── compare.py       # POST /api/compare { tickers: ["AAPL", "MSFT"] }
└── _shared/
    ├── analytics.py      # (reutilizar do código atual)
    ├── news.py           # (reutilizar do código atual)
    ├── summarizer.py     # (reutilizar do código atual)
    └── cache.py          # Upstash Redis client
```

**Exemplo de endpoint:**
```python
# api/analyze.py
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from _shared.analytics import IndicatorCalculator
from _shared.news import NewsAggregator
from _shared.summarizer import GroqSummarizer
import json

app = FastAPI()

@app.get("/api/analyze/{ticker}")
async def analyze_stock(ticker: str, period: str = "1y"):
    async def generate():
        # Stream 1: Dados de preço
        yield json.dumps({"type": "price", "data": {...}}) + "\n"
        
        # Stream 2: Indicadores técnicos
        indicators = IndicatorCalculator.calculate_all(data)
        yield json.dumps({"type": "indicators", "data": indicators}) + "\n"
        
        # Stream 3: Notícias
        news = await NewsAggregator.fetch(ticker)
        yield json.dumps({"type": "news", "data": news}) + "\n"
        
        # Stream 4: Análise LLM (streaming)
        async for chunk in GroqSummarizer.stream_analysis(ticker, news):
            yield json.dumps({"type": "llm_chunk", "data": chunk}) + "\n"
    
    return StreamingResponse(generate(), media_type="application/x-ndjson")
```

**vercel.json:**
```json
{
  "functions": {
    "api/**/*.py": {
      "runtime": "python3.11",
      "maxDuration": 30
    }
  }
}
```

---

### Cache: Upstash Redis (Grátis)

**Por que Upstash?**
- ✅ 10,000 comandos/dia grátis
- ✅ Redis serverless (sem servidor para gerenciar)
- ✅ Edge caching (baixa latência global)
- ✅ TTL automático (24h)

**Uso:**
```python
from upstash_redis import Redis

redis = Redis(url=os.getenv("UPSTASH_REDIS_URL"), token=os.getenv("UPSTASH_REDIS_TOKEN"))

# Cache stock data por 24h
cache_key = f"stock:{ticker}:{period}"
cached = redis.get(cache_key)
if cached:
    return json.loads(cached)

# Se não estiver em cache, busca e armazena
data = fetch_from_yfinance(ticker, period)
redis.setex(cache_key, 86400, json.dumps(data))  # 24h TTL
```

**Alternativa:** Se não quiser depender de Upstash, use **Vercel KV** (10k leituras/dia grátis).

---

### LLM: Groq (Grátis) ou Ollama Local

**Opção 1: Groq (Recomendado para Produção)**

- ✅ **14,400 requests/dia grátis** (limite generoso)
- ✅ Latência baixíssima (~500ms para llama3-70b)
- ✅ API compatível com OpenAI
- ✅ Modelos: llama3-70b, mixtral-8x7b, gemma-7b

```python
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

response = client.chat.completions.create(
    model="llama3-70b-8192",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Analise {ticker}..."}
    ],
    max_tokens=2000,
    temperature=0.3
)
```

**Opção 2: Ollama Local (Para Deploy em VPS Próprio)**

Se você tiver um servidor próprio (Hetzner €5/mês), pode rodar Ollama lá e chamar via API.

**Opção 3: Mock (Fallback)**

Se ultrapassar limite do Groq, volta para template mock (sem IA).

---

## 🎨 UI/UX Design

### Página Inicial
```
┌────────────────────────────────────────────────────────┐
│  🏦 Ainvestment                          [Comparar]   │
├────────────────────────────────────────────────────────┤
│                                                        │
│       Análise Profissional de Ações com IA            │
│       ────────────────────────────────────             │
│                                                        │
│       ┌──────────────────────────┐                    │
│       │  Digite o ticker (ex:    │  [Analisar →]     │
│       │  AAPL, MSFT, PETR4.SA)   │                    │
│       └──────────────────────────┘                    │
│                                                        │
│       📊 Exemplos: [AAPL] [TSLA] [BTC-USD] [PETR4.SA] │
│                                                        │
│       ✨ Recursos:                                     │
│       • Dados em tempo real (Yahoo Finance)           │
│       • 20+ indicadores técnicos                      │
│       • Notícias agregadas de múltiplas fontes        │
│       • Análise com IA (Groq Llama 3)                 │
│       • Exportar relatório PDF/Markdown               │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### Página de Análise (Streaming)
```
┌────────────────────────────────────────────────────────┐
│  ← Voltar    AAPL - Apple Inc.                  $185.50│
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ +28.45%  │ │ 1.85%    │ │ 1.45     │ │ BULLISH  │ │
│  │ Retorno  │ │ Volatil. │ │ Sharpe   │ │ Tendência│ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
│                                                        │
│  📈 Gráfico Interativo (1 ano)                        │
│  ┌────────────────────────────────────────────────┐   │
│  │       ╱╲    ╱╲                                 │   │
│  │    ╱╲    ╲╱    ╲╱                              │   │
│  │ ╲╱                ╲                            │   │
│  │                     ╲    ╱╲                    │   │
│  │                       ╲╱    ╲                  │   │
│  └────────────────────────────────────────────────┘   │
│  [1D] [1W] [1M] [3M] [1Y] [5Y] [MAX]                  │
│                                                        │
│  📰 Notícias Recentes (8)                             │
│  ┌────────────────────────────────────────────────┐   │
│  │ 📄 Apple Unveils AI Features                   │   │
│  │ Reuters · 2 horas atrás                        │   │
│  │ Apple announced new AI capabilities... [Ler]   │   │
│  └────────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────────┐   │
│  │ 📄 Q4 Earnings Beat Expectations               │   │
│  │ CNBC · 1 dia atrás                             │   │
│  │ Apple reported earnings that surpassed... [Ler]│   │
│  └────────────────────────────────────────────────┘   │
│                                                        │
│  🤖 Análise com IA (Groq Llama 3 70B)                 │
│  ┌────────────────────────────────────────────────┐   │
│  │ ⚡ Gerando análise em tempo real...            │   │
│  │                                                 │   │
│  │ According to [Reuters, 25/01/2026](...),       │   │
│  │ Apple announced new AI-powered features        │   │
│  │ emphasizing on-device processing...            │   │
│  │                                                 │   │
│  │ [CNBC, 20/01/2026](...) reported Q4 earnings   │   │
│  │ beat expectations by 5%, with revenue...       │   │
│  └────────────────────────────────────────────────┘   │
│                                                        │
│  [📥 Exportar PDF] [📄 Exportar Markdown]             │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## 📊 Comparação: Streamlit vs Next.js

| Aspecto | Streamlit (Atual) | Next.js (Proposto) |
|---------|-------------------|-------------------|
| **Tempo de Dev** | 1-2 semanas (já feito!) | 3-4 semanas |
| **Curva de Aprendizado** | Baixa (Python puro) | Média (TypeScript + React) |
| **Performance (1 user)** | Excelente | Excelente |
| **Performance (100 users)** | Ruim (trava) | Excelente (serverless) |
| **Custo (0-1000 users)** | $0 (limite baixo) | $0 (limite alto) |
| **Profissionalismo** | 6/10 | 10/10 |
| **SEO** | ❌ Não | ✅ Sim |
| **Custom Domain** | ❌ Não (free tier) | ✅ Sim |
| **Cold Start** | 30-60s | 1-3s |
| **Streaming UI** | ❌ Não | ✅ Sim |
| **Mobile** | Responsivo mas limitado | Nativo |

---

## 🚀 Plano de Migração

### Fase 1: Protótipo Local (✅ COMPLETO)
- Streamlit app funcionando localmente
- Testar lógica de negócio
- Validar indicadores técnicos
- Testar prompts LLM

**Status:** Você está aqui! Execute `./setup.sh` para rodar.

### Fase 2: MVP Produção (2-3 semanas)
1. **Setup Next.js** (2 dias)
   - `npx create-next-app@latest ainvestment-web`
   - Configurar Tailwind + shadcn/ui
   - Criar páginas básicas (home, stock/[ticker])

2. **Migrar Backend para FastAPI Serverless** (1 semana)
   - Copiar `analytics.py`, `news.py`, `summarizer.py` para `api/_shared/`
   - Criar endpoints `/api/stock`, `/api/news`, `/api/analyze`
   - Configurar Upstash Redis
   - Testar localmente com `vercel dev`

3. **Frontend Next.js** (1 semana)
   - Componente `StockChart` (Recharts)
   - Componente `MetricsCard` (cards de métricas)
   - Componente `NewsCard` (lista de notícias)
   - Componente `AnalysisStream` (streaming LLM)

4. **Deploy** (1 dia)
   - `vercel deploy`
   - Configurar variáveis de ambiente (GROQ_API_KEY, UPSTASH_URL)
   - Custom domain (opcional)

### Fase 3: Otimizações (1-2 semanas)
- Página de comparação multi-ticker
- Export PDF com Puppeteer
- Alertas por email (usando Resend free tier)
- SEO optimization (meta tags, sitemap)

---

## 🎯 Recomendação Final

### Para Demonstração/Teste Interno (próximos dias)
**Use Streamlit (código já pronto):**
```bash
./setup.sh          # Instala dependências
source venv/bin/activate
streamlit run app.py
```

**Vantagens:**
- ✅ Funciona AGORA (código já está pronto)
- ✅ Testa toda a lógica de negócio
- ✅ Valida prompts LLM
- ✅ Perfeito para mostrar para 1-5 pessoas

### Para Lançamento Público (próximas semanas)
**Migre para Next.js + Vercel:**
- ✅ Suporta centenas/milhares de usuários simultâneos
- ✅ Custo zero até ~100k pageviews/mês
- ✅ UI profissional (indistinguível de produto pago)
- ✅ SEO (suas análises aparecem no Google)
- ✅ Custom domain (ainvestment.com.br)
- ✅ Streaming UI (análise aparece em tempo real)

---

## 📋 Checklist de Decisão

Execute `./setup.sh` agora e teste o Streamlit. Depois decida:

**Marque SIM se:**
- [ ] Você vai demonstrar para **mais de 20 pessoas** simultaneamente
- [ ] Você quer um **domínio próprio** (ainvestment.com)
- [ ] Você quer que apareça no **Google**
- [ ] Você quer UX **indistinguível de produto profissional**
- [ ] Você tem **3-4 semanas** para desenvolver

**Se 3+ marcados = Migre para Next.js**  
**Se 0-2 marcados = Fique com Streamlit**

---

## 💡 Minha Recomendação

**Abordagem Híbrida:**

1. **Esta semana:** Rode o Streamlit (`./setup.sh`), teste tudo, mostre para amigos/colegas
2. **Próximas 3 semanas:** Migre para Next.js + Vercel enquanto coleta feedback
3. **Semana 4:** Lance publicamente com Next.js

**Racional:** Streamlit valida a ideia AGORA, Next.js escala quando você anunciar.

---

## 📞 Próximos Passos

**Agora (5 minutos):**
```bash
./setup.sh
source venv/bin/activate
streamlit run app.py
# Teste com AAPL, TSLA, BTC-USD
```

**Se quiser migrar para Next.js, me avise e eu:**
1. Crio o projeto Next.js com estrutura completa
2. Migro toda lógica Python para FastAPI serverless
3. Crio componentes React profissionais
4. Configuro deploy Vercel com 1 comando

**Sua decisão?** 🤔
