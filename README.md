# ⚜️ ACANTHUS — Sistema de Gestão da Intendência
## 4º Batalhão de Operações Litorâneas de Fuzileiros Navais

A folha de acanto, símbolo do Corpo de Intendentes da Marinha, dá nome e
identidade ao sistema.

## Módulos
| Módulo | Conteúdo |
|---|---|
| 🏠 Painel Geral | KPIs consolidados de todos os módulos, gauges, evolução, status de processos, atenções do momento (inclui conformidade Lei 4.320/64) |
| 💰 Financeiro | 6 abas: Visão Geral (com submetas FC/MN/MP da Circ nº 1/2026 EMA), Empenhos, Restos a Pagar, Por PI, Por ND, Evolução |
| 🛒 Obtenção | Controle editável de processos licitatórios com export/import CSV e verificação de limites da Lei 14.133/2021 (valores 2026 — Decreto 12.807/2025) |
| 🏛️ Patrimônio | Bens móveis (CADBEM), estoque (SISTOQUE) e incumbências, conforme SGM-303 Rev.7 |
| 📋 Tarefas | Cards, calendário, kanban, tabela e análise; recorrência e cores por urgência |

Todo módulo possui abas de **📝 Observações** (com autor/data-hora; exclusão lógica
— some do painel, fica no histórico) e **🗂️ Histórico** (log permanente de tudo:
logins, uploads, inclusões/alterações/exclusões, com usuário e data/hora).
O Painel Geral gera **Relatório Executivo em PDF** no ciclo
Avaliar–Direcionar–Monitorar (Circ nº 9/2025 EMA). A Obtenção controla
**prazos por fase processual** com alertas da Lei nº 9.784/99.

## Estrutura do repositório
```
dashboard-financeiro/
├── app.py
├── requirements.txt        # streamlit 1.45.1 · pandas 2.2.3 · plotly 5.24.1 · reportlab 4.2.5
├── .python-version         # 3.11
└── .streamlit/
    └── config.toml         # tema dark
```
O logo está embutido no código (base64) — não é preciso subir a imagem.

## Login (NIP = senha)
27 contas cadastradas (login = senha = NIP). A lista pode ser
sobrescrita via Streamlit Secrets, seção `[usuarios]`.

## Persistência
Duas camadas:
1. **Disco local** (cache rápido) — perdido em reboot/hibernação do Streamlit Cloud.
2. **GitHub** (definitiva) — pickle de cada base gravado em um repositório
   PRIVADO separado via API. Sobrevive a reboot/redeploy.

Configurar em *Settings → Secrets* do Streamlit Cloud:
```toml
[github]
token     = "ghp_xxxxxxxxxxxx"        # token clássico com escopo "repo"
data_repo = "cana789/acanthus-dados"  # repo privado SÓ para dados
branch    = "main"
```
Importante: usar repositório **separado** do app — gravar no repo do app
dispararia um redeploy a cada salvamento. Sem secrets, o app funciona com
persistência local apenas (status indicado na sidebar).
