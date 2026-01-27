# 🚀 Guia de Instalação - Ainvestment

**Data:** 27/01/2026  
**Repositório:** https://github.com/LucasAmaralll/Ainvestment

Este guia mostra como instalar e rodar o Ainvestment em qualquer computador Linux (Ubuntu/Debian).

---

## 📋 Pré-requisitos

- **Sistema Operacional:** Ubuntu 20.04+ ou Debian 11+
- **RAM:** Mínimo 4GB (recomendado 8GB para usar Ollama)
- **Espaço em Disco:** ~5GB livres
- **Internet:** Necessária para baixar dependências

---

## ⚡ Instalação Rápida (1 comando)

```bash
git clone https://github.com/LucasAmaralll/Ainvestment.git
cd Ainvestment
chmod +x setup.sh && ./setup.sh
```

Isso vai:
- ✅ Instalar Python 3.12+ e pip
- ✅ Criar ambiente virtual (venv)
- ✅ Instalar todas as dependências Python
- ✅ Criar arquivo `.env` de configuração

---

## 📝 Instalação Passo a Passo

### 1. Clonar o Repositório

```bash
git clone https://github.com/LucasAmaralll/Ainvestment.git
cd Ainvestment
```

### 2. Instalar Dependências do Sistema

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip
```

### 3. Criar Ambiente Virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

Você verá `(venv)` no início do prompt.

### 4. Instalar Pacotes Python

```bash
pip install --upgrade pip
pip install -r requirements-new.txt
```

### 5. Configurar Variáveis de Ambiente

```bash
cp .env.example .env
nano .env  # ou use outro editor
```

**Configuração mínima (funciona sem IA):**
```bash
LLM_PROVIDER=mock
CACHE_ENABLED=true
```

**Configuração com Ollama (IA local grátis):**
```bash
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2:3b
OLLAMA_BASE_URL=http://localhost:11434
```

**Configuração com OpenAI (pago):**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-sua-chave-aqui
```

---

## 🦙 Instalar Ollama (Opcional - IA Local)

Se você quer análises com IA **gratuitas e locais**, instale o Ollama:

```bash
chmod +x install-ollama.sh
./install-ollama.sh
```

Depois de instalar:

```bash
# 1. Iniciar servidor Ollama
ollama serve &

# 2. Baixar modelo leve (recomendado)
ollama pull llama3.2:3b

# 3. Atualizar .env
# Mude LLM_PROVIDER=mock para LLM_PROVIDER=ollama
nano .env

# 4. Verificar se funcionou
ollama list
```

**Modelos disponíveis:**
- `llama3.2:3b` → 2GB (recomendado, rápido)
- `llama3.1:8b` → 4.9GB (mais preciso, mais lento)
- `llama3.1:70b` → 40GB (melhor qualidade, requer 64GB RAM)

---

## 🎯 Executar o Projeto

### Rodar pela primeira vez

```bash
# 1. Ativar ambiente virtual
source venv/bin/activate

# 2. Iniciar Ollama (se instalado)
ollama serve &

# 3. Rodar Streamlit
streamlit run app.py
```

### Rodar nas próximas vezes

```bash
cd Ainvestment
source venv/bin/activate
streamlit run app.py
```

O app abrirá em: **http://localhost:8501**

---

## 🧪 Testar Instalação

Execute estes comandos para verificar se está tudo funcionando:

### Teste 1: Ambiente Python

```bash
source venv/bin/activate
python --version  # Deve mostrar Python 3.12+
pip list | grep streamlit  # Deve mostrar streamlit instalado
```

### Teste 2: Dependências

```bash
python -c "import streamlit, yfinance, plotly, structlog; print('✅ Todas as dependências OK')"
```

### Teste 3: Ollama (se instalado)

```bash
curl http://localhost:11434/api/tags | grep llama3.2
# Deve mostrar o modelo instalado
```

### Teste 4: App Streamlit

```bash
streamlit run app.py
# Abra http://localhost:8501
# Digite ticker: PETR4.SA
# Período: 1y
# Clique "Gerar Relatório"
```

---

## 🛠️ Solução de Problemas

### Erro: `python3.12: command not found`

```bash
# Ubuntu 22.04+
sudo apt install python3.12 python3.12-venv

# Ubuntu 20.04
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12 python3.12-venv
```

### Erro: `ensurepip is not available`

```bash
sudo apt install python3.12-venv python3-pip
rm -rf venv  # Remover venv quebrado
python3 -m venv venv  # Recriar
```

