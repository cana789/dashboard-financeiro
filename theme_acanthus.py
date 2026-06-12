# -*- coding: utf-8 -*-
"""
theme_acanthus.py — Tema "C · Ousada" (azul-noite + ouro) para o ACANTHUS
═══════════════════════════════════════════════════════════════════════════

Tema completo injetado via CSS — NÃO depende do .streamlit/config.toml.
Funciona em qualquer hospedagem (Streamlit Cloud, Docker, VPS, domínio próprio).

COMO USAR (3 passos):
    1. Coloque este arquivo na raiz do repositório, ao lado do app.py
       (junto com acanto.png — o logo da folha de acanto)
    2. No topo do app.py, logo após st.set_page_config(...), adicione:

           from theme_acanthus import aplicar_tema, top_nav, modulo_atual, hero, carregar_logo_b64, plotly_layout
           aplicar_tema(esconder_sidebar=True)

           modulo = modulo_atual()          # lê ?modulo=... da URL (padrão: "painel")
           top_nav(ativo=modulo, usuario="Sgt SILVA", nip="1234567",
                   logo_b64=carregar_logo_b64("acanto.png"))

           if modulo == "painel":
               hero("Painel Geral", "EXECUÇÃO FINANCEIRA · 2026")
               ...  # renderiza Painel Geral
           elif modulo == "financeiro": ... # etc.

    3. Em cada gráfico Plotly, aplique o layout do tema:

           fig.update_layout(**plotly_layout())
           # ou para gauges/indicadores:
           fig.update_layout(**plotly_layout(altura=260))

OPCIONAL — config.toml mínimo (melhora widgets nativos como date picker):
    [theme]
    base = "dark"
    primaryColor = "#F5B91E"
    backgroundColor = "#04070F"
    secondaryBackgroundColor = "#070D1A"
    textColor = "#AFC0D8"
"""

import streamlit as st

# ─── PALETA ──────────────────────────────────────────────────────────────────
CORES = {
    "bg":        "#04070F",   # fundo geral — azul-noite quase preto
    "s1":        "#070D1A",   # superfície 1 — cards, sidebar
    "s2":        "#0B1424",   # superfície 2 — hover, inputs
    "gold":      "#F5B91E",   # ouro — acento principal (folha de acanto)
    "gold_dim":  "rgba(245,185,30,0.08)",
    "border":    "rgba(245,185,30,0.12)",
    "border_hi": "rgba(245,185,30,0.45)",
    "red":       "#FF2D55",
    "green":     "#00D26A",
    "amber":     "#FF9F1C",
    "blue":      "#3D9BE9",
    "text":      "#AFC0D8",
    "muted":     "#3E5066",
    "bright":    "#F0F5FC",
}

# Recorte angular (cantos cortados a 45°) — assinatura visual do tema
CUT    = "polygon(0 0, calc(100% - 14px) 0, 100% 14px, 100% 100%, 14px 100%, 0 calc(100% - 14px))"
CUT_SM = "polygon(0 0, calc(100% - 8px) 0, 100% 8px, 100% 100%, 8px 100%, 0 calc(100% - 8px))"

