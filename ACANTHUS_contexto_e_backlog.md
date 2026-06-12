# ⚜️ ACANTHUS — Documento de Contexto, Histórico e Backlog
### Sistema de Gestão da Intendência · 4º Batalhão de Operações Litorâneas de Fuzileiros Navais (4ºBtlOpLitFN)

> **Finalidade deste documento:** transferir todo o contexto do desenvolvimento para um novo chat.
> Anexe este arquivo na nova conversa e o desenvolvimento pode continuar do ponto exato em que parou.

---

## 1. CONCEITO

**Acanthus** é um sistema web de gestão da Intendência, batizado em referência à **folha de acanto**, símbolo do Corpo de Intendentes da Marinha. O logo (folha dourada com contorno navy) está **embutido no código em base64** — favicon, tela de login, sidebar e cabeçalho.

- **Identidade visual:** dark BI (fundo navy `#0B1120`), marca em **dourado** (`#FFC533→#FF9F0A`), dados em **ciano/teal/roxo/âmbar/rosa** (separação visual entre marca e informação)
- **Usuário-alvo:** oficiais e praças da Intendência da OM; visão executiva para o Comando
- **Princípio de ingestão:** o usuário **só faz upload dos documentos oficiais** (CSVs do SIAFI, PDFs do SISTOQUE/CADBEM, tabela de incumbências) — o sistema identifica cada arquivo automaticamente pelo conteúdo e incorpora os dados

---

## 2. STACK E DEPLOY

| Item | Valor |
|---|---|
| Framework | Streamlit `1.45.1` (single-file `app.py`, ~3.000 linhas) |
| Dados | pandas `2.2.3` · Gráficos: plotly `5.24.1` · PDFs: pdfplumber `0.11.4` |
| Python | **3.11** (fixado via arquivo `.python-version` — crítico!) |
| Hospedagem | Streamlit Community Cloud (gratuito), repositório GitHub `cana789/dashboard-financeiro`, branch `main` |
| URL | `https://dashboard-financeiro-123.streamlit.app` (aprox.) |
| Tema | `.streamlit/config.toml` com base dark |

**Estrutura do repositório:**
```
dashboard-financeiro/
├── app.py                  ← TODO o sistema (single-file)
├── requirements.txt        ← versões EXATAS (nunca usar >=)
├── .python-version         ← "3.11"
└── .streamlit/config.toml  ← tema dark
```

**Fluxo de atualização:** editar/substituir `app.py` no GitHub → Streamlit Cloud redeploya automaticamente.

---

## 3. AUTENTICAÇÃO

Login obrigatório (tela própria com logo). Credenciais: **login = senha = NIP**. 27 NIPs cadastrados na lista `_NIPS_PADRAO` no topo do `app.py`; pode ser sobrescrita pela seção `[usuarios]` do Streamlit Secrets (preparação para senhas ≠ NIP).

⚠️ **Risco conhecido:** o repositório é público (exigência do plano gratuito) e as credenciais estão no código. Mitigação planejada no backlog (Streamlit Secrets).

---

## 4. MÓDULOS (estado atual)

Navegação por radio estilizado na sidebar; controles contextuais por módulo.

### 🏠 Painel Geral
KPIs consolidados de todos os módulos: execução financeira (provisão, taxas de empenho/execução, % RP pago), obtenção (processos, vigentes, valor ativo), patrimônio (total, bens, estoque, incumbências), tarefas (4 contadores por urgência + 6 próximas tarefas). Gauges, evolução mensal, rosca de status de processos e bloco **"Atenções do momento"** (alertas cruzados de todos os módulos).

### 💰 Financeiro  *(renomeado de “Execução Financeira” em JUN/2026)*
6 abas: Visão Geral · Empenhos · Restos a Pagar · Por PI · Por ND · Evolução.
- **Entrada:** upload único dos 3 CSVs do SIAFI (Controle de Empenhos, Restos a Pagar, Controle de Saldo Geral) com **detecção automática por conteúdo** (`detectar_tipo`)
- Visão Geral: KPIs, 3 gauges, funil da despesa, barras de fases, **saldo disponível por PI e por ND**
- Por PI: cards compactos em grade 2 colunas (1 barra + chips Prov/Saldo/Liq/Pago)
- Por ND: gráfico empilhado único (Pago/Liq. a pagar/A liquidar)
- Lançamento manual de empenho; filtros por PI/ND na sidebar

### 🛒 Obtenção
Controle de processos licitatórios — **27 processos pré-carregados** da planilha real do usuário.
Campos: ID interno, Objeto, MOD (DE/DE SRP/PE/PE SRP/ADESÃO/TJIL), NUP, Status (11 opções), Valor, Desenvolvimento, Setor, Vigência.
Tabela 100% editável (`st.data_editor`, linhas dinâmicas), KPIs, rosca por status (cores semânticas), barras por setor, export/import CSV (`;`, utf-8-sig).

