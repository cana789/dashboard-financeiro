# ⚜️ ACANTHUS — Sistema de Gestão da Intendência
## 4º Batalhão de Operações Litorâneas de Fuzileiros Navais

A folha de acanto, símbolo do Corpo de Intendentes da Marinha, dá nome e
identidade ao sistema.

## Módulos
| Módulo | Conteúdo |
|---|---|
| 🏠 Painel Geral | KPIs consolidados dos dois módulos, gauges, evolução, status de processos, atenções do momento |
| 💰 Execução Financeira | 6 abas: Visão Geral, Empenhos, Restos a Pagar, Por PI, Por ND, Evolução |
| 🛒 Obtenção | Controle editável de processos licitatórios com export/import CSV |

## Estrutura do repositório
```
dashboard-financeiro/
├── app.py
├── requirements.txt        # streamlit 1.45.1 · pandas 2.2.3 · plotly 5.24.1
├── .python-version         # 3.11
└── .streamlit/
    └── config.toml         # tema dark
```
O logo está embutido no código (base64) — não é preciso subir a imagem.

## Login (NIP = senha)
17056004 · 03105288 · 13130510 · 96007494

## Persistência
Dados de uploads e edições ficam salvos no servidor (sobrevivem a logout/login).
São perdidos em reboot/redeploy — use Exportar CSV como backup permanente.
