# 🚀 Guia de Execução - Ainvestment v2.0

## ✅ Checklist Pré-Execução

Antes de rodar o app, confirme:

- [ ] Python 3.11+ instalado (`python --version`)
- [ ] Terminal/cmd aberto na pasta do projeto
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas
- [ ] Arquivo `.env` configurado (mesmo que vazio)

---

## 📦 Passo 1: Instalação (PRIMEIRA VEZ)

```bash
# 1. Clonar repositório (se ainda não fez)
git clone https://github.com/seu-usuario/ainvestment.git
cd ainvestment

# 2. Criar ambiente virtual
python3 -m venv venv

# 3. Ativar ambiente virtual
# Linux/Mac:
source venv/bin/activate

# Windows (cmd):
venv\Scripts\activate.bat

# Windows (PowerShell):
venv\Scripts\Activate.ps1

# 4. Atualizar pip
pip install --upgrade pip

# 5. Instalar dependências
pip install -r requirements-new.txt

# ⏱️ Tempo estimado: 2-3 minutos
```

**✅ Verificar instalação:**
```bash
python -c "import streamlit; print(f'Streamlit {streamlit.__version__} OK')"
python -c "import yfinance; print('yfinance OK')"
python -c "import pandas; print('pandas OK')"
```

---

## ⚙️ Passo 2: Configuração

### Opção A: Configuração Mínima (Recomendado para teste)

```bash
# Copiar template
cp .env.example .env

# Editar .env (ou usar valores padrão)
# Valores padrão já funcionam!
```

**Conteúdo mínimo do `.env`:**
```bash
LLM_PROVIDER=mock
NEWSAPI_ENABLED=false
CACHE_ENABLED=true
LOG_LEVEL=INFO
```

### Opção B: Com Ollama (LLM Local Gratuito)

```bash
# 1. Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Baixar modelo
ollama pull llama3.1:8b

# 3. Iniciar servidor (deixar rodando)
ollama serve &

# 4. Configurar .env
echo "LLM_PROVIDER=ollama" >> .env
echo "OLLAMA_BASE_URL=http://localhost:11434" >> .env
```

### Opção C: Com OpenAI (Pago)

```bash
# 1. Obter API key: https://platform.openai.com/api-keys

# 2. Configurar .env
echo "LLM_PROVIDER=openai" >> .env
echo "OPENAI_API_KEY=sk-proj-seu-key-aqui" >> .env
echo "DAILY_TOKEN_LIMIT=100000" >> .env
echo "MONTHLY_BUDGET_USD=5.00" >> .env
```

### Opção D: Com NewsAPI (Opcional)

```bash
# 1. Signup grátis: https://newsapi.org/register

# 2. Configurar .env
echo "NEWSAPI_ENABLED=true" >> .env
echo "NEWSAPI_KEY=seu-key-aqui" >> .env
```

---

## 🏃 Passo 3: Executar

### Método 1: Streamlit (UI Web) ⭐ RECOMENDADO

```bash
# Rodar app
streamlit run app.py

# Output esperado:
# You can now view your Streamlit app in your browser.
# Local URL: http://localhost:8501
# Network URL: http://192.168.x.x:8501

# ✅ Abrir navegador automaticamente
# ✅ App acessível em http://localhost:8501
```

**Opções úteis:**
```bash
# Rodar em porta diferente
streamlit run app.py --server.port 8080

# Desabilitar auto-reload
streamlit run app.py --server.runOnSave false

# Configurar tema
streamlit run app.py --theme.base dark
```

---

### Método 2: Python Script (Programático)

```python
# Criar arquivo: test_analysis.py
from src.services.orchestrator import orchestrator

# Analisar AAPL
result = orchestrator.analyze(
    ticker="AAPL",
    period="1y",
    include_llm=False  # Mock (sem LLM)
)

# Imprimir resumo
print(f"Ticker: {result.ticker}")
print(f"Preço: ${result.stock_data.latest_price:.2f}")
print(f"Retorno 30d: {result.indicators.return_30d * 100:.2f}%")
print(f"Notícias: {result.news.article_count}")

# Salvar relatório
with open("AAPL_report.md", "w") as f:
    f.write(result.to_markdown())

print("\n✅ Relatório salvo em AAPL_report.md")
```

```bash
# Executar
python test_analysis.py
```

---

## 🧪 Passo 4: Testar

### Teste 1: Validadores

```bash
# Rodar testes unitários
pytest tests/unit/test_validators.py -v

# Output esperado:
# test_validators.py::TestValidateTicker::test_valid_tickers PASSED
# test_validators.py::TestValidateTicker::test_invalid_ticker_empty PASSED
# ... (todos PASSED)

# ✅ Todos passando = instalação OK
```

### Teste 2: Análise Básica (no navegador)

1. Abrir http://localhost:8501
2. Ticker: `AAPL`
3. Período: `1y`
4. Clicar "🚀 Generate Report"
5. Aguardar ~10-15 segundos
6. ✅ Verificar:
   - [ ] Métricas aparecem (preço, retorno, trend)
   - [ ] Gráfico carrega
   - [ ] Notícias listadas (ao menos 3)
   - [ ] Pode exportar Markdown