### 🏛️ Patrimônio
3 fontes de dados com upload único e detecção automática:
1. **Estoque** — PDF do SISTOQUE (`parse_estoque_pdf`)
2. **Bens móveis** — PDF do CADBEM, 106 págs/2.440 bens validados (`parse_bens_pdf`)
3. **Incumbências** — arquivo `.xls` que na verdade é **TSV latin-1** (`parse_incumbencias`; NIPs lidos como string p/ preservar zeros)

Abas: Visão Geral (top 10 incumbências por valor, composição bens×estoque, top 10 bens) · Bens Móveis (filtro+busca) · Estoque · **Incumbências** (cards com encarregado/NIP/valores sob responsabilidade; alerta vermelho p/ sem encarregado).

⚠️ **Peculiaridade dos dados:** a numeração de incumbência do SISTOQUE **difere** da tabela/CADBEM (ex.: 002 = Paiol Mat. Comum no estoque, mas 002 = Sala do Imediato na tabela). Bens cruzam por **código**; estoque cruza por **nome normalizado** (`_norm_nome`, contains bidirecional). Validado: "PAIOL DE MATERIAL COMUM" → 030 PMC.

### 📋 Tarefas
Campos: Tarefa, Responsável, Prazo, Referência, Observações, **Divisão** (= futuro módulo: Financeiro, Obtenção, Pagamento de Pessoal, Rancho/Municiamento, Patrimônio, Geral), Status, **Recorrência** 🔁 (Diária/Semanal/Quinzenal/Mensal).
- **Cores por urgência** (pedido explícito): 🔴 esta semana/atrasada · 🟡 próxima semana · 🟢 >1 semana · 🔵 concluída. Semana = seg→dom (`fim_da_semana`, `cor_prazo`)
- **Edição por clique** em todas as abas via `st.dialog` (modal estilo Google Calendar) com Salvar/Excluir
- **Recorrência:** concluir tarefa recorrente gera a próxima ocorrência automaticamente (`spawn_recorrencia`); o calendário projeta ocorrências futuras como chips "fantasma" tracejados
- 5 visões: Cards (grade 3 col) · **Calendário** (grade mensal HTML, navegação ◀ Hoje ▶, chips coloridos, lista "tarefas do mês — clique p/ editar") · Kanban (3 colunas, botões ✏️ e ▶ avançar) · Tabela editável · Análise (carga por responsável, rosca por urgência, timeline de prazos com linha "hoje")
- Migração de schema automática (`normalizar_tarefas`) para dados antigos sem a coluna Recorrência

---

## 5. PERSISTÊNCIA (v2 — JUN/2026)

- **Duas camadas:** disco local (`dados_persistentes/*.pkl`, cache) + **GitHub** (definitiva, via API Contents num repo privado SEPARADO — `[github]` em Secrets: `token`, `data_repo`, `branch`)
- Diagnóstico que motivou a v2: o Streamlit Cloud apaga o disco a cada reboot/hibernação; a Obtenção *parecia* persistir porque recaía nos 27 processos hardcoded, o Financeiro recaía em DataFrame vazio
- **Regra de ouro:** o repo de dados deve ser DIFERENTE do repo do app (commit no repo do app dispara redeploy a cada save)
- `carregar_dados`: tenta disco → tenta GitHub (e repovoa o cache); `salvar_dados`: grava nos dois; `limpar_dados_salvos`: apaga nos dois
- **Chaves:** `empenhos, restos, saldo, mensal, processos, tarefas, pat_bens, pat_estoque, pat_incumb` (constante `CHAVES_PERSISTENCIA`)
- Status na sidebar: GitHub ✓ / GitHub ⚠️ / somente local
- Dados compartilhados entre todos os usuários; Exportar CSV continua como backup adicional

---

## 6. LIÇÕES TÉCNICAS CRÍTICAS (não repetir erros)

1. **`requirements.txt` sempre com `==`** (versões exatas). Com `>=`, o Cloud instalou pandas 3.0/plotly 6/Py 3.14 e quebrou tudo.
2. **`.python-version` = 3.11 é obrigatório** — Py 3.14 trava o build (sem wheels).
3. **`pd.read_csv` dos CSVs do SIAFI exige `engine="python"`** — o engine C descarta linhas silenciosamente (aspas não padronizadas).
4. **CSVs do SIAFI têm colunas VARIÁVEIS por mês** — mapear dinamicamente pelos **códigos de item** do cabeçalho: saldo `15=Provisão, 19=Créd.Disp, 29=Empenhado, 30=A Liq, 31=Liquidado, 32=Liq a Pagar, 34=Pago`; RP `40=Inscrito, 43=A Liq, 44=Liquidado, 45=Liq a Pagar, 46=Pago, 47=A Pagar`. Dados dos blocos começam **sempre no índice 7**; separador de blocos `Páginas:`; encoding latin-1; sep TAB.
5. **Provisão: usar apenas o ÚLTIMO bloco mensal** (somar todos quintuplica o valor).
6. **Plotly em tema escuro:** nunca `plot_bgcolor="white"`; usar `rgba(0,0,0,0)`. `titlefont` está depreciado → `title=dict(text=..., font=...)`.
7. **PDFs SISTOQUE/CADBEM têm descrições multilinha** — itens "sem descrição" na linha de dados; reconstituir com órfã anterior + órfãs seguintes, parando antes de órfã que pertence ao próximo item (`_desc_multilinha`).
8. **Logo:** o PNG original tinha fundo preto OPACO (não transparência) — removido por componentes conectados (só preto que toca a borda), preservando o contorno navy quase-preto.
9. **Merges pandas:** sempre `astype(str).str.strip()` nas chaves antes (tipos divergentes geram ValueError).
10. **Erro "Huh" no login do Streamlit Cloud** = sessão OAuth corrompida → limpar cookies + revogar app no GitHub (Settings→Applications) + relogar. Build travado = deletar e recriar o app.