_CSS = f"""
<style>
/* ── FONTES ─────────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Archivo:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root {{
  --ac-bg: {CORES["bg"]};
  --ac-s1: {CORES["s1"]};
  --ac-s2: {CORES["s2"]};
  --ac-gold: {CORES["gold"]};
  --ac-border: {CORES["border"]};
  --ac-text: {CORES["text"]};
  --ac-muted: {CORES["muted"]};
  --ac-bright: {CORES["bright"]};
}}

/* ── FUNDO GERAL + textura diagonal sutil ───────────────────────────────── */
.stApp, [data-testid="stAppViewContainer"] {{
  background-color: var(--ac-bg) !important;
  background-image: repeating-linear-gradient(115deg,
    rgba(245,185,30,0.012) 0 1px, transparent 1px 14px) !important;
  color: var(--ac-text);
  font-family: 'Archivo', sans-serif;
}}
header[data-testid="stHeader"] {{
  background: transparent !important;
}}

/* ── SIDEBAR ────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {{
  background-color: var(--ac-s1) !important;
  border-right: 1px solid var(--ac-border);
}}
[data-testid="stSidebar"] * {{ color: var(--ac-text); }}

/* ── TÍTULOS — Oswald condensada, caixa alta, espaçamento largo ─────────── */
h1, h2, h3 {{
  font-family: 'Oswald', sans-serif !important;
  text-transform: uppercase;
  letter-spacing: 0.08em !important;
  color: var(--ac-bright) !important;
}}
h1 {{ font-weight: 700 !important; }}
h2, h3 {{ font-weight: 600 !important; }}

/* ── MÉTRICAS (st.metric) — cards angulares com borda dourada ───────────── */
[data-testid="stMetric"] {{
  background: var(--ac-s1);
  border: 1px solid var(--ac-border);
  clip-path: {CUT};
  padding: 16px 18px !important;
}}
[data-testid="stMetricLabel"] {{
  font-family: 'Oswald', sans-serif !important;
  text-transform: uppercase;
  letter-spacing: 0.2em !important;
  font-size: 11px !important;
  color: var(--ac-gold) !important;
}}
[data-testid="stMetricValue"] {{
  font-family: 'Oswald', sans-serif !important;
  font-weight: 600 !important;
  color: var(--ac-bright) !important;
}}
[data-testid="stMetricDelta"] {{ font-family: 'Archivo', sans-serif !important; }}

/* ── ABAS (st.tabs) — chips angulares, ativa em ouro ────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
  gap: 8px;
  background: transparent;
  border-bottom: 1px solid var(--ac-border);
}}
.stTabs [data-baseweb="tab"] {{
  font-family: 'Oswald', sans-serif;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-size: 12px;
  background: rgba(255,255,255,0.04);
  color: var(--ac-muted);
  clip-path: {CUT_SM};
  padding: 6px 16px;
  border-radius: 0 !important;
}}
.stTabs [aria-selected="true"] {{
  background: var(--ac-gold) !important;
  color: {CORES["bg"]} !important;
  font-weight: 600;
}}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{
  display: none;
}}

/* ── BOTÕES — dourados, chanfrados, caixa alta ──────────────────────────── */
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {{
  font-family: 'Oswald', sans-serif !important;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-weight: 600;
  background: var(--ac-gold) !important;
  color: {CORES["bg"]} !important;
  border: none !important;
  border-radius: 0 !important;
  clip-path: {CUT_SM};
  transition: filter .15s;
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
  filter: brightness(1.15);
}}
/* Botões secundários (kind="secondary") — vazados */
.stButton > button[kind="secondary"] {{
  background: transparent !important;
  color: var(--ac-gold) !important;
  border: 1px solid {CORES["border_hi"]} !important;
}}

/* ── TABELAS / DATAFRAMES ───────────────────────────────────────────────── */
[data-testid="stDataFrame"], [data-testid="stTable"] {{
  background: var(--ac-s1);
  border: 1px solid var(--ac-border);
}}
[data-testid="stDataFrame"] [role="columnheader"] {{
  font-family: 'Oswald', sans-serif !important;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 11px;
  color: var(--ac-muted) !important;
  background: var(--ac-s1) !important;
}}

/* ── INPUTS / SELECTS ───────────────────────────────────────────────────── */
.stTextInput input, .stNumberInput input, .stDateInput input,
.stSelectbox [data-baseweb="select"] > div, .stTextArea textarea {{
  background: var(--ac-s2) !important;
  border: 1px solid var(--ac-border) !important;
  border-radius: 0 !important;
  color: var(--ac-bright) !important;
  font-family: 'Archivo', sans-serif !important;
}}
.stTextInput input:focus, .stNumberInput input:focus {{
  border-color: var(--ac-gold) !important;
  box-shadow: none !important;
}}

/* ── EXPANDERS ──────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {{
  background: var(--ac-s1);
  border: 1px solid var(--ac-border) !important;
  border-radius: 0 !important;
}}
[data-testid="stExpander"] summary {{
  font-family: 'Oswald', sans-serif;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--ac-text) !important;
}}

/* ── PROGRESS BAR — dourada ─────────────────────────────────────────────── */
.stProgress > div > div > div {{
  background: var(--ac-gold) !important;
}}
.stProgress > div > div {{
  background: rgba(255,255,255,0.07) !important;
}}

/* ── ALERTAS (st.info/success/warning/error) ────────────────────────────── */
[data-testid="stAlert"] {{
  border-radius: 0 !important;
  clip-path: {CUT_SM};
  font-family: 'Archivo', sans-serif;
}}

/* ── DIVISOR + SCROLLBAR ────────────────────────────────────────────────── */
hr {{ border-color: var(--ac-border) !important; }}
::-webkit-scrollbar {{ width: 10px; height: 10px; }}
::-webkit-scrollbar-track {{ background: var(--ac-bg); }}
::-webkit-scrollbar-thumb {{ background: {CORES["s2"]}; border: 1px solid var(--ac-border); }}
::-webkit-scrollbar-thumb:hover {{ background: {CORES["muted"]}; }}
</style>
"""


