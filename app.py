"""
Dashboard de Execução Financeira — 4º Btl Op Lit FN
Design BI — dark theme com KPIs em destaque
Execução: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import StringIO
from datetime import datetime

st.set_page_config(
    page_title="Execução Financeira — 4º Btl Op Lit FN",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═════════════════════════════════════════════
# PALETA BI — NEON SOBRE NAVY
# ═════════════════════════════════════════════
BG        = "#0B1120"
CARD      = "#111A2E"
CARD_2    = "#16213B"
BORDER    = "rgba(56,189,248,0.15)"
CYAN      = "#00D4FF"
TEAL      = "#00F5A0"
PURPLE    = "#A78BFA"
AMBER     = "#FFB020"
PINK      = "#FF4D6D"
BLUE      = "#3B82F6"
TXT       = "#E2E8F0"
TXT_DIM   = "#94A3B8"
TXT_FAINT = "#64748B"

PALETA_ND = [CYAN, TEAL, PURPLE, AMBER, PINK, BLUE,
             "#38BDF8", "#34D399", "#F472B6"]


# ═════════════════════════════════════════════
# AUTENTICAÇÃO — LOGIN POR NIP
# ═════════════════════════════════════════════
USUARIOS = {
    "17056004": "17056004",
    "03105288": "03105288",
    "13130510": "13130510",
    "96007494": "96007494",
}

def parse_br(s):
    """Converte valor monetário brasileiro (1.234,56) para float."""
    try:
        return float(str(s).strip().strip('"').replace(".", "").replace(",", "."))
    except Exception:
        return 0.0


def fmt_brl(v):
    """Formata float como R$ 1.234,56."""
    try:
        v = float(v)
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"


def fmt_pct(a, b):
    if not b:
        return "—"
    return f"{a / b * 100:.1f}%".replace(".", ",")


def num_pct(a, b):
    if not b:
        return 0
    return min(100, round(a / b * 100))


def safe_float(v):
    """Garante que um valor seja float válido, nunca NaN/None."""
    try:
        f = float(v)
        return f if f == f else 0.0  # NaN check
    except Exception:
        return 0.0


def detectar_tipo(file_bytes: bytes) -> str:
    """
    Identifica o tipo do CSV pelo conteúdo:
    - 'saldo'    → contém 'Páginas:' e 'PROVISAO RECEBIDA'
    - 'restos'   → contém 'Restos a pagar' ou item '40' + 'RESTOS A PAGAR'
    - 'empenhos' → contém 'NE CCor' com colunas de empenho/liquidação
    - 'desconhecido' → nenhum padrão reconhecido
    """
    try:
        preview = file_bytes[:2000].decode("latin-1", errors="ignore").upper()
    except Exception:
        return "desconhecido"

    if "PROVISAO RECEBIDA" in preview or ("PÁGINAS:" in preview and "CREDITO DISPONIVEL" in preview):
        return "saldo"
    if "RESTOS A PAGAR" in preview and ("NE CCOR" in preview or '"40"' in preview):
        return "restos"
    if "NE CCOR" in preview and ("EMPENHADA" in preview or "LIQUIDADA" in preview or "A LIQUIDAR" in preview):
        return "empenhos"
    # Fallback por exclusão
    if "PAGINAS:" in preview or "PÁGINAS:" in preview:
        if "RESTOS" in preview:
            return "restos"
        return "saldo"
    return "desconhecido"


def parse_empenhos(file_bytes):
    content = file_bytes.decode("latin-1")
    lines = content.split("\r\n")
    data_lines = [l for l in lines[8:] if l.strip()]
    df = pd.read_csv(
        StringIO("\r\n".join(data_lines)),
        sep="\t",
        names=["NE", "CNPJ", "Favorecido", "PI", "Desc_PI",
               "Nat_Desp", "Desc_Nat", "Empenhado", "A_Liquidar",
               "Liquidado", "Liq_A_Pagar", "Pago"],
        on_bad_lines="skip",
        engine="python",
    )
    df = df[df["NE"].str.contains("NE", na=False)].copy()
    for col in ["Empenhado", "A_Liquidar", "Liquidado", "Liq_A_Pagar", "Pago"]:
        df[col] = df[col].apply(parse_br)
    # Extrair número limpo do empenho
    df["NE_display"] = df["NE"].str.extract(r"(NE\d+)").fillna(df["NE"])
    df["Favorecido"] = df["Favorecido"].str.strip().str.title()
    return df


def parse_restos(file_bytes):
    """
    Parse robusto do arquivo de Restos a Pagar.
    Estrutura: linha 0=título, linha 2='Páginas:', linhas 6-7=headers, linha 8+=dados.
    Os itens financeiros (40,43,44,45,46,47) são identificados na linha de header
    e mapeados dinamicamente para os índices corretos.
    """
    import re as _re

    ITEM_COLS_RP = {
        "40": "RP_Inscrito",
        "43": "RP_A_Liquidar",
        "44": "RP_Liquidado",
        "45": "RP_Liq_A_Pagar",
        "46": "RP_Pago",
        "47": "RP_A_Pagar",
    }
    ALL_FIELDS_RP = list(ITEM_COLS_RP.values())

    content = file_bytes.decode("latin-1")
    line_sep = "\r\n" if "\r\n" in content else ("\r" if "\r" in content else "\n")
    lines = content.split(line_sep)

    # Localizar linha de header com código "40"
    header_line = next(
        (l for l in lines[:15] if _re.search(r'"40"', l)), ""
    )
    item_codes = _re.findall(r'"(\d{2})"', header_line)

    # Colunas fixas: 0=NE,1=CNPJ,2=Favorecido,3=Ano,4=Nat_Desp,5=Desc_Nat,6=PI,7=Desc_PI
    # Colunas financeiras começam no índice 8
    col_map = {
        0: "NE", 1: "CNPJ", 2: "Favorecido", 3: "Ano",
        4: "Nat_Desp", 5: "Desc_Nat", 6: "PI", 7: "Desc_PI",
    }
    for i, code in enumerate(item_codes):
        if code in ITEM_COLS_RP:
            col_map[8 + i] = ITEM_COLS_RP[code]

    # Dados: linhas que contêm número de empenho (padrão NE + 6 dígitos)
    data_lines = [
        l for l in lines
        if l.strip() and _re.search(r'NE\d{6}', l)
    ]

    if not data_lines:
        return pd.DataFrame()

    df = pd.read_csv(
        StringIO(line_sep.join(data_lines)),
        sep="\t", header=None,
        on_bad_lines="skip", quotechar='"',
        engine="python",
    )
    df = df.rename(columns=col_map)

    for field in ALL_FIELDS_RP:
        if field in df.columns:
            df[field] = df[field].apply(parse_br)
        else:
            df[field] = 0.0

    df["NE_display"] = df["NE"].astype(str).str.extract(r"(NE\d+)").fillna(df["NE"])
    df["Favorecido"] = df["Favorecido"].astype(str).str.strip().str.title()
    return df


def parse_saldo(file_bytes):
    """
    Parse robusto do Controle de Saldo Geral.
    O arquivo é dividido em blocos mensais por 'Páginas:'.
    Cada bloco tem 3 linhas de header (índices 4-6) e dados a partir do índice 7.
    As colunas financeiras variam por mês conforme os itens disponíveis,
    identificados pelos códigos numéricos na linha de header (índice 4).
    """
    import re as _re

    ITEM_COLS_SG = {
        "15": "Provisao",
        "19": "Credito_Disp",
        "29": "Empenhado",
        "30": "A_Liquidar",
        "31": "Liquidado",
        "32": "Liq_A_Pagar",
        "34": "Pago",
    }
    ALL_FIELDS = list(ITEM_COLS_SG.values())

    content = file_bytes.decode("latin-1")
    line_sep = "\r\n" if "\r\n" in content else ("\r" if "\r" in content else "\n")
    sep = "Páginas:" if "Páginas:" in content else "Paginas:"
    blocks = content.split(sep)

    mensal_rows, all_pi = [], []

    for block in blocks[1:]:
        lines = block.split(line_sep)

        # Mês — linha com 'Lançamento' ou 'Lancamento'
        mes = next(
            (l.split(":")[-1].strip() for l in lines[:6]
             if "an" in l and "amento" in l.lower()),
            ""
        )

        # Header de itens — linha que contém "15" entre aspas (sempre índice 4)
        header_line = lines[4] if len(lines) > 4 else ""
        item_codes = _re.findall(r'"(\d{2})"', header_line)

        # Mapeamento de índice → nome de campo
        # Colunas fixas: 0=PI, 1=Desc_PI, 2=Nat_Desp, 3=Desc_Nat
        # Colunas financeiras começam no índice 4
        col_map = {0: "PI", 1: "Desc_PI", 2: "Nat_Desp", 3: "Desc_Nat"}
        for i, code in enumerate(item_codes):
            if code in ITEM_COLS_SG:
                col_map[4 + i] = ITEM_COLS_SG[code]

        # Dados começam SEMPRE no índice 7 (linhas 4,5,6 são header)
        # Filtrar linhas não-vazias e não-header (header começa com espaço ou "PI")
        data_lines = []
        for l in lines[7:]:
            stripped = l.strip()
            if not stripped:
                continue
            # Ignorar linhas de subtotal/rodapé (não começam com letra maiúscula entre aspas)
            if not _re.match(r'^"[A-Z]', stripped):
                continue
            # Ignorar linha de header remanescente
            if stripped.startswith('"') and "Item Informa" in stripped:
                continue
            data_lines.append(l)

        if not data_lines:
            continue

        try:
            df_tmp = pd.read_csv(
                StringIO(line_sep.join(data_lines)),
                sep="\t", header=None,
                on_bad_lines="skip", quotechar='"', engine='python',
            )
            df_tmp = df_tmp.rename(columns=col_map)

            for field in ALL_FIELDS:
                if field in df_tmp.columns:
                    df_tmp[field] = df_tmp[field].apply(parse_br)
                else:
                    df_tmp[field] = 0.0

            df_tmp["Mes"] = mes
            all_pi.append(df_tmp)

            mensal_rows.append({
                "Mes":          mes,
                "Provisao":     safe_float(df_tmp["Provisao"].sum()),
                "Credito_Disp": safe_float(df_tmp["Credito_Disp"].sum()),
                "Empenhado":    safe_float(df_tmp["Empenhado"].sum()),
                "Liquidado":    safe_float(df_tmp["Liquidado"].sum()),
                "Pago":         safe_float(df_tmp["Pago"].sum()),
            })
        except Exception:
            pass

    df_mensal = pd.DataFrame(mensal_rows)
    df_saldo  = pd.concat(all_pi, ignore_index=True) if all_pi else pd.DataFrame()
    return df_mensal, df_saldo


def check_login(nip: str, senha: str) -> bool:
    nip   = nip.strip()
    senha = senha.strip()
    return USUARIOS.get(nip) == senha


def logout():
    st.session_state.autenticado = False
    st.session_state.usuario_nip = ""
    st.rerun()

# Inicializa estado de autenticação


def status_empenho(emp, liq, pago):
    if emp <= 0:
        return "Sem saldo", "gray"
    if pago >= emp:
        return "Pago", "ok"
    if pago > 0 and pago < liq:
        return "Liq. a pagar", "info"
    if liq >= emp:
        return "Liquidado", "info"
    if liq > 0:
        return "Parcialmente liq.", "warn"
    return "Empenhado", "warn"


if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_nip" not in st.session_state:
    st.session_state.usuario_nip = ""
if "login_erro" not in st.session_state:
    st.session_state.login_erro = False

if not st.session_state.autenticado:
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stHeader"]  { background: transparent; }
    .stApp { background: radial-gradient(ellipse at top, #16213B 0%, #0B1120 55%) !important; }
    div[data-testid="stForm"] {
        background: rgba(17,26,46,0.85);
        border: 1px solid rgba(56,189,248,0.2);
        border-radius: 18px;
        padding: 1.6rem 1.5rem;
        box-shadow: 0 0 60px rgba(0,212,255,0.08), 0 18px 40px rgba(0,0,0,0.5);
        backdrop-filter: blur(8px);
    }
    div[data-testid="stForm"] label p { color: #94A3B8 !important; font-size: 0.75rem;
        text-transform: uppercase; letter-spacing: 0.08em; }
    .stTextInput input {
        background: #0B1120 !important; color: #E2E8F0 !important;
        border: 1px solid rgba(56,189,248,0.25) !important; border-radius: 10px !important;
    }
    .stFormSubmitButton button {
        background: linear-gradient(90deg, #00D4FF, #00F5A0) !important;
        color: #0B1120 !important; font-weight: 700 !important;
        border: none !important; border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 1.1, 1])
    with mid:
        st.markdown("""
        <div style="text-align:center; padding:2.2rem 0 1.2rem;">
          <div style="font-size:2.6rem; filter:drop-shadow(0 0 14px rgba(0,212,255,0.6));">⚓</div>
          <div style="font-size:1.25rem; font-weight:800; letter-spacing:0.02em;
               background:linear-gradient(90deg,#00D4FF,#00F5A0);
               -webkit-background-clip:text; -webkit-text-fill-color:transparent;
               margin-top:0.5rem;">
            EXECUÇÃO FINANCEIRA
          </div>
          <div style="font-size:0.8rem; color:#94A3B8; margin-top:0.25rem;">
            4º Batalhão de Operações Litorâneas de Fuzileiros Navais · 2026
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_login"):
            nip_input   = st.text_input("NIP (login)", placeholder="Digite seu NIP", max_chars=12)
            senha_input = st.text_input("Senha", placeholder="Digite sua senha",
                                        type="password", max_chars=12)
            if st.session_state.login_erro:
                st.markdown('<div style="background:rgba(255,77,109,0.12);color:#FF4D6D;'
                            'border:1px solid rgba(255,77,109,0.3);border-radius:8px;'
                            'padding:0.5rem 0.8rem;font-size:0.8rem;margin:0.4rem 0;">'
                            '⚠️ NIP ou senha incorretos.</div>', unsafe_allow_html=True)
            if st.form_submit_button("ENTRAR", use_container_width=True):
                if check_login(nip_input, senha_input):
                    st.session_state.autenticado = True
                    st.session_state.usuario_nip = nip_input.strip()
                    st.session_state.login_erro = False
                    st.rerun()
                else:
                    st.session_state.login_erro = True
                    st.rerun()

        st.markdown('<div style="text-align:center;font-size:0.7rem;color:#64748B;'
                    'margin-top:1rem;">Acesso restrito a usuários autorizados</div>',
                    unsafe_allow_html=True)
    st.stop()


# ═════════════════════════════════════════════
# CSS GLOBAL — TEMA BI DARK
# ═════════════════════════════════════════════
st.markdown("""
<style>
.stApp { background: radial-gradient(ellipse at top left, #131F38 0%, #0B1120 50%) !important; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0E1729 0%, #0B1120 100%);
    border-right: 1px solid rgba(56,189,248,0.12);
}
[data-testid="stSidebar"] .stMarkdown h3 { color: #E2E8F0; }

/* ── KPI HERO CARDS ── */
.kpi-hero {
    background: linear-gradient(135deg, #111A2E 0%, #16213B 100%);
    border: 1px solid rgba(56,189,248,0.15);
    border-radius: 16px;
    padding: 1.1rem 1.3rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 24px rgba(0,0,0,0.35);
}
.kpi-hero::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: var(--accent, linear-gradient(90deg,#00D4FF,#00F5A0));
}
.kpi-hero .lbl {
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: #64748B; margin-bottom: 0.45rem;
}
.kpi-hero .val {
    font-size: 2.0rem; font-weight: 800; line-height: 1.05;
    color: #E2E8F0; font-variant-numeric: tabular-nums;
}
.kpi-hero .val.gradient {
    background: linear-gradient(90deg, #00D4FF, #00F5A0);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.kpi-hero .sub { font-size: 0.7rem; color: #64748B; margin-top: 0.35rem; }
.kpi-hero .delta {
    display: inline-block; font-size: 0.68rem; font-weight: 700;
    padding: 2px 10px; border-radius: 20px; margin-top: 0.5rem;
}
.d-ok   { background: rgba(0,245,160,0.12); color: #00F5A0; border: 1px solid rgba(0,245,160,0.3); }
.d-warn { background: rgba(255,176,32,0.12); color: #FFB020; border: 1px solid rgba(255,176,32,0.3); }
.d-bad  { background: rgba(255,77,109,0.12); color: #FF4D6D; border: 1px solid rgba(255,77,109,0.3); }
.d-info { background: rgba(0,212,255,0.12); color: #00D4FF; border: 1px solid rgba(0,212,255,0.3); }

/* ── SECTION TITLES ── */
.sec {
    font-size: 0.7rem; font-weight: 800; letter-spacing: 0.14em;
    text-transform: uppercase; color: #38BDF8;
    margin: 1.6rem 0 0.8rem; display: flex; align-items: center; gap: 10px;
}
.sec::after { content: ''; flex: 1; height: 1px;
    background: linear-gradient(90deg, rgba(56,189,248,0.35), transparent); }

/* ── PI CARDS ── */
.pi-card {
    background: linear-gradient(135deg, #111A2E, #141E36);
    border: 1px solid rgba(56,189,248,0.12);
    border-radius: 14px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.7rem;
}
.pi-code { font-family: 'SF Mono', monospace; font-size: 0.68rem; color: #38BDF8;
           letter-spacing: 0.06em; }
.pi-name { font-size: 0.92rem; font-weight: 700; color: #E2E8F0; margin: 0.2rem 0; }
.pi-meta { font-size: 0.75rem; color: #94A3B8; }
.pi-meta b { color: #E2E8F0; }

/* ── PROGRESS BARS NEON ── */
.nbar-track { background: rgba(148,163,184,0.12); border-radius: 4px;
              height: 8px; overflow: hidden; }
.nbar-fill  { height: 100%; border-radius: 4px;
              box-shadow: 0 0 8px var(--glow, rgba(0,212,255,0.5)); }

/* ── ALERTAS ── */
.alert {
    border-radius: 12px; padding: 0.7rem 1rem; font-size: 0.82rem;
    margin-bottom: 0.6rem; border: 1px solid;
}
.alert-warn { background: rgba(255,176,32,0.08); color: #FFB020; border-color: rgba(255,176,32,0.25); }
.alert-info { background: rgba(0,212,255,0.08);  color: #00D4FF; border-color: rgba(0,212,255,0.25); }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] { gap: 6px; background: transparent; }
.stTabs [data-baseweb="tab"] {
    background: rgba(17,26,46,0.6); border-radius: 10px;
    border: 1px solid rgba(56,189,248,0.1); color: #94A3B8;
    font-size: 0.82rem; padding: 6px 16px;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(0,212,255,0.15), rgba(0,245,160,0.1)) !important;
    border-color: rgba(0,212,255,0.4) !important; color: #00D4FF !important;
    font-weight: 700;
}

/* ── DATAFRAMES ── */
[data-testid="stDataFrame"] { border: 1px solid rgba(56,189,248,0.12); border-radius: 12px; }

/* ── HEADER PRINCIPAL ── */
.main-hero {
    background: linear-gradient(120deg, #0E1B33 0%, #14264A 60%, #0E1B33 100%);
    border: 1px solid rgba(56,189,248,0.2);
    border-radius: 18px;
    padding: 1.4rem 1.8rem;
    margin-bottom: 1.4rem;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 0 50px rgba(0,212,255,0.06);
}
.main-hero h1 {
    font-size: 1.5rem; font-weight: 800; margin: 0; letter-spacing: 0.01em;
    background: linear-gradient(90deg, #00D4FF, #00F5A0);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.main-hero p { color: #94A3B8; font-size: 0.8rem; margin: 0.25rem 0 0; }
.hero-badge {
    font-size: 0.7rem; color: #00F5A0; border: 1px solid rgba(0,245,160,0.3);
    background: rgba(0,245,160,0.08); padding: 4px 14px; border-radius: 20px;
    font-weight: 700; letter-spacing: 0.08em;
}
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════
# HELPERS DE GRÁFICO — TEMA BI DARK
# ═════════════════════════════════════════════
def _dark_layout(fig, height=320, **kw):
    fig.update_layout(
        height=height,
        margin=dict(t=30, b=20, l=10, r=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TXT_DIM, size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    font=dict(color=TXT_DIM, size=11)),
        hoverlabel=dict(bgcolor=CARD_2, bordercolor=CYAN, font=dict(color=TXT)),
        **kw,
    )
    fig.update_xaxes(showgrid=False, color=TXT_FAINT, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,0.08)",
                     color=TXT_FAINT, zeroline=False)
    return fig


def gauge(valor, titulo, cor=CYAN, sufixo="%", max_val=100):
    """Gauge circular estilo BI."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor,
        number=dict(suffix=sufixo, font=dict(size=34, color=TXT, family="Arial Black")),
        title=dict(text=titulo.upper(),
                   font=dict(size=11, color=TXT_FAINT)),
        gauge=dict(
            axis=dict(range=[0, max_val], tickcolor=TXT_FAINT,
                      tickfont=dict(size=9, color=TXT_FAINT)),
            bar=dict(color=cor, thickness=0.75),
            bgcolor="rgba(148,163,184,0.08)",
            borderwidth=0,
            threshold=dict(line=dict(color=PINK, width=2),
                           thickness=0.8, value=max_val * 0.9),
        ),
    ))
    fig.update_layout(height=210, margin=dict(t=40, b=10, l=25, r=25),
                      paper_bgcolor="rgba(0,0,0,0)",
                      font=dict(color=TXT_DIM))
    return fig