---

## 7. BACKLOG (próximos passos sugeridos)

### Prioridade alta
- [x] **Persistência definitiva** — implementada via GitHub API (JUN/2026); restou ao usuário criar o repo privado `acanthus-dados` e configurar o token em Secrets
- [~] **Credenciais em Streamlit Secrets** — suporte a `[usuarios]` em Secrets implementado; falta migrar para senhas ≠ NIP com hash
- [ ] **Módulo Pagamento de Pessoal** (base normativa: SGM-302 — SISPAG2, BP/BP-Online, RR, calendário SRF)
- [ ] **Módulo Rancho/Municiamento** (divisão já prevista; possível leitura de NF por foto via API Anthropic)

### Prioridade média
- [ ] **Histórico/série temporal** na Execução Financeira: guardar cada upload mensal e comparar evoluções entre meses (hoje cada upload substitui o anterior)
- [ ] Patrimônio: **comparativo entre inventários** (o que entrou/saiu/mudou de incumbência entre dois uploads)
- [ ] Tarefas: notificação de prazos (e-mail/abertura do app), tarefa vinculada a processo de Obtenção
- [ ] Obtenção: linha do tempo por processo (datas de cada fase), alertas de vigência a vencer
- [ ] Relatórios PDF exportáveis (resumo executivo do Painel Geral p/ despacho com o Comando)

### Prioridade baixa / ideias
- [ ] Perfis de acesso (admin × consulta; visibilidade por divisão)
- [ ] Log de auditoria (quem alterou o quê)
- [ ] Refinamento mobile
- [ ] Tema claro opcional

### Verificação normativa (JUN/2026) — implementado e sugerido
**Implementado:**
- Submetas FC/MN/MP do Agregador GOLF (Apêndice II, Anexo B, Circ nº 1/2026 EMA): `classificar_submeta()` + gráfico empilhado na Visão Geral do Financeiro
- Conformidade Lei 4.320/64 (estágios da despesa: empenho ≥ liquidação ≥ pagamento) — alertas na Visão Geral e nas Atenções do Painel Geral
- Limites Lei 14.133/2021 atualizados p/ 2026 (Decreto nº 12.807/2025): dispensa art. 75 I = R$ 130.984,20 (obras/eng) e II = R$ 65.492,11 (compras/serviços); art. 184-A = R$ 1.646.430,90 — constante `LIMITES_14133_2026` + alerta no módulo Obtenção p/ processos DE acima do limite

**Sugerido (não implementado):**
- SGM-303: checklist mensal automático em Tarefas (conferência DMB×SIAFI, RMM, DDM, TRI por incumbência); conciliação SISBENS×SIAFI por upload do balancete; alerta de inventário anual no encerramento de exercício
- SGM-302: estrutura do módulo Pagamento de Pessoal em torno de BP/BP-Online, RR (implantação/encerramento/suspensão) e calendário SRF
- Circ 1/2026 EMA: aba “Planejamento PA-2027” — projeção de necessidades por submeta a partir da série histórica de empenhos (subsídio a EVO/QOPS)
- Lei 9.784/99: campo de data-limite por fase processual na Obtenção, com alerta de prazos administrativos
- Circular Governança 9/2025: relatório executivo em PDF (avaliar–dirigir–monitorar) para despacho com o Comando

### Pendências conhecidas
- Cruzamento estoque×incumbência é heurístico (por nome) — avaliar tabela de-para mantida pelo usuário
- Estoque atual tem só 1 página de exemplo — revalidar parser com inventário completo multi-incumbência
- `use_container_width` ficará depreciado em Streamlit futuro (migrar para `width="stretch"` quando atualizar versão)

---

## 8. COMO RETOMAR EM UM NOVO CHAT

1. Anexar este documento + o `app.py` atual (baixar do GitHub)
2. Informar o pedido novo (ex.: "implementar item X do backlog")
3. Padrão de trabalho estabelecido: Claude edita o `app.py` por patches cirúrgicos, valida sintaxe (`ast.parse`) e testa parsers contra arquivos reais antes de entregar; usuário substitui arquivo(s) no GitHub; em mudança de dependências, atualizar também `requirements.txt`
