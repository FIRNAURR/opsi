"""
components/ui.py
=================
Seluruh elemen presentasi aplikasi: injeksi CSS global, kompas arah,
kartu grid wisata, kartu amenitas/sosial media, topbar, dan form
login admin.

DESAIN TEMA
-----------
CSS dibangun di atas CSS custom properties (variabel) sehingga tema
gelap (default) dan tema admin (ungu) cukup meng-override beberapa
variabel warna di :root — bukan menduplikasi puluhan aturan seperti
pada versi sebelumnya. Ini menjamin konsistensi warna di seluruh
elemen (tombol, tag, border, input form, kompas) tanpa risiko ada
elemen yang "lupa" di-override saat mode admin aktif.

Fungsi di modul ini murni untuk RENDER. Pemanggilan jaringan/OSRM
sengaja tidak dilakukan di sini — itu tanggung jawab
`utils/map_helpers.py`, dipanggil dari `main.py` — agar lapisan UI
tetap mudah diuji dan tidak bercampur dengan I/O eksternal.
"""

import urllib.parse

import plotly.graph_objects as go
import streamlit as st

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
# CSS GLOBAL & TEMA
# ------------------------------------------------------------------
def inject_global_css() -> None:
    """CSS utama aplikasi. Dipanggil sekali per rerun dari main.py."""
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

        #MainMenu, header[data-testid="stHeader"], footer, .stDeployButton { visibility: hidden; height:0; }
        .stApp { background-color: var(--ritam-bg); color: var(--ritam-text); }
        .block-container { max-width: 460px; padding-top: 14px; padding-bottom: 60px; padding-left: 16px; padding-right: 16px; }
        h1, h2, h3, h4 { font-family: 'Trebuchet MS', sans-serif; letter-spacing: 0.02em; }

        .ritam-brand { display:flex; align-items:center; gap:8px; }
        .ritam-dot-ring { width:26px; height:26px; border-radius:50%; border:2px solid var(--ritam-accent); position:relative; flex-shrink:0; transition: border-color .2s ease; }
        .ritam-dot-ring::after { content:''; position:absolute; inset:0; margin:auto; width:5px; height:5px; border-radius:50%; background:var(--ritam-accent); transition: background-color .2s ease; }
        .ritam-brand span { font-family:'Trebuchet MS',sans-serif; font-size:15px; letter-spacing:0.04em; }
        .ritam-status { font-family:monospace; font-size:9.5px; color:var(--ritam-text-dim); display:flex; align-items:center; gap:5px; }
        .ritam-status-dot { width:7px; height:7px; border-radius:50%; background:var(--ritam-success); box-shadow:0 0 6px var(--ritam-success); }
        .ritam-heading { font-size:13px; color:var(--ritam-text-muted); margin-bottom:2px; }
        .ritam-heading b { color:var(--ritam-text); }

        .ritam-photo-card { position:relative; border-radius:14px; overflow:hidden; height:150px; background-size:cover; background-position:center; margin-bottom:6px; border:1px solid rgba(var(--ritam-line-rgb),0.12); transition: transform .15s ease; }
        .ritam-photo-card:hover { transform: translateY(-2px); }
        .ritam-photo-overlay { position:absolute; inset:0; background:linear-gradient(180deg, rgba(22,36,28,0) 35%, rgba(22,36,28,0.92) 100%); display:flex; flex-direction:column; justify-content:flex-end; padding:10px 12px; }
        .ritam-photo-zone { position:absolute; top:8px; right:8px; font-family:monospace; font-size:8.5px; padding:3px 8px; border-radius:20px; backdrop-filter:blur(2px); }
        .ritam-photo-zone.merah { background:rgba(var(--ritam-danger-rgb),0.85); color:#fff; }
        .ritam-photo-zone.kuning { background:rgba(var(--ritam-accent-rgb),0.9); color:#412402; }
        .ritam-photo-title { font-size:13.5px; font-weight:600; color:#fff; margin-bottom:2px; line-height:1.25; }
        .ritam-photo-cat { font-size:10px; color:#d8ddd0; }
        .ritam-photo-edit-flag { position:absolute; top:8px; left:8px; width:26px; height:26px; border-radius:50%; background:rgba(var(--ritam-accent-rgb),0.9); color:#1a1230; display:flex; align-items:center; justify-content:center; font-size:12px; z-index:2; }

        div[data-testid="stButton"] > button { width:100%; background:var(--ritam-card-bg) !important; border:1px solid rgba(var(--ritam-line-rgb),0.18) !important; color:var(--ritam-text) !important; font-size:12px !important; padding:8px !important; margin-bottom:16px; transition: border-color .15s ease, color .15s ease; }
        div[data-testid="stButton"] > button:hover { border-color:var(--ritam-accent) !important; color:var(--ritam-accent) !important; }
        .ritam-back button { width:auto !important; background:none !important; border:none !important; color:var(--ritam-text-muted) !important; font-size:12px !important; padding:0 !important; margin-bottom:10px !important; }

        button[data-baseweb="tab"] { font-size: 13px; padding: 10px 6px; }
        div[data-baseweb="tab-list"] { gap: 4px; }
        div[data-baseweb="tab-highlight"] { background-color:var(--ritam-accent) !important; }

        .ritam-tag { display:inline-block; font-family: monospace; font-size: 10px; padding: 3px 9px; border-radius: 20px; border: 1px solid rgba(var(--ritam-line-rgb),0.2); color:var(--ritam-text-muted); margin-right:6px; margin-bottom:6px; }
        .ritam-tag.zone { color:var(--ritam-danger); border-color:rgba(var(--ritam-danger-rgb),0.4); background:rgba(var(--ritam-danger-rgb),0.12); }
        .ritam-hero { border-radius:14px; overflow:hidden; height:150px; background-size:cover; background-position:center; margin-bottom:14px; border:1px solid rgba(var(--ritam-line-rgb),0.12); }

        .ritam-evac { background: linear-gradient(160deg, rgba(var(--ritam-danger-rgb),0.10), transparent 65%); border:1px solid rgba(var(--ritam-danger-rgb),0.35); border-radius:14px; padding:18px; text-align:center; margin-bottom:14px; }
        .ritam-evac h3 { font-family:'Trebuchet MS',sans-serif; font-size:17px; margin:6px 0 12px; }
        .ritam-eyebrow { font-family:monospace; font-size:10px; letter-spacing:0.1em; color:var(--ritam-danger); text-transform:uppercase; }
        .ritam-meta-row { display:flex; justify-content:center; gap:16px; flex-wrap:wrap; margin-bottom:12px; }
        .ritam-meta-row div { font-family:monospace; font-size:10px; color:var(--ritam-text-muted); }
        .ritam-meta-row b { display:block; font-size:15px; color:var(--ritam-text); font-family:Georgia,serif; margin-top:2px; }
        .ritam-note { font-size:12.5px; color:var(--ritam-text-muted); line-height:1.55; text-align:left; border-top:1px solid rgba(var(--ritam-danger-rgb),0.25); padding-top:10px; }

        .ritam-step { background:var(--ritam-card-bg); border:1px solid rgba(var(--ritam-line-rgb),0.12); border-radius:10px; padding:13px 14px; font-size:13px; color:#cfd6c6; line-height:1.5; display:flex; gap:12px; align-items:flex-start; margin-bottom:10px; }
        .ritam-step-num { font-family:monospace; font-size:11px; color:var(--ritam-accent); background:rgba(var(--ritam-accent-rgb),0.12); border-radius:50%; width:26px; height:26px; display:flex; align-items:center; justify-content:center; flex-shrink:0; margin-top:1px; }

        .ritam-card { background:var(--ritam-card-bg); border:1px solid rgba(var(--ritam-line-rgb),0.12); border-radius:10px; padding:15px; margin-bottom:12px; }
        .ritam-card h4 { font-family:'Trebuchet MS',sans-serif; font-size:12px; letter-spacing:0.04em; text-transform:uppercase; margin-bottom:0; }
        .amen-head { display:flex; align-items:center; gap:10px; margin-bottom:12px; }
        .amen-icon-circle { width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
        .amen-icon-circle.resto { background:rgba(var(--ritam-accent-rgb),0.15); color:var(--ritam-accent); }
        .amen-icon-circle.mushola { background:rgba(var(--ritam-success-rgb),0.15); color:var(--ritam-success); }
        .amen-icon-circle.fasilitas { background:rgba(var(--ritam-info-rgb),0.15); color:var(--ritam-info); }

        .ritam-item { display:flex; justify-content:space-between; align-items:center; padding:9px 0; border-top:1px solid rgba(var(--ritam-line-rgb),0.10); font-size:12.5px; color:#cfd6c6; gap:10px; }
        .ritam-item:first-of-type { border-top:none; }
        .ritam-item-left { display:flex; align-items:center; gap:8px; }
        .ritam-item-left svg { opacity:0.55; flex-shrink:0; }
        .ritam-item-thumb { width:34px; height:34px; border-radius:8px; object-fit:cover; flex-shrink:0; border:1px solid rgba(var(--ritam-line-rgb),0.15); }
        .ritam-item-thumb-empty { display:flex; align-items:center; justify-content:center; background:rgba(var(--ritam-line-rgb),0.05); color:var(--ritam-text-dim); }
        .ritam-dist-pill { font-family:monospace; font-size:9.5px; padding:3px 8px; border-radius:20px; white-space:nowrap; flex-shrink:0; }
        .ritam-dist-pill.resto { background:rgba(var(--ritam-accent-rgb),0.12); color:var(--ritam-accent); }
        .ritam-dist-pill.mushola { background:rgba(var(--ritam-success-rgb),0.12); color:var(--ritam-success); }
        .ritam-dist-pill.fasilitas { background:rgba(var(--ritam-info-rgb),0.12); color:var(--ritam-info); }

        .ritam-footer { font-size:10.5px; color:var(--ritam-text-dim); line-height:1.6; padding-top:10px; }
        .ritam-social-sub { font-size:11px; color:#8a9384; margin:-4px 0 12px; line-height:1.4; }
        .ritam-social-pill { flex:1; min-width:96px; text-align:center; padding:10px 6px; border-radius:10px; font-size:11px; font-weight:600; text-decoration:none; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:4px; border:1px solid; line-height:1.3; }
        .ritam-social-pill span.handle { font-size:9px; font-weight:400; opacity:0.85; }
        .ritam-social-pill.ig { background:rgba(214,65,122,0.13); color:#e78bb0; border-color:rgba(214,65,122,0.35); }

        .ritam-admin-toggle button { background:none !important; border:1px solid rgba(var(--ritam-line-rgb),0.15) !important; color:var(--ritam-text-dim) !important; font-size:11px !important; padding:4px 10px !important; border-radius:20px !important; width:auto !important; margin-bottom:0 !important; }
        .ritam-admin-badge { display:inline-flex; align-items:center; gap:5px; font-family:monospace; font-size:9.5px; color:var(--ritam-accent); background:rgba(var(--ritam-accent-rgb),0.12); border:1px solid rgba(var(--ritam-accent-rgb),0.35); padding:3px 10px; border-radius:20px; margin-bottom:12px; }
        .ritam-login-box { background:var(--ritam-card-bg-alt); border:1px solid rgba(var(--ritam-line-rgb),0.15); border-radius:10px; padding:14px; margin-bottom:14px; }

        .ritam-empty-state { text-align:center; padding:22px 14px; color:var(--ritam-text-dim); font-size:12.5px; border:1px dashed rgba(var(--ritam-line-rgb),0.2); border-radius:10px; }

        /* Input form — konsisten dengan tema gelap & tema admin */
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea {
            background-color: var(--ritam-card-bg-alt) !important;
            color: var(--ritam-text) !important;
            border: 1px solid rgba(var(--ritam-line-rgb),0.18) !important;
        }
        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stTextArea"] textarea:focus {
            border-color: var(--ritam-accent) !important;
            box-shadow: 0 0 0 1px var(--ritam-accent) !important;
        }
        div[data-testid="stFormSubmitButton"] button {
            background: rgba(var(--ritam-accent-rgb), 0.14) !important;
            border: 1px solid rgba(var(--ritam-accent-rgb), 0.4) !important;
            color: var(--ritam-accent) !important;
        }
        div[data-testid="stSlider"] [role="slider"] { background-color: var(--ritam-accent) !important; }
        div[data-testid="stSlider"] > div > div > div { background: rgba(var(--ritam-accent-rgb),0.35) !important; }

        .st-key-ritam_topbar div[data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; flex-direction: row !important; gap: 8px !important; }
        .st-key-ritam_topbar div[data-testid="column"] { width: auto !important; min-width: 0 !important; flex: initial !important; }
        .st-key-ritam_topbar div[data-testid="column"]:first-child { flex: 1 1 auto !important; }
        .st-key-ritam_topbar div[data-testid="column"]:last-child { flex: 0 0 auto !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_admin_theme() -> None:
    """
    Mengaktifkan tema ungu mode admin.

    Karena seluruh CSS di atas memakai var(--ritam-accent), cukup
    meng-override nilai variabel tersebut agar tombol, tag, kompas,
    tab aktif, dan border ikut berubah warna secara konsisten —
    tanpa duplikasi aturan seperti pada versi sebelum refactor.
    """
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
# TOPBAR & STATUS
# ------------------------------------------------------------------
def render_topbar(is_admin: bool, admin_name: str | None) -> str:
    """Merender brand + tombol admin. Mengembalikan 'login_toggle', 'logout', atau ''."""
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
        '<div class="ritam-status" style="margin:-6px 0 14px;">'
        '<span class="ritam-status-dot"></span> NORMAL · DEMO</div>',
        unsafe_allow_html=True,
    )
    if is_admin:
        st.markdown(
            f'<div class="ritam-admin-badge">⚙️ Mode admin — masuk sebagai <b>{admin_name}</b></div>',
            unsafe_allow_html=True,
        )


def render_locate_me_widget() -> None:
    """
    Tombol "Gunakan lokasi saya" — meminta izin GPS browser lalu
    mengarahkan ulang halaman dengan koordinat pengguna disisipkan ke
    query params (?lat=..&lon=..), sehingga main.py bisa memakainya
    sebagai titik awal rute. Ini yang membuat pengalamannya mirip
    Google Maps: arah & rute dihitung dari posisi asli pengguna menuju
    titik kumpul, bukan dari titik acuan statis milik lokasi wisata.

    Dipakai lewat st.html (bukan st.markdown), karena dua alasan:
      1. st.html merender langsung ke DOM utama halaman (tidak di
         dalam iframe seperti st.components.v1.html), sehingga
         Permissions-Policy browser tidak memblokir
         navigator.geolocation.
      2. st.markdown men-sanitasi/menghapus tag <script> walau
         unsafe_allow_html=True — JS di dalamnya tidak akan pernah
         benar-benar berjalan.

    CATATAN: Geolocation API browser mensyaratkan "secure context"
    (HTTPS atau localhost). Di hosting tanpa HTTPS, tombol ini akan
    selalu gagal meminta izin — itu keterbatasan browser, bukan bug
    aplikasi.
    """
    st.html(
        """
        <div style="margin-bottom:14px;">
          <button id="ritam-geo-btn" type="button" style="
              width:100%; background:rgba(var(--ritam-accent-rgb),0.14);
              border:1px solid rgba(var(--ritam-accent-rgb),0.4); color:var(--ritam-accent);
              font-size:12.5px; font-weight:600; padding:10px; border-radius:10px;
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
                if (err.code === 1) text = 'Izin lokasi ditolak. Aktifkan izin lokasi untuk situs ini di pengaturan browser.';
                else if (err.code === 2) text = 'Posisi tidak tersedia. Pastikan GPS/layanan lokasi perangkat aktif.';
                else if (err.code === 3) text = 'Permintaan lokasi melebihi batas waktu, coba lagi.';
                msg.textContent = text;
              },
              { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
            );
          });
        })();
        </script>
        """,
        unsafe_allow_javascript=True,
    )


def render_admin_login_form(auth_available: bool):
    """
    Merender kotak login admin.

    Returns tuple (username, password) apabila form disubmit, atau
    None jika belum ada submit. Jika secrets.toml belum dikonfigurasi
    (auth_available=False), menampilkan pesan informatif dan tidak
    menampilkan form sama sekali — mencegah pengguna mencoba login
    ke sistem yang memang belum siap.
    """
    st.markdown('<div class="ritam-login-box">', unsafe_allow_html=True)
    if not auth_available:
        st.warning(
            "Login admin belum dikonfigurasi. Tambahkan bagian **[admins]** pada "
            "`.streamlit/secrets.toml` untuk mengaktifkan fitur ini "
            "(lihat `secrets.toml.example`).",
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


# ------------------------------------------------------------------
# KOMPAS
# ------------------------------------------------------------------
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


# ------------------------------------------------------------------
# GRID WISATA
# ------------------------------------------------------------------
def _zone_class(zone: str) -> str:
    return "merah" if "Merah" in zone else "kuning"


def render_spot_grid(spots: list, is_admin: bool) -> str | None:
    """Merender grid 2 kolom kartu wisata. Mengembalikan id spot yang diklik, atau None."""
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


# ------------------------------------------------------------------
# DETAIL: HEADER, SOP, AMENITAS, SOSIAL
# ------------------------------------------------------------------
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
    if not spot["social"].get("instagram"):
        return
    name_q = urllib.parse.quote(spot["name"])
    ig = spot["social"]["instagram"]
    ig_url = spot["social"]["instagram_url"] or f"https://www.instagram.com/explore/tags/{name_q}/"

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


def render_footer(text: str) -> None:
    st.markdown(f'<div class="ritam-footer">{text}</div>', unsafe_allow_html=True)