def grafico_funil(prov, emp, liq, pago):
    prov, emp  = safe_float(prov), safe_float(emp)
    liq, pago  = safe_float(liq), safe_float(pago)
    steps  = ["PROVISIONADO", "EMPENHADO", "LIQUIDADO", "PAGO"]
    values = [prov, emp, liq, pago]
    colors = [BLUE, CYAN, PURPLE, TEAL]
    pcts   = [100, num_pct(emp, prov), num_pct(liq, prov), num_pct(pago, prov)]

    fig = go.Figure(go.Bar(
        y=steps[::-1], x=values[::-1],
        orientation="h",
        marker=dict(color=colors[::-1],
                    line=dict(width=0)),
        text=[f"<b>{fmt_brl(v)}</b>  ·  {p}%" for v, p in zip(values[::-1], pcts[::-1])],
        textposition="auto",
        textfont=dict(color="#0B1120", size=13, family="Arial Black"),
        hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>",
    ))
    return _dark_layout(fig, height=300)


def grafico_evolucao(df_mensal):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        name="Provisão", x=df_mensal["Mes"], y=df_mensal["Provisao"],
        mode="lines", line=dict(color=BLUE, width=3, shape="spline"),
        fill="tozeroy", fillcolor="rgba(59,130,246,0.12)",
    ))
    fig.add_trace(go.Bar(
        name="Empenhado", x=df_mensal["Mes"], y=df_mensal["Empenhado"],
        marker=dict(color=CYAN, opacity=0.9), width=0.32, offset=-0.34,
    ))
    fig.add_trace(go.Bar(
        name="Pago", x=df_mensal["Mes"], y=df_mensal["Pago"],
        marker=dict(color=TEAL, opacity=0.95), width=0.32, offset=0.02,
    ))
    return _dark_layout(fig, height=360, hovermode="x unified", barmode="overlay")


