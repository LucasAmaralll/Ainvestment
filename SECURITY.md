# Checklist de Segurança e Custos - Ainvestment

## 🔒 Visão Geral

Este documento cobre práticas de segurança, controle de custos e proteção de dados para o Ainvestment.

---

## 💰 CONTROLE DE CUSTOS

### 1. LLM - OpenAI

**Riscos:**
- ❌ Custos imprevisíveis se não limitados
- ❌ Tokens podem crescer exponencialmente
- ❌ Requisições maliciosas (se exposto publicamente)

**Mitigações:**

```python
# .env
DAILY_TOKEN_LIMIT=100000           # 100k tokens/dia (~$0.50)
MONTHLY_BUDGET_USD=5.00            # Hard limit mensal
MAX_REQUESTS_PER_HOUR=100          # Rate limit por hora

# Implementação
class BudgetManager:
    def check_budget(self) -> bool:
        if daily_tokens > DAILY_TOKEN_LIMIT:
            logger.warning("daily_limit_reached")
            return False
        return True
    
    def track_cost(self, tokens: int):
        # Custo GPT-4o-mini
        cost_usd = (tokens / 1_000_000) * 0.15  # Input
        self.daily_cost += cost_usd
```

**Monitoramento:**
```bash
# Ver usage em OpenAI dashboard
https://platform.openai.com/usage

# Configurar alertas
Settings → Billing → Usage Limits
- Set soft limit: $5/month
- Set hard limit: $10/month (safety)
```

**Fallback Automático:**
```python
if budget_exceeded():
    logger.warning("switching_to_mock_summarizer")
    return MockSummarizer()
```

---

### 2. NewsAPI

**Plano Free:**
- ✅ 100 requisições/dia
- ❌ Apenas para desenvolvimento (não produção)

**Custos:**
- Free: $0
- Developer ($449/mês): 250k req/mês
- Business ($1,249/mês): 1M req/mês

**Proteção:**

```python
# .env
NEWSAPI_ENABLED=false  # Desabilitar se quota excedido

# Circuit Breaker
class NewsAPIProvider:
    def __init__(self):
        self.failures = 0
        self.circuit_open = False
    
    def fetch(self):
        if self.circuit_open:
            logger.warning("newsapi_circuit_open")
            return []  # Fallback para DuckDuckGo
        
        try:
            # ... fetch ...
        except RateLimitError:
            self.failures += 1
            if self.failures >= 5:
                self.circuit_open = True
                # Esperar 1 hora antes de tentar novamente
```

**Alternativas Gratuitas:**
- ✅ DuckDuckGo (sem limite, mas menos confiável)
- ✅ RSS Feeds (Yahoo Finance, Reuters)
- ✅ Finnhub Free Tier (60 req/min)

---

### 3. Yahoo Finance (yfinance)

**Riscos:**
- ⚠️ API não-oficial (pode mudar sem aviso)
- ⚠️ Rate limiting implícito
- ⚠️ Pode bloquear IPs com uso excessivo

**Proteção:**

```python
# Retry com backoff exponencial
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
def fetch_with_retry(ticker, period):
    return yf.download(ticker, period=period, timeout=10)

# Cache agressivo
cache.set(f"stock_{ticker}_{period}", data, ttl_hours=24)

# Rate limiting (não mais que 10 req/min)
time.sleep(6)  # 6s entre requisições
```

**Alternativas Pagas (se yfinance falhar):**
- Alpha Vantage: $50/mês (500 req/dia)
- Polygon.io: $29/mês (5 req/s)
- IEX Cloud: $9/mês (50k msg/mês)

---

## 🔐 PROTEÇÃO DE API KEYS

### 1. Armazenamento Seguro

**❌ NUNCA FAZER:**
```python
# PERIGO! Hardcoded key
OPENAI_API_KEY = "sk-proj-abc123..."

# PERIGO! Commit .env para Git
git add .env
```

**✅ FAZER:**
```bash
# .env (adicionar ao .gitignore)
OPENAI_API_KEY=sk-proj-...
NEWSAPI_KEY=abc123...

# .gitignore
.env
.env.local
*.key
secrets/
```

```python
# Carregar de forma segura
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found")
```

---

### 2. Streamlit Secrets (para deploy)

**Produção no Streamlit Cloud:**

```toml
# .streamlit/secrets.toml (não commitar!)
[openai]
api_key = "sk-proj-..."

[newsapi]
api_key = "abc123..."
```

