# Dashboard de Execução Financeira
## 4º Batalhão de Operações Ribeirinhas — Exercício 2026

Dashboard gerencial de execução financeira desenvolvido com Streamlit + Plotly.

---

## Arquivos do projeto

```
dashboard_financeiro/
├── app.py              ← código principal do app
├── requirements.txt    ← dependências Python
└── README.md           ← este arquivo
```

---

## Instalação (primeira vez)

### Pré-requisito: Python 3.9 ou superior
Verifique com: `python --version` ou `python3 --version`

Caso não tenha Python instalado, baixe em: https://www.python.org/downloads/

### Passo 1 — Instalar as dependências

Abra o terminal (Prompt de Comando ou PowerShell no Windows,
Terminal no macOS/Linux), navegue até a pasta do projeto e execute:

```bash
pip install -r requirements.txt
```

Ou instale manualmente:

```bash
pip install streamlit pandas plotly
```

### Passo 2 — Executar o app

```bash
streamlit run app.py
```

O app abrirá automaticamente no navegador em:
**http://localhost:8501**

---

## Como usar

### Importar dados via CSV

Na barra lateral, use os três botões de upload para carregar:

1. **Controle de Empenhos** — arquivo exportado do SIAFI com empenhos do exercício
2. **Restos a Pagar** — arquivo com restos a pagar de exercícios anteriores
3. **Controle de Saldo Geral** — arquivo com provisão e crédito disponível por mês e PI

Os arquivos devem estar no formato original exportado pelo SIAFI
(CSV separado por tabulação, codificação Latin-1).

### Lançamento manual

Use o formulário "Novo empenho" na barra lateral para incluir
empenhos manualmente. Os KPIs são recalculados automaticamente.

### Filtros

Use os filtros de PI e Natureza de Despesa na barra lateral
para restringir a visualização a um programa interno ou
categoria de despesa específica.

---

## Abas do dashboard

| Aba | Conteúdo |
|-----|----------|
| Visão Geral | KPIs consolidados, funil de despesa, barras de progresso |
| Empenhos 2026 | Tabela detalhada por NE, pendências de liquidação |
| Restos a Pagar | Tabela de RP, pendências de quitação |
| Por PI | Cards com pipeline por Programa Interno, gráfico comparativo |
| Por Natureza de Despesa | Tabela + rosca de participação + barras de pipeline por ND |
| Evolução Mensal | Gráfico de barras agrupadas + taxa de execução mensal |

---

## Acesso em rede interna (outros computadores da OM)

Para que outros computadores da rede acessem o app,
execute com o parâmetro de servidor:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

Os demais usuários acessam via navegador em:
**http://[IP_DO_COMPUTADOR]:8501**

Para descobrir o IP da máquina:
- Windows: `ipconfig` no prompt → IPv4 Address
- Linux/macOS: `hostname -I`

---

## Publicar na internet (Streamlit Community Cloud) — gratuito

1. Crie uma conta em https://github.com e suba o arquivo `app.py` e `requirements.txt`
2. Acesse https://share.streamlit.io e clique em "New app"
3. Conecte ao repositório GitHub e selecione `app.py`
4. O Streamlit gera uma URL pública automaticamente

---

## Dependências

| Biblioteca | Versão mínima | Finalidade |
|------------|---------------|------------|
| streamlit  | 1.32          | Framework web / interface |
| pandas     | 2.0           | Leitura e processamento dos CSVs |
| plotly     | 5.18          | Gráficos interativos |

---

## Suporte

App desenvolvido com Claude (Anthropic) para gestão de execução
orçamentária e financeira de unidades do Comando da Marinha do Brasil.