_CSS_SEM_SIDEBAR = """
<style>
/* ── ESCONDE SIDEBAR + ajusta o container para o top-nav ────────────── */
[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] { display: none !important; }
.block-container {
  padding-top: 1.0rem !important;
  padding-bottom: 2rem !important;
}
/* Links do top-nav */
a.ac-nav-item { text-decoration: none !important; }
a.ac-nav-item:hover span { color: #F5B91E !important; }
</style>
"""


def aplicar_tema(esconder_sidebar=False):
    """Injeta o CSS do tema C · Ousada. Chamar logo após st.set_page_config().

    esconder_sidebar=True — oculta a sidebar do Streamlit (usar com top_nav()).
    """
    st.markdown(_CSS, unsafe_allow_html=True)
    if esconder_sidebar:
        st.markdown(_CSS_SEM_SIDEBAR, unsafe_allow_html=True)


# ─── TOP-NAV (substitui a sidebar) ──────────────────────────────────
MODULOS = [
    ("painel",     "PAINEL GERAL"),
    ("financeiro", "FINANCEIRO"),
    ("obtencao",   "OBTENÇÃO"),
    ("patrimonio", "PATRIMÔNIO"),
    ("tarefas",    "TAREFAS"),
]


def carregar_logo_b64(caminho="acanto.png"):
    """Lê o PNG do logo e devolve em base64 (para o top_nav). Retorna None se não existir."""
    import base64
    from pathlib import Path

    arquivo = Path(caminho)
    if not arquivo.exists():
        return None
    return base64.b64encode(arquivo.read_bytes()).decode("ascii")


def modulo_atual(padrao="painel"):
    """Lê o módulo ativo do query param ?modulo=... (navegação do top-nav)."""
    try:
        valor = st.query_params.get("modulo", padrao)
    except Exception:  # compatibilidade com versões antigas
        valor = st.experimental_get_query_params().get("modulo", [padrao])[0]
    chaves = [m[0] for m in MODULOS]
    return valor if valor in chaves else padrao