def grafico_pi(df_pi):
    df_plot = df_pi.sort_values("Provisao", ascending=True).tail(10)
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Provisão", y=df_plot["PI"], x=df_plot["Provisao"],
                         orientation="h", marker_color="rgba(59,130,246,0.35)"))
    fig.add_trace(go.Bar(name="Empenhado", y=df_plot["PI"], x=df_plot["Empenhado"],
                         orientation="h", marker_color=CYAN))
    fig.add_trace(go.Bar(name="Pago", y=df_plot["PI"], x=df_plot["Pago"],
                         orientation="h", marker_color=TEAL))
    fig = _dark_layout(fig, height=max(300, len(df_plot) * 44), barmode="overlay")
    fig.update_yaxes(showgrid=False, tickfont=dict(size=10, family="monospace"))
    return fig


def grafico_nd_rosca(df_nd, col="Empenhado"):
    df_plot = df_nd[df_nd[col] > 0].sort_values(col, ascending=False)
    fig = go.Figure(go.Pie(
        labels=df_plot["Desc_Nat"].astype(str).str[:32],
        values=df_plot[col],
        hole=0.62,
        marker=dict(colors=PALETA_ND, line=dict(color=BG, width=3)),
        textinfo="percent",
        textfont=dict(color=TXT, size=11),
        hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>",
    ))
    total = df_plot[col].sum()
    fig.add_annotation(text=f"<b>{fmt_brl(total)}</b><br><span style='font-size:10px;color:#64748B'>TOTAL</span>",
                       showarrow=False, font=dict(size=15, color=TXT))
    fig.update_layout(height=340, margin=dict(t=20, b=20, l=10, r=10),
                      paper_bgcolor="rgba(0,0,0,0)",
                      legend=dict(font=dict(size=10, color=TXT_DIM), orientation="v", x=1.02),
                      font=dict(color=TXT_DIM))
    return fig