### Teste 3: Com LLM (se configurado)

1. Se `LLM_PROVIDER=ollama`:
   - Verificar se `ollama serve` está rodando
   - Análise leva ~15-30s (dependendo do hardware)
   - ✅ Seção "🤖 AI Analysis" aparece

2. Se `LLM_PROVIDER=openai`:
   - Análise leva ~5-10s
   - ✅ Seção "🤖 AI Analysis" com citações

---

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'streamlit'"

**Causa:** Ambiente virtual não ativado ou dependências não instaladas

**Solução:**
```bash
# Verificar ambiente virtual
which python  # Linux/Mac (deve mostrar venv/bin/python)
where python  # Windows (deve mostrar venv\Scripts\python.exe)

# Se não ativado:
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstalar dependências
pip install -r requirements-new.txt
```

---

### Erro: "Ticker AAPL not found"

**Causa:** Sem conexão com internet ou yfinance bloqueado

**Solução:**
```bash
# Testar conexão
ping finance.yahoo.com

# Testar yfinance diretamente
python -c "import yfinance as yf; print(yf.Ticker('AAPL').info.get('regularMarketPrice'))"

# Se retornar preço = OK
# Se erro = verificar firewall/proxy
```

---

### Erro: "Ollama connection failed"

**Causa:** Servidor Ollama não está rodando

**Solução:**
```bash
# Verificar se Ollama está instalado
ollama --version

# Iniciar servidor (terminal separado)
ollama serve

# Testar conexão
curl http://localhost:11434/api/tags

# Se retornar JSON com modelos = OK
```

---

### Erro: "NewsAPI quota exceeded"

**Causa:** Limite de 100 requisições/dia atingido

**Solução:**
```bash
# Opção 1: Desabilitar NewsAPI temporariamente
# .env
NEWSAPI_ENABLED=false

# Opção 2: Limpar cache (reset quota local)
python -c "from src.utils.cache import cache; cache.clear_all()"

# Opção 3: Aguardar 24h para reset
```

---

### Erro: "Port 8501 already in use"

**Causa:** Outra instância do Streamlit rodando

**Solução:**
```bash
# Opção 1: Matar processo existente
# Linux/Mac:
pkill -f streamlit

# Windows:
taskkill /F /IM streamlit.exe

# Opção 2: Usar porta diferente
streamlit run app.py --server.port 8080
```

---

## 📊 Monitoramento em Tempo Real

### Ver logs estruturados

```bash
# Logs aparecem no terminal onde rodou `streamlit run`
# Formato JSON (se LOG_FORMAT=json)

# Exemplos:
# {"event": "analysis_started", "ticker": "AAPL", ...}
# {"event": "data_fetched_successfully", "rows": 252, ...}
# {"event": "analysis_completed", "duration_ms": 1234, ...}
```

### Ver cache stats

```python
# No Streamlit app (sidebar), ver métricas:
# Cache Hits: 5 valid
#            -2 expired
```

---

## 🎯 Próximos Passos

Após confirmar que tudo funciona:

1. **Explorar funcionalidades:**
   - Testar diferentes tickers (MSFT, GOOGL, BTC-USD)
   - Testar períodos diferentes (3mo, 2y, 5y)
   - Comparar com Bitcoin (checkbox "Include BTC")

2. **Configurar LLM (opcional):**
   - Ollama para análises locais gratuitas
   - OpenAI para melhor qualidade (pago)

3. **Adicionar NewsAPI (opcional):**
   - Melhora qualidade das notícias
   - 100 req/dia grátis

4. **Deploy (futuro):**
   - Streamlit Cloud (grátis, público)
   - Heroku/Railway (grátis com limites)
   - AWS/GCP (escalável, pago)

---

## 📚 Documentação Adicional

- [ARCHITECTURE.md](ARCHITECTURE.md) - Decisões técnicas
- [REFACTORING_PLAN.md](REFACTORING_PLAN.md) - Roadmap
- [PROMPTS.md](PROMPTS.md) - Estratégia anti-alucinação
- [SECURITY.md](SECURITY.md) - Segurança e custos

---

## ✅ Checklist Final

Antes de considerar setup completo:

- [ ] App abre em http://localhost:8501
- [ ] Análise de AAPL (1y) funciona
- [ ] Notícias aparecem (ao menos 3)
- [ ] Gráfico interativo funciona
- [ ] Export Markdown funciona
- [ ] Cache stats aparecem no sidebar
- [ ] Logs estruturados no terminal
- [ ] Sem erros críticos (warnings OK)

---

**Se todos os checkmarks acima estiverem ✅, parabéns! Setup completo! 🎉**

Hora de explorar e personalizar conforme suas necessidades!

---

**Dúvidas?** Abrir issue: https://github.com/seu-usuario/ainvestment/issues
