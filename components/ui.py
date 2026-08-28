from __future__ import annotations

import urllib.parse
import plotly.graph_objects as go
import streamlit as st
import config
from utils.asset_helpers import image_to_data_uri

# ------------------------------------------------------------------
# IKON (SVG inline, mewarisi warna teks via currentColor)
# ------------------------------------------------------------------
AMENITY_ICONS = {
    "resto": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 3v8a2 2 0 002 2v8M4 3v0M7 3v8M10 3v8m0 0a2 2 0 002-2V3M17 3v18M17 3c-3 0-3 4-3 6s0 4 3 4"/></svg>',
    "mushola": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 2v3M8 8a4 4 0 118 0c0 2-2 3-2 5h-4c0-2-2-3-2-5z"/><path d="M4 22v-6a8 8 0 0116 0v6"/><path d="M4 22h16"/></svg>',
    "fasilitas": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/></svg>',
}
PIN_ICON = (
    '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2"><path d="M12 21s7-7.5 7-12a7 7 0 00-14 0c0 4.5 7 12 7 12z"/>'
    '<circle cx="12" cy="9" r="2.5"/></svg>'
)

# ------------------------------------------------------------------
# CSS GLOBAL & TEMA (MOBILE OPTIMIZED)
# ------------------------------------------------------------------
def inject_global_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ritam-bg: #16241c;
            --ritam-card-bg: #24392c;
            --ritam-card-bg-alt: #1d2f24;
            --ritam-text: #eee9dc;
            --ritam-text-muted: #b7bfae;
            --ritam-text-dim: #7c8a76;
            --ritam-line-rgb: 238,233,220;

            --ritam-accent: #f2b544;
            --ritam-accent-rgb: 242,181,68;
            --ritam-danger: #e6572a;
            --ritam-danger-rgb: 230,87,42;
            --ritam-success: #7fae67;
            --ritam-success-rgb: 127,174,103;
            --ritam-info: #7fb1f7;
            --ritam-info-rgb: 127,177,247;
        }

        /* 1. Sembunyikan elemen Streamlit bawaan secara total */
        #MainMenu, header[data-testid="stHeader"], footer, .stDeployButton { 
            display: none !important; 
        }

        /* 2. Latar belakang luar (desktop) dibuat gelap pekat agar kontras */
        .stApp { 
            background-color: #0b120e; 
            color: var(--ritam-text); 
        }

        /* 3. Container utama dipaksa menjadi bingkai HP (Mobile Frame) */
        .block-container { 
            background-color: var(--ritam-bg) !important;
            max-width: 430px !important; /* Standar lebar layar iPhone Max */
            margin: 0 auto !important;
            padding: 0 16px 80px 16px !important;
            min-height: 100vh !important;
            box-shadow: 0 0 30px rgba(0,0,0,0.6);
            position: relative;
        }

        h1, h2, h3, h4 { font-family: 'Trebuchet MS', sans-serif; letter-spacing: 0.02em; }

        /* 4. Sticky Topbar agar navigasi selalu di atas saat di-scroll */
        .st-key-ritam_topbar {
            position: sticky !important;
            top: 0 !important;
            z-index: 1000 !important;
            background: rgba(22, 36, 28, 0.90) !important;
            backdrop-filter: blur(8px);
            padding: 16px 0 8px 0 !important;
            margin: 0 -16px 12px -16px !important;
            border-bottom: 1px solid rgba(var(--ritam-line-rgb), 0.1);
        }
        .st-key-ritam_topbar > div { padding: 0 16px; }

        .ritam-brand { display:flex; align-items:center; gap:8px; }
        .ritam-dot-ring { width:26px; height:26px; border-radius:50%; border:2px solid var(--ritam-accent); position:relative; flex-shrink:0; }
        .ritam-dot-ring::after { content:''; position:absolute; inset:0; margin:auto; width:5px; height:5px; border-radius:50%; background:var(--ritam-accent); }
        .ritam-brand span { font-family:'Trebuchet MS',sans-serif; font-size:16px; font-weight:bold; letter-spacing:0.04em; }
        
        .ritam-status { font-family:monospace; font-size:10px; color:var(--ritam-text-dim); display:flex; align-items:center; gap:5px; margin-bottom: 16px; }
        .ritam-status-dot { width:7px; height:7px; border-radius:50%; background:var(--ritam-success); box-shadow:0 0 6px var(--ritam-success); }
        .ritam-heading { font-size:14px; color:var(--ritam-text-muted); margin-bottom:2px; line-height: 1.4; }
        .ritam-heading b { color:var(--ritam-text); }

        .ritam-photo-card { position:relative; border-radius:14px; overflow:hidden; height:160px; background-size:cover; background-position:center; margin-bottom:8px; border:1px solid rgba(var(--ritam-line-rgb),0.12); }
        .ritam-photo-overlay { position:absolute; inset:0; background:linear-gradient(180deg, rgba(22,36,28,0) 30%, rgba(22,36,28,0.95) 100%); display:flex; flex-direction:column; justify-content:flex-end; padding:12px; }
        .ritam-photo-zone { position:absolute; top:8px; right:8px; font-family:monospace; font-size:9.5px; padding:4px 10px; border-radius:20px; font-weight:bold; }
        .ritam-photo-zone.merah { background:rgba(var(--ritam-danger-rgb),0.9); color:#fff; }
        .ritam-photo-zone.kuning { background:rgba(var(--ritam-accent-rgb),0.9); color:#412402; }
        .ritam-photo-title { font-size:14.5px; font-weight:700; color:#fff; margin-bottom:3px; line-height:1.2; }
        .ritam-photo-cat { font-size:11px; color:#d8ddd0; }
        .ritam-photo-edit-flag { position:absolute; top:8px; left:8px; width:28px; height:28px; border-radius:50%; background:rgba(var(--ritam-accent-rgb),0.9); color:#1a1230; display:flex; align-items:center; justify-content:center; font-size:13px; z-index:2; }

        /* 5. Touch Targets: Tinggi tombol minimal 46px untuk layar sentuh */
        div[data-testid="stButton"] > button { 
            width:100%; 
            background:var(--ritam-card-bg) !important; 
            border:1px solid rgba(var(--ritam-line-rgb),0.2) !important; 
            color:var(--ritam-text) !important; 
            font-size:13px !important; 
            min-height: 46px !important; 
            border-radius: 12px !important;
            margin-bottom:16px; 
            transition: border-color .15s ease, color .15s ease;
        }
        div[data-testid="stButton"] > button:active { border-color:var(--ritam-accent) !important; color:var(--ritam-accent) !important; }
        
        .ritam-back button { 
            width:auto !important; 
            background:none !important; 
            border:none !important; 
            color:var(--ritam-text-muted) !important; 
            font-size:13px !important; 
            min-height: 36px !important;
            padding:0 !important; 
            margin-bottom:12px !important; 
        }

        button[data-baseweb="tab"] { font-size: 14px; padding: 14px 6px; }
        div[data-baseweb="tab-list"] { gap: 4px; }
        div[data-baseweb="tab-highlight"] { background-color:var(--ritam-accent) !important; }

        .ritam-tag { display:inline-block; font-family: monospace; font-size: 10.5px; padding: 4px 10px; border-radius: 20px; border: 1px solid rgba(var(--ritam-line-rgb),0.2); color:var(--ritam-text-muted); margin-right:6px; margin-bottom:8px; }
        .ritam-tag.zone { color:var(--ritam-danger); border-color:rgba(var(--ritam-danger-rgb),0.4); background:rgba(var(--ritam-danger-rgb),0.12); font-weight:bold; }
        .ritam-hero { border-radius:14px; overflow:hidden; height:180px; background-size:cover; background-position:center; margin-bottom:16px; border:1px solid rgba(var(--ritam-line-rgb),0.12); }

        .ritam-evac { background: linear-gradient(160deg, rgba(var(--ritam-danger-rgb),0.12), transparent 65%); border:1px solid rgba(var(--ritam-danger-rgb),0.4); border-radius:14px; padding:20px 16px; text-align:center; margin-bottom:16px; }
        .ritam-evac h3 { font-family:'Trebuchet MS',sans-serif; font-size:18px; margin:8px 0 14px; }
        .ritam-eyebrow { font-family:monospace; font-size:11px; letter-spacing:0.1em; color:var(--ritam-danger); text-transform:uppercase; }
        .ritam-meta-row { display:flex; justify-content:center; gap:20px; flex-wrap:wrap; margin-bottom:14px; }
        .ritam-meta-row div { font-family:monospace; font-size:11px; color:var(--ritam-text-muted); }
        .ritam-meta-row b { display:block; font-size:16px; color:var(--ritam-text); font-family:Georgia,serif; margin-top:4px; }
        .ritam-note { font-size:13px; color:var(--ritam-text-muted); line-height:1.6; text-align:left; border-top:1px solid rgba(var(--ritam-danger-rgb),0.25); padding-top:12px; }

        .ritam-step { background:var(--ritam-card-bg); border:1px solid rgba(var(--ritam-line-rgb),0.12); border-radius:12px; padding:16px; font-size:13.5px; color:#cfd6c6; line-height:1.55; display:flex; gap:14px; align-items:flex-start; margin-bottom:12px; }
        .ritam-step-num { font-family:monospace; font-size:12px; font-weight:bold; color:var(--ritam-accent); background:rgba(var(--ritam-accent-rgb),0.15); border-radius:50%; width:28px; height:28px; display:flex; align-items:center; justify-content:center; flex-shrink:0; margin-top:2px; }

        .ritam-card { background:var(--ritam-card-bg); border:1px solid rgba(var(--ritam-line-rgb),0.12); border-radius:12px; padding:16px; margin-bottom:14px; }
        .ritam-card h4 { font-family:'Trebuchet MS',sans-serif; font-size:13px; letter-spacing:0.04em; text-transform:uppercase; margin-bottom:0; }
        .amen-head { display:flex; align-items:center; gap:12px; margin-bottom:14px; }
        .amen-icon-circle { width:34px; height:34px; border-radius:50%; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
        .amen-icon-circle.resto { background:rgba(var(--ritam-accent-rgb),0.15); color:var(--ritam-accent); }
        .amen-icon-circle.mushola { background:rgba(var(--ritam-success-rgb),0.15); color:var(--ritam-success); }
        .amen-icon-circle.fasilitas { background:rgba(var(--ritam-info-rgb),0.15); color:var(--ritam-info); }

        .ritam-item { display:flex; justify-content:space-between; align-items:center; padding:12px 0; border-top:1px solid rgba(var(--ritam-line-rgb),0.10); font-size:13.5px; color:#cfd6c6; gap:12px; }
        .ritam-item:first-of-type { border-top:none; }
        .ritam-item-left { display:flex; align-items:center; gap:10px; }
        .ritam-item-left svg { opacity:0.6; flex-shrink:0; }
        .ritam-item-thumb { width:40px; height:40px; border-radius:10px; object-fit:cover; flex-shrink:0; border:1px solid rgba(var(--ritam-line-rgb),0.15); }
        .ritam-item-thumb-empty { display:flex; align-items:center; justify-content:center; background:rgba(var(--ritam-line-rgb),0.05); color:var(--ritam-text-dim); }
        .ritam-dist-pill { font-family:monospace; font-size:10.5px; padding:4px 10px; border-radius:20px; white-space:nowrap; flex-shrink:0; font-weight:bold; }
        .ritam-dist-pill.resto { background:rgba(var(--ritam-accent-rgb),0.12); color:var(--ritam-accent); }
        .ritam-dist-pill.mushola { background:rgba(var(--ritam-success-rgb),0.12); color:var(--ritam-success); }
        .ritam-dist-pill.fasilitas { background:rgba(var(--ritam-info-rgb),0.12); color:var(--ritam-info); }

        .ritam-footer { font-size:11px; color:var(--ritam-text-dim); line-height:1.6; padding-top:16px; text-align:center; }
        .ritam-social-sub { font-size:12px; color:#8a9384; margin:-4px 0 14px; line-height:1.5; }
        .ritam-social-pill { flex:1; min-width:96px; text-align:center; padding:12px; border-radius:12px; font-size:12px; font-weight:700; text-decoration:none; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:6px; border:1px solid; line-height:1.3; }
        .ritam-social-pill span.handle { font-size:10px; font-weight:400; opacity:0.85; }
        .ritam-social-pill.ig { background:rgba(214,65,122,0.13); color:#e78bb0; border-color:rgba(214,65,122,0.35); }

        .ritam-admin-toggle button { background:none !important; border:1px solid rgba(var(--ritam-line-rgb),0.2) !important; color:var(--ritam-text-dim) !important; font-size:12px !important; padding:6px 12px !important; border-radius:20px !important; min-height:36px !important; width:auto !important; margin-bottom:0 !important; }
        .ritam-admin-badge { display:inline-flex; align-items:center; gap:6px; font-family:monospace; font-size:10.5px; color:var(--ritam-accent); background:rgba(var(--ritam-accent-rgb),0.12); border:1px solid rgba(var(--ritam-accent-rgb),0.35); padding:4px 12px; border-radius:20px; margin-bottom:14px; font-weight:bold; }
        .ritam-login-box { background:var(--ritam-card-bg-alt); border:1px solid rgba(var(--ritam-line-rgb),0.15); border-radius:12px; padding:16px; margin-bottom:16px; }

        .ritam-empty-state { text-align:center; padding:24px 16px; color:var(--ritam-text-dim); font-size:13px; border:1px dashed rgba(var(--ritam-line-rgb),0.2); border-radius:12px; }
        .ritam-subtitle { font-size:12.5px; color:var(--ritam-text-dim); line-height:1.5; margin:-4px 0 16px; max-width:340px; }

        .ritam-legend { display:flex; flex-wrap:wrap; gap:8px; margin-bottom:16px; }
        .ritam-legend-chip { font-size:11px; padding:6px 12px 6px 10px; border-radius:20px; display:inline-flex; align-items:center; gap:8px; border:1px solid; font-weight:600; }
        .ritam-legend-chip::before { content:''; width:8px; height:8px; border-radius:50%; flex-shrink:0; }
        .ritam-legend-chip.merah { color:var(--ritam-danger); border-color:rgba(var(--ritam-danger-rgb),0.4); background:rgba(var(--ritam-danger-rgb),0.1); }
        .ritam-legend-chip.merah::before { background:var(--ritam-danger); }
        .ritam-legend-chip.kuning { color:var(--ritam-accent); border-color:rgba(var(--ritam-accent-rgb),0.4); background:rgba(var(--ritam-accent-rgb),0.1); }
        .ritam-legend-chip.kuning::before { background:var(--ritam-accent); }

        div[data-testid="stButton"] > button[kind="primary"] {
            background: var(--ritam-accent) !important;
            color: var(--ritam-bg) !important;
            border-color: var(--ritam-accent) !important;
            font-weight: 700 !important;
        }

        .ritam-stat-row { display:flex; gap:12px; margin-bottom:16px; }
        .ritam-stat-pill { flex:1; background:var(--ritam-card-bg); border:1px solid rgba(var(--ritam-line-rgb),0.12); border-radius:12px; padding:12px; text-align:center; }
        .ritam-stat-pill b { display:block; font-size:18px; color:var(--ritam-accent); font-family:Georgia,serif; }
        .ritam-stat-pill span { font-size:10px; color:var(--ritam-text-dim); text-transform:uppercase; letter-spacing:0.04em; font-weight:600; }

        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea {
            background-color: var(--ritam-card-bg-alt) !important;
            color: var(--ritam-text) !important;
            border: 1px solid rgba(var(--ritam-line-rgb),0.2) !important;
            padding: 12px !important;
            border-radius: 10px !important;
        }
        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stTextArea"] textarea:focus {
            border-color: var(--ritam-accent) !important;
            box-shadow: 0 0 0 1px var(--ritam-accent) !important;
        }
        div[data-testid="stFormSubmitButton"] button {
            background: rgba(var(--ritam-accent-rgb), 0.15) !important;
            border: 1px solid rgba(var(--ritam-accent-rgb), 0.4) !important;
            color: var(--ritam-accent) !important;
            font-weight: bold !important;
        }
        div[data-testid="stSlider"] [role="slider"] { background-color: var(--ritam-accent) !important; }
        div[data-testid="stSlider"] > div > div > div { background: rgba(var(--ritam-accent-rgb),0.35) !important; }

        .st-key-ritam_topbar div[data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; flex-direction: row !important; gap: 8px !important; align-items:center !important;}
        .st-key-ritam_topbar div[data-testid="column"] { width: auto !important; min-width: 0 !important; flex: initial !important; }
        .st-key-ritam_topbar div[data-testid="column"]:first-child { flex: 1 1 auto !important; }
        .st-key-ritam_topbar div[data-testid="column"]:last-child { flex: 0 0 auto !important; }

        /* --- PERBAIKAN TOMBOL FILTER PADA LAYAR HP --- */
        .st-key-ritam_filter_bar {
            margin-bottom: 16px;
        }
        .st-key-ritam_filter_bar div[data-testid="stHorizontalBlock"] {
            flex-wrap: nowrap !important;
            flex-direction: row !important;
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch;
            gap: 6px !important;
            padding-bottom: 4px;
        }
        .st-key-ritam_filter_bar div[data-testid="column"] {
            width: auto !important;
            min-width: max-content !important;
            flex: 1 1 auto !important;
        }
        .st-key-ritam_filter_bar div[data-testid="stButton"] > button {
            white-space: nowrap !important;
            padding: 0 10px !important;
            margin-bottom: 0 !important;
            min-height: 38px !important;
            font-size: 12px !important;
        }
        .st-key-ritam_filter_bar div[data-testid="stHorizontalBlock"]::-webkit-scrollbar {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def inject_admin_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ritam-accent: #a78bfa;
            --ritam-accent-rgb: 167,139,250;
        }
        .ritam-admin-banner {
            background:repeating-linear-gradient(135deg, #a78bfa, #a78bfa 10px, #8b6ff0 10px, #8b6ff0 20px);
            color:#1a1230; font-family:'Trebuchet MS',sans-serif; font-size:11px; font-weight:700;
            letter-spacing:0.06em; text-transform:uppercase; text-align:center; padding:6px;
            margin:-14px -16px 14px; border-radius:0 0 8px 8px;
        }
        .ritam-admin-badge { color:#c4b5fd !important; }
        </style>
        <div class="ritam-admin-banner">⚙️ Mode Admin — tampilan khusus tim pengelola RITAM</div>
        """,
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------------
# RENDER LOGIC
# ------------------------------------------------------------------
def render_topbar(is_admin: bool, admin_name: str | None) -> str:
    action = ""
    with st.container(key="ritam_topbar"):
        top_l, top_r = st.columns([3, 1], gap="small")
        with top_l:
            st.markdown(
                '<div class="ritam-brand" style="margin-bottom:6px;">'
                '<div class="ritam-dot-ring"></div><span>RITAM</span></div>',
                unsafe_allow_html=True,
            )
        with top_r:
            st.markdown('<div class="ritam-admin-toggle" style="text-align:right;">', unsafe_allow_html=True)
            if is_admin:
                if st.button(f"🔓 {admin_name}", key="admin_logout_btn"):
                    action = "logout"
            else:
                if st.button("🔒 Admin", key="admin_login_toggle"):
                    action = "login_toggle"
            st.markdown("</div>", unsafe_allow_html=True)
    return action

def render_status_bar(is_admin: bool, admin_name: str | None) -> None:
    st.markdown(
        '<div class="ritam-subtitle">Peta jalur & panduan evakuasi mandiri untuk pengunjung '
        'kawasan wisata Cikole–Lembang saat kondisi darurat.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ritam-status" style="margin:-6px 0 14px;">'
        '<span class="ritam-status-dot"></span> NORMAL · DEMO</div>',
        unsafe_allow_html=True,
    )
    if is_admin:
        st.markdown(
            f'<div class="ritam-admin-badge">⚙️ Mode admin — masuk sebagai <b>{admin_name}</b></div>',
            unsafe_allow_html=True,
        )

def render_type_filter(active: str, counts: dict) -> str | None:
    options = [
        ("semua", "Semua"),
        ("wisata", "🧭 Wisata"),
        ("resto", "🍽️ Resto"),
        ("penginapan", "🛏️ Penginapan"),
    ]
    clicked = None
    with st.container(key="ritam_filter_bar"):
        cols = st.columns(len(options))
        for col, (key, label) in zip(cols, options):
            with col:
                full_label = f"{label} ({counts.get(key, 0)})"
                if st.button(full_label, key=f"filter_{key}", type="primary" if active == key else "secondary"):
                    clicked = key
    return clicked

def render_zone_legend() -> None:
    config.render_html(
        '<div class="ritam-legend">'
        '<span class="ritam-legend-chip merah">Zona Merah — risiko tinggi</span>'
        '<span class="ritam-legend-chip kuning">Zona Kuning — risiko sedang</span>'
        '</div>'
    )

def render_stat_row(wisata_n: int, resto_n: int, penginapan_n: int) -> None:
    config.render_html(
        f"""
        <div class="ritam-stat-row">
          <div class="ritam-stat-pill"><b>{wisata_n}</b><span>Wisata</span></div>
          <div class="ritam-stat-pill"><b>{resto_n}</b><span>Resto</span></div>
          <div class="ritam-stat-pill"><b>{penginapan_n}</b><span>Penginapan</span></div>
        </div>
        """
    )

def render_locate_me_widget() -> None:
    config.render_html(
        """
        <div style="margin-bottom:14px;">
          <button id="ritam-geo-btn" type="button" style="
              width:100%; background:rgba(var(--ritam-accent-rgb),0.14);
              border:1px solid rgba(var(--ritam-accent-rgb),0.4); color:var(--ritam-accent);
              font-size:13px; font-weight:600; padding:12px; border-radius:12px;
              cursor:pointer; font-family:'Trebuchet MS',sans-serif;">
            📍 Gunakan lokasi saya sebagai titik awal
          </button>
          <div id="ritam-geo-msg" style="font-size:11px; color:var(--ritam-text-dim); margin-top:6px; text-align:center;"></div>
        </div>
        <script>
        (function () {
          var btn = document.getElementById('ritam-geo-btn');
          var msg = document.getElementById('ritam-geo-msg');
          if (!btn) return;
          btn.addEventListener('click', function () {
            if (!('geolocation' in navigator)) {
              msg.textContent = 'Perangkat/browser ini tidak mendukung layanan lokasi.';
              return;
            }
            btn.disabled = true;
            btn.textContent = '📡 Mencari lokasi Anda...';
            navigator.geolocation.getCurrentPosition(
              function (pos) {
                var url = new URL(window.location.href);
                url.searchParams.set('lat', pos.coords.latitude);
                url.searchParams.set('lon', pos.coords.longitude);
                window.location.href = url.toString();
              },
              function (err) {
                btn.disabled = false;
                btn.textContent = '📍 Gunakan lokasi saya sebagai titik awal';
                var text = 'Gagal mengambil lokasi.';
                if (err.code === 1) text = 'Izin lokasi ditolak.';
                else if (err.code === 2) text = 'Posisi tidak tersedia.';
                else if (err.code === 3) text = 'Permintaan lokasi melebihi batas waktu.';
                msg.textContent = text;
              },
              { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
            );
          });
        })();
        </script>
        """,
        allow_js=True,
    )

def render_admin_login_form(auth_available: bool):
    st.markdown('<div class="ritam-login-box">', unsafe_allow_html=True)
    if not auth_available:
        st.warning(
            "Login admin belum dikonfigurasi. Tambahkan bagian **[admins]** pada `.streamlit/secrets.toml`.",
            icon="🔒",
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return None

    result = None
    with st.form("admin_login_form", clear_on_submit=True):
        uname = st.text_input("Username", placeholder="Username")
        pw = st.text_input("Password", type="password", placeholder="Password")
        submitted = st.form_submit_button("Masuk")
        if submitted:
            result = (uname, pw)
    st.markdown("</div>", unsafe_allow_html=True)
    return result

def compass_figure(bearing: int) -> go.Figure:
    fig = go.Figure()
    theta_ring = list(range(0, 361, 5))
    fig.add_trace(go.Scatterpolar(
        r=[1] * len(theta_ring), theta=theta_ring, mode="lines",
        line=dict(color="rgba(238,233,220,0.15)", width=1), showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatterpolar(
        r=[0.68] * len(theta_ring), theta=theta_ring, mode="lines",
        line=dict(color="rgba(238,233,220,0.08)", width=1), showlegend=False, hoverinfo="skip",
    ))
    polar_theta = (90 - bearing) % 360
    fig.add_trace(go.Scatterpolar(
        r=[0, 1], theta=[polar_theta, polar_theta], mode="lines",
        line=dict(color="#e6572a", width=6), showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatterpolar(
        r=[0, -0.7], theta=[polar_theta, polar_theta], mode="lines",
        line=dict(color="#4a5c46", width=6), showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatterpolar(
        r=[0], theta=[0], mode="markers",
        marker=dict(size=16, color="#f2b544"), showlegend=False, hoverinfo="skip",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=False, range=[-1, 1]),
            angularaxis=dict(
                tickmode="array", tickvals=[90, 0, 270, 180], ticktext=["U", "T", "S", "B"],
                tickfont=dict(color="#7c8a76", size=13, family="monospace"),
                showline=False, gridcolor="rgba(0,0,0,0)",
            ),
        ),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False, margin=dict(l=10, r=10, t=10, b=10), height=200,
    )
    return fig

def _zone_class(zone: str) -> str:
    return "merah" if "Merah" in zone else "kuning"

def render_spot_grid(spots: list, is_admin: bool) -> str | None:
    clicked_id = None
    cols = st.columns(2)
    for i, spot in enumerate(spots):
        with cols[i % 2]:
            data_uri = image_to_data_uri(spot["image"])
            bg_style = f"background-image:url('{data_uri}')" if data_uri else "background:var(--ritam-card-bg);"
            zc = _zone_class(spot["zone"])
            edit_flag = '<div class="ritam-photo-edit-flag">✎</div>' if is_admin else ""
            st.markdown(
                f"""
                <div class="ritam-photo-card" style="{bg_style}">
                  {edit_flag}
                  <div class="ritam-photo-zone {zc}">{spot['zone']}</div>
                  <div class="ritam-photo-overlay">
                    <div class="ritam-photo-title">{spot['name']}</div>
                    <div class="ritam-photo-cat">{spot['category']}</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            btn_label = "✎ Kelola data lokasi" if is_admin else "Lihat arah evakuasi"
            if st.button(btn_label, key=f"btn_{spot['id']}"):
                clicked_id = spot["id"]
    return clicked_id

def render_detail_header(spot: dict) -> None:
    data_uri = image_to_data_uri(spot["image"])
    bg_style = f"background-image:url('{data_uri}')" if data_uri else "background:var(--ritam-card-bg);"
    st.markdown(f'<div class="ritam-hero" style="{bg_style}"></div>', unsafe_allow_html=True)
    st.markdown(f"### {spot['name']}")
    st.markdown(
        f'<span class="ritam-tag">{spot["category"]}</span>'
        f'<span class="ritam-tag zone">{spot["zone"]}</span>'
        f'<span class="ritam-tag">Tiket {spot["ticket"]}</span>',
        unsafe_allow_html=True,
    )

def render_sop_steps() -> None:
    steps = [
        ("Lindungi diri", "Jauhi kaca, papan reklame, dan pohon/tebing tinggi. Lindungi kepala."),
        ("Tetap tenang", "Jangan berlari panik. Ikuti arah petunjuk staf & papan evakuasi."),
        ("Bantu Kelompok Rentan", "Bantu lansia, anak-anak, dan penyandang disabilitas untuk evakuasi."),
        ("Menuju titik kumpul", "Bergerak ke titik kumpul terbuka sesuai arah pada tab Evakuasi."),
        ("Tunggu instruksi", "Tetap di titik kumpul hingga ada instruksi resmi dari petugas/BPBD."),
    ]
    for i, (label, text) in enumerate(steps, start=1):
        st.markdown(
            f'<div class="ritam-step"><span class="ritam-step-num">{i}</span>'
            f'<div><b>{label}</b><br>{text}</div></div>',
            unsafe_allow_html=True,
        )

def render_amenity_card(title: str, items: list, kind: str) -> None:
    if not items:
        st.markdown(
            f'<div class="ritam-card"><div class="amen-head">'
            f'<div class="amen-icon-circle {kind}">{AMENITY_ICONS[kind]}</div><h4>{title}</h4></div>'
            f'<div class="ritam-empty-state">Belum ada data untuk kategori ini.</div></div>',
            unsafe_allow_html=True,
        )
        return

    rows = ""
    for item in items:
        name, dist = item[0], item[1]
        photo = item[2] if len(item) > 2 and item[2] else None
        thumb_uri = image_to_data_uri(photo) if photo else ""
        thumb = (
            f'<img class="ritam-item-thumb" src="{thumb_uri}" alt="">'
            if thumb_uri
            else f'<span class="ritam-item-thumb ritam-item-thumb-empty">{PIN_ICON}</span>'
        )
        rows += (
            f'<div class="ritam-item">'
            f'<span class="ritam-item-left">{thumb}<span>{name}</span></span>'
            f'<span class="ritam-dist-pill {kind}">{dist}</span>'
            f"</div>"
        )
    st.markdown(
        f"""
        <div class="ritam-card">
          <div class="amen-head">
            <div class="amen-icon-circle {kind}">{AMENITY_ICONS[kind]}</div>
            <h4>{title}</h4>
          </div>
          {rows}
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_social_card(spot: dict) -> None:
    # Safe lookup: gunakan key 'social' jika ada, fallback ke 'contact'
    social_data = spot.get("social") or spot.get("contact", {})
    
    # Jika tidak ada data Instagram, hentikan eksekusi tanpa throw Error
    if not social_data or not social_data.get("instagram"):
        return
        
    name_q = urllib.parse.quote(spot["name"])
    ig = social_data.get("instagram", "")
    ig_url = social_data.get("instagram_url") or f"https://www.instagram.com/explore/tags/{name_q}/"

    st.markdown(
        f"""
        <div class="ritam-card">
          <h4>📣 Info & Promo Terbaru</h4>
          <div class="ritam-social-sub">Follow Instagram resmi untuk update promo tiket dan wahana di {spot['name']}.</div>
          <a class="ritam-social-pill ig" href="{ig_url}" target="_blank" rel="noopener"
             style="width:100%; flex-direction:row; justify-content:flex-start; gap:10px; padding:12px 14px;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" style="flex-shrink:0">
              <rect x="3" y="3" width="18" height="18" rx="5.5"/>
              <circle cx="12" cy="12" r="4"/>
              <circle cx="17.3" cy="6.7" r="0.6" fill="currentColor" stroke="none"/>
            </svg>
            <span style="display:flex; flex-direction:column; align-items:flex-start; gap:1px;">
              <span style="font-size:12.5px; font-weight:600;">Instagram</span>
              <span class="handle">{ig}</span>
            </span>
          </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_map_card(image_path: str, title: str = "Peta Kawasan Wisata", desc: str = "Panduan visual area dan rute evakuasi di dalam kawasan.") -> None:
    # Render header/judul card
    st.markdown(
        f"""
        <div class="ritam-card" style="margin-bottom: 0; border-bottom-left-radius: 0; border-bottom-right-radius: 0; border-bottom: none;">
          <h4>🗺️ {title}</h4>
          <div class="ritam-social-sub" style="margin-bottom: 8px;">{desc}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Render gambar (dibungkus dalam try-except agar tidak crash jika file gambar tidak ditemukan)
    try:
        # st.image otomatis memberikan fitur klik-untuk-perbesar (lightbox) pada gambar
        st.image(image_path, use_container_width=True)
        # Menutup styling bagian bawah agar rapi
        st.markdown('<div style="margin-bottom: 16px;"></div>', unsafe_allow_html=True)
    except Exception:
        st.error("⚠️ File gambar peta tidak ditemukan. Pastikan file ada di path yang benar.")

def render_footer(text: str) -> None:
    st.markdown(
        f'<div class="ritam-footer">{text}</div>',
        unsafe_allow_html=True,
    )
