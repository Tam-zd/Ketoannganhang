import re

import streamlit as st
from dateutil.relativedelta import relativedelta
import pandas as pd
import plotly.graph_objects as go

# ============================================================
# CẤU HÌNH TRANG
# ============================================================

st.set_page_config(
    page_title="Tính tiền gửi tiết kiệm",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# THEME SYSTEM — Light / Dark qua CSS custom properties
# ============================================================

if "theme" not in st.session_state:
    st.session_state.theme = "light"

THEMES = {
    "light": dict(
        app_bg="linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%)",
        text="#0F172A", muted="#64748B", heading="#0B192C",
        navy="#0B192C", sapphire="#1E3E62", emerald="#00D26A",
        crimson="#FF4D4D", amber="#FFB020",
        panel_bg="rgba(255,255,255,0.68)", panel_border="rgba(255,255,255,0.6)",
        panel_shadow1="rgba(163,177,198,0.35)", panel_shadow2="rgba(255,255,255,0.65)",
        card_bg="rgba(255,255,255,0.78)",
        input_bg="#FFFFFF", input_text="#0F172A", input_border="rgba(15,23,42,0.16)",
        placeholder="#94A3B8",
        table_bg="#FFFFFF", table_border="rgba(15,23,42,0.08)", table_head_bg="#F1F5F9",
        table_row_alt="#F8FAFC",
        grid_line="rgba(11,25,44,0.08)",
        slider_track="rgba(30,62,98,0.14)",
        chip_bg="rgba(255,255,255,0.8)",
        expander_bg="rgba(255,255,255,0.65)",
        color_scheme="light",
    ),
    "dark": dict(
        app_bg="linear-gradient(135deg, #0A0F1C 0%, #111A2E 100%)",
        text="#E2E8F0", muted="#94A3B8", heading="#F1F5F9",
        navy="#0B192C", sapphire="#4C86C6", emerald="#22E88A",
        crimson="#FF6B6B", amber="#FFC24B",
        panel_bg="rgba(19,26,46,0.72)", panel_border="rgba(255,255,255,0.08)",
        panel_shadow1="rgba(0,0,0,0.5)", panel_shadow2="rgba(255,255,255,0.03)",
        card_bg="rgba(24,32,54,0.85)",
        input_bg="#1B2438", input_text="#E2E8F0", input_border="rgba(255,255,255,0.14)",
        placeholder="#64748B",
        table_bg="#151E33", table_border="rgba(255,255,255,0.08)", table_head_bg="#1E2A45",
        table_row_alt="#1A2438",
        grid_line="rgba(255,255,255,0.08)",
        slider_track="rgba(255,255,255,0.12)",
        chip_bg="rgba(27,36,56,0.85)",
        expander_bg="rgba(19,26,46,0.6)",
        color_scheme="dark",
    ),
}

TH = THEMES[st.session_state.theme]

ICONS = {
    "wallet": '<path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"/><path d="M3 5v14a2 2 0 0 0 2 2h16v-5"/><path d="M18 12a2 2 0 0 0 0 4h4v-4Z"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
    "trending": '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
    "banknote": '<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/>',
    "repeat": '<polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/>',
    "check": '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
}


def svg_icon(name, size=20):
    return f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>'


def build_css(th: dict) -> str:
    return f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], .stApp, p, span, div, label {{
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif !important;
    }}
    [data-testid="stIconMaterial"], span[data-testid="stIconMaterial"],
    .material-symbols-rounded, .material-symbols-outlined, .material-icons,
    [class*="material-symbols"] {{
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
    }}

    .stApp {{ background: {th['app_bg']}; color: {th['text']}; }}
    #MainMenu, footer {{ visibility: hidden; }}

    /* ---- Chữ mặc định toàn app ---- */
    .stApp, .stApp p, .stApp span, .stApp label, .stApp li,
    .stMarkdown, .stCaption, [data-testid="stMarkdownContainer"] {{
        color: {th['text']};
    }}
    h1, h2, h3, h4, h5, h6 {{ color: {th['heading']} !important; }}
    .stCaption, [data-testid="stCaptionContainer"] {{ color: {th['muted']} !important; }}

    /* ---- Panels (container border=True) ---- */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        border-radius: 22px !important;
        border: 1px solid {th['panel_border']} !important;
        background: {th['panel_bg']} !important;
        backdrop-filter: blur(14px);
        box-shadow: 10px 10px 26px {th['panel_shadow1']}, -10px -10px 26px {th['panel_shadow2']};
    }}

    .panel-title {{
        font-size: 15.5px; font-weight: 800; color: {th['heading']};
        display: flex; align-items: center; gap: 8px;
        margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.4px;
    }}
    .panel-title .pt-icon {{
        width: 26px; height: 26px; border-radius: 8px;
        background: linear-gradient(135deg, {th['sapphire']}, {th['navy']});
        color: white; display: flex; align-items: center; justify-content: center;
    }}

    /* ---- Inputs: text_input, number_input, selectbox, textarea ---- */
    .stTextInput input, .stNumberInput input,
    .stSelectbox div[data-baseweb="select"] > div, textarea {{
        background: {th['input_bg']} !important;
        color: {th['input_text']} !important;
        border: 1px solid {th['input_border']} !important;
        border-radius: 10px !important;
    }}
    .stTextInput input::placeholder, .stNumberInput input::placeholder {{
        color: {th['placeholder']} !important;
    }}
    .stSelectbox div[data-baseweb="select"] span {{ color: {th['input_text']} !important; }}
    ul[data-baseweb="menu"] {{ background: {th['input_bg']} !important; }}
    ul[data-baseweb="menu"] li {{ color: {th['input_text']} !important; }}
    ul[data-baseweb="menu"] li:hover {{ background: {th['slider_track']} !important; }}

    /* ---- Slider ---- */
    div[data-testid="stSlider"] [data-baseweb="slider"] > div > div {{
        background: {th['slider_track']} !important;
    }}
    div[data-testid="stSlider"] [role="slider"] {{
        background-color: {th['emerald']} !important;
        border-color: {th['emerald']} !important;
    }}
    div[data-testid="stSliderTickBarMin"], div[data-testid="stSliderTickBarMax"],
    div[data-testid="stThumbValue"] {{ color: {th['muted']} !important; }}

    /* ---- Radio (segmented control) ---- */
    div[role="radiogroup"] label {{ color: {th['text']} !important; }}
    .st-key-toggle_method div[role="radiogroup"] {{
        background: {th['slider_track']}; padding: 5px; border-radius: 14px; gap: 4px;
    }}
    .st-key-toggle_method label {{ border-radius: 10px !important; padding: 6px 10px !important; font-weight: 600 !important; }}

    /* ---- Quick-select chips ---- */
    .st-key-quick_chips .stButton>button, .st-key-adj_chips .stButton>button {{
        border-radius: 999px !important;
        border: 1px solid {th['input_border']} !important;
        background: {th['chip_bg']} !important;
        color: {th['sapphire']} !important; font-weight: 700 !important; font-size: 12.5px !important;
        box-shadow: 3px 3px 8px {th['panel_shadow1']}, -3px -3px 8px {th['panel_shadow2']} !important;
        padding: 2px 4px !important;
    }}
    .st-key-quick_chips .stButton>button:hover, .st-key-adj_chips .stButton>button:hover {{
        border-color: {th['emerald']} !important; color: {th['emerald']} !important;
    }}

    /* ---- Nút chính ---- */
    .st-key-calc_btn .stButton>button {{
        background: linear-gradient(135deg, {th['navy']} 0%, {th['sapphire']} 50%, #146356 100%) !important;
        background-size: 200% 200% !important;
        color: white !important; border: none !important; font-weight: 800 !important;
        border-radius: 14px !important; padding: 12px !important; font-size: 15px !important;
        box-shadow: 0 10px 24px rgba(11,25,44,0.3) !important;
        transition: background-position 0.5s ease, transform 0.2s ease !important;
    }}
    .st-key-calc_btn .stButton>button:hover {{ background-position: 100% 50% !important; transform: translateY(-2px) !important; }}
    .st-key-reset_btn .stButton>button, .st-key-theme_btn .stButton>button {{
        border-radius: 14px !important; font-weight: 700 !important;
        background: {th['chip_bg']} !important; color: {th['sapphire']} !important;
        border: 1px solid {th['input_border']} !important;
    }}
    .stButton>button {{ color: {th['sapphire']}; }}
    .st-key-calc_btn .stButton>button p {{ color: white !important; }}

    /* ---- Tabs ---- */
    div[data-testid="stTabs"] button p {{ color: {th['muted']}; font-weight: 600; }}
    div[data-testid="stTabs"] button[aria-selected="true"] p {{ color: {th['sapphire']}; font-weight: 800; }}
    div[data-testid="stTabs"] div[data-baseweb="tab-highlight"] {{ background-color: {th['emerald']} !important; }}
    div[data-testid="stTabs"] div[data-baseweb="tab-border"] {{ background-color: {th['input_border']} !important; }}

    /* ---- Expander ---- */
    div[data-testid="stExpander"] {{
        background: {th['expander_bg']} !important; border-radius: 16px !important;
        border: 1px solid {th['panel_border']} !important;
    }}
    div[data-testid="stExpander"] summary {{ color: {th['heading']} !important; font-weight: 700; }}
    div[data-testid="stExpander"] p, div[data-testid="stExpander"] li {{ color: {th['text']} !important; }}

    /* ---- Alert boxes (info/success/warning/error) ---- */
    div[data-testid="stAlert"] {{ border-radius: 14px !important; }}
    div[data-testid="stAlert"] p {{ color: {th['text']} !important; }}

    hr {{ opacity: 0.15; border-color: {th['input_border']}; }}

    /* ================= HERO BANNER ================= */
    .hero-banner {{
        position: relative;
        background: linear-gradient(120deg, {th['navy']} 0%, {th['sapphire']} 60%, #24507F 100%);
        border-radius: 24px; padding: 22px 30px 18px 30px; margin-bottom: 20px;
        overflow: hidden; box-shadow: 0 20px 45px rgba(11, 25, 44, 0.35);
    }}
    .hero-top {{ display: flex; align-items: center; justify-content: space-between; position: relative; z-index: 2; }}
    .hero-badge {{
        display: inline-flex; align-items: center; gap: 6px;
        background: rgba(0, 210, 106, 0.15); border: 1px solid rgba(0,210,106,0.4);
        color: {th['emerald']}; padding: 5px 14px; border-radius: 999px;
        font-size: 12.5px; font-weight: 700; letter-spacing: 0.3px;
    }}
    .hero-glow-icon {{
        width: 48px; height: 48px; border-radius: 16px;
        background: radial-gradient(circle at 30% 30%, rgba(0,210,106,0.35), rgba(30,62,98,0.6));
        display: flex; align-items: center; justify-content: center;
        box-shadow: 0 0 24px rgba(0,210,106,0.45), inset 0 0 12px rgba(255,255,255,0.15);
        color: {th['emerald']};
    }}
    .hero-title {{ font-size: 26px; font-weight: 800; color: #FFFFFF !important; margin: 12px 0 2px 0; position: relative; z-index: 2; letter-spacing: -0.3px; }}
    .hero-sub {{ color: rgba(255,255,255,0.68) !important; font-size: 13.5px; position: relative; z-index: 2; }}
    .ticker-wrap {{ margin-top: 14px; overflow: hidden; position: relative; z-index: 2; border-top: 1px solid rgba(255,255,255,0.12); padding-top: 10px; }}
    .ticker-track {{ display: flex; gap: 34px; white-space: nowrap; animation: ticker-scroll 18s linear infinite; }}
    @keyframes ticker-scroll {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-50%); }} }}
    .ticker-item {{ color: rgba(255,255,255,0.85) !important; font-size: 12.5px; font-weight: 600; display: inline-flex; align-items: center; gap: 6px; }}
    .ticker-item .dot {{ width: 6px; height: 6px; border-radius: 50%; background: {th['emerald']}; box-shadow: 0 0 8px {th['emerald']}; }}
    .ticker-item.warn .dot {{ background: {th['crimson']}; box-shadow: 0 0 8px {th['crimson']}; }}
    .ticker-item.info .dot {{ background: {th['amber']}; box-shadow: 0 0 8px {th['amber']}; }}

    /* ================= KPI CARDS ================= */
    .kpi-card {{
        position: relative; overflow: hidden; border-radius: 20px; padding: 18px 18px 16px 18px;
        background: {th['card_bg']}; border: 1px solid {th['panel_border']};
        box-shadow: 8px 8px 18px {th['panel_shadow1']}, -8px -8px 18px {th['panel_shadow2']};
        transition: transform 0.25s ease; --accent: {th['navy']}; height: 100%;
    }}
    .kpi-card:hover {{ transform: translateY(-4px); }}
    .kpi-card .kpi-bg-icon {{ position: absolute; top: -10px; right: -6px; opacity: 0.10; color: var(--accent); transform: scale(2.6); }}
    .kpi-card .kpi-label {{
        font-size: 12px; font-weight: 700; color: {th['muted']} !important;
        text-transform: uppercase; letter-spacing: 0.4px; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;
    }}
    .kpi-card .kpi-label .ic {{ color: var(--accent); }}
    .kpi-card .kpi-value {{ font-size: 22px; font-weight: 800; color: {th['heading']} !important; line-height: 1.15; position: relative; z-index: 2; }}
    .kpi-card .kpi-note {{ margin-top: 9px; position: relative; z-index: 2; }}
    .kpi-chip {{ display: inline-flex; align-items: center; gap: 5px; font-size: 11.5px; font-weight: 700; padding: 3px 10px; border-radius: 999px; }}
    .kpi-chip.pos {{ background: rgba(0,210,106,0.16); color: {th['emerald']}; }}
    .kpi-chip.neg {{ background: rgba(255,77,77,0.16); color: {th['crimson']}; }}
    .kpi-chip.warn {{ background: rgba(255,176,32,0.18); color: {th['amber']}; }}
    .kpi-navy {{ --accent: {th['sapphire']}; }}
    .kpi-emerald {{ --accent: {th['emerald']}; }}
    .kpi-crimson {{ --accent: {th['crimson']}; }}
    .kpi-amber {{ --accent: {th['amber']}; }}

    /* ================= RESULT HERO ================= */
    .result-hero {{
        border-radius: 22px; padding: 24px 26px; color: white !important; position: relative; overflow: hidden;
        background: linear-gradient(135deg, {th['navy']} 0%, {th['sapphire']} 100%);
        box-shadow: 0 18px 34px rgba(11,25,44,0.3);
    }}
    .result-hero.crimson {{ background: linear-gradient(135deg, #7A1414 0%, {th['crimson']} 100%); }}
    .result-hero.amber {{ background: linear-gradient(135deg, #7A4B00 0%, {th['amber']} 100%); }}
    .result-hero * {{ color: white !important; }}
    .result-hero .rh-label {{ font-size: 13px; letter-spacing: 0.4px; opacity: 0.85; font-weight: 700; text-transform: uppercase; }}
    .result-hero .rh-value {{ font-size: 32px; font-weight: 800; margin: 6px 0 12px 0; }}
    .result-hero .rh-detail {{ font-size: 13.5px; opacity: 0.92; line-height: 1.8; }}

    /* ================= PROGRESS BAR ================= */
    .progress-labels {{ display: flex; justify-content: space-between; font-size: 12.5px; font-weight: 700; color: {th['muted']} !important; margin-bottom: 6px; }}
    .progress-track {{
        height: 12px; border-radius: 999px; background: {th['slider_track']};
        box-shadow: inset 3px 3px 6px {th['panel_shadow1']}, inset -3px -3px 6px {th['panel_shadow2']}; overflow: hidden;
    }}
    .progress-fill {{
        height: 100%; border-radius: 999px;
        background: linear-gradient(90deg, {th['sapphire']}, {th['emerald']});
        box-shadow: 0 0 10px rgba(0,210,106,0.5); transition: width 0.4s ease;
    }}

    /* ================= BATTLE CARDS ================= */
    .battle-wrap {{ display: flex; align-items: stretch; gap: 14px; }}
    .battle-card {{
        flex: 1; border-radius: 20px; padding: 20px; position: relative;
        background: {th['card_bg']}; border: 1.5px solid {th['panel_border']};
        box-shadow: 8px 8px 18px {th['panel_shadow1']}, -8px -8px 18px {th['panel_shadow2']};
    }}
    .battle-card.winner {{ border-color: {th['emerald']}; box-shadow: 0 0 0 3px rgba(0,210,106,0.18); }}
    .battle-card .bc-tag {{ font-size: 11.5px; font-weight: 800; text-transform: uppercase; color: {th['muted']} !important; }}
    .battle-card .bc-title {{ font-size: 15.5px; font-weight: 800; color: {th['heading']} !important; margin: 4px 0 12px 0; }}
    .battle-card .bc-value {{ font-size: 23px; font-weight: 800; color: {th['heading']} !important; }}
    .battle-card .bc-line {{ font-size: 12.5px; color: {th['muted']} !important; margin-top: 4px; }}
    .battle-vs {{
        display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 13px; color: white !important;
        background: linear-gradient(135deg, {th['navy']}, {th['sapphire']}); width: 40px; height: 40px; border-radius: 50%;
        box-shadow: 0 6px 14px rgba(11,25,44,0.3); align-self: center; flex-shrink: 0;
    }}
    .winner-crown {{ position: absolute; top: -10px; right: 16px; font-size: 20px; }}
    .verdict-box {{
        margin-top: 14px; padding: 14px 16px; border-radius: 14px;
        background: rgba(0,210,106,0.10); border: 1px solid rgba(0,210,106,0.3);
        color: {th['emerald']} !important; font-size: 13.5px; font-weight: 600; line-height: 1.6;
    }}
    .verdict-box.neg {{ background: rgba(255,77,77,0.10); border-color: rgba(255,77,77,0.3); color: {th['crimson']} !important; }}
    .verdict-box b {{ color: inherit !important; }}

    /* ================= BADGES ================= */
    .badge-pill {{ display: inline-flex; align-items: center; gap: 6px; padding: 5px 14px; border-radius: 999px; font-size: 12.5px; font-weight: 700; margin-bottom: 10px; }}
    .badge-pill.emerald {{ background: rgba(0,210,106,0.16); color: {th['emerald']} !important; }}
    .badge-pill.crimson {{ background: rgba(255,77,77,0.16); color: {th['crimson']} !important; }}
    .badge-pill.amber {{ background: rgba(255,176,32,0.2); color: {th['amber']} !important; }}

    /* ================= BẢNG DỮ LIỆU DẠNG HTML TỰ VẼ ================= */
    .bank-table-wrap {{ overflow-x: auto; border-radius: 14px; border: 1px solid {th['table_border']}; }}
    table.bank-table {{ width: 100%; border-collapse: collapse; background: {th['table_bg']}; font-size: 13px; }}
    table.bank-table thead th {{
        background: {th['table_head_bg']}; color: {th['heading']} !important; font-weight: 700;
        text-align: left; padding: 10px 14px; border-bottom: 2px solid {th['table_border']}; white-space: nowrap;
    }}
    table.bank-table tbody td {{ padding: 9px 14px; color: {th['text']} !important; border-bottom: 1px solid {th['table_border']}; white-space: nowrap; }}
    table.bank-table tbody tr:nth-child(even) {{ background: {th['table_row_alt']}; }}
    table.bank-table tbody tr:hover {{ background: {th['slider_track']}; }}

    @media (min-width: 1000px) {{
        div[data-testid="column"]:first-child > div {{ position: sticky; top: 14px; }}
    }}

    /* ========================================================
       DATE INPUT — khối CSS hợp nhất (fix mất chữ ở Dark Mode)
       Trước đây có 3 khối rời rạc chồng chéo nhau; nay gộp lại
       thành 1 khối duy nhất, dùng selector wildcard để chắc chắn
       bắt được mọi lớp con do BaseWeb/Streamlit sinh ra.
       ======================================================== */
    :root {{ color-scheme: {th['color_scheme']}; }}
    html {{ color-scheme: {th['color_scheme']} !important; }}

    [data-testid="stDateInput"] * {{
        background-color: {th['input_bg']} !important;
        color: {th['input_text']} !important;
        -webkit-text-fill-color: {th['input_text']} !important;
    }}
    [data-testid="stDateInput"] input::placeholder,
    [data-testid="stDateInput"] input::-webkit-input-placeholder {{
        color: {th['placeholder']} !important;
        -webkit-text-fill-color: {th['placeholder']} !important;
        opacity: 1 !important;
    }}
    [data-testid="stDateInput"] svg {{
        fill: {th['muted']} !important;
        stroke: {th['muted']} !important;
        background: transparent !important;
    }}
    [data-testid="stDateInput"] [data-baseweb="input"],
    [data-testid="stDateInput"] [data-baseweb="base-input"] {{
        border: 1px solid {th['input_border']} !important;
        border-radius: 10px !important;
        box-shadow: none !important;
    }}
    [data-testid="stDateInput"] button:hover {{
        background: {th['slider_track']} !important;
    }}

    /* Popover lịch khi mở */
    div[data-baseweb="popover"] [data-baseweb="calendar"],
    div[data-baseweb="calendar"] {{
        background: {th['input_bg']} !important;
        color: {th['input_text']} !important;
        border-color: {th['input_border']} !important;
    }}
    div[data-baseweb="calendar"] *,
    div[data-baseweb="calendar"] button {{
        color: {th['input_text']} !important;
    }}
    div[data-baseweb="calendar"] button:hover {{
        background: {th['slider_track']} !important;
    }}

    /* ---------- SELECTBOX ---------- */
    .stSelectbox [data-baseweb="select"],
    .stSelectbox [data-baseweb="select"] > div,
    .stSelectbox [data-baseweb="select"] > div > div {{
        background: {th['input_bg']} !important;
        color: {th['input_text']} !important;
        border-color: {th['input_border']} !important;
    }}
    .stSelectbox [data-baseweb="select"] input {{
        color: {th['input_text']} !important;
        -webkit-text-fill-color: {th['input_text']} !important;
    }}
    .stSelectbox [data-baseweb="select"] span,
    .stSelectbox [data-baseweb="select"] div[role="option"] {{
        color: {th['input_text']} !important;
    }}
    ul[data-baseweb="menu"],
    ul[data-baseweb="menu"] > li,
    div[data-baseweb="popover"] ul {{
        background: {th['input_bg']} !important;
        color: {th['input_text']} !important;
    }}
    ul[data-baseweb="menu"] li[aria-selected="true"],
    ul[data-baseweb="menu"] li:hover {{
        background: {th['slider_track']} !important;
        color: {th['input_text']} !important;
    }}
    .stSelectbox svg {{
        color: {th['muted']} !important;
        fill: currentColor !important;
    }}

    /* ---------- NUMBER / TEXT INPUT ---------- */
    .stTextInput [data-baseweb="input"],
    .stNumberInput [data-baseweb="input"],
    .stTextArea [data-baseweb="base-input"],
    .stTextArea textarea,
    .stTextInput input,
    .stNumberInput input {{
        background: {th['input_bg']} !important;
        color: {th['input_text']} !important;
        -webkit-text-fill-color: {th['input_text']} !important;
        border-color: {th['input_border']} !important;
        opacity: 1 !important;
    }}
    .stTextInput input::placeholder,
    .stNumberInput input::placeholder,
    .stTextArea textarea::placeholder {{
        color: {th['placeholder']} !important;
        -webkit-text-fill-color: {th['placeholder']} !important;
        opacity: 1 !important;
    }}

    /* ---------- SLIDER ---------- */
    div[data-testid="stSlider"] {{ color: {th['text']} !important; }}
    div[data-testid="stSlider"] label,
    div[data-testid="stSlider"] p,
    div[data-testid="stSlider"] span {{
        color: {th['text']} !important;
    }}
    div[data-testid="stSlider"] [data-baseweb="slider"] > div {{
        background: transparent !important;
    }}
    div[data-testid="stSlider"] [data-baseweb="slider"] > div > div {{
        background: {th['slider_track']} !important;
    }}
    div[data-testid="stSlider"] [role="slider"] {{
        background: {th['emerald']} !important;
        border: 2px solid {th['emerald']} !important;
        box-shadow: 0 0 0 3px {th['slider_track']} !important;
    }}
    div[data-testid="stSlider"] [data-testid="stThumbValue"],
    div[data-testid="stSlider"] [data-testid="stSliderTickBarMin"],
    div[data-testid="stSlider"] [data-testid="stSliderTickBarMax"] {{
        color: {th['muted']} !important;
        -webkit-text-fill-color: {th['muted']} !important;
    }}

    /* ---------- BUTTON ---------- */
    .stButton > button,
    .stDownloadButton > button {{
        color: {th['sapphire']} !important;
        background: {th['chip_bg']} !important;
        border: 1px solid {th['input_border']} !important;
        opacity: 1 !important;
    }}
    .stButton > button p,
    .stButton > button span,
    .stDownloadButton > button p,
    .stDownloadButton > button span {{
        color: inherit !important;
        -webkit-text-fill-color: currentColor !important;
    }}
    .stButton > button:hover,
    .stDownloadButton > button:hover {{
        border-color: {th['emerald']} !important;
        color: {th['emerald']} !important;
    }}
    .st-key-calc_btn .stButton > button,
    .st-key-calc_btn .stButton > button p,
    .st-key-calc_btn .stButton > button span {{
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }}

    /* ---------- TABS / EXPANDER / CHECKBOX / RADIO ---------- */
    div[data-testid="stTabs"] button,
    div[data-testid="stTabs"] button p,
    div[data-testid="stTabs"] button span {{
        color: {th['text']} !important;
    }}
    div[data-testid="stTabs"] button[aria-selected="true"],
    div[data-testid="stTabs"] button[aria-selected="true"] p {{
        color: {th['sapphire']} !important;
    }}
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] summary span {{
        color: {th['heading']} !important;
    }}
    div[role="radiogroup"] label,
    div[role="radiogroup"] label p,
    div[role="radiogroup"] label span {{
        color: {th['text']} !important;
    }}

    /* ---------- BẢNG HTML ---------- */
    .bank-table-wrap {{
        background: {th['table_bg']} !important;
        border-color: {th['table_border']} !important;
    }}
    table.bank-table,
    table.bank-table thead,
    table.bank-table tbody {{
        background: {th['table_bg']} !important;
        color: {th['text']} !important;
    }}
    table.bank-table thead th {{
        background: {th['table_head_bg']} !important;
        color: {th['heading']} !important;
        border-color: {th['table_border']} !important;
    }}
    table.bank-table tbody td {{
        background: transparent !important;
        color: {th['text']} !important;
        border-color: {th['table_border']} !important;
    }}
    table.bank-table tbody tr:nth-child(even) td {{
        background: {th['table_row_alt']} !important;
    }}
    table.bank-table tbody tr:hover td {{
        background: {th['slider_track']} !important;
    }}

</style>
"""


st.markdown(build_css(TH), unsafe_allow_html=True)


def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"


top_l, top_r = st.columns([6, 1])
with top_r:
    with st.container(key="theme_btn"):
        st.button(
            "🌙 Tối" if st.session_state.theme == "light" else "☀️ Sáng",
            on_click=toggle_theme, use_container_width=True,
        )


# ============================================================
# HÀM ĐỊNH DẠNG
# ============================================================

def format_money(value: float) -> str:
    return f"{round(value):,.0f} VNĐ"


def format_million(value: float) -> str:
    return f"{value:,.2f} triệu đồng"


def auto_label(v: float) -> str:
    v = float(v)
    if v >= 1_000_000_000:
        return f"{v / 1_000_000_000:g} tỷ"
    if v >= 1_000_000:
        return f"{v / 1_000_000:g} triệu"
    if v >= 1_000:
        return f"{v / 1_000:g} nghìn"
    return f"{v:g} đồng"


def kpi_card(label, value, icon="wallet", variant="navy", note_html=""):
    st.markdown(
        f"""
        <div class="kpi-card kpi-{variant}">
            <div class="kpi-bg-icon">{svg_icon(icon, 90)}</div>
            <div class="kpi-label"><span class="ic">{svg_icon(icon, 15)}</span>{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-note">{note_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def progress_bar_custom(percent, left_label, right_label):
    percent = max(0, min(100, percent))
    st.markdown(
        f"""
        <div class="progress-wrap">
            <div class="progress-labels"><span>{left_label}</span><span>{right_label}</span></div>
            <div class="progress-track"><div class="progress-fill" style="width:{percent}%;"></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_html_table(df: pd.DataFrame, currency_cols=None, date_cols=None):
    """Vẽ bảng bằng HTML/CSS thuần để tô màu đúng theo theme sáng/tối (khác với st.dataframe
    vốn render trong iframe riêng và không ăn theo CSS tuỳ biến của trang)."""
    currency_cols = currency_cols or []
    date_cols = date_cols or []
    df2 = df.copy()
    for c in currency_cols:
        if c in df2.columns:
            df2[c] = df2[c].map(lambda x: f"{round(x):,.0f} ₫" if pd.notna(x) else "")
    for c in date_cols:
        if c in df2.columns:
            df2[c] = df2[c].map(lambda x: x.strftime("%d/%m/%Y") if hasattr(x, "strftime") else x)

    head = "".join(f"<th>{c}</th>" for c in df2.columns)
    body_rows = []
    for _, row in df2.iterrows():
        cells = "".join(f"<td>{row[c]}</td>" for c in df2.columns)
        body_rows.append(f"<tr>{cells}</tr>")
    html = f"""
    <div class="bank-table-wrap">
    <table class="bank-table">
        <thead><tr>{head}</tr></thead>
        <tbody>{''.join(body_rows)}</tbody>
    </table>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ============================================================
# Ô NHẬP TIỀN THÔNG MINH — hỗ trợ: 500000000 / 500 triệu / 1.5 tỷ / 1,5 tỷ / 200k / 50tr
# ============================================================

_SUFFIX_MULT = {
    "": 1, "d": 1, "dong": 1, "đ": 1, "đồng": 1,
    "k": 1_000, "nghin": 1_000, "nghìn": 1_000,
    "tr": 1_000_000, "trieu": 1_000_000, "triệu": 1_000_000, "m": 1_000_000,
    "ty": 1_000_000_000, "tỷ": 1_000_000_000, "b": 1_000_000_000,
}
_PARSE_RE = re.compile(r"^([\d]+(?:[.,]\d+)?)\s*([^\d\s]*)$", re.UNICODE)


def parse_smart_amount(text: str):
    if not text:
        return None
    t = text.strip().lower().replace("vnđ", "").replace("vnd", "").strip()

    # Số nguyên lớn có dấu phân cách hàng nghìn kiểu 500.000.000 hoặc 500,000,000
    # (nhiều nhóm 3 chữ số cách nhau bởi , hoặc . và không có hậu tố chữ)
    bare_grouped = re.match(r"^\d{1,3}([.,]\d{3})+$", t)
    if bare_grouped:
        return float(t.replace(".", "").replace(",", ""))

    m = _PARSE_RE.match(t)
    if not m:
        return None
    num_str, suffix = m.groups()
    suffix = suffix.strip()
    if suffix not in _SUFFIX_MULT:
        return None

    # Dấu , hoặc . đều hiểu là dấu thập phân (cả có hậu tố lẫn không).
    num_str_clean = num_str.replace(",", ".")

    try:
        number = float(num_str_clean)
    except ValueError:
        return None
    return number * _SUFFIX_MULT[suffix]


# ============================================================


# ============================================================
# CẤU HÌNH NGHIỆP VỤ MỚI
# ============================================================

DAYS_PER_YEAR = 365

# Hỗ trợ đầy đủ kỳ hạn theo tháng, bao gồm 4 tháng và các kỳ hạn khác.
TERM_OPTIONS = {"Không kỳ hạn": 0}
TERM_OPTIONS.update({f"{m} tháng": m for m in range(1, 61)})
TERM_OPTIONS["Tùy chọn số tháng"] = -1

INTEREST_METHODS = [
    "💵 Cuối kỳ",
    "📆 Hàng tháng",
    "💰 Đầu kỳ",
]
CALC_METHODS = ["Lãi đơn", "Lãi kép"]


# ============================================================
# HÀM TÍNH TOÁN
# ============================================================

def days_between(start_date, withdrawal_date):
    """Tính [ngày gửi, ngày rút): có ngày gửi, không có ngày rút."""
    return (withdrawal_date - start_date).days


def simple_interest(principal, annual_rate, days):
    return principal * annual_rate / 100 * days / DAYS_PER_YEAR


def compound_amount_daily(principal, annual_rate, days):
    """Lãi kép theo ngày, dùng đúng quy ước 365 ngày/năm."""
    return principal * (1 + annual_rate / 100 / DAYS_PER_YEAR) ** days


def compound_interest(principal, annual_rate, days):
    return compound_amount_daily(principal, annual_rate, days) - principal


def maturity_date(start_date, term_months):
    if term_months <= 0:
        return None
    return start_date + relativedelta(months=term_months)


def month_periods(start_date, end_date):
    """Chia khoảng [start_date, end_date) thành các tháng lịch."""
    periods = []
    current = start_date
    while current < end_date:
        next_date = min(current + relativedelta(months=1), end_date)
        days = (next_date - current).days
        if days > 0:
            periods.append((current, next_date, days))
        current = next_date
    return periods


def build_monthly_table(principal, annual_rate, start_date, withdrawal_date, method):
    """Bảng lãi theo tháng. Với lãi kép, lãi mỗi tháng được cộng dồn vào gốc."""
    rows = []
    current_principal = principal
    cumulative_interest = 0.0

    for idx, (period_start, period_end, days) in enumerate(
        month_periods(start_date, withdrawal_date), start=1
    ):
        if method == "Lãi đơn":
            interest = simple_interest(current_principal, annual_rate, days)
            closing = current_principal + interest
        else:
            closing = compound_amount_daily(current_principal, annual_rate, days)
            interest = closing - current_principal

        cumulative_interest += interest
        rows.append({
            "Kỳ": idx,
            "Từ ngày": period_start,
            "Đến trước ngày": period_end,
            "Số ngày": days,
            "Gốc đầu kỳ": current_principal,
            "Tiền lãi kỳ này": interest,
            "Lãi lũy kế": cumulative_interest,
            "Gốc + lãi cuối kỳ": closing,
        })

        if method == "Lãi kép":
            current_principal = closing

    return pd.DataFrame(rows)


def calculate_result(principal, annual_rate, start_date, withdrawal_date, calc_method):
    days = days_between(start_date, withdrawal_date)

    if calc_method == "Lãi đơn":
        interest = simple_interest(principal, annual_rate, days)
        total = principal + interest
    else:
        interest = compound_interest(principal, annual_rate, days)
        total = principal + interest

    return days, interest, total


def method_explanation(interest_method, total_interest, principal, total_value):
    if interest_method == "💵 Cuối kỳ":
        return (
            f"Ngày rút nhận gốc + toàn bộ lãi: <b>{format_money(total_value)}</b>. "
            f"Tổng lãi: <b>{format_money(total_interest)}</b>."
        )
    if interest_method == "📆 Hàng tháng":
        return (
            f"Lãi được chi trả theo từng tháng; tổng lãi trong thời gian gửi là "
            f"<b>{format_money(total_interest)}</b>. Ngày rút nhận lại gốc "
            f"<b>{format_money(principal)}</b> (không cộng lại phần lãi đã nhận trước đó)."
        )
    return (
        f"Lãi được xác định và nhận ngay đầu kỳ: <b>{format_money(total_interest)}</b>. "
        f"Ngày rút nhận lại gốc: <b>{format_money(principal)}</b>."
    )


# ============================================================
# HÀM HIỂN THỊ
# ============================================================

def render_kpi(label, value, icon, variant="navy", note=""):
    kpi_card(label, value, icon, variant, note)


def render_donut(principal, interest):
    interest = max(float(interest), 0.0)
    fig = go.Figure(go.Pie(
        labels=["Tiền gốc", "Tiền lãi"],
        values=[principal, interest],
        hole=0.64,
        marker=dict(
            colors=[TH["sapphire"], TH["emerald"]],
            line=dict(color="rgba(0,0,0,0)", width=2),
        ),
        textinfo="percent",
        textfont=dict(color="white", size=13),
        hovertemplate="%{label}: %{value:,.0f} VNĐ (%{percent})<extra></extra>",
    ))
    fig.update_layout(
        height=300,
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, Inter, sans-serif", color=TH["text"]),
        legend=dict(orientation="h", y=-0.12, x=0.5, xanchor="center"),
        annotations=[dict(
            text=f"<b>{auto_label(principal + interest)}</b><br>"
                 f"<span style='font-size:11px;color:{TH['muted']}'>Tổng giá trị</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=15, color=TH["heading"]),
        )],
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_interest_chart(monthly_df):
    if monthly_df.empty:
        st.info("Chưa có dữ liệu để vẽ biểu đồ.")
        return

    labels = [f"Kỳ {int(x)}" for x in monthly_df["Kỳ"]]
    interest = monthly_df["Tiền lãi kỳ này"].tolist()
    cumulative = monthly_df["Lãi lũy kế"].tolist()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=interest, name="Lãi từng kỳ",
        marker_color=TH["sapphire"],
        hovertemplate="%{x}<br>Lãi: %{y:,.0f} VNĐ<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=labels, y=cumulative, name="Lãi lũy kế",
        mode="lines+markers",
        line=dict(color=TH["emerald"], width=3),
        marker=dict(size=7),
        hovertemplate="%{x}<br>Lũy kế: %{y:,.0f} VNĐ<extra></extra>",
    ))
    fig.update_layout(
        height=360,
        margin=dict(t=20, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, Inter, sans-serif", color=TH["text"]),
        xaxis=dict(color=TH["text"], gridcolor=TH["grid_line"]),
        yaxis=dict(title="VNĐ", color=TH["text"], gridcolor=TH["grid_line"]),
        legend=dict(orientation="h", y=1.08, x=0),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def result_badge(status):
    if status == "Đúng hạn":
        return '<span class="badge-pill emerald">🏁 ĐÚNG NGÀY ĐÁO HẠN</span>'
    if status == "Trước hạn":
        return '<span class="badge-pill crimson">⏱️ RÚT TRƯỚC KỲ HẠN</span>'
    if status == "Sau hạn":
        return '<span class="badge-pill amber">📅 RÚT SAU NGÀY ĐÁO HẠN</span>'
    return '<span class="badge-pill amber">🕊️ KHÔNG KỲ HẠN</span>'


def csv_download(df, filename, label="⬇️ Tải kết quả (CSV)"):
    st.download_button(
        label,
        df.to_csv(index=False).encode("utf-8-sig"),
        file_name=filename,
        mime="text/csv",
        use_container_width=True,
    )


# ============================================================
# HERO BANNER
# ============================================================

st.markdown(
    f"""
    <div class="hero-banner">
        <div class="hero-top">
            <div>
                <span class="hero-badge">{svg_icon('check', 13)} HỆ THỐNG ĐANG HOẠT ĐỘNG</span>
                <div class="hero-title">🏦 Trung tâm tính tiền gửi tiết kiệm</div>
                <div class="hero-sub">Tính gốc – lãi – số ngày – dòng tiền theo đúng ngày gửi và ngày rút</div>
            </div>
            <div class="hero-glow-icon">{svg_icon('trending', 24)}</div>
        </div>
        <div class="ticker-wrap">
            <div class="ticker-track">
                <span class="ticker-item"><span class="dot"></span>1 năm = 365 ngày</span>
                <span class="ticker-item info"><span class="dot"></span>Tính lãi từ ngày gửi</span>
                <span class="ticker-item warn"><span class="dot"></span>Không tính ngày rút</span>
                <span class="ticker-item"><span class="dot"></span>Lãi kép chỉ áp dụng cuối kỳ</span>
                <span class="ticker-item"><span class="dot"></span>1 năm = 365 ngày</span>
                <span class="ticker-item info"><span class="dot"></span>Tính lãi từ ngày gửi</span>
                <span class="ticker-item warn"><span class="dot"></span>Không tính ngày rút</span>
                <span class="ticker-item"><span class="dot"></span>Lãi kép chỉ áp dụng cuối kỳ</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LAYOUT CHÍNH
# ============================================================

col_left, col_right = st.columns([0.35, 0.65], gap="medium")

with col_left:
    with st.container(border=True):
        st.markdown(
            f'<div class="panel-title"><span class="pt-icon">{svg_icon("wallet", 15)}</span>BẢNG ĐIỀU KHIỂN</div>',
            unsafe_allow_html=True,
        )

        # ---------------- SỐ TIỀN ----------------
        if "so_tien_goc" not in st.session_state:
            st.session_state.so_tien_goc = 0.0
        if "so_tien_text" not in st.session_state:
            st.session_state.so_tien_text = ""

        def set_amount(value):
            value = max(float(value), 0.0)
            st.session_state.so_tien_goc = value
            st.session_state.so_tien_text = f"{value:,.0f}" if value else ""

        def amount_changed():
            raw = st.session_state.so_tien_text
            if not raw.strip():
                st.session_state.so_tien_goc = 0.0
                return
            value = parse_smart_amount(raw)
            if value is not None:
                st.session_state.so_tien_goc = max(value, 0.0)
                st.session_state.so_tien_text = f"{value:,.0f}"

        def slider_changed():
            set_amount(st.session_state.slider_amount)

        st.markdown("**💰 Số tiền gửi**")
        st.text_input(
            "Nhập số tiền",
            key="so_tien_text",
            on_change=amount_changed,
            placeholder="Ví dụ: 500 triệu, 1.5 tỷ, 200k, 500000000...",
            label_visibility="collapsed",
        )
        st.slider(
            "Điều chỉnh số tiền",
            min_value=0,
            max_value=10_000_000_000,
            value=int(st.session_state.so_tien_goc),
            step=1_000_000,
            key="slider_amount",
            on_change=slider_changed,
            label_visibility="collapsed",
            format="%d ₫",
        )
        st.caption(
            f"➡️ Đang chọn: **{format_money(st.session_state.so_tien_goc)}**"
            if st.session_state.so_tien_goc > 0 else "➡️ Chưa nhập số tiền."
        )

        st.markdown(
            f"<div style='font-size:12.5px;font-weight:700;color:{TH['muted']};margin-top:6px;'>Chọn nhanh</div>",
            unsafe_allow_html=True,
        )
        with st.container(key="quick_chips"):
            quick = [50_000_000, 100_000_000, 200_000_000, 500_000_000, 1_000_000_000, 2_000_000_000]
            qc = st.columns(3)
            for i, value in enumerate(quick):
                qc[i % 3].button(
                    auto_label(value), key=f"quick_{value}", use_container_width=True,
                    on_click=set_amount, args=(value,),
                )

        with st.container(key="adj_chips"):
            st.markdown(
                f"<div style='font-size:12.5px;font-weight:700;color:{TH['muted']};margin-top:8px;'>Điều chỉnh nhanh</div>",
                unsafe_allow_html=True,
            )
            ac = st.columns(3)
            deltas = [("➕1tr", 1_000_000), ("➕10tr", 10_000_000), ("➕50tr", 50_000_000),
                      ("➖1tr", -1_000_000), ("➖10tr", -10_000_000), ("➖50tr", -50_000_000)]
            for i, (label, delta) in enumerate(deltas):
                # Giá trị được tính lúc render từ trạng thái hiện tại.
                ac[i % 3].button(
                    label, key=f"delta_{i}", use_container_width=True,
                    on_click=set_amount,
                    args=(max(st.session_state.so_tien_goc + delta, 0),),
                )

        st.divider()

        # ---------------- KỲ HẠN ----------------
        st.markdown("**📅 Kỳ hạn & lãi suất**")
        term_choice = st.selectbox(
            "Kỳ hạn gửi tiền",
            list(TERM_OPTIONS.keys()),
            key="term_choice",
        )
        term_months = TERM_OPTIONS[term_choice]

        custom_months = None
        if term_months == -1:
            custom_months = st.number_input(
                "Số tháng kỳ hạn tùy chọn",
                min_value=1,
                max_value=120,
                value=4,
                step=1,
                key="custom_months",
            )
            term_months = int(custom_months)

        annual_rate = st.number_input(
            "📈 Lãi suất theo năm (%/năm)",
            min_value=0.0,
            max_value=100.0,
            value=5.0,
            step=0.01,
            format="%.4f",
            key="annual_rate",
            help="Quy ước 1 năm = 365 ngày.",
        )

        st.divider()

        # ---------------- PHƯƠNG THỨC ----------------
        st.markdown("**💳 Hình thức nhận lãi**")
        interest_method = st.radio(
            "Hình thức nhận lãi",
            INTEREST_METHODS,
            horizontal=True,
            key="interest_method",
            label_visibility="collapsed",
        )

        # Lãi kép chỉ được bật khi nhận cuối kỳ.
        compound_allowed = interest_method == "💵 Cuối kỳ"
        calc_method = st.radio(
            "Phương pháp tính lãi",
            CALC_METHODS if compound_allowed else ["Lãi đơn"],
            horizontal=True,
            key="calc_method",
        )
        if not compound_allowed:
            st.caption("ℹ️ Lãi kép chỉ áp dụng cho hình thức **nhận lãi cuối kỳ**; hệ thống dùng lãi đơn cho lựa chọn này.")

        st.divider()

        # ---------------- NGÀY ----------------
        st.markdown("**🗓️ Thời gian gửi tiền**")
        start_date = st.date_input(
            "Ngày khách hàng gửi tiền",
            value=date.today(),
            format="DD/MM/YYYY",
            key="start_date",
        )
        withdrawal_date = st.date_input(
            "Ngày khách hàng rút tiền",
            value=date.today() + relativedelta(months=4),
            format="DD/MM/YYYY",
            key="withdrawal_date",
        )

        st.caption("📌 Ngày gửi **được tính lãi**; ngày rút **không tính lãi**.")

        st.write("")
        with st.container(key="calc_btn"):
            calc_clicked = st.button("⚡ TÍNH TOÁN NGAY", use_container_width=True)
        with st.container(key="reset_btn"):
            reset_clicked = st.button("↺ Làm mới toàn bộ", use_container_width=True)


# ============================================================
# RESET
# ============================================================

if reset_clicked:
    for key in [
        "so_tien_goc", "so_tien_text", "slider_amount", "term_choice", "custom_months",
        "annual_rate", "interest_method", "calc_method", "start_date", "withdrawal_date",
        "last_calc", "calc_errors",
    ]:
        st.session_state.pop(key, None)
    st.rerun()


# ============================================================
# TÍNH TOÁN KHI BẤM NÚT
# ============================================================

if calc_clicked:
    errors = []
    principal = float(st.session_state.get("so_tien_goc", 0))
    rate = float(st.session_state.get("annual_rate", 0))
    start = st.session_state.get("start_date")
    withdrawal = st.session_state.get("withdrawal_date")
    selected_term = int(term_months) if term_months is not None else None
    selected_method = st.session_state.get("interest_method")
    selected_calc = st.session_state.get("calc_method", "Lãi đơn")

    if principal <= 0:
        errors.append("Vui lòng nhập **số tiền gửi lớn hơn 0**.")
    if selected_term is None:
        errors.append("Vui lòng chọn **kỳ hạn**.")
    if rate < 0:
        errors.append("Lãi suất không được âm.")
    if start is None or withdrawal is None:
        errors.append("Vui lòng chọn đầy đủ **ngày gửi** và **ngày rút**.")
    elif withdrawal <= start:
        errors.append("**Ngày rút tiền phải lớn hơn ngày gửi tiền** để có ít nhất 1 ngày tính lãi.")
    if selected_method is None:
        errors.append("Vui lòng chọn **hình thức nhận lãi**.")
    if selected_calc == "Lãi kép" and selected_method != "💵 Cuối kỳ":
        errors.append("Lãi kép chỉ áp dụng cho **nhận lãi cuối kỳ**.")

    if errors:
        st.session_state["calc_errors"] = errors
        st.session_state.pop("last_calc", None)
    else:
        st.session_state["calc_errors"] = []
        st.session_state["last_calc"] = {
            "principal": principal,
            "annual_rate": rate,
            "term_months": selected_term,
            "interest_method": selected_method,
            "calc_method": selected_calc,
            "start_date": start,
            "withdrawal_date": withdrawal,
        }


# ============================================================
# CỘT PHẢI — KẾT QUẢ
# ============================================================

with col_right:
    if st.session_state.get("calc_errors"):
        st.error(
            "⚠️ Vui lòng hoàn thiện thông tin trước khi tính toán:\n\n" +
            "\n\n".join(f"- {e}" for e in st.session_state["calc_errors"])
        )

    tab1, tab2, tab3 = st.tabs([
        "📊 Tổng quan",
        "📋 Bảng lãi hàng tháng",
        "🧮 Công thức & kiểm tra",
    ])

    calc = st.session_state.get("last_calc")

    if not calc:
        with tab1:
            st.info("👈 Nhập thông tin ở **Bảng điều khiển** bên trái rồi bấm **TÍNH TOÁN NGAY** để xem kết quả.")
        with tab2:
            st.info("Chưa có dữ liệu để hiển thị.")
        with tab3:
            st.info("Chưa có phép tính để kiểm tra.")
    else:
        principal = calc["principal"]
        annual_rate = calc["annual_rate"]
        term_months = calc["term_months"]
        interest_method = calc["interest_method"]
        calc_method = calc["calc_method"]
        start_date = calc["start_date"]
        withdrawal_date = calc["withdrawal_date"]

        days, total_interest, total_value = calculate_result(
            principal, annual_rate, start_date, withdrawal_date, calc_method
        )

        maturity = maturity_date(start_date, term_months)
        if term_months == 0:
            status = "Không kỳ hạn"
        elif withdrawal_date < maturity:
            status = "Trước hạn"
        elif withdrawal_date == maturity:
            status = "Đúng hạn"
        else:
            status = "Sau hạn"

        # Với lãi tháng/đầu kỳ, số tiền thực nhận vào NGÀY RÚT chỉ là gốc;
        # tổng giá trị nhận được trong toàn bộ khoản gửi = gốc + toàn bộ lãi.
        amount_on_withdrawal = principal if interest_method != "💵 Cuối kỳ" else total_value

        monthly_df = build_monthly_table(
            principal, annual_rate, start_date, withdrawal_date, calc_method
        )

        # Bảng tổng hợp theo từng kỳ để dùng chung cho CSV.
        detail_df = monthly_df.copy()
        if not detail_df.empty:
            detail_df["Phương pháp"] = calc_method
            detail_df["Hình thức nhận lãi"] = interest_method

        with tab1:
            st.markdown(result_badge(status), unsafe_allow_html=True)

            if maturity:
                status_text = (
                    f"Kỳ hạn {term_months} tháng · Ngày đáo hạn dự kiến: "
                    f"**{maturity.strftime('%d/%m/%Y')}**"
                )
            else:
                status_text = "Không kỳ hạn · Tính theo toàn bộ số ngày thực tế"
            st.caption(status_text)

            full_term_days = days_between(start_date, maturity) if maturity else days
            elapsed_pct = 100 if not maturity else min(100, max(0, days / max(full_term_days, 1) * 100))
            if maturity:
                progress_bar_custom(
                    elapsed_pct,
                    f"Đã gửi {days}/{full_term_days} ngày",
                    f"{elapsed_pct:.1f}% kỳ hạn",
                )

            k1, k2, k3, k4 = st.columns(4)
            with k1:
                render_kpi("Tiền gốc", format_million(principal / 1e6), "wallet", "navy")
            with k2:
                render_kpi("Số ngày tính lãi", f"{days} ngày", "calendar", "navy")
            with k3:
                render_kpi(
                    "Tổng tiền lãi", format_million(total_interest / 1e6), "trending", "emerald",
                    f'<span class="kpi-chip pos">{annual_rate:.4f}%/năm</span>',
                )
            with k4:
                render_kpi("Tổng gốc + lãi", format_million(total_value / 1e6), "banknote", "emerald")

            st.markdown("### 💰 Kết quả nhận tiền")
            result_col, chart_col = st.columns([1.3, 1])

            with result_col:
                method_note = method_explanation(
                    interest_method, total_interest, principal, total_value
                )
                st.markdown(
                    f"""
                    <div class="result-hero">
                        <div class="rh-label">TỔNG GIÁ TRỊ GỐC + LÃI</div>
                        <div class="rh-value">{format_money(total_value)}</div>
                        <div class="rh-detail">
                            Gốc: <b>{format_money(principal)}</b><br>
                            Tổng lãi: <b>{format_money(total_interest)}</b><br>
                            Số ngày tính lãi: <b>{days} ngày</b> · 365 ngày/năm<br>
                            Phương pháp: <b>{calc_method}</b>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div class='verdict-box'>💳 {method_note}</div>",
                    unsafe_allow_html=True,
                )

                if interest_method == "💵 Cuối kỳ":
                    st.success(
                        f"Ngày **{withdrawal_date.strftime('%d/%m/%Y')}**, khách hàng nhận "
                        f"**{format_money(total_value)}** gồm gốc + toàn bộ lãi."
                    )
                else:
                    st.info(
                        f"Ngày **{withdrawal_date.strftime('%d/%m/%Y')}**, khách hàng nhận lại gốc "
                        f"**{format_money(principal)}**. Phần lãi đã được nhận {('theo tháng' if interest_method == '📆 Hàng tháng' else 'ngay đầu kỳ')}."
                    )

                csv_download(
                    detail_df if not detail_df.empty else pd.DataFrame([{
                        "Tiền gốc": principal,
                        "Tổng tiền lãi": total_interest,
                        "Tổng gốc + lãi": total_value,
                    }]),
                    "ket_qua_tien_gui.csv",
                )

            with chart_col:
                render_donut(principal, total_interest)

            st.markdown("### 📈 Lãi phát sinh theo từng tháng")
            render_interest_chart(monthly_df)

        with tab2:
            st.markdown("### 📋 Chi tiết tiền lãi hàng tháng")
            if monthly_df.empty:
                st.info("Không có kỳ nào vì khoảng thời gian tính lãi bằng 0 ngày.")
            else:
                st.caption(
                    "Khoảng ngày được tính theo quy tắc **từ ngày gửi đến trước ngày rút**. "
                    "Mỗi dòng là một tháng lịch; tháng cuối có thể là tháng lẻ."
                )
                render_html_table(
                    monthly_df,
                    currency_cols=[
                        "Gốc đầu kỳ", "Tiền lãi kỳ này", "Lãi lũy kế", "Gốc + lãi cuối kỳ"
                    ],
                    date_cols=["Từ ngày", "Đến trước ngày"],
                )

            st.divider()
            summary_df = pd.DataFrame([
                {"Chỉ tiêu": "Số tiền gửi", "Giá trị": format_money(principal)},
                {"Chỉ tiêu": "Lãi suất năm", "Giá trị": f"{annual_rate:.4f}%/năm"},
                {"Chỉ tiêu": "Kỳ hạn", "Giá trị": "Không kỳ hạn" if term_months == 0 else f"{term_months} tháng"},
                {"Chỉ tiêu": "Ngày gửi", "Giá trị": start_date.strftime("%d/%m/%Y")},
                {"Chỉ tiêu": "Ngày rút", "Giá trị": withdrawal_date.strftime("%d/%m/%Y")},
                {"Chỉ tiêu": "Số ngày tính lãi", "Giá trị": f"{days} ngày"},
                {"Chỉ tiêu": "Hình thức nhận lãi", "Giá trị": interest_method},
                {"Chỉ tiêu": "Phương pháp tính", "Giá trị": calc_method},
                {"Chỉ tiêu": "Tổng tiền lãi", "Giá trị": format_money(total_interest)},
                {"Chỉ tiêu": "Tổng gốc + lãi", "Giá trị": format_money(total_value)},
                {"Chỉ tiêu": "Số tiền nhận đúng ngày rút", "Giá trị": format_money(amount_on_withdrawal)},
            ])
            st.markdown("### 🧾 Tổng hợp khoản tiền gửi")
            render_html_table(summary_df)

        with tab3:
            st.markdown("### 🧮 Công thức đang sử dụng")

            st.markdown(
                """
                **Quy ước số ngày**

                Khoảng tính lãi là **[ngày gửi, ngày rút)**:

                - Ngày gửi: **được tính lãi**.
                - Ngày rút: **không tính lãi**.
                - Ví dụ gửi 01/01 và rút 02/01 → tính **1 ngày**.
                - Một năm luôn quy ước **365 ngày**.
                """
            )

            st.latex(r"I = P \times \frac{r}{100} \times \frac{n}{365}")
            st.markdown(
                "Trong đó `P` là tiền gốc, `r` là lãi suất %/năm và `n` là số ngày tính lãi."
            )

            st.markdown("**Lãi kép — chỉ áp dụng khi nhận lãi cuối kỳ:**")
            st.latex(r"A = P\times\left(1+\frac{r}{100\times365}\right)^n")
            st.markdown(
                "Lãi kép được mô phỏng theo **tích lũy hàng ngày**, phù hợp với quy ước 365 ngày/năm; "
                "lãi không được trả ra trong kỳ mà tiếp tục cộng vào số dư để sinh lãi."
            )

            st.markdown("### 🔎 Kiểm tra khoảng thời gian")
            check_df = pd.DataFrame([
                {"Mốc": "Ngày gửi", "Ngày": start_date.strftime("%d/%m/%Y"), "Có tính lãi?": "✅ Có"},
                {"Mốc": "Ngày ngay trước ngày rút", "Ngày": (withdrawal_date - timedelta(days=1)).strftime("%d/%m/%Y"), "Có tính lãi?": "✅ Có"},
                {"Mốc": "Ngày rút", "Ngày": withdrawal_date.strftime("%d/%m/%Y"), "Có tính lãi?": "❌ Không"},
            ])
            render_html_table(check_df)

            if interest_method != "💵 Cuối kỳ" and calc_method == "Lãi kép":
                st.error("Dữ liệu không hợp lệ: lãi kép chỉ được dùng cho nhận lãi cuối kỳ.")
            else:
                st.success("✅ Phương pháp và hình thức nhận lãi đang phù hợp với quy tắc bạn yêu cầu.")


# ============================================================
# HƯỚNG DẪN & CÔNG THỨC
# ============================================================

st.divider()

with st.expander("📖 Hướng dẫn sử dụng"):
    st.markdown(
        """
        **1. Số tiền gửi** — nhập trực tiếp hoặc dùng dạng `500 triệu`, `1.5 tỷ`, `200k`, `50tr`.

        **2. Kỳ hạn** — hỗ trợ Không kỳ hạn và các kỳ hạn từ **1 đến 60 tháng**, bao gồm **4 tháng**; ngoài ra có thể chọn số tháng tùy chọn.

        **3. Lãi suất** — nhập lãi suất năm. Hệ thống luôn dùng quy ước **365 ngày/năm**.

        **4. Hình thức nhận lãi**:
        - **Cuối kỳ**: ngày rút nhận gốc + toàn bộ lãi.
        - **Hàng tháng**: lãi được tính và thể hiện theo từng tháng; ngày rút nhận lại gốc.
        - **Đầu kỳ**: toàn bộ lãi được xác định/nhận trước; ngày rút nhận lại gốc.

        **5. Lãi đơn** — lãi chỉ tính trên tiền gốc ban đầu.

        **6. Lãi kép** — chỉ cho phép khi chọn **Cuối kỳ**. Lãi được tích lũy hàng ngày và nhập vào số dư để tiếp tục sinh lãi.

        **7. Ngày tính lãi** — tính từ **ngày khách hàng gửi tiền**, bao gồm ngày gửi, đến **trước một ngày của ngày rút**; ngày rút không tính.
        """
    )

with st.expander("🧮 Tóm tắt công thức"):
    st.markdown(
        """
        **Lãi đơn:** `Tiền lãi = Tiền gốc × Lãi suất năm × Số ngày / 365`

        **Lãi kép:** `Tổng tiền = Gốc × (1 + Lãi suất năm / (100 × 365)) ^ Số ngày`

        **Tổng tiền = Tiền gốc + Tiền lãi**
        """
    )

st.divider()
st.caption("🏦 Hệ thống tính tiền gửi tiết kiệm | Streamlit + Plotly | 365 ngày/năm | Ngày gửi tính lãi, ngày rút không tính lãi")