def grafico_rp_nd(df_rp_nd):
    df_plot = df_rp_nd[df_rp_nd["RP_Inscrito"] > 0].sort_values(
        "RP_Inscrito", ascending=True).tail(10)
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Pago", y=df_plot["Desc_Nat"].astype(str).str[:28],
                         x=df_plot["RP_Pago"], orientation="h", marker_color=TEAL))
    fig.add_trace(go.Bar(name="A pagar", y=df_plot["Desc_Nat"].astype(str).str[:28],
                         x=df_plot["RP_A_Pagar"], orientation="h", marker_color=AMBER))
    fig = _dark_layout(fig, height=max(280, len(df_plot) * 40), barmode="stack")
    fig.update_yaxes(showgrid=False, tickfont=dict(size=10))
    return fig


def kpi_card(label, value, sub="", delta=None, delta_cls="d-info", accent="linear-gradient(90deg,#00D4FF,#00F5A0)", gradient=False):
    val_cls = "val gradient" if gradient else "val"
    delta_html = f'<span class="delta {delta_cls}">{delta}</span>' if delta else ""
    return f"""
    <div class="kpi-hero" style="--accent:{accent};">
      <div class="lbl">{label}</div>
      <div class="{val_cls}">{value}</div>
      <div class="sub">{sub}</div>
      {delta_html}
    </div>"""


def neon_bar(label, a, b, cor, glow):
    p = num_pct(a, b)
    return f"""
    <div style="margin-bottom:0.75rem;">
      <div style="display:flex;justify-content:space-between;font-size:0.78rem;
           color:#94A3B8;margin-bottom:4px;">
        <span>{label}</span>
        <span style="color:#E2E8F0;font-weight:700;">{fmt_pct(a,b)}</span>
      </div>
      <div class="nbar-track">
        <div class="nbar-fill" style="width:{p}%;background:{cor};--glow:{glow};"></div>
      </div>
    </div>"""


# ═════════════════════════════════════════════
# SESSION STATE
# ═════════════════════════════════════════════
for key, default in [("empenhos", pd.DataFrame()), ("restos", pd.DataFrame()),
                     ("saldo", pd.DataFrame()), ("mensal", pd.DataFrame()),
                     ("lancamentos_manuais", [])]:
    if key not in st.session_state:
        st.session_state[key] = default