**Uso no código:**
```python
import streamlit as st

# Funciona em Streamlit Cloud e local (.env)
openai_key = st.secrets.get("openai", {}).get("api_key") or os.getenv("OPENAI_API_KEY")
```

**Configurar secrets no Streamlit Cloud:**
```
App Settings → Secrets
Colar conteúdo do secrets.toml
```

---

### 3. Rotação de Keys

**Política:**
- 🔄 Rotacionar keys a cada 90 dias
- 🔄 Rotacionar imediatamente se:
  - Leak em commit
  - Suspeita de comprometimento
  - Saída de membro da equipe

**Processo:**
```bash
# 1. Gerar nova key (OpenAI Dashboard)
# 2. Atualizar .env local
OPENAI_API_KEY=sk-proj-NEW-KEY

# 3. Atualizar Streamlit Cloud secrets
# 4. Testar
streamlit run app.py

# 5. Revogar key antiga (OpenAI Dashboard)
```

---

## 🛡️ SEGURANÇA DE DADOS

### 1. Dados do Usuário

**Princípios:**
- ✅ Não armazenar dados pessoais sem consentimento
- ✅ Cache apenas dados públicos (preços, notícias)
- ✅ Logs não devem conter PII (emails, IPs)

**Implementação:**
```python
# Logger: não incluir dados sensíveis
logger.info("analysis_completed", ticker="AAPL")  # OK
logger.info("user_email", email=user.email)       # ❌ NUNCA

# Cache: apenas dados públicos
cache.set(f"stock_{ticker}", data)  # OK
cache.set(f"user_{user_id}", data)  # ❌ Evitar
```

---

### 2. Input Validation (Prevenir Injection)

**Riscos:**
- ❌ LLM Injection: usuário tenta manipular prompt
- ❌ SQL Injection: se usar DB relacional (futuro)
- ❌ Path Traversal: ao exportar arquivos

**Mitigações:**

```python
# Validar ticker (apenas alphanumeric + hífen)
def validate_ticker(ticker: str) -> str:
    if not re.match(r'^[A-Z0-9\-\.]+$', ticker):
        raise ValidationError("Invalid ticker format")
    return ticker

# Sanitizar filename
def sanitize_filename(filename: str) -> str:
    # Remove caracteres perigosos
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    return filename[:200]  # Limitar tamanho

# Prompt injection protection
def sanitize_prompt_input(user_input: str) -> str:
    # Remover comandos de sistema
    forbidden = ["<|im_start|>", "<|im_end|>", "SYSTEM:", "USER:"]
    for token in forbidden:
        user_input = user_input.replace(token, "")
    return user_input[:500]  # Limitar tamanho
```

---

### 3. Cache Security

**Riscos:**
- ⚠️ Cache pode crescer infinitamente (disk full)
- ⚠️ Dados sensíveis em cache não criptografado

**Mitigações:**

```python
# Limitar tamanho do cache
class CacheManager:
    MAX_SIZE_MB = 500
    
    def check_size(self):
        size_mb = get_db_size(self.db_path) / (1024 * 1024)
        if size_mb > self.MAX_SIZE_MB:
            logger.warning("cache_size_exceeded", size_mb=size_mb)
            self.clear_oldest(percent=0.3)  # Remover 30%

# Cleanup automático (cron job)
# 0 2 * * * cd /app && python -m src.utils.cache --cleanup
```

---

## 🚨 RATE LIMITING & DDOS PROTECTION

### 1. Proteção Local

```python
from functools import wraps
import time

class RateLimiter:
    def __init__(self, max_calls: int, period_seconds: int):
        self.max_calls = max_calls
        self.period = period_seconds
        self.calls = []
    
    def allow_request(self) -> bool:
        now = time.time()
        # Remove chamadas antigas
        self.calls = [c for c in self.calls if c > now - self.period]
        
        if len(self.calls) >= self.max_calls:
            return False
        
        self.calls.append(now)
        return True

# Uso
limiter = RateLimiter(max_calls=10, period_seconds=60)

@rate_limited(limiter)
def analyze_stock(ticker):
    if not limiter.allow_request():
        raise TooManyRequestsError("Rate limit exceeded")
    # ...
```

---

### 2. Streamlit Cloud (Deploy)

**Limitações Nativas:**
- Streamlit Cloud: ~5 GB RAM, 1 CPU
- Timeout: 5 minutos de inatividade
- Concurrent users: ~10-20 (free tier)