def top_nav(ativo="painel", usuario=None, nip=None, logo_b64=None, sync_ok=True):
    """Renderiza o top-nav do tema (estilo Proposta C) no lugar da sidebar.

    ativo    — chave do módulo ativo (ver MODULOS)
    usuario  — nome exibido à direita (ex.: "Sgt SILVA")
    nip      — NIP exibido abaixo do nome
    logo_b64 — PNG base64 da folha de acanto (use carregar_logo_b64("acanto.png"))
    sync_ok  — True = ponto verde "GitHub sync ativo"; False = ponto vermelho
    """
    from datetime import datetime

    logo_html = (
        f'<img src="data:image/png;base64,{logo_b64}" style="height:30px" alt=""/>'
        if logo_b64 else ""
    )

    itens = []
    for chave, rotulo in MODULOS:
        e_ativo = chave == ativo
        sublinhado = (
            f'<div style="height:3px;background:{CORES["gold"]};'
            f'transform:skewX(-20deg);margin-top:3px"></div>'
            if e_ativo else '<div style="height:3px;margin-top:3px"></div>'
        )
        cor = CORES["gold"] if e_ativo else CORES["muted"]
        peso = "600" if e_ativo else "400"
        itens.append(
            f'<a class="ac-nav-item" href="?modulo={chave}" target="_self">'
            f'<span style="font-family:Oswald,sans-serif;font-size:12px;font-weight:{peso};'
            f'letter-spacing:0.16em;color:{cor};white-space:nowrap">{rotulo}</span>'
            f'{sublinhado}</a>'
        )
    nav_html = '<div style="display:flex;gap:30px;align-items:flex-start">' + "".join(itens) + "</div>"

    cor_sync = CORES["green"] if sync_ok else CORES["red"]
    rotulo_sync = "SYNC ATIVO" if sync_ok else "SYNC OFFLINE"
    agora = datetime.now().strftime("%d.%b.%Y %H:%M").upper()

    usuario_html = ""
    if usuario:
        nip_html = (
            f'<div style="font-size:9px;color:{CORES["muted"]}">NIP {nip}</div>' if nip else ""
        )
        usuario_html = (
            f'<div style="text-align:right;line-height:1.3">'
            f'<div style="font-size:11px;color:{CORES["text"]};font-weight:500">{usuario}</div>'
            f'{nip_html}</div>'
        )

    st.markdown(
        f'''
<div style="display:flex;align-items:center;justify-content:space-between;gap:24px;
  padding:12px 4px 10px;border-bottom:1px solid {CORES["border"]};
  background:{CORES["s1"]};margin-bottom:6px">
  <div style="display:flex;align-items:center;gap:14px;flex-shrink:0">
    {logo_html}
    <span style="font-family:Oswald,sans-serif;font-size:19px;font-weight:600;
      letter-spacing:0.34em;color:{CORES["bright"]}">ACANTHUS</span>
    <div style="width:1px;height:24px;background:{CORES["border"]}"></div>
    <span style="font-size:9px;color:{CORES["muted"]};letter-spacing:0.12em;line-height:1.5">
      INTENDÊNCIA<br/>4º BTLOPLITFUZNAV</span>
  </div>
  {nav_html}
  <div style="display:flex;align-items:center;gap:14px;flex-shrink:0">
    <span style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:{CORES["muted"]}">{agora}</span>
    <div style="display:flex;align-items:center;gap:6px">
      <div style="width:6px;height:6px;border-radius:50%;background:{cor_sync};
        box-shadow:0 0 6px {cor_sync}"></div>
      <span style="font-family:Oswald,sans-serif;font-size:9px;letter-spacing:0.1em;
        color:{CORES["muted"]}">{rotulo_sync}</span>
    </div>
    {usuario_html}
  </div>
</div>''',
        unsafe_allow_html=True,
    )