# ═════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ⚓ Execução Financeira")
    st.markdown('<span style="color:#94A3B8;font-size:0.8rem;">4º Btl Op Lit FN · 2026</span>',
                unsafe_allow_html=True)

    col_nip, col_sair = st.columns([2, 1])
    with col_nip:
        st.caption(f"🔒 NIP {st.session_state.usuario_nip}")
    with col_sair:
        if st.button("Sair", use_container_width=True):
            logout()

    st.divider()
    st.markdown("#### 📂 Importar planilhas")
    st.caption("Envie os 3 arquivos de uma vez — identificação automática.")
    arquivos = st.file_uploader("Arquivos CSV", type="csv",
                                accept_multiple_files=True, key="up_multi",
                                label_visibility="collapsed")
    if arquivos:
        erros = []
        for arq in arquivos:
            raw = arq.read()
            tipo = detectar_tipo(raw)
            try:
                if tipo == "empenhos":
                    st.session_state.empenhos = parse_empenhos(raw)
                    st.success(f"✓ Empenhos: {len(st.session_state.empenhos)}")
                elif tipo == "restos":
                    st.session_state.restos = parse_restos(raw)
                    st.success(f"✓ Restos a pagar: {len(st.session_state.restos)}")
                elif tipo == "saldo":
                    df_m, df_s = parse_saldo(raw)
                    st.session_state.mensal = df_m
                    st.session_state.saldo = df_s
                    st.success(f"✓ Saldo geral: {len(df_m)} meses")
                else:
                    erros.append(arq.name)
            except Exception as exc:
                st.error(f"Erro em {arq.name}: {exc}")
        if erros:
            st.warning(f"Não reconhecido(s): {', '.join(erros)}")

    st.divider()
    st.markdown("#### ✏️ Lançamento manual")
    with st.expander("Novo empenho"):
        ne_in   = st.text_input("Nº Empenho", placeholder="2026NE000099")
        fav_in  = st.text_input("Favorecido")
        pi_in   = st.text_input("PI", placeholder="G471FC801L0")
        desc_pi = st.text_input("Descrição do PI")
        nd_in   = st.text_input("Natureza de Despesa", placeholder="33903919")
        emp_in  = st.number_input("Valor empenhado (R$)", min_value=0.0, step=0.01)
        liq_in  = st.number_input("Valor liquidado (R$)", min_value=0.0, step=0.01)
        pag_in  = st.number_input("Valor pago (R$)", min_value=0.0, step=0.01)
        if st.button("➕ Incluir", use_container_width=True):
            novo = {"NE": ne_in or f"MANUAL{len(st.session_state.lancamentos_manuais)+1:03d}",
                    "NE_display": ne_in or "MANUAL",
                    "Favorecido": fav_in or "Não informado",
                    "PI": pi_in, "Desc_PI": desc_pi,
                    "Nat_Desp": nd_in, "Desc_Nat": "",
                    "Empenhado": emp_in, "A_Liquidar": emp_in - liq_in,
                    "Liquidado": liq_in, "Liq_A_Pagar": liq_in - pag_in,
                    "Pago": pag_in}
            st.session_state.lancamentos_manuais.append(novo)
            novo_df = pd.DataFrame([novo])
            st.session_state.empenhos = (novo_df if st.session_state.empenhos.empty
                else pd.concat([st.session_state.empenhos, novo_df], ignore_index=True))
            st.success(f"Empenho {novo['NE_display']} incluído!")
            st.rerun()

    if st.session_state.lancamentos_manuais:
        st.caption(f"📝 {len(st.session_state.lancamentos_manuais)} lançamento(s) nesta sessão")

    st.divider()
    st.markdown("#### 🔍 Filtros")
    filtro_pi, filtro_nd = "", ""
    if not st.session_state.empenhos.empty:
        pis = ["Todos"] + sorted(st.session_state.empenhos["PI"].dropna().astype(str).unique().tolist())
        filtro_pi = st.selectbox("Programa Interno (PI)", pis)
        nds = ["Todos"] + sorted(st.session_state.empenhos["Nat_Desp"].dropna().astype(str).unique().tolist())
        filtro_nd = st.selectbox("Natureza de Despesa", nds)

    st.divider()
    st.caption(f"Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")


# ═════════════════════════════════════════════
# DADOS FILTRADOS + CÁLCULOS
# ═════════════════════════════════════════════
df_emp = st.session_state.empenhos.copy()
df_rp  = st.session_state.restos.copy()
df_sg  = st.session_state.saldo.copy()
df_men = st.session_state.mensal.copy()

if not df_emp.empty:
    if filtro_pi and filtro_pi != "Todos":
        df_emp = df_emp[df_emp["PI"].astype(str) == filtro_pi]
    if filtro_nd and filtro_nd != "Todos":
        df_emp = df_emp[df_emp["Nat_Desp"].astype(str) == filtro_nd]

ultimo_mes_lbl = df_men["Mes"].iloc[-1] if not df_men.empty else "—"

st.markdown(f"""
<div class="main-hero">
  <div>
    <h1>⚓ EXECUÇÃO FINANCEIRA</h1>
    <p>4º Batalhão de Operações Litorâneas de Fuzileiros Navais — Exercício 2026</p>
  </div>
  <div class="hero-badge">POSIÇÃO · {ultimo_mes_lbl}</div>
</div>
""", unsafe_allow_html=True)

if df_emp.empty and df_rp.empty:
    st.markdown('<div class="alert alert-info">📂 <b>Nenhum dado carregado.</b> '
                'Use a barra lateral para importar os 3 arquivos CSV de uma vez '
                'ou lançar empenhos manualmente.</div>', unsafe_allow_html=True)
    st.stop()

if not df_sg.empty and "Mes" in df_sg.columns:
    _um = df_sg["Mes"].iloc[-1]
    _sg_last = df_sg[df_sg["Mes"] == _um]
else:
    _sg_last = df_sg

total_prov = safe_float(_sg_last["Provisao"].sum()) if not _sg_last.empty else 0
total_cred = safe_float(_sg_last["Credito_Disp"].sum()) if not _sg_last.empty else 0
total_emp  = safe_float(df_emp["Empenhado"].sum()) if not df_emp.empty else 0
total_liq  = safe_float(df_emp["Liquidado"].sum()) if not df_emp.empty else 0
total_pago = safe_float(df_emp["Pago"].sum()) if not df_emp.empty else 0

rp_ins  = safe_float(df_rp["RP_Inscrito"].sum()) if not df_rp.empty else 0
rp_pago = safe_float(df_rp["RP_Pago"].sum()) if not df_rp.empty else 0
rp_apr  = safe_float(df_rp["RP_A_Pagar"].sum()) if not df_rp.empty else 0

tx_emp  = total_emp / total_prov * 100 if total_prov else 0
tx_exec = total_pago / total_prov * 100 if total_prov else 0
tx_rp   = rp_pago / rp_ins * 100 if rp_ins else 0

# Alertas
if tx_emp < 30 and total_prov > 0:
    st.markdown(f'<div class="alert alert-warn">⚠️ Taxa de empenho baixa: '
                f'<b>{tx_emp:.1f}%</b> — {fmt_brl(total_emp)} de {fmt_brl(total_prov)} provisionados.</div>',
                unsafe_allow_html=True)
liq_pend = total_liq - total_pago
if liq_pend > 0.01:
    st.markdown(f'<div class="alert alert-info">💡 Liquidadas a pagar: '
                f'<b>{fmt_brl(liq_pend)}</b> aguardando pagamento.</div>',
                unsafe_allow_html=True)


# ═════════════════════════════════════════════
# ABAS
# ═════════════════════════════════════════════
tabs = st.tabs(["⚡ VISÃO GERAL", "📋 EMPENHOS", "🔄 RESTOS A PAGAR",
                "📁 POR PI", "🏷️ POR ND", "📈 EVOLUÇÃO"])

