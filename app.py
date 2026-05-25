"""
Dashboard de Execução Financeira — 4º Btl Op Lit FN
Desenvolvido com Streamlit + Plotly
Execução: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from io import StringIO
import json
import os
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Execução Financeira — 4º Btl Op Lit FN",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# AUTENTICAÇÃO — LOGIN POR NIP
# ─────────────────────────────────────────────

# Cadastro de usuários: { "NIP": "senha" }
# Neste sistema o login E a senha são o próprio NIP.
USUARIOS = {
    "17056004": "17056004",
    "03105288": "03105288",
    "13130510": "13130510",
    "96007494": "96007494",
}

def check_login(nip: str, senha: str) -> bool:
    nip   = nip.strip()
    senha = senha.strip()
    return USUARIOS.get(nip) == senha

def logout():
    st.session_state.autenticado = False
    st.session_state.usuario_nip = ""
    st.rerun()

# Inicializa estado de autenticação
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_nip" not in st.session_state:
    st.session_state.usuario_nip = ""
if "login_erro" not in st.session_state:
    st.session_state.login_erro = False

# Se não autenticado, exibe tela de login e para aqui
if not st.session_state.autenticado:
    # CSS específico da tela de login
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] > .main { background: #0a2342; }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stToolbar"] { display: none; }
    section[data-testid="stSidebar"] { display: none; }

    .login-wrapper {
        display: flex; flex-direction: column; align-items: center;
        justify-content: center; min-height: 80vh;
    }
    .login-card {
        background: white; border-radius: 16px;
        padding: 2.5rem 2rem; width: 100%; max-width: 380px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        text-align: center;
    }
    .login-anchor { color: #0a2342; font-size: 2rem; margin-bottom: 0.25rem; }
    .login-title  { font-size: 1.1rem; font-weight: 700; color: #0a2342; margin-bottom: 0.15rem; }
    .login-sub    { font-size: 0.78rem; color: #6b7a8d; margin-bottom: 1.5rem; }
    .login-divider { border: none; border-top: 1px solid #e8ecf0; margin: 1rem 0; }
    .login-erro {
        background: #f8d7da; color: #721c24; border-radius: 8px;
        padding: 0.5rem 0.75rem; font-size: 0.8rem;
        margin-bottom: 0.75rem; text-align: left;
    }
    </style>
    """, unsafe_allow_html=True)

    # Layout centralizado via colunas
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("""
        <div style="text-align:center; padding: 2rem 0 1rem;">
          <div style="font-size:2.5rem;">⚓</div>
          <div style="font-size:1.05rem; font-weight:700; color:white; margin-top:0.4rem;">
            Dashboard de Execução Financeira
          </div>
          <div style="font-size:0.8rem; color:rgba(255,255,255,0.65); margin-top:0.2rem;">
            4º Batalhão de Operações Litorâneas de Fuzileiros Navais — 2026
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_login", clear_on_submit=False):
            st.markdown(
                '<div style="font-size:0.78rem;font-weight:600;color:#6b7a8d;'
                'text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.4rem;">'
                'NIP (login)</div>',
                unsafe_allow_html=True,
            )
            nip_input = st.text_input(
                "NIP", label_visibility="collapsed",
                placeholder="Digite seu NIP", max_chars=12,
            )
            st.markdown(
                '<div style="font-size:0.78rem;font-weight:600;color:#6b7a8d;'
                'text-transform:uppercase;letter-spacing:0.05em;'
                'margin-top:0.75rem;margin-bottom:0.4rem;">'
                'Senha</div>',
                unsafe_allow_html=True,
            )
            senha_input = st.text_input(
                "Senha", label_visibility="collapsed",
                placeholder="Digite sua senha", type="password", max_chars=12,
            )

            if st.session_state.login_erro:
                st.markdown(
                    '<div class="login-erro">⚠️ NIP ou senha incorretos. Verifique e tente novamente.</div>',
                    unsafe_allow_html=True,
                )

            submitted = st.form_submit_button(
                "Entrar", use_container_width=True, type="primary"
            )

            if submitted:
                if check_login(nip_input, senha_input):
                    st.session_state.autenticado = True
                    st.session_state.usuario_nip = nip_input.strip()
                    st.session_state.login_erro  = False
                    st.rerun()
                else:
                    st.session_state.login_erro = True
                    st.rerun()

        st.markdown(
            '<div style="text-align:center;font-size:0.72rem;color:rgba(255,255,255,0.45);'
            'margin-top:1rem;">Acesso restrito a usuários autorizados</div>',
            unsafe_allow_html=True,
        )

    st.stop()  # Interrompe execução — nada abaixo é renderizado sem login


# ─────────────────────────────────────────────
# ESTILOS CUSTOMIZADOS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Fonte e espaçamento geral */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Cabeçalho principal */
    .main-header {
        background: linear-gradient(135deg, #0a2342 0%, #1a3a5c 100%);
        color: white;
        padding: 1.25rem 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    .main-header h1 { color: white; margin: 0; font-size: 1.4rem; font-weight: 600; }
    .main-header p  { color: rgba(255,255,255,0.7); margin: 0.25rem 0 0; font-size: 0.85rem; }

    /* Cards de KPI */
    .kpi-card {
        background: white;
        border: 1px solid #e8ecf0;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        text-align: center;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .kpi-label { font-size: 0.72rem; color: #6b7a8d; text-transform: uppercase;
                 letter-spacing: 0.05em; margin-bottom: 0.3rem; font-weight: 600; }
    .kpi-value { font-size: 1.55rem; font-weight: 700; color: #0a2342; line-height: 1.1; }
    .kpi-sub   { font-size: 0.72rem; color: #9baab8; margin-top: 0.2rem; }

    /* Badges */
    .badge {
        display: inline-block; font-size: 0.68rem; font-weight: 600;
        padding: 2px 9px; border-radius: 20px; margin-top: 0.35rem;
    }
    .badge-ok     { background: #d4edda; color: #155724; }
    .badge-warn   { background: #fff3cd; color: #856404; }
    .badge-danger { background: #f8d7da; color: #721c24; }
    .badge-info   { background: #d1ecf1; color: #0c5460; }
    .badge-gray   { background: #e9ecef; color: #495057; }

    /* Seções */
    .section-title {
        font-size: 0.72rem; font-weight: 700; color: #6b7a8d;
        text-transform: uppercase; letter-spacing: 0.08em;
        margin: 1.5rem 0 0.75rem; border-bottom: 1px solid #e8ecf0;
        padding-bottom: 0.4rem;
    }

    /* Cards de PI */
    .pi-card {
        background: white; border: 1px solid #e8ecf0;
        border-radius: 10px; padding: 1rem 1.25rem;
        margin-bottom: 0.75rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .pi-code  { font-family: monospace; font-size: 0.72rem; color: #9baab8; }
    .pi-name  { font-size: 0.92rem; font-weight: 600; color: #0a2342; margin: 0.15rem 0; }
    .pi-prov  { font-size: 0.78rem; color: #6b7a8d; }

    /* Tabelas */
    .stDataFrame { border-radius: 8px; overflow: hidden; }

    /* Sidebar */
    [data-testid="stSidebar"] { background: #f8f9fb; }
    [data-testid="stSidebar"] .stMarkdown h3 { color: #0a2342; }

    /* Abas */
    .stTabs [data-baseweb="tab"] { font-size: 0.85rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }

    /* Métricas Streamlit nativas */
    [data-testid="stMetricValue"] { font-size: 1.4rem !important; }

    /* Alertas de status */
    .status-bar {
        padding: 0.6rem 1rem; border-radius: 8px;
        font-size: 0.82rem; margin-bottom: 1rem;
    }
    .status-ok     { background: #d4edda; color: #155724; border-left: 4px solid #28a745; }
    .status-warn   { background: #fff3cd; color: #856404; border-left: 4px solid #ffc107; }
    .status-danger { background: #f8d7da; color: #721c24; border-left: 4px solid #dc3545; }

    div[data-testid="stHorizontalBlock"] > div { padding: 0 0.3rem; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PERSISTÊNCIA DE DADOS (session_state)
# ─────────────────────────────────────────────
if "empenhos" not in st.session_state:
    st.session_state.empenhos = pd.DataFrame()
if "restos" not in st.session_state:
    st.session_state.restos = pd.DataFrame()
if "saldo" not in st.session_state:
    st.session_state.saldo = pd.DataFrame()
if "mensal" not in st.session_state:
    st.session_state.mensal = pd.DataFrame()
if "lancamentos_manuais" not in st.session_state:
    st.session_state.lancamentos_manuais = []


# ─────────────────────────────────────────────
# FUNÇÕES DE PARSE
# ─────────────────────────────────────────────
def parse_br(s):
    """Converte valor monetário brasileiro (1.234,56) para float."""
    try:
        return float(str(s).strip().replace(".", "").replace(",", "."))
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


def badge_html(label, cls):
    return f'<span class="badge badge-{cls}">{label}</span>'


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


# ─────────────────────────────────────────────
# PARSE — EMPENHOS
# ─────────────────────────────────────────────
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
    )
    df = df[df["NE"].str.contains("NE", na=False)].copy()
    for col in ["Empenhado", "A_Liquidar", "Liquidado", "Liq_A_Pagar", "Pago"]:
        df[col] = df[col].apply(parse_br)
    # Extrair número limpo do empenho
    df["NE_display"] = df["NE"].str.extract(r"(NE\d+)").fillna(df["NE"])
    df["Favorecido"] = df["Favorecido"].str.strip().str.title()
    return df


# ─────────────────────────────────────────────
# PARSE — RESTOS A PAGAR
# ─────────────────────────────────────────────
def parse_restos(file_bytes):
    """Parse dinâmico: lê os códigos de item do header para mapear colunas corretamente."""
    import re as _re
    content = file_bytes.decode("latin-1")
    lines = content.split("\r\n")

    ITEM_COLS_RP = {
        "40": "RP_Inscrito",
        "43": "RP_A_Liquidar",
        "44": "RP_Liquidado",
        "45": "RP_Liq_A_Pagar",
        "46": "RP_Pago",
        "47": "RP_A_Pagar",
    }

    # Encontrar linha de header com os códigos de item
    header_line = next((l for l in lines[:10] if _re.search(r'"40"', l)), "")
    item_codes = _re.findall(r'"(\d{2})"', header_line)

    # Colunas fixas: 0=NE,1=CNPJ,2=Favorecido,3=Ano,4=Nat_Desp,5=Desc_Nat,6=PI,7=Desc_PI
    col_map = {0:"NE",1:"CNPJ",2:"Favorecido",3:"Ano",
               4:"Nat_Desp",5:"Desc_Nat",6:"PI",7:"Desc_PI"}
    for i, code in enumerate(item_codes):
        if code in ITEM_COLS_RP:
            col_map[8 + i] = ITEM_COLS_RP[code]

    # Dados começam após as linhas de header (linha 8 em diante)
    data_lines = [l for l in lines[8:] if l.strip() and not l.startswith(" \t")]
    if not data_lines:
        return pd.DataFrame()

    df = pd.read_csv(StringIO("\r\n".join(data_lines)),
                     sep="\t", header=None,
                     on_bad_lines="skip", quotechar='"')
    df = df.rename(columns=col_map)

    for field in ITEM_COLS_RP.values():
        if field in df.columns:
            df[field] = df[field].apply(parse_br)
        else:
            df[field] = 0.0

    df = df[df["NE"].astype(str).str.contains("NE", na=False)].copy()
    df["NE_display"] = df["NE"].astype(str).str.extract(r"(NE\d+)").fillna(df["NE"])
    df["Favorecido"] = df["Favorecido"].astype(str).str.strip().str.title()
    return df


# ─────────────────────────────────────────────
# PARSE — SALDO GERAL (mensal)
# ─────────────────────────────────────────────
def parse_saldo(file_bytes):
    """Parse dinâmico: colunas financeiras variam por mês conforme itens disponíveis."""
    import re as _re
    content = file_bytes.decode("latin-1")
    blocks = content.split("Páginas:")
    mensal_rows = []
    all_pi = []

    ITEM_COLS_SG = {
        "15": "Provisao",
        "19": "Credito_Disp",
        "29": "Empenhado",
        "30": "A_Liquidar",
        "31": "Liquidado",
        "32": "Liq_A_Pagar",
        "34": "Pago",
    }

    for block in blocks[1:]:
        lines = block.split("\r\n")
        mes = next((l.split(":")[-1].strip() for l in lines[:4]
                    if "Lançamento" in l or "Lancamento" in l), "")

        # Linha 4 contém os códigos de item: "15", "19", "29"...
        header_line = lines[4] if len(lines) > 4 else ""
        item_codes = _re.findall(r'"(\d{2})"', header_line)

        # 4 colunas fixas: PI, Desc_PI, Nat_Desp, Desc_Nat (índices 0-3)
        col_map = {0: "PI", 1: "Desc_PI", 2: "Nat_Desp", 3: "Desc_Nat"}
        for i, code in enumerate(item_codes):
            if code in ITEM_COLS_SG:
                col_map[4 + i] = ITEM_COLS_SG[code]

        data_lines = [l for l in lines[7:] if l.strip() and not l.startswith(" \t")]
        if not data_lines:
            continue
        try:
            df_tmp = pd.read_csv(StringIO("\r\n".join(data_lines)),
                                 sep="\t", header=None,
                                 on_bad_lines="skip", quotechar='"')
            df_tmp = df_tmp.rename(columns=col_map)

            for field in ITEM_COLS_SG.values():
                if field in df_tmp.columns:
                    df_tmp[field] = df_tmp[field].apply(parse_br)
                else:
                    df_tmp[field] = 0.0

            df_tmp["Mes"] = mes
            all_pi.append(df_tmp)

            mensal_rows.append({
                "Mes":          mes,
                "Provisao":     df_tmp["Provisao"].sum(),
                "Credito_Disp": df_tmp["Credito_Disp"].sum(),
                "Empenhado":    df_tmp["Empenhado"].sum(),
                "Liquidado":    df_tmp["Liquidado"].sum(),
                "Pago":         df_tmp["Pago"].sum(),
            })
        except Exception:
            pass

    df_mensal = pd.DataFrame(mensal_rows)
    df_saldo  = pd.concat(all_pi, ignore_index=True) if all_pi else pd.DataFrame()
    return df_mensal, df_saldo


# ─────────────────────────────────────────────
# CORES PADRÃO
# ─────────────────────────────────────────────
COR_PROVISAO  = "#B5D4F4"
COR_EMPENHADO = "#378ADD"
COR_LIQUIDADO = "#185FA5"
COR_PAGO      = "#0C447C"
COR_RP_PAGO   = "#1D9E75"
COR_RP_SALDO  = "#FAC775"
PALETA_ND     = ["#378ADD", "#185FA5", "#1D9E75", "#D85A30",
                 "#BA7517", "#A32D2D", "#534AB7", "#888780", "#0F6E56"]


# ─────────────────────────────────────────────
# GRÁFICO — FUNIL DE DESPESA
# ─────────────────────────────────────────────
def safe_float(v):
    """Garante que um valor seja float válido, nunca NaN/None."""
    try:
        f = float(v)
        return f if f == f else 0.0  # NaN check
    except Exception:
        return 0.0


def grafico_funil(prov, emp, liq, pago):
    prov, emp, liq, pago = safe_float(prov), safe_float(emp), safe_float(liq), safe_float(pago)
    steps  = ["Provisionado", "Empenhado", "Liquidado", "Pago"]
    values = [prov, emp, liq, pago]
    colors = [COR_PROVISAO, COR_EMPENHADO, COR_LIQUIDADO, COR_PAGO]
    pcts   = [100, num_pct(emp, prov), num_pct(liq, prov), num_pct(pago, prov)]

    fig = go.Figure()
    for s, v, c, p in zip(steps, values, colors, pcts):
        fig.add_trace(go.Bar(
            name=s, x=[s], y=[v],
            marker_color=c,
            text=[f"<b>{fmt_brl(v)}</b><br>{p}%"],
            textposition="outside",
            textfont=dict(size=11),
            hovertemplate=f"<b>{s}</b><br>{fmt_brl(v)}<br>{p}% da provisão<extra></extra>",
        ))
    fig.update_layout(
        barmode="group", showlegend=False,
        height=320, margin=dict(t=50, b=10, l=10, r=10),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.2)", tickformat=",.0f",
                   title=dict(text="R$", font=dict(size=11))),
        xaxis=dict(showgrid=False),
    )
    return fig


# ─────────────────────────────────────────────
# GRÁFICO — EVOLUÇÃO MENSAL
# ─────────────────────────────────────────────
def grafico_evolucao(df_mensal):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Provisão", x=df_mensal["Mes"], y=df_mensal["Provisao"],
        marker_color=COR_PROVISAO, opacity=0.85,
    ))
    fig.add_trace(go.Bar(
        name="Empenhado", x=df_mensal["Mes"], y=df_mensal["Empenhado"],
        marker_color=COR_EMPENHADO,
    ))
    fig.add_trace(go.Bar(
        name="Pago", x=df_mensal["Mes"], y=df_mensal["Pago"],
        marker_color=COR_PAGO,
    ))
    fig.update_layout(
        barmode="group", height=340,
        margin=dict(t=20, b=20, l=10, r=10),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.2)", tickformat=",.0f", title=dict(text="R$")),
        xaxis=dict(showgrid=False),
        hovermode="x unified",
    )
    return fig


# ─────────────────────────────────────────────
# GRÁFICO — BARRAS HORIZONTAIS POR PI
# ─────────────────────────────────────────────
def grafico_pi(df_pi):
    df_plot = df_pi.sort_values("Provisao", ascending=True).tail(10)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Provisão", y=df_plot["PI"], x=df_plot["Provisao"],
        orientation="h", marker_color=COR_PROVISAO, opacity=0.7,
    ))
    fig.add_trace(go.Bar(
        name="Empenhado", y=df_plot["PI"], x=df_plot["Empenhado"],
        orientation="h", marker_color=COR_EMPENHADO,
    ))
    fig.add_trace(go.Bar(
        name="Pago", y=df_plot["PI"], x=df_plot["Pago"],
        orientation="h", marker_color=COR_PAGO,
    ))
    fig.update_layout(
        barmode="overlay", height=max(280, len(df_plot) * 42),
        margin=dict(t=20, b=10, l=10, r=10),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
        xaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.2)", tickformat=",.0f", title=dict(text="R$")),
        yaxis=dict(showgrid=False),
        hovermode="y unified",
    )
    return fig


# ─────────────────────────────────────────────
# GRÁFICO — ROSCA POR ND
# ─────────────────────────────────────────────
def grafico_nd_rosca(df_nd, col="Empenhado"):
    df_plot = df_nd[df_nd[col] > 0].sort_values(col, ascending=False)
    fig = go.Figure(go.Pie(
        labels=df_plot["Desc_Nat"].str[:35],
        values=df_plot[col],
        hole=0.45,
        marker_colors=PALETA_ND,
        textinfo="percent",
        hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(
        height=340, margin=dict(t=20, b=20, l=10, r=10),
        showlegend=True,
        legend=dict(font=dict(size=10), orientation="v", x=1.02),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


# ─────────────────────────────────────────────
# GRÁFICO — BARRAS RP POR ND
# ─────────────────────────────────────────────
def grafico_rp_nd(df_rp_nd):
    df_plot = df_rp_nd[df_rp_nd["RP_Inscrito"] > 0].sort_values("RP_Inscrito", ascending=True).tail(10)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Pago", y=df_plot["Desc_Nat"].str[:30],
        x=df_plot["RP_Pago"], orientation="h", marker_color=COR_RP_PAGO,
    ))
    fig.add_trace(go.Bar(
        name="A pagar", y=df_plot["Desc_Nat"].str[:30],
        x=df_plot["RP_A_Pagar"], orientation="h", marker_color=COR_RP_SALDO,
    ))
    fig.update_layout(
        barmode="stack",
        height=max(260, len(df_plot) * 38),
        margin=dict(t=20, b=10, l=10, r=10),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=1.05),
        xaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.2)", tickformat=",.0f", title=dict(text="R$")),
        yaxis=dict(showgrid=False),
    )
    return fig


# ─────────────────────────────────────────────
# SIDEBAR — UPLOAD E LANÇAMENTO MANUAL
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚓ Execução Financeira")
    st.markdown("**4º Btl Op Lit FN · 2026**")

    # Usuário logado + botão de logout
    col_nip, col_sair = st.columns([2, 1])
    with col_nip:
        st.caption(f"🔒 NIP {st.session_state.usuario_nip}")
    with col_sair:
        if st.button("Sair", use_container_width=True):
            logout()

    st.divider()

    st.markdown("#### 📂 Importar planilhas")
    f_emp = st.file_uploader("Controle de Empenhos", type="csv", key="up_emp")
    f_rp  = st.file_uploader("Restos a Pagar",       type="csv", key="up_rp")
    f_sg  = st.file_uploader("Controle de Saldo Geral", type="csv", key="up_sg")

    if f_emp:
        st.session_state.empenhos = parse_empenhos(f_emp.read())
        st.success(f"✓ {len(st.session_state.empenhos)} empenhos carregados")
    if f_rp:
        st.session_state.restos = parse_restos(f_rp.read())
        st.success(f"✓ {len(st.session_state.restos)} restos carregados")
    if f_sg:
        df_m, df_s = parse_saldo(f_sg.read())
        st.session_state.mensal = df_m
        st.session_state.saldo  = df_s
        st.success(f"✓ {len(df_m)} meses carregados")

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
        pag_in  = st.number_input("Valor pago (R$)",      min_value=0.0, step=0.01)

        if st.button("➕ Incluir empenho", use_container_width=True):
            novo = {
                "NE": ne_in or f"MANUAL{len(st.session_state.lancamentos_manuais)+1:03d}",
                "NE_display": ne_in or "MANUAL",
                "Favorecido": fav_in or "Não informado",
                "PI": pi_in, "Desc_PI": desc_pi,
                "Nat_Desp": nd_in, "Desc_Nat": "",
                "Empenhado": emp_in, "A_Liquidar": emp_in - liq_in,
                "Liquidado": liq_in, "Liq_A_Pagar": liq_in - pag_in,
                "Pago": pag_in,
            }
            st.session_state.lancamentos_manuais.append(novo)
            # Adicionar ao DataFrame de empenhos
            novo_df = pd.DataFrame([novo])
            if st.session_state.empenhos.empty:
                st.session_state.empenhos = novo_df
            else:
                st.session_state.empenhos = pd.concat(
                    [st.session_state.empenhos, novo_df], ignore_index=True
                )
            st.success(f"Empenho {novo['NE_display']} incluído!")
            st.rerun()

    if st.session_state.lancamentos_manuais:
        st.caption(f"📝 {len(st.session_state.lancamentos_manuais)} lançamento(s) manual(is) nesta sessão")

    st.divider()
    st.markdown("#### 🔍 Filtros globais")
    filtro_pi = ""
    filtro_nd = ""
    if not st.session_state.empenhos.empty:
        pis = ["Todos"] + sorted(st.session_state.empenhos["PI"].dropna().unique().tolist())
        filtro_pi = st.selectbox("Programa Interno (PI)", pis)
        nds = ["Todos"] + sorted(st.session_state.empenhos["Nat_Desp"].dropna().unique().tolist())
        filtro_nd = st.selectbox("Natureza de Despesa", nds)

    st.divider()
    st.caption(f"Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")


# ─────────────────────────────────────────────
# DADOS FILTRADOS
# ─────────────────────────────────────────────
df_emp = st.session_state.empenhos.copy()
df_rp  = st.session_state.restos.copy()
df_sg  = st.session_state.saldo.copy()
df_men = st.session_state.mensal.copy()

if not df_emp.empty:
    if filtro_pi and filtro_pi != "Todos":
        df_emp = df_emp[df_emp["PI"] == filtro_pi]
    if filtro_nd and filtro_nd != "Todos":
        df_emp = df_emp[df_emp["Nat_Desp"] == filtro_nd]


# ─────────────────────────────────────────────
# CABEÇALHO PRINCIPAL
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>⚓ Dashboard de Execução Financeira</h1>
  <p>4º Batalhão de Operações Litorâneas de Fuzileiros Navais — Exercício 2026</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ESTADO: SEM DADOS
# ─────────────────────────────────────────────
if df_emp.empty and df_rp.empty:
    st.info(
        "📂 **Nenhum dado carregado.** Use a barra lateral para importar os arquivos CSV "
        "ou lançar empenhos manualmente.",
        icon="ℹ️",
    )
    st.stop()


# ─────────────────────────────────────────────
# CÁLCULOS CONSOLIDADOS
# ─────────────────────────────────────────────
# Usar apenas o último mês do saldo geral (evita somar meses repetidos)
if not df_sg.empty and "Mes" in df_sg.columns:
    _ultimo_mes = df_sg["Mes"].iloc[-1]
    _df_sg_last = df_sg[df_sg["Mes"] == _ultimo_mes]
else:
    _df_sg_last = df_sg

total_prov  = safe_float(_df_sg_last["Provisao"].sum())    if not _df_sg_last.empty else 0
total_cred  = safe_float(_df_sg_last["Credito_Disp"].sum()) if not _df_sg_last.empty else 0
total_emp   = safe_float(df_emp["Empenhado"].sum())  if not df_emp.empty else 0
total_liq   = safe_float(df_emp["Liquidado"].sum())  if not df_emp.empty else 0
total_pago  = safe_float(df_emp["Pago"].sum())       if not df_emp.empty else 0

rp_ins  = safe_float(df_rp["RP_Inscrito"].sum())  if not df_rp.empty else 0
rp_pago = safe_float(df_rp["RP_Pago"].sum())      if not df_rp.empty else 0
rp_apr  = safe_float(df_rp["RP_A_Pagar"].sum())   if not df_rp.empty else 0

tx_emp  = total_emp  / total_prov * 100 if total_prov else 0
tx_exec = total_pago / total_prov * 100 if total_prov else 0
tx_rp   = rp_pago   / rp_ins    * 100  if rp_ins    else 0


def badge_tx(v, lim_ok=60, lim_warn=30):
    if v >= lim_ok:   return "ok",     "bom"
    if v >= lim_warn: return "warn",   "atenção"
    return "danger", "baixo"


# ─────────────────────────────────────────────
# ALERTAS DE STATUS
# ─────────────────────────────────────────────
alertas = []
if tx_emp < 30:
    alertas.append(("warn", f"Taxa de empenho baixa: {tx_emp:.1f}%. Apenas {fmt_brl(total_emp)} empenhados de {fmt_brl(total_prov)} provisionados."))
if rp_apr > 0:
    alertas.append(("info", f"Restos a pagar: {fmt_brl(rp_apr)} ainda pendentes de pagamento ({fmt_pct(rp_apr, rp_ins)} do total inscrito)."))
liq_pend = total_liq - total_pago
if liq_pend > 0:
    alertas.append(("warn", f"Despesas liquidadas a pagar: {fmt_brl(liq_pend)} aguardando pagamento."))

for tipo, msg in alertas:
    cls = "status-warn" if tipo == "warn" else "status-info"
    st.markdown(f'<div class="status-bar {cls}">⚠️ {msg}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ABAS PRINCIPAIS
# ─────────────────────────────────────────────
tabs = st.tabs([
    "📊 Visão Geral",
    "📋 Empenhos 2026",
    "🔄 Restos a Pagar",
    "📁 Por PI",
    "🏷️ Por Natureza de Despesa",
    "📈 Evolução Mensal",
])


# ════════════════════════════════════════════
# ABA 1 — VISÃO GERAL
# ════════════════════════════════════════════
with tabs[0]:
    st.markdown('<div class="section-title">Recursos — Dotação e Disponibilidade</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    bc, bl = badge_tx(tx_emp)
    with c1:
        st.metric("Provisão Recebida", fmt_brl(total_prov), help="Teto de crédito autorizado")
    with c2:
        st.metric("Crédito Disponível", fmt_brl(total_cred), help="Saldo ainda não comprometido")
    with c3:
        st.metric("Taxa de Empenho", f"{tx_emp:.1f}%",
                  delta=f"{bl}", delta_color="normal" if bc == "ok" else "inverse",
                  help="Empenhado / Provisão")
    with c4:
        be, bl2 = badge_tx(tx_exec, 50, 20)
        st.metric("Taxa de Execução", f"{tx_exec:.1f}%",
                  delta=f"{bl2}", delta_color="normal" if be == "ok" else "inverse",
                  help="Pago / Provisão")

    st.markdown('<div class="section-title">Pipeline de Despesa — Ano Corrente 2026</div>', unsafe_allow_html=True)
    st.plotly_chart(grafico_funil(total_prov, total_emp, total_liq, total_pago),
                    use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Fases da despesa (% sobre a fase anterior)**")
        fases = [
            ("Empenhado / Provisionado", total_emp,  total_prov, COR_EMPENHADO),
            ("Liquidado / Empenhado",    total_liq,  total_emp,  COR_LIQUIDADO),
            ("Pago / Liquidado",         total_pago, total_liq,  COR_PAGO),
            ("Pago / Provisionado",      total_pago, total_prov, "#4d7fa6"),
        ]
        for label, a, b, cor in fases:
            p = num_pct(a, b)
            st.markdown(f"""
            <div style="margin-bottom:0.6rem;">
              <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:#6b7a8d;margin-bottom:3px;">
                <span>{label}</span><span><b>{fmt_pct(a,b)}</b></span>
              </div>
              <div style="background:#f0f2f5;border-radius:4px;height:8px;overflow:hidden;">
                <div style="width:{p}%;background:{cor};height:100%;border-radius:4px;"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    with col_b:
        st.markdown("**Restos a pagar — exercícios anteriores**")
        st.metric("RP Inscrito",    fmt_brl(rp_ins))
        st.metric("RP Pago",        fmt_brl(rp_pago))
        st.metric("RP a Pagar",     fmt_brl(rp_apr))
        br, lr = badge_tx(tx_rp, 90, 70)
        st.metric("% Pago dos RP",  f"{tx_rp:.1f}%",
                  delta=lr, delta_color="normal" if br == "ok" else "inverse")


# ════════════════════════════════════════════
# ABA 2 — EMPENHOS 2026
# ════════════════════════════════════════════
with tabs[1]:
    if df_emp.empty:
        st.info("Importe o arquivo de Controle de Empenhos na barra lateral.")
    else:
        st.markdown('<div class="section-title">Empenhos do Exercício 2026</div>', unsafe_allow_html=True)

        # Métricas rápidas
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total de empenhos", len(df_emp))
        c2.metric("Total empenhado",   fmt_brl(df_emp["Empenhado"].sum()))
        c3.metric("Total liquidado",   fmt_brl(df_emp["Liquidado"].sum()))
        c4.metric("Total pago",        fmt_brl(df_emp["Pago"].sum()))

        # Tabela detalhada
        df_show = df_emp[["NE_display", "Favorecido", "PI", "Desc_Nat",
                           "Empenhado", "Liquidado", "Pago"]].copy()

        def situacao(row):
            s, _ = status_empenho(row["Empenhado"], row["Liquidado"], row["Pago"])
            return s

        df_show["Situação"] = df_emp.apply(situacao, axis=1)
        df_show.columns = ["Empenho", "Favorecido", "PI", "Natureza de Despesa",
                           "Empenhado (R$)", "Liquidado (R$)", "Pago (R$)", "Situação"]

        st.dataframe(
            df_show.style.format({
                "Empenhado (R$)": "R$ {:,.2f}",
                "Liquidado (R$)": "R$ {:,.2f}",
                "Pago (R$)":      "R$ {:,.2f}",
            }),
            use_container_width=True,
            height=420,
        )

        # Empenhos pendentes de liquidação
        pend = df_emp[df_emp["A_Liquidar"] > 0.01]
        if not pend.empty:
            st.markdown(f'<div class="section-title">Empenhos Pendentes de Liquidação ({len(pend)})</div>',
                        unsafe_allow_html=True)
            st.dataframe(
                pend[["NE_display", "Favorecido", "Empenhado", "A_Liquidar"]].rename(columns={
                    "NE_display": "Empenho", "A_Liquidar": "A Liquidar (R$)",
                    "Empenhado": "Empenhado (R$)"
                }).style.format({"Empenhado (R$)": "R$ {:,.2f}", "A Liquidar (R$)": "R$ {:,.2f}"}),
                use_container_width=True,
            )


# ════════════════════════════════════════════
# ABA 3 — RESTOS A PAGAR
# ════════════════════════════════════════════
with tabs[2]:
    if df_rp.empty:
        st.info("Importe o arquivo de Restos a Pagar na barra lateral.")
    else:
        st.markdown('<div class="section-title">Restos a Pagar — Exercícios Anteriores</div>',
                    unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("RP Inscrito",    fmt_brl(rp_ins))
        c2.metric("RP Liquidado",   fmt_brl(df_rp["RP_Liquidado"].sum()))
        c3.metric("RP Pago",        fmt_brl(rp_pago))
        c4.metric("RP a Pagar",     fmt_brl(rp_apr))

        df_rp_show = df_rp[["NE_display", "Favorecido", "PI", "Desc_Nat",
                             "RP_Inscrito", "RP_Liquidado", "RP_Pago", "RP_A_Pagar"]].copy()

        def sit_rp(row):
            if row["RP_A_Pagar"] <= 0.01 and row["RP_Pago"] > 0:
                return "Quitado"
            if row["RP_Liquidado"] > 0 and row["RP_A_Pagar"] > 0:
                return "Liq. a pagar"
            if row["RP_A_Pagar"] > 0:
                return "Pendente"
            return "—"

        df_rp_show["Situação"] = df_rp.apply(sit_rp, axis=1)
        df_rp_show.columns = ["Empenho", "Favorecido", "PI", "Natureza",
                              "Inscrito (R$)", "Liquidado (R$)", "Pago (R$)",
                              "A Pagar (R$)", "Situação"]

        st.dataframe(
            df_rp_show.style.format({
                "Inscrito (R$)":  "R$ {:,.2f}",
                "Liquidado (R$)": "R$ {:,.2f}",
                "Pago (R$)":      "R$ {:,.2f}",
                "A Pagar (R$)":   "R$ {:,.2f}",
            }),
            use_container_width=True,
            height=380,
        )

        # Pendências
        pend_rp = df_rp[df_rp["RP_A_Pagar"] > 0.01].sort_values("RP_A_Pagar", ascending=False)
        if not pend_rp.empty:
            st.markdown(f'<div class="section-title">Pendências de RP a Quitar ({len(pend_rp)} empenhos · {fmt_brl(pend_rp["RP_A_Pagar"].sum())})</div>',
                        unsafe_allow_html=True)
            st.dataframe(
                pend_rp[["NE_display", "Favorecido", "RP_Inscrito", "RP_A_Pagar"]].rename(columns={
                    "NE_display": "Empenho", "RP_Inscrito": "Inscrito (R$)", "RP_A_Pagar": "A Pagar (R$)"
                }).style.format({"Inscrito (R$)": "R$ {:,.2f}", "A Pagar (R$)": "R$ {:,.2f}"}),
                use_container_width=True,
            )


# ════════════════════════════════════════════
# ABA 4 — POR PI
# ════════════════════════════════════════════
with tabs[3]:
    if df_emp.empty and df_sg.empty:
        st.info("Importe os arquivos de Empenhos e/ou Saldo Geral na barra lateral.")
    else:
        st.markdown('<div class="section-title">Execução por Programa Interno (PI)</div>',
                    unsafe_allow_html=True)

        # Consolidar por PI usando saldo geral + empenhos
        if not df_sg.empty:
            ultimo_mes = df_sg["Mes"].iloc[-1] if "Mes" in df_sg.columns else ""
            _sg_last = df_sg[df_sg["Mes"] == ultimo_mes].copy()
            _sg_last["PI"] = _sg_last["PI"].astype(str).str.strip()
            df_pi = _sg_last.groupby(["PI", "Desc_PI"]).agg(
                Provisao=("Provisao", "sum"),
                Credito_Disp=("Credito_Disp", "sum"),
                Empenhado=("Empenhado", "sum"),
                Pago=("Pago", "sum"),
            ).reset_index()
        else:
            _emp_copy = df_emp.copy()
            _emp_copy["PI"] = _emp_copy["PI"].astype(str).str.strip()
            df_pi = _emp_copy.groupby(["PI", "Desc_PI"]).agg(
                Empenhado=("Empenhado", "sum"),
                Liquidado=("Liquidado", "sum"),
                Pago=("Pago", "sum"),
            ).reset_index()
            df_pi["Provisao"] = df_pi["Empenhado"]
            df_pi["Credito_Disp"] = 0

        # Merge com liquidado dos empenhos — forcar tipos compativeis
        if not df_emp.empty:
            _emp_merge = df_emp.copy()
            _emp_merge["PI"] = _emp_merge["PI"].astype(str).str.strip()
            df_pi["PI"] = df_pi["PI"].astype(str).str.strip()
            liq_pi = _emp_merge.groupby("PI").agg(Liquidado=("Liquidado", "sum")).reset_index()
            if "Liquidado" in df_pi.columns:
                df_pi = df_pi.drop(columns=["Liquidado"])
            df_pi = df_pi.merge(liq_pi, on="PI", how="left")
            df_pi["Liquidado"] = df_pi["Liquidado"].fillna(0)

        sub1, sub2 = st.tabs(["Empenhos 2026", "Restos a Pagar"])

        with sub1:
            # Cards de PI
            for _, row in df_pi.sort_values("Provisao", ascending=False).iterrows():
                prov = row["Provisao"]
                emp  = row.get("Empenhado", 0)
                liq  = row.get("Liquidado", 0)
                pago = row.get("Pago", 0)
                cred = row.get("Credito_Disp", 0)
                tx   = num_pct(emp, prov)

                if prov <= 0 and emp <= 0:
                    continue

                bs, bl = badge_tx(tx)
                with st.container():
                    st.markdown(f"""
                    <div class="pi-card">
                      <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:6px;">
                        <div>
                          <div class="pi-code">{row['PI']}</div>
                          <div class="pi-name">{str(row.get('Desc_PI','')).title()}</div>
                          <div class="pi-prov">Provisão: <b>{fmt_brl(prov)}</b> &nbsp;·&nbsp; Crédito disp.: <b>{fmt_brl(cred)}</b></div>
                        </div>
                        {badge_html(bl, bs)}
                      </div>
                      <div style="margin-top:10px;">
                        <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;font-size:0.78rem;">
                          <span style="width:90px;color:#6b7a8d;">Empenhado</span>
                          <div style="flex:1;background:#f0f2f5;border-radius:3px;height:7px;overflow:hidden;">
                            <div style="width:{num_pct(emp,prov)}%;background:{COR_EMPENHADO};height:100%;border-radius:3px;"></div>
                          </div>
                          <span style="width:60px;text-align:right;color:#444;">{fmt_pct(emp,prov)}</span>
                          <span style="width:90px;text-align:right;color:#888;font-size:0.72rem;">{fmt_brl(emp)}</span>
                        </div>
                        <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;font-size:0.78rem;">
                          <span style="width:90px;color:#6b7a8d;">Liquidado</span>
                          <div style="flex:1;background:#f0f2f5;border-radius:3px;height:7px;overflow:hidden;">
                            <div style="width:{num_pct(liq,emp)}%;background:{COR_LIQUIDADO};height:100%;border-radius:3px;"></div>
                          </div>
                          <span style="width:60px;text-align:right;color:#444;">{fmt_pct(liq,emp)}</span>
                          <span style="width:90px;text-align:right;color:#888;font-size:0.72rem;">{fmt_brl(liq)}</span>
                        </div>
                        <div style="display:flex;align-items:center;gap:6px;font-size:0.78rem;">
                          <span style="width:90px;color:#6b7a8d;">Pago</span>
                          <div style="flex:1;background:#f0f2f5;border-radius:3px;height:7px;overflow:hidden;">
                            <div style="width:{num_pct(pago,emp)}%;background:{COR_PAGO};height:100%;border-radius:3px;"></div>
                          </div>
                          <span style="width:60px;text-align:right;color:#444;">{fmt_pct(pago,emp)}</span>
                          <span style="width:90px;text-align:right;color:#888;font-size:0.72rem;">{fmt_brl(pago)}</span>
                        </div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown('<div class="section-title">Comparativo Gráfico por PI</div>', unsafe_allow_html=True)
            st.plotly_chart(grafico_pi(df_pi), use_container_width=True)

        with sub2:
            if df_rp.empty:
                st.info("Importe o arquivo de Restos a Pagar.")
            else:
                df_rp_pi = df_rp.groupby(["PI", "Desc_PI"]).agg(
                    RP_Inscrito=("RP_Inscrito", "sum"),
                    RP_Pago=("RP_Pago", "sum"),
                    RP_A_Pagar=("RP_A_Pagar", "sum"),
                ).reset_index()

                for _, row in df_rp_pi.sort_values("RP_Inscrito", ascending=False).iterrows():
                    ins  = row["RP_Inscrito"]
                    pago = row["RP_Pago"]
                    apr  = row["RP_A_Pagar"]
                    total = max(ins, pago + apr)
                    if total <= 0:
                        continue
                    quitado = apr <= 0.01
                    bs = "ok" if quitado else ("info" if num_pct(pago, total) >= 80 else "warn")
                    bl = "Quitado" if quitado else fmt_pct(pago, total) + " pago"

                    st.markdown(f"""
                    <div class="pi-card">
                      <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:6px;">
                        <div>
                          <div class="pi-code">{row['PI']}</div>
                          <div class="pi-name">{str(row.get('Desc_PI','')).title()}</div>
                        </div>
                        {badge_html(bl, bs)}
                      </div>
                      <div style="margin-top:10px;">
                        <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;font-size:0.78rem;">
                          <span style="width:90px;color:#6b7a8d;">Pago</span>
                          <div style="flex:1;background:#f0f2f5;border-radius:3px;height:7px;overflow:hidden;">
                            <div style="width:{num_pct(pago,total)}%;background:{COR_RP_PAGO};height:100%;border-radius:3px;"></div>
                          </div>
                          <span style="width:60px;text-align:right;color:#444;">{fmt_pct(pago,total)}</span>
                          <span style="width:90px;text-align:right;color:#888;font-size:0.72rem;">{fmt_brl(pago)}</span>
                        </div>
                        <div style="display:flex;align-items:center;gap:6px;font-size:0.78rem;">
                          <span style="width:90px;color:#6b7a8d;">A pagar</span>
                          <div style="flex:1;background:#f0f2f5;border-radius:3px;height:7px;overflow:hidden;">
                            <div style="width:{num_pct(apr,total)}%;background:{COR_RP_SALDO};height:100%;border-radius:3px;"></div>
                          </div>
                          <span style="width:60px;text-align:right;color:#444;">{fmt_pct(apr,total)}</span>
                          <span style="width:90px;text-align:right;color:#888;font-size:0.72rem;">{fmt_brl(apr)}</span>
                        </div>
                      </div>
                      <div style="display:flex;gap:16px;margin-top:10px;">
                        <span style="font-size:0.75rem;color:#6b7a8d;">Inscrito: <b>{fmt_brl(ins)}</b></span>
                        <span style="font-size:0.75rem;color:#6b7a8d;">Pago: <b>{fmt_brl(pago)}</b></span>
                        <span style="font-size:0.75rem;color:#6b7a8d;">Saldo: <b style="color:{'#856404' if apr>0 else '#155724'};">{fmt_brl(apr)}</b></span>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)


# ════════════════════════════════════════════
# ABA 5 — POR NATUREZA DE DESPESA
# ════════════════════════════════════════════
with tabs[4]:
    if df_emp.empty and df_rp.empty:
        st.info("Importe os arquivos CSV na barra lateral.")
    else:
        sub_nd1, sub_nd2 = st.tabs(["Empenhos 2026", "Restos a Pagar"])

        with sub_nd1:
            if df_emp.empty:
                st.info("Importe o arquivo de Empenhos.")
            else:
                df_nd = df_emp.groupby(["Nat_Desp", "Desc_Nat"]).agg(
                    Empenhado=("Empenhado", "sum"),
                    Liquidado=("Liquidado", "sum"),
                    Pago=("Pago", "sum"),
                ).reset_index().sort_values("Empenhado", ascending=False)

                st.markdown('<div class="section-title">Execução por Natureza de Despesa</div>',
                            unsafe_allow_html=True)

                col_tab, col_chart = st.columns([1, 1])

                with col_tab:
                    df_nd_show = df_nd.copy()
                    df_nd_show["% Exec."] = df_nd_show.apply(
                        lambda r: fmt_pct(r["Pago"], r["Empenhado"]), axis=1
                    )
                    df_nd_show = df_nd_show.rename(columns={
                        "Nat_Desp": "Cód. ND", "Desc_Nat": "Natureza de Despesa",
                        "Empenhado": "Empenhado (R$)", "Liquidado": "Liquidado (R$)", "Pago": "Pago (R$)"
                    })
                    st.dataframe(
                        df_nd_show.style.format({
                            "Empenhado (R$)": "R$ {:,.2f}",
                            "Liquidado (R$)": "R$ {:,.2f}",
                            "Pago (R$)":      "R$ {:,.2f}",
                        }),
                        use_container_width=True,
                        height=380,
                    )

                with col_chart:
                    st.plotly_chart(grafico_nd_rosca(df_nd), use_container_width=True)

                # Barras horizontais
                st.markdown('<div class="section-title">Pipeline por Natureza de Despesa</div>',
                            unsafe_allow_html=True)
                max_emp = df_nd["Empenhado"].max()
                for _, row in df_nd.iterrows():
                    nd_name = str(row["Desc_Nat"])[:45]
                    emp = row["Empenhado"]
                    liq = row["Liquidado"]
                    pago = row["Pago"]
                    st.markdown(f"""
                    <div style="margin-bottom:0.9rem;">
                      <div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:3px;">
                        <span style="color:#0a2342;font-weight:600;">{nd_name}</span>
                        <span style="color:#6b7a8d;font-size:0.72rem;">{row['Nat_Desp']}</span>
                      </div>
                      <div style="display:flex;gap:4px;margin-bottom:2px;align-items:center;">
                        <span style="width:72px;font-size:0.7rem;color:#6b7a8d;">Emp.</span>
                        <div style="flex:1;background:#f0f2f5;border-radius:3px;height:6px;overflow:hidden;">
                          <div style="width:{num_pct(emp,max_emp)}%;background:{COR_EMPENHADO};height:100%;"></div>
                        </div>
                        <span style="width:80px;text-align:right;font-size:0.72rem;color:#444;">{fmt_brl(emp)}</span>
                      </div>
                      <div style="display:flex;gap:4px;margin-bottom:2px;align-items:center;">
                        <span style="width:72px;font-size:0.7rem;color:#6b7a8d;">Liq.</span>
                        <div style="flex:1;background:#f0f2f5;border-radius:3px;height:6px;overflow:hidden;">
                          <div style="width:{num_pct(liq,emp)}%;background:{COR_LIQUIDADO};height:100%;"></div>
                        </div>
                        <span style="width:80px;text-align:right;font-size:0.72rem;color:#444;">{fmt_brl(liq)}</span>
                      </div>
                      <div style="display:flex;gap:4px;align-items:center;">
                        <span style="width:72px;font-size:0.7rem;color:#6b7a8d;">Pago</span>
                        <div style="flex:1;background:#f0f2f5;border-radius:3px;height:6px;overflow:hidden;">
                          <div style="width:{num_pct(pago,emp)}%;background:{COR_PAGO};height:100%;"></div>
                        </div>
                        <span style="width:80px;text-align:right;font-size:0.72rem;color:#444;">{fmt_brl(pago)}</span>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

        with sub_nd2:
            if df_rp.empty:
                st.info("Importe o arquivo de Restos a Pagar.")
            else:
                df_rp_nd = df_rp.groupby(["Nat_Desp", "Desc_Nat"]).agg(
                    RP_Inscrito=("RP_Inscrito", "sum"),
                    RP_Pago=("RP_Pago", "sum"),
                    RP_A_Pagar=("RP_A_Pagar", "sum"),
                ).reset_index().sort_values("RP_Inscrito", ascending=False)

                col_t, col_g = st.columns([1, 1])
                with col_t:
                    df_rp_nd_show = df_rp_nd.rename(columns={
                        "Nat_Desp": "Cód. ND", "Desc_Nat": "Natureza",
                        "RP_Inscrito": "Inscrito (R$)", "RP_Pago": "Pago (R$)",
                        "RP_A_Pagar": "A Pagar (R$)"
                    })
                    df_rp_nd_show["% Pago"] = df_rp_nd.apply(
                        lambda r: fmt_pct(r["RP_Pago"], r["RP_Inscrito"]), axis=1
                    )
                    st.dataframe(
                        df_rp_nd_show.style.format({
                            "Inscrito (R$)": "R$ {:,.2f}",
                            "Pago (R$)":     "R$ {:,.2f}",
                            "A Pagar (R$)":  "R$ {:,.2f}",
                        }),
                        use_container_width=True,
                        height=380,
                    )
                with col_g:
                    st.plotly_chart(grafico_rp_nd(df_rp_nd), use_container_width=True)


# ════════════════════════════════════════════
# ABA 6 — EVOLUÇÃO MENSAL
# ════════════════════════════════════════════
with tabs[5]:
    if df_men.empty:
        st.info("Importe o arquivo de Controle de Saldo Geral para ver a evolução mensal.")
    else:
        st.markdown('<div class="section-title">Evolução Mensal da Execução — 2026</div>',
                    unsafe_allow_html=True)
        st.plotly_chart(grafico_evolucao(df_men), use_container_width=True)

        # Tabela resumo mensal
        st.markdown('<div class="section-title">Resumo por Mês</div>', unsafe_allow_html=True)
        df_men_show = df_men.copy()
        for col in ["Provisao", "Credito_Disp", "Empenhado", "Liquidado", "Pago"]:
            if col in df_men_show.columns:
                df_men_show[col] = df_men_show[col].apply(fmt_brl)
        df_men_show.columns = [c.replace("_", " ") for c in df_men_show.columns]
        st.dataframe(df_men_show, use_container_width=True)

        # Taxa de execução mensal
        if "Provisao" in df_men.columns and "Pago" in df_men.columns:
            st.markdown('<div class="section-title">Taxa de Execução por Mês (Pago / Provisão)</div>',
                        unsafe_allow_html=True)
            df_tx = df_men.copy()
            df_tx["tx_exec"] = df_tx.apply(
                lambda r: round(r["Pago"] / r["Provisao"] * 100, 2) if r["Provisao"] else 0, axis=1
            )
            fig_tx = go.Figure(go.Scatter(
                x=df_tx["Mes"], y=df_tx["tx_exec"],
                mode="lines+markers+text",
                text=[f"{v:.1f}%" for v in df_tx["tx_exec"]],
                textposition="top center",
                line=dict(color=COR_PAGO, width=2.5),
                marker=dict(size=8, color=COR_PAGO),
                fill="tozeroy", fillcolor="rgba(12,68,124,0.08)",
            ))
            fig_tx.update_layout(
                height=260, margin=dict(t=20, b=20, l=10, r=10),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.2)",
                           ticksuffix="%", title="% executado"),
                xaxis=dict(showgrid=False),
            )
            st.plotly_chart(fig_tx, use_container_width=True)
