"""
Ainvestment - Professional Stock Research Terminal
Main Streamlit Application
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

from src.services.orchestrator import orchestrator
from src.utils.config import settings
from src.utils.logger import logger
from src.utils.cache import cache
from src.utils.validators import ValidationError


# Configuração da página
st.set_page_config(
    page_title="Ainvestment",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para aparência profissional
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .danger-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: 600;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #1557a0;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Aplicação principal."""
    
    # Cabeçalho
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<div class="main-header">📈 Ainvestment</div>', unsafe_allow_html=True)
        st.markdown("*Terminal Profissional de Pesquisa de Ações*")
    
    with col2:
        # Estatísticas de cache
        stats = cache.get_stats()
        if stats.get("enabled"):
            st.metric(
                "Cache Ativo",
                f"{stats.get('valid_entries', 0)} válidos",
                delta=f"-{stats.get('expired_entries', 0)} expirados"
            )
    
    # Configuração da barra lateral
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Configurações de IA
        st.subheader("Análise com IA")
        llm_provider = st.selectbox(
            "Provedor de IA",
            ["mock", "ollama", "openai"],
            index=["mock", "ollama", "openai"].index(settings.llm_provider),
            help="Mock = sem IA (só fatos), Ollama = local/grátis, OpenAI = nuvem/pago"
        )
        
        if llm_provider == "mock":
            st.info("✅ Usando resumo baseado em template (sem IA)")
        elif llm_provider == "ollama":
            st.info("🖥️ Usando Ollama local (certifique-se que está rodando)")
            st.code("ollama serve", language="bash")
        elif llm_provider == "openai":
            st.warning("💰 Usando API OpenAI (custos aplicam-se)")
            api_key_input = st.text_input(
                "Chave API OpenAI",
                value=settings.openai_api_key or "",
                type="password"
            )
        
        st.divider()
        
        # NewsAPI
        st.subheader("Fontes de Notícias")
        newsapi_enabled = st.checkbox(
            "Ativar NewsAPI",
            value=settings.newsapi_enabled,
            help="Requer chave API de newsapi.org"
        )
        
        if newsapi_enabled:
            newsapi_key = st.text_input(
                "Chave NewsAPI",
                value=settings.newsapi_key or "",
                type="password"
            )
        
        st.divider()
        
        # Gerenciamento de cache
        st.subheader("Cache")
        if st.button("Limpar Cache"):
            cache.clear_all()
            st.success("Cache limpo!")
        
        if st.button("Limpar Expirados"):
            count = cache.clear_expired()
            st.success(f"{count} entradas expiradas removidas")
    
    # Área de conteúdo principal
    st.header("🔍 Análise de Ações")
    
    # Seletor de mercado
    st.subheader("📊 Selecione o Mercado")
    market = st.radio(
        "Mercado",
        ["Ibovespa (Brasil)", "NASDAQ (EUA)"],
        index=0,
        horizontal=True,
        help="Escolha o mercado principal para análise"
    )
    
    # Definir ticker padrão baseado no mercado
    if "Ibovespa" in market:
        default_ticker = "PETR4.SA"
        ticker_examples = "ex: PETR4.SA, VALE3.SA, ITUB4.SA, BBDC4.SA"
    else:
        default_ticker = "AAPL"
        ticker_examples = "ex: AAPL, MSFT, GOOGL, NVDA, TSLA"
    
    st.divider()
    
    # Formulário de entrada
    with st.form("analysis_form"):
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            ticker = st.text_input(
                "Ticker da Ação",
                value=default_ticker,
                placeholder=ticker_examples,
                help="Digite um símbolo válido de ação"
            ).strip().upper()
        
        with col2:
            period = st.selectbox(
                "Período",
                ["3mo", "6mo", "1y", "2y", "5y"],
                index=2,
                help="Período de dados históricos"
            )
        
        with col3:
            include_btc = st.checkbox(
                "Incluir BTC",
                value=False,
                help="Adicionar comparação com Bitcoin"
            )
        
        submitted = st.form_submit_button("🚀 Gerar Relatório", use_container_width=True)
    
    # Processar análise
    if submitted and ticker:
        # Determinar tickers para analisar
        tickers = [ticker]
        if include_btc and ticker != "BTC-USD":
            tickers.append("BTC-USD")
        
        # Barra de progresso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(message: str, percent: int):
            """Callback para atualizações de progresso."""
            status_text.text(message)
            progress_bar.progress(percent)
        
        try:
            results = {}
            
            for i, t in enumerate(tickers):
                st.subheader(f"Analisando {t}...")
                
                # Executar análise
                result = orchestrator.analyze(
                    ticker=t,
                    period=period,
                    include_llm=(llm_provider != "mock"),
                    progress_callback=update_progress
                )
                
                results[t] = result
                
                # Limpar progresso para próximo ticker
                if i < len(tickers) - 1:
                    progress_bar.progress(0)
            
            # Limpar indicadores de progresso
            progress_bar.empty()
            status_text.empty()
            
            # Exibir resultados
            for ticker_symbol, result in results.items():
                display_analysis_result(result)
                
                # Divisor entre tickers
                if len(results) > 1:
                    st.divider()
            
        except ValidationError as e:
            st.error(f"❌ Erro de Validação: {e}")
            logger.error("validation_error_ui", error=str(e))
        
        except Exception as e:
            st.error(f"❌ Falha na Análise: {e}")
            logger.error("analysis_error_ui", error=str(e))
            st.exception(e)
    
    # Rodapé
    st.divider()
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption("📊 Dados: Yahoo Finance")
    with col2:
        st.caption("📰 Notícias: DuckDuckGo, NewsAPI")
    with col3:
        st.caption(f"🤖 IA: {settings.llm_provider.title()}")
    
    # Aviso legal
    st.markdown('<div class="danger-box">', unsafe_allow_html=True)
    st.markdown("""
    **⚠️ Aviso Legal:** Esta ferramenta é apenas para fins educacionais e informativos. 
    Não constitui aconselhamento financeiro. Investimentos envolvem risco de perda. 
    Sempre consulte um consultor financeiro qualificado antes de tomar decisões de investimento.
    """)
    st.markdown('</div>', unsafe_allow_html=True)