# ── ABA 1: VISÃO GERAL ──
with tabs[0]:
    st.markdown('<div class="sec">Recursos — dotação e disponibilidade</div>',
                unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card("Provisão Recebida", fmt_brl(total_prov),
                    "teto de crédito autorizado", gradient=True), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("Crédito Disponível", fmt_brl(total_cred),
                    "saldo a empenhar",
                    accent="linear-gradient(90deg,#3B82F6,#00D4FF)"), unsafe_allow_html=True)
    with c3:
        cls = "d-ok" if tx_emp >= 60 else ("d-warn" if tx_emp >= 30 else "d-bad")
        lbl = "BOM" if tx_emp >= 60 else ("ATENÇÃO" if tx_emp >= 30 else "BAIXO")
        st.markdown(kpi_card("Taxa de Empenho", f"{tx_emp:.1f}%",
                    "empenhado / provisão", lbl, cls,
                    accent="linear-gradient(90deg,#A78BFA,#00D4FF)"), unsafe_allow_html=True)
    with c4:
        cls = "d-ok" if tx_exec >= 50 else ("d-warn" if tx_exec >= 20 else "d-bad")
        lbl = "BOM" if tx_exec >= 50 else ("ATENÇÃO" if tx_exec >= 20 else "BAIXO")
        st.markdown(kpi_card("Taxa de Execução", f"{tx_exec:.1f}%",
                    "pago / provisão", lbl, cls,
                    accent="linear-gradient(90deg,#FFB020,#FF4D6D)"), unsafe_allow_html=True)

    st.markdown('<div class="sec">Indicadores de performance</div>', unsafe_allow_html=True)
    g1, g2, g3 = st.columns(3)
    with g1:
        st.plotly_chart(gauge(round(tx_emp, 1), "Taxa de empenho", CYAN),
                        use_container_width=True, config={"displayModeBar": False})
    with g2:
        st.plotly_chart(gauge(round(tx_exec, 1), "Taxa de execução", AMBER),
                        use_container_width=True, config={"displayModeBar": False})
    with g3:
        st.plotly_chart(gauge(round(tx_rp, 1), "% pago dos RP", TEAL),
                        use_container_width=True, config={"displayModeBar": False})

    col_l, col_r = st.columns([1.3, 1])
    with col_l:
        st.markdown('<div class="sec">Pipeline da despesa — 2026</div>', unsafe_allow_html=True)
        st.plotly_chart(grafico_funil(total_prov, total_emp, total_liq, total_pago),
                        use_container_width=True, config={"displayModeBar": False})
    with col_r:
        st.markdown('<div class="sec">Fases (% sobre a anterior)</div>', unsafe_allow_html=True)
        st.markdown(
            neon_bar("Empenhado / Provisionado", total_emp, total_prov, CYAN, "rgba(0,212,255,0.5)") +
            neon_bar("Liquidado / Empenhado", total_liq, total_emp, PURPLE, "rgba(167,139,250,0.5)") +
            neon_bar("Pago / Liquidado", total_pago, total_liq, TEAL, "rgba(0,245,160,0.5)") +
            neon_bar("Pago / Provisionado", total_pago, total_prov, AMBER, "rgba(255,176,32,0.5)"),
            unsafe_allow_html=True)

        st.markdown('<div class="sec">Restos a pagar</div>', unsafe_allow_html=True)
        r1, r2 = st.columns(2)
        with r1:
            st.markdown(kpi_card("RP Inscrito", fmt_brl(rp_ins), "",
                        accent="linear-gradient(90deg,#A78BFA,#FF4D6D)"), unsafe_allow_html=True)
        with r2:
            cls = "d-ok" if tx_rp >= 90 else "d-info"
            st.markdown(kpi_card("RP Pago", fmt_brl(rp_pago),
                        f"{tx_rp:.1f}% do inscrito", "ÓTIMO" if tx_rp >= 90 else None, cls,
                        accent="linear-gradient(90deg,#00F5A0,#00D4FF)"), unsafe_allow_html=True)

