Vou ajustar o README e o post no LinkedIn para incluir o nome do projeto **Ainvestiment**.

### README do Projeto

## Ainvestiment: Análise de Ações com Streamlit e LangChain

**Ainvestiment** é uma aplicação web desenvolvida em Python que realiza a análise de ações utilizando o Yahoo Finance e fornece resumos de notícias relacionadas às ações. A interface é implementada com Streamlit, oferecendo uma experiência de usuário interativa e intuitiva.

#### Funcionalidades

1. **Análise de Preços de Ações**:
   - Obtém dados históricos de preços de ações do Yahoo Finance para o último ano.
   - Analisa a tendência dos preços (alta, baixa ou estável).

2. **Resumo de Notícias de Mercado**:
   - Utiliza DuckDuckGo para obter as principais notícias relacionadas à ação solicitada.
   - Gera um resumo das notícias e avalia a tendência do mercado (alta, baixa ou estável) com base nas notícias.

3. **Geração de Relatórios**:
   - Cria um boletim informativo de 3 parágrafos sobre a ação analisada, incluindo um resumo executivo, análise detalhada e previsão de tendência.

#### Tecnologias Utilizadas

- **Streamlit**: Para criar a interface web interativa.
- **Yahoo Finance**: Para obter dados históricos de preços de ações.
- **DuckDuckGo**: Para buscar e resumir notícias de mercado.
- **LangChain**: Para orquestrar agentes de IA que realizam análises e geram relatórios.
- **OpenAI GPT-3.5 Turbo**: Para análise de tendências e criação de resumos e relatórios.

#### Instalação

1. Clone este repositório:
   ```bash
   git clone https://github.com/seu_usuario/ainvestiment.git
   ```
2. Navegue até o diretório do projeto:
   ```bash
   cd ainvestiment
   ```
3. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```
4. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
5. Defina a variável de ambiente para a chave da API do OpenAI:
   ```bash
   export OPENAI_API_KEY="sua-chave-api-aqui"  # No Windows: set OPENAI_API_KEY=sua-chave-api-aqui
   ```

#### Executando o Projeto

Para executar a aplicação Streamlit, use o seguinte comando:
```bash
streamlit run crewai-stocks.py
```