def hero(titulo, kicker="", direita_html=""):
    """Cabeçalho de módulo no estilo da Proposta C (título grande + racing stripe).

    Uso: hero("Painel Geral", "EXECUÇÃO FINANCEIRA · 2026")
    """
    kicker_html = ""
    if kicker:
        kicker_html = (
            f'<div style="display:flex;align-items:center;gap:14px;margin-bottom:4px">'
            f'<div style="width:54px;height:10px;background-image:repeating-linear-gradient('
            f'115deg,{CORES["gold"]} 0 3px,transparent 3px 9px)"></div>'
            f'<span style="font-family:Oswald,sans-serif;font-size:11px;letter-spacing:0.3em;'
            f'color:{CORES["gold"]}">{kicker}</span></div>'
        )
    st.markdown(
        f'<div style="display:flex;align-items:flex-end;justify-content:space-between;'
        f'padding:14px 0 12px"><div>{kicker_html}'
        f'<div style="font-family:Oswald,sans-serif;font-size:42px;font-weight:700;'
        f'letter-spacing:0.06em;color:{CORES["bright"]};line-height:1;'
        f'text-transform:uppercase">{titulo}</div></div>{direita_html}</div>',
        unsafe_allow_html=True,
    )


def plotly_layout(altura=None):
    """
    Layout padrão para gráficos Plotly no tema.
    Uso: fig.update_layout(**plotly_layout())
    """
    layout = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Archivo, sans-serif", color=CORES["text"], size=12),
        title_font=dict(family="Oswald, sans-serif", size=14, color=CORES["bright"]),
        colorway=[CORES["gold"], CORES["green"], CORES["blue"], CORES["amber"], CORES["red"]],
        xaxis=dict(gridcolor="rgba(245,185,30,0.06)", zerolinecolor=CORES["border"],
                   tickfont=dict(family="Oswald, sans-serif", size=10, color=CORES["muted"])),
        yaxis=dict(gridcolor="rgba(245,185,30,0.06)", zerolinecolor=CORES["border"],
                   tickfont=dict(family="IBM Plex Mono, monospace", size=10, color=CORES["muted"])),
        legend=dict(font=dict(family="Oswald, sans-serif", size=10, color=CORES["text"]),
                    bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=36, b=10),
        hoverlabel=dict(bgcolor=CORES["s2"], font_family="Archivo, sans-serif",
                        font_color=CORES["bright"], bordercolor=CORES["gold"]),
    )
    if altura:
        layout["height"] = altura
    return layout


def gauge_config(cor=None):
    """
    Configuração para gauges (go.Indicator) no estilo do tema.
    Uso:
        go.Indicator(mode="gauge+number", value=67.6,
                     gauge=gauge_config(),  number={"font": {"family": "Oswald"}})
    """
    cor = cor or CORES["gold"]
    return dict(
        axis=dict(range=[0, 100], tickcolor=CORES["muted"],
                  tickfont=dict(family="Oswald, sans-serif", size=9, color=CORES["muted"])),
        bar=dict(color=cor, thickness=0.28),
        bgcolor="rgba(0,0,0,0)",
        borderwidth=0,
        steps=[dict(range=[0, 100], color="rgba(255,255,255,0.05)")],
    )


# ─── BÔNUS: helpers de marcação no estilo do tema ────────────────────────────
def titulo_secao(texto):
    """Título de seção com traço dourado inclinado (estilo racing)."""
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;margin:8px 0 12px">'
        f'<div style="width:14px;height:3px;background:{CORES["gold"]};transform:skewX(-20deg)"></div>'
        f'<span style="font-family:Oswald,sans-serif;font-size:13px;font-weight:600;'
        f'letter-spacing:0.22em;color:{CORES["text"]};text-transform:uppercase">{texto}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def chip(texto, cor=None, vazado=False):
    """Retorna HTML de um chip angular (usar dentro de st.markdown com unsafe_allow_html)."""
    cor = cor or CORES["gold"]
    estilo_fundo = (
        f"background:transparent;color:{cor};border:1px solid {cor}" if vazado
        else f"background:{cor};color:{CORES['bg']}"
    )
    return (
        f'<span style="display:inline-block;font-family:Oswald,sans-serif;font-size:10px;'
        f'font-weight:600;letter-spacing:0.14em;padding:3px 10px;clip-path:{CUT_SM};'
        f'{estilo_fundo};text-transform:uppercase">{texto}</span>'
    )