# ── ABA 2: EMPENHOS ──
with tabs[1]:
    if df_emp.empty:
        st.info("Importe o arquivo de Controle de Empenhos.")
    else:
        st.markdown('<div class="sec">Empenhos do exercício 2026</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(kpi_card("Empenhos", str(len(df_emp)), "registros"), unsafe_allow_html=True)
        with c2:
            st.markdown(kpi_card("Empenhado", fmt_brl(df_emp["Empenhado"].sum()), "",
                        accent="linear-gradient(90deg,#00D4FF,#3B82F6)"), unsafe_allow_html=True)
        with c3:
            st.markdown(kpi_card("Liquidado", fmt_brl(df_emp["Liquidado"].sum()), "",
                        accent="linear-gradient(90deg,#A78BFA,#00D4FF)"), unsafe_allow_html=True)
        with c4:
            st.markdown(kpi_card("Pago", fmt_brl(df_emp["Pago"].sum()), "",
                        accent="linear-gradient(90deg,#00F5A0,#00D4FF)", gradient=True),
                        unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        df_show = df_emp[["NE_display", "Favorecido", "PI", "Desc_Nat",
                          "Empenhado", "Liquidado", "Pago"]].copy()
        df_show["Situação"] = df_emp.apply(
            lambda r: status_empenho(r["Empenhado"], r["Liquidado"], r["Pago"])[0], axis=1)
        df_show.columns = ["Empenho", "Favorecido", "PI", "Natureza",
                           "Empenhado (R$)", "Liquidado (R$)", "Pago (R$)", "Situação"]
        st.dataframe(df_show.style.format({
            "Empenhado (R$)": "R$ {:,.2f}", "Liquidado (R$)": "R$ {:,.2f}",
            "Pago (R$)": "R$ {:,.2f}"}), use_container_width=True, height=420)

        pend = df_emp[df_emp["A_Liquidar"] > 0.01]
        if not pend.empty:
            st.markdown(f'<div class="sec">Pendentes de liquidação ({len(pend)})</div>',
                        unsafe_allow_html=True)
            st.dataframe(pend[["NE_display", "Favorecido", "Empenhado", "A_Liquidar"]]
                .rename(columns={"NE_display": "Empenho", "Empenhado": "Empenhado (R$)",
                                 "A_Liquidar": "A Liquidar (R$)"})
                .style.format({"Empenhado (R$)": "R$ {:,.2f}", "A Liquidar (R$)": "R$ {:,.2f}"}),
                use_container_width=True)

# ── ABA 3: RESTOS A PAGAR ──
with tabs[2]:
    if df_rp.empty:
        st.info("Importe o arquivo de Restos a Pagar.")
    else:
        st.markdown('<div class="sec">Restos a pagar — exercícios anteriores</div>',
                    unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(kpi_card("RP Inscrito", fmt_brl(rp_ins), ""), unsafe_allow_html=True)
        with c2:
            st.markdown(kpi_card("RP Liquidado", fmt_brl(df_rp["RP_Liquidado"].sum()), "",
                        accent="linear-gradient(90deg,#A78BFA,#00D4FF)"), unsafe_allow_html=True)
        with c3:
            st.markdown(kpi_card("RP Pago", fmt_brl(rp_pago),
                        f"{tx_rp:.1f}% do inscrito",
                        accent="linear-gradient(90deg,#00F5A0,#00D4FF)", gradient=True),
                        unsafe_allow_html=True)
        with c4:
            st.markdown(kpi_card("RP a Pagar", fmt_brl(rp_apr), "saldo residual",
                        accent="linear-gradient(90deg,#FFB020,#FF4D6D)"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        df_rp_show = df_rp[["NE_display", "Favorecido", "PI", "Desc_Nat",
                            "RP_Inscrito", "RP_Liquidado", "RP_Pago", "RP_A_Pagar"]].copy()
        def _sit_rp(row):
            if row["RP_A_Pagar"] <= 0.01 and row["RP_Pago"] > 0: return "Quitado"
            if row["RP_Liquidado"] > 0 and row["RP_A_Pagar"] > 0: return "Liq. a pagar"
            if row["RP_A_Pagar"] > 0: return "Pendente"
            return "—"
        df_rp_show["Situação"] = df_rp.apply(_sit_rp, axis=1)
        df_rp_show.columns = ["Empenho", "Favorecido", "PI", "Natureza",
                              "Inscrito (R$)", "Liquidado (R$)", "Pago (R$)",
                              "A Pagar (R$)", "Situação"]
        st.dataframe(df_rp_show.style.format({
            "Inscrito (R$)": "R$ {:,.2f}", "Liquidado (R$)": "R$ {:,.2f}",
            "Pago (R$)": "R$ {:,.2f}", "A Pagar (R$)": "R$ {:,.2f}"}),
            use_container_width=True, height=380)

        pend_rp = df_rp[df_rp["RP_A_Pagar"] > 0.01].sort_values("RP_A_Pagar", ascending=False)
        if not pend_rp.empty:
            st.markdown(f'<div class="sec">Pendências a quitar '
                        f'({len(pend_rp)} · {fmt_brl(pend_rp["RP_A_Pagar"].sum())})</div>',
                        unsafe_allow_html=True)
            st.dataframe(pend_rp[["NE_display", "Favorecido", "RP_Inscrito", "RP_A_Pagar"]]
                .rename(columns={"NE_display": "Empenho", "RP_Inscrito": "Inscrito (R$)",
                                 "RP_A_Pagar": "A Pagar (R$)"})
                .style.format({"Inscrito (R$)": "R$ {:,.2f}", "A Pagar (R$)": "R$ {:,.2f}"}),
                use_container_width=True)

# ── ABA 4: POR PI ──
with tabs[3]:
    if df_emp.empty and df_sg.empty:
        st.info("Importe os arquivos de Empenhos e/ou Saldo Geral.")
    else:
        if not df_sg.empty:
            _um2 = df_sg["Mes"].iloc[-1] if "Mes" in df_sg.columns else ""
            _sgl = df_sg[df_sg["Mes"] == _um2].copy()
            _sgl["PI"] = _sgl["PI"].astype(str).str.strip()
            df_pi = _sgl.groupby(["PI", "Desc_PI"]).agg(
                Provisao=("Provisao", "sum"), Credito_Disp=("Credito_Disp", "sum"),
                Empenhado=("Empenhado", "sum"), Pago=("Pago", "sum")).reset_index()
        else:
            _ec = df_emp.copy()
            _ec["PI"] = _ec["PI"].astype(str).str.strip()
            df_pi = _ec.groupby(["PI", "Desc_PI"]).agg(
                Empenhado=("Empenhado", "sum"), Liquidado=("Liquidado", "sum"),
                Pago=("Pago", "sum")).reset_index()
            df_pi["Provisao"] = df_pi["Empenhado"]
            df_pi["Credito_Disp"] = 0

        if not df_emp.empty:
            _em = df_emp.copy()
            _em["PI"] = _em["PI"].astype(str).str.strip()
            df_pi["PI"] = df_pi["PI"].astype(str).str.strip()
            liq_pi = _em.groupby("PI").agg(Liquidado=("Liquidado", "sum")).reset_index()
            if "Liquidado" in df_pi.columns:
                df_pi = df_pi.drop(columns=["Liquidado"])
            df_pi = df_pi.merge(liq_pi, on="PI", how="left")
            df_pi["Liquidado"] = df_pi["Liquidado"].fillna(0)

        sub1, sub2 = st.tabs(["Empenhos 2026", "Restos a Pagar"])
        with sub1:
            for _, row in df_pi.sort_values("Provisao", ascending=False).iterrows():
                prov, emp = row["Provisao"], row.get("Empenhado", 0)
                liq, pago = row.get("Liquidado", 0), row.get("Pago", 0)
                cred = row.get("Credito_Disp", 0)
                if prov <= 0 and emp <= 0:
                    continue
                tx = num_pct(emp, prov)
                cls = "d-ok" if tx >= 80 else ("d-info" if tx >= 40 else
                      ("d-warn" if tx > 0 else "d-bad"))
                lbl = "ALTO" if tx >= 80 else ("PARCIAL" if tx >= 40 else
                      ("BAIXO" if tx > 0 else "SEM EMPENHO"))
                st.markdown(f"""
                <div class="pi-card">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;
                       flex-wrap:wrap;gap:8px;margin-bottom:0.7rem;">
                    <div>
                      <div class="pi-code">{row['PI']}</div>
                      <div class="pi-name">{str(row.get('Desc_PI','')).title()}</div>
                      <div class="pi-meta">Provisão <b>{fmt_brl(prov)}</b> ·
                           Crédito disp. <b>{fmt_brl(cred)}</b></div>
                    </div>
                    <span class="delta {cls}">{lbl}</span>
                  </div>
                  {neon_bar("Empenhado", emp, prov, CYAN, "rgba(0,212,255,0.5)")}
                  {neon_bar("Liquidado", liq, emp, PURPLE, "rgba(167,139,250,0.5)")}
                  {neon_bar("Pago", pago, emp, TEAL, "rgba(0,245,160,0.5)")}
                </div>""", unsafe_allow_html=True)

            st.markdown('<div class="sec">Comparativo por PI</div>', unsafe_allow_html=True)
            st.plotly_chart(grafico_pi(df_pi), use_container_width=True,
                            config={"displayModeBar": False})

        with sub2:
            if df_rp.empty:
                st.info("Importe o arquivo de Restos a Pagar.")
            else:
                df_rp_pi = df_rp.groupby(["PI", "Desc_PI"]).agg(
                    RP_Inscrito=("RP_Inscrito", "sum"), RP_Pago=("RP_Pago", "sum"),
                    RP_A_Pagar=("RP_A_Pagar", "sum")).reset_index()
                for _, row in df_rp_pi.sort_values("RP_Inscrito", ascending=False).iterrows():
                    ins, pago, apr = row["RP_Inscrito"], row["RP_Pago"], row["RP_A_Pagar"]
                    total = max(ins, pago + apr)
                    if total <= 0:
                        continue
                    quit_ = apr <= 0.01
                    cls = "d-ok" if quit_ else ("d-info" if num_pct(pago, total) >= 80 else "d-warn")
                    lbl = "QUITADO" if quit_ else f"{fmt_pct(pago, total)} PAGO"
                    st.markdown(f"""
                    <div class="pi-card">
                      <div style="display:flex;justify-content:space-between;align-items:flex-start;
                           flex-wrap:wrap;gap:8px;margin-bottom:0.7rem;">
                        <div>
                          <div class="pi-code">{row['PI']}</div>
                          <div class="pi-name">{str(row.get('Desc_PI','')).title()}</div>
                          <div class="pi-meta">Inscrito <b>{fmt_brl(ins)}</b> ·
                               Pago <b>{fmt_brl(pago)}</b> · Saldo <b>{fmt_brl(apr)}</b></div>
                        </div>
                        <span class="delta {cls}">{lbl}</span>
                      </div>
                      {neon_bar("Pago", pago, total, TEAL, "rgba(0,245,160,0.5)")}
                      {neon_bar("A pagar", apr, total, AMBER, "rgba(255,176,32,0.5)")}
                    </div>""", unsafe_allow_html=True)

# ── ABA 5: POR ND ──
with tabs[4]:
    if df_emp.empty and df_rp.empty:
        st.info("Importe os arquivos CSV.")
    else:
        sub_n1, sub_n2 = st.tabs(["Empenhos 2026", "Restos a Pagar"])
        with sub_n1:
            if df_emp.empty:
                st.info("Importe o arquivo de Empenhos.")
            else:
                df_nd = df_emp.groupby(["Nat_Desp", "Desc_Nat"]).agg(
                    Empenhado=("Empenhado", "sum"), Liquidado=("Liquidado", "sum"),
                    Pago=("Pago", "sum")).reset_index().sort_values("Empenhado", ascending=False)

                col_t, col_g = st.columns([1, 1])
                with col_t:
                    st.markdown('<div class="sec">Por natureza de despesa</div>',
                                unsafe_allow_html=True)
                    dfn = df_nd.rename(columns={
                        "Nat_Desp": "ND", "Desc_Nat": "Natureza",
                        "Empenhado": "Empenhado (R$)", "Liquidado": "Liquidado (R$)",
                        "Pago": "Pago (R$)"})
                    st.dataframe(dfn.style.format({
                        "Empenhado (R$)": "R$ {:,.2f}", "Liquidado (R$)": "R$ {:,.2f}",
                        "Pago (R$)": "R$ {:,.2f}"}), use_container_width=True, height=360)
                with col_g:
                    st.markdown('<div class="sec">Participação no empenhado</div>',
                                unsafe_allow_html=True)
                    st.plotly_chart(grafico_nd_rosca(df_nd), use_container_width=True,
                                    config={"displayModeBar": False})

                st.markdown('<div class="sec">Pipeline por ND</div>', unsafe_allow_html=True)
                max_emp = df_nd["Empenhado"].max()
                for _, row in df_nd.iterrows():
                    st.markdown(f"""
                    <div class="pi-card" style="padding:0.8rem 1.1rem;">
                      <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem;">
                        <span style="font-size:0.85rem;font-weight:700;color:#E2E8F0;">
                          {str(row['Desc_Nat'])[:48]}</span>
                        <span class="pi-code">{row['Nat_Desp']}</span>
                      </div>
                      {neon_bar("Empenhado", row['Empenhado'], max_emp, CYAN, "rgba(0,212,255,0.5)")}
                      {neon_bar("Liquidado", row['Liquidado'], row['Empenhado'], PURPLE, "rgba(167,139,250,0.5)")}
                      {neon_bar("Pago", row['Pago'], row['Empenhado'], TEAL, "rgba(0,245,160,0.5)")}
                    </div>""", unsafe_allow_html=True)

        with sub_n2:
            if df_rp.empty:
                st.info("Importe o arquivo de Restos a Pagar.")
            else:
                df_rp_nd = df_rp.groupby(["Nat_Desp", "Desc_Nat"]).agg(
                    RP_Inscrito=("RP_Inscrito", "sum"), RP_Pago=("RP_Pago", "sum"),
                    RP_A_Pagar=("RP_A_Pagar", "sum")).reset_index().sort_values(
                    "RP_Inscrito", ascending=False)
                col_t2, col_g2 = st.columns([1, 1])
                with col_t2:
                    st.markdown('<div class="sec">RP por natureza</div>', unsafe_allow_html=True)
                    dfr = df_rp_nd.rename(columns={
                        "Nat_Desp": "ND", "Desc_Nat": "Natureza",
                        "RP_Inscrito": "Inscrito (R$)", "RP_Pago": "Pago (R$)",
                        "RP_A_Pagar": "A Pagar (R$)"})
                    st.dataframe(dfr.style.format({
                        "Inscrito (R$)": "R$ {:,.2f}", "Pago (R$)": "R$ {:,.2f}",
                        "A Pagar (R$)": "R$ {:,.2f}"}), use_container_width=True, height=360)
                with col_g2:
                    st.markdown('<div class="sec">Pago × A pagar</div>', unsafe_allow_html=True)
                    st.plotly_chart(grafico_rp_nd(df_rp_nd), use_container_width=True,
                                    config={"displayModeBar": False})

# ── ABA 6: EVOLUÇÃO ──
with tabs[5]:
    if df_men.empty:
        st.info("Importe o arquivo de Controle de Saldo Geral.")
    else:
        st.markdown('<div class="sec">Evolução mensal — 2026</div>', unsafe_allow_html=True)
        st.plotly_chart(grafico_evolucao(df_men), use_container_width=True,
                        config={"displayModeBar": False})

        st.markdown('<div class="sec">Taxa de execução mensal</div>', unsafe_allow_html=True)
        df_tx = df_men.copy()
        df_tx["tx"] = df_tx.apply(
            lambda r: round(r["Pago"] / r["Provisao"] * 100, 2) if r["Provisao"] else 0, axis=1)
        fig_tx = go.Figure(go.Scatter(
            x=df_tx["Mes"], y=df_tx["tx"], mode="lines+markers+text",
            text=[f"{v:.1f}%" for v in df_tx["tx"]], textposition="top center",
            textfont=dict(color=TEAL, size=11),
            line=dict(color=TEAL, width=3, shape="spline"),
            marker=dict(size=9, color=TEAL, line=dict(color=BG, width=2)),
            fill="tozeroy", fillcolor="rgba(0,245,160,0.08)"))
        fig_tx = _dark_layout(fig_tx, height=280)
        fig_tx.update_yaxes(ticksuffix="%")
        st.plotly_chart(fig_tx, use_container_width=True, config={"displayModeBar": False})

        st.markdown('<div class="sec">Resumo por mês</div>', unsafe_allow_html=True)
        df_ms = df_men.copy()
        for col in ["Provisao", "Credito_Disp", "Empenhado", "Liquidado", "Pago"]:
            if col in df_ms.columns:
                df_ms[col] = df_ms[col].apply(fmt_brl)
        df_ms.columns = [c.replace("_", " ") for c in df_ms.columns]
        st.dataframe(df_ms, use_container_width=True)