### Erro: `ModuleNotFoundError: No module named 'streamlit'`

```bash
# Certifique-se que o venv está ativo
source venv/bin/activate
pip install -r requirements-new.txt
```

### Erro: `Ollama connection refused`

```bash
# Verificar se Ollama está rodando
pgrep -f "ollama serve" || ollama serve &

# Testar conexão
curl http://localhost:11434/api/tags
```

### Erro: `can't subtract offset-naive and offset-aware datetimes`

Já corrigido! Atualize o código:
```bash
git pull origin master
```

### Ollama muito lento (timeout após 30s)

Edite `.env` e aumente o timeout:
```bash
TIMEOUT_SECONDS=60  # ou mais
```

Ou use o modelo mock (sem IA):
```bash
LLM_PROVIDER=mock
```

---

## 📊 Estrutura do Projeto

```
Ainvestment/
├── app.py                      # App principal Streamlit
├── setup.sh                    # Script de instalação automática
├── install-ollama.sh           # Script para instalar Ollama
├── requirements-new.txt        # Dependências Python
├── .env.example                # Exemplo de configuração
├── .env                        # Sua configuração (criar manualmente)
├── src/
│   ├── models/                 # Modelos de dados
│   │   ├── stock_data.py
│   │   ├── news_article.py
│   │   └── analysis_result.py
│   ├── services/               # Lógica de negócio
│   │   ├── data_sources.py     # yfinance provider
│   │   ├── analytics.py        # Indicadores técnicos
│   │   ├── news.py             # Agregador de notícias
│   │   ├── summarizer.py       # LLM summarizers
│   │   ├── orchestrator.py     # Orquestrador principal
│   │   └── prompts.py          # Prompts LLM
│   └── utils/                  # Utilidades
│       ├── config.py           # Configurações (Pydantic)
│       ├── logger.py           # Logging estruturado
│       ├── cache.py            # Cache SQLite
│       └── validators.py       # Validação de inputs
├── tests/
│   └── unit/
│       └── test_validators.py
└── docs/
    ├── ARCHITECTURE.md         # Decisões arquiteturais
    ├── REFACTORING_PLAN.md    # Plano de refatoração
    ├── PROMPTS.md              # Engenharia de prompts
    ├── SECURITY.md             # Controles de segurança
    └── INSTALACAO.md           # Este arquivo
```

---

## 🔄 Atualizar o Projeto

Quando houver novas versões no GitHub:

```bash
cd Ainvestment
git pull origin master
source venv/bin/activate
pip install -r requirements-new.txt --upgrade
streamlit run app.py
```

---

## 🌐 Usar em Produção

Para usar com múltiplos usuários, consulte:
- **[PRODUCTION_ARCHITECTURE.md](PRODUCTION_ARCHITECTURE.md)** - Migração para Next.js + Vercel
- Deployment gratuito com Streamlit Cloud (limitado a ~20 usuários simultâneos)
- Deployment escalável com Next.js + Vercel (milhares de usuários, custo zero)

---

## 📞 Suporte

- **GitHub Issues:** https://github.com/LucasAmaralll/Ainvestment/issues
- **Documentação:** Leia os arquivos `.md` na pasta do projeto
- **Logs:** Verifique os logs em `.cache/ainvestment.log`

---

## ✅ Checklist de Instalação

Marque conforme for completando:

- [ ] Git instalado
- [ ] Python 3.12+ instalado
- [ ] Repositório clonado
- [ ] Ambiente virtual criado (`venv`)
- [ ] Dependências instaladas (`requirements-new.txt`)
- [ ] Arquivo `.env` criado
- [ ] Ollama instalado (opcional)
- [ ] Modelo Ollama baixado (opcional)
- [ ] Streamlit rodando em `http://localhost:8501`
- [ ] Análise de teste executada com sucesso (PETR4.SA)

---

## 🎯 Próximos Passos

Depois de instalar:

1. **Testar com ações brasileiras:** PETR4.SA, VALE3.SA, ITUB4.SA
2. **Testar com ações americanas:** AAPL, MSFT, GOOGL
3. **Testar com Bitcoin:** BTC-USD
4. **Explorar recomendações:** Veja COMPRA/VENDA automático
5. **Experimentar com Ollama:** Compare análise com IA vs Mock
6. **Exportar relatórios:** Baixe Markdown ou JSON

---

**Última atualização:** 27/01/2026  
**Versão:** 2.0 (Refatoração completa)