**Se precisar escalar:**
- Streamlit Cloud Team ($250/mês): 16 GB RAM, mais usuários
- Self-hosted: AWS/GCP/Azure com autoscaling

---

## 📊 MONITORAMENTO & ALERTAS

### 1. Logs Estruturados

```python
# src/utils/logger.py já implementa
logger.info(
    "analysis_completed",
    ticker="AAPL",
    duration_ms=1234,
    news_count=8,
    llm_provider="ollama",
    cost_usd=0.0
)

# Output (JSON)
{
    "event": "analysis_completed",
    "ticker": "AAPL",
    "duration_ms": 1234,
    "news_count": 8,
    "llm_provider": "ollama",
    "cost_usd": 0.0,
    "timestamp": "2026-01-27T10:30:00Z"
}
```

**Análise de Logs:**
```bash
# Contar erros por tipo
cat logs/*.json | jq -r '.error_type' | sort | uniq -c

# Latência média
cat logs/*.json | jq -r '.duration_ms' | awk '{s+=$1; c++} END {print s/c}'

# Custo total (OpenAI)
cat logs/*.json | jq -r '.cost_usd' | awk '{s+=$1} END {print s}'
```

---

### 2. Alertas (Futuro)

```python
# Integração com Sentry (opcional)
import sentry_sdk

sentry_sdk.init(
    dsn="https://...",
    environment="production",
    traces_sample_rate=0.1
)

# Capturar erros críticos
try:
    result = orchestrator.analyze(ticker)
except Exception as e:
    sentry_sdk.capture_exception(e)
    raise
```

**Alertas via Email (SendGrid):**
```python
def send_alert(subject: str, message: str):
    if settings.daily_cost_usd > settings.monthly_budget_usd / 30:
        send_email(
            to="admin@example.com",
            subject="⚠️ Daily Budget Exceeded",
            body=f"Daily cost: ${daily_cost:.2f}"
        )
```

---

## ✅ CHECKLIST FINAL

### Antes de Deploy

- [ ] `.env` está no `.gitignore`
- [ ] Secrets configurados no Streamlit Cloud
- [ ] Rate limits configurados (LLM, NewsAPI)
- [ ] Budget limits configurados (OpenAI)
- [ ] Cache cleanup automático ativado
- [ ] Logs estruturados funcionando
- [ ] Input validation em todos endpoints
- [ ] Error handling robusto (try/except)
- [ ] Fallbacks configurados (mock summarizer)
- [ ] README atualizado com instruções

### Monitoramento Contínuo

- [ ] Verificar custos OpenAI semanalmente
- [ ] Limpar cache mensalmente
- [ ] Rotacionar API keys trimestralmente
- [ ] Review logs de erro semanalmente
- [ ] Atualizar dependências mensalmente (`pip list --outdated`)
- [ ] Backup de dados (se aplicável)

---

## 🆘 RESPOSTA A INCIDENTES

### Cenário 1: Custos Inesperados

```bash
# 1. Pausar app imediatamente
# Streamlit Cloud: Settings → Turn off app

# 2. Verificar usage
https://platform.openai.com/usage

# 3. Identificar causa
cat logs/*.json | jq -r 'select(.cost_usd > 0)' | tail -100

# 4. Implementar fix
# - Reduzir DAILY_TOKEN_LIMIT
# - Adicionar rate limiting
# - Trocar para Ollama local

# 5. Reativar app com monitoramento
```

---

### Cenário 2: API Key Vazou

```bash
# 1. Revogar key IMEDIATAMENTE
https://platform.openai.com/api-keys
→ Delete key

# 2. Gerar nova key
→ Create new key

# 3. Atualizar .env e Streamlit secrets

# 4. Git history cleanup (se commitado)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# 5. Force push (com cuidado!)
git push origin --force --all
```

---

### Cenário 3: App Offline

```bash
# 1. Verificar Streamlit Cloud status
https://status.streamlit.io

# 2. Verificar logs
Streamlit Cloud → App → Logs

# 3. Common fixes:
# - Dependência quebrada: revisar requirements.txt
# - Timeout: otimizar queries (cache)
# - OOM: reduzir uso de memória (limpar dataframes)

# 4. Rollback se necessário
git revert HEAD
git push origin main
```

---

## 📚 Referências

- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [OpenAI Safety Best Practices](https://platform.openai.com/docs/guides/safety-best-practices)
- [Streamlit Security](https://docs.streamlit.io/knowledge-base/deploy/authentication-without-sso)

---

**Última atualização:** Janeiro 2026  
**Versão:** 2.0.0