def display_analysis_result(result):
    """Exibir resultado da análise em formato profissional."""
    
    st.header(f"📊 Análise {result.ticker}")
    
    # Metadados
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Período", result.period)
    with col2:
        st.metric("Tempo de Processamento", f"{result.processing_time_seconds:.2f}s")
    with col3:
        st.metric("Qualidade dos Dados", f"{result.data_quality_score * 100:.0f}%")
    with col4:
        st.metric("Gerado em", result.generated_at.strftime("%H:%M:%S"))
    
    st.divider()
    
    # Recomendação em Destaque
    rec = result.recommendation
    if "COMPRA FORTE" in rec:
        st.success(f"### 🚀 RECOMENDAÇÃO: {rec}")
    elif "COMPRA" in rec:
        st.info(f"### 📈 RECOMENDAÇÃO: {rec}")
    elif "NEUTRO" in rec:
        st.warning(f"### ⚖️ RECOMENDAÇÃO: {rec}")
    elif "VENDA" in rec:
        st.warning(f"### 📉 RECOMENDAÇÃO: {rec}")
    else:
        st.error(f"### 🔻 RECOMENDAÇÃO: {rec}")
    
    st.caption("⚠️ Recomendação baseada em análise técnica automática. Não constitui aconselhamento financeiro.")
    st.divider()
    
    # Métricas Principais
    st.subheader("📈 Métricas Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Preço Atual",
            f"${result.indicators.current_price:.2f}",
            delta=None
        )
    
    with col2:
        return_30d_pct = result.indicators.return_30d * 100
        st.metric(
            "Retorno 30 dias",
            f"{return_30d_pct:+.2f}%",
            delta=f"{return_30d_pct:+.2f}%"
        )
    
    with col3:
        st.metric(
            "Tendência",
            result.indicators.trend_signal,
            delta=None
        )
    
    with col4:
        st.metric(
            "Nível de Risco",
            result.indicators.risk_level,
            delta=None
        )
    
    # Métricas detalhadas
    with st.expander("📊 Indicadores Técnicos Detalhados"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Retornos**")
            st.write(f"- 7 dias: {result.indicators.return_7d * 100:+.2f}%")
            st.write(f"- 30 dias: {result.indicators.return_30d * 100:+.2f}%")
            st.write(f"- Ano atual: {result.indicators.return_ytd * 100:+.2f}%")
            
            st.markdown("**Métricas de Risco**")
            st.write(f"- Volatilidade (30d): {result.indicators.volatility_30d * 100:.2f}%")
            st.write(f"- Queda Máxima: {result.indicators.max_drawdown * 100:.2f}%")
            if result.indicators.sharpe_ratio:
                st.write(f"- Índice Sharpe: {result.indicators.sharpe_ratio:.2f}")
        
        with col2:
            st.markdown("**Médias Móveis**")
            sma_20_status = "✅ Acima" if result.indicators.above_sma_20 else "❌ Abaixo"
            sma_50_status = "✅ Acima" if result.indicators.above_sma_50 else "❌ Abaixo"
            sma_200_status = "✅ Acima" if result.indicators.above_sma_200 else "❌ Abaixo"
            
            st.write(f"- MMA 20: ${result.indicators.sma_20:.2f} ({sma_20_status})")
            st.write(f"- MMA 50: ${result.indicators.sma_50:.2f} ({sma_50_status})")
            st.write(f"- MMA 200: ${result.indicators.sma_200:.2f} ({sma_200_status})")
    
    # Gráfico de preços
    st.subheader("📈 Gráfico de Preços")
    fig = create_price_chart(result)
    st.plotly_chart(fig, use_container_width=True)
    
    # Seção de notícias
    st.subheader(f"📰 Notícias ({result.news.article_count} artigos)")
    
    if result.news.article_count == 0:
        st.warning("Nenhuma notícia recente encontrada para este ticker")
    else:
        # Mostrar notícias em tabela
        news_data = []
        for article in result.news.articles[:10]:
            news_data.append({
                "Título": f"[{article.title[:60]}...]({article.url})",
                "Fonte": article.source,
                "Data": article.published_at.strftime("%d/%m/%Y %H:%M"),
                "Idade (horas)": f"{article.age_hours:.1f}h"
            })
        
        st.dataframe(news_data, use_container_width=True)
        
        # Resumo das fontes
        st.caption(f"Fontes: {', '.join(result.news.unique_sources)}")
    
    # Resumo com IA (se disponível)
    if result.summary:
        st.subheader("🤖 Análise com IA")
        
        # Indicador de confiança
        confidence_pct = result.summary.confidence_score * 100
        if confidence_pct >= 70:
            st.success(f"✅ Alta Confiança ({confidence_pct:.0f}%)")
        elif confidence_pct >= 40:
            st.warning(f"⚠️ Confiança Média ({confidence_pct:.0f}%)")
        else:
            st.error(f"❌ Baixa Confiança ({confidence_pct:.0f}%) - Dados insuficientes")
        
        # Texto do resumo
        st.markdown(result.summary.summary_text)
        
        # Citações
        if result.summary.citations:
            with st.expander(f"📚 Fontes Citadas ({len(result.summary.citations)})"):
                for citation in result.summary.citations:
                    st.markdown(f"- {citation.to_markdown()}")
    
    # Opções de exportação
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        markdown_content = result.to_markdown()
        st.download_button(
            label="📄 Baixar Markdown",
            data=markdown_content,
            file_name=f"{result.ticker}_{result.period}_analise.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    with col2:
        json_content = str(result.to_dict())
        st.download_button(
            label="📊 Baixar JSON",
            data=json_content,
            file_name=f"{result.ticker}_{result.period}_analise.json",
            mime="application/json",
            use_container_width=True
        )


def create_price_chart(result):
    """Criar gráfico interativo de preços com médias móveis."""
    
    df = result.stock_data.data
    
    fig = go.Figure()
    
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name=result.ticker
    ))
    
    # Médias móveis
    if len(df) >= 20:
        sma_20 = df['Close'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(
            x=df.index,
            y=sma_20,
            mode='lines',
            name='MMA 20',
            line=dict(color='orange', width=1)
        ))
    
    if len(df) >= 50:
        sma_50 = df['Close'].rolling(window=50).mean()
        fig.add_trace(go.Scatter(
            x=df.index,
            y=sma_50,
            mode='lines',
            name='MMA 50',
            line=dict(color='blue', width=1)
        ))
    
    if len(df) >= 200:
        sma_200 = df['Close'].rolling(window=200).mean()
        fig.add_trace(go.Scatter(
            x=df.index,
            y=sma_200,
            mode='lines',
            name='MMA 200',
            line=dict(color='red', width=1)
        ))
    
    fig.update_layout(
        title=f"{result.ticker} - {result.period}",
        xaxis_title="Data",
        yaxis_title="Preço (USD)",
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    return fig


if __name__ == "__main__":
    main()
