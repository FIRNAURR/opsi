import base64
import copy
import os
import urllib.parse
from datetime import datetime
import streamlit as st
import plotly.graph_objects as go

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------
st.set_page_config(
    page_title="RITAM — Evakuasi Cikole",
    page_icon="🧭",
    layout="centered",
    initial_sidebar_state="collapsed",
)

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# Daftar akun admin dibaca dari .streamlit/secrets.toml, format:
#   [admins]
#   reyra = "passwordReyra"
#   khayyira = "passwordKhayyira"
# Kalau belum diset (atau file secrets.toml belum ada sama sekali), pakai default ini
# HANYA untuk demo — wajib diganti/dilengkapi sebelum dipakai beneran di lapangan.
try:
    ADMIN_USERS = dict(st.secrets.get("admins", {"admin": "kayaraya2026"}))
except Exception:
    ADMIN_USERS = {"admin": "kayaraya2026"}

# ------------------------------------------------------------------
# DATA (ILUSTRATIF — lihat catatan di footer)
# ------------------------------------------------------------------
DIR_LABEL = {
    "U": "Utara", "TL": "Timur Laut", "T": "Timur", "TG": "Tenggara",
    "S": "Selatan", "BD": "Barat Daya", "B": "Barat", "BL": "Barat Laut",
}

SPOTS = [
    {
        "id": "orchid", "name": "Orchid Forest Cikole", "image": "orchid.jpg",
        "category": "Wisata Alam & Outbound", "zone": "Zona Merah",
        "ticket": "Rp40.000 – Rp100.000",
        "evac": {"point": "Lapangan Parkir Utama", "bearing": 35,
                  "dist": "180 m", "time": "≈3 mnt",
                  "note": "Jauhi jembatan gantung (Wood Bridge) dan area pepohonan tinggi. "
                          "Menuju lapangan parkir yang lebih terbuka dan jauh dari tebing."},
        "amenities": {
            "resto": [("Kedai kuliner Rabbit Forest", "T · 90 m", None),
                       ("Golden Pine Cafe", "TL · 140 m", "golden_pine.jpg")],
            "mushola": [("Mushola dekat loket masuk", "B · 60 m")],
            "fasilitas": [("Toilet umum area parkir", "B · 70 m"),
                           ("Pos informasi & P3K", "T · 100 m")],
        },
        "social": {"instagram": "@orchidforestcikole",
                    "instagram_url": "https://www.instagram.com/orchidforestcikole/"},
    },
    {
        "id": "grafika", "name": "Terminal Wisata Grafika Cikole", "image": "grafika.jpg",
        "category": "Alam, Outbound & Kuliner", "zone": "Zona Merah",
        "ticket": "Rp15.000",
        "evac": {"point": "Lapangan Api Unggun", "bearing": 110,
                  "dist": "220 m", "time": "≈4 mnt",
                  "note": "Segera menjauh dari pohon pinus tinggi dan bangunan kayu vintage. "
                          "Lapangan api unggun menjadi titik kumpul terluas di kawasan ini."},
        "amenities": {
            "resto": [("Restoran Sangkuriang", "TG · 130 m", "sangkuriang.jpg"),
                       ("Saung Pengkolan 2", "T · 80 m", "saung_pengkolan2.jpg")],
            "mushola": [("Mushola dekat area camping ground", "BD · 150 m")],
            "fasilitas": [("Toilet & kamar bilas", "T · 90 m"),
                           ("Pos keamanan", "BD · 60 m")],
        },
        "social": {"instagram": "@officialgrafika",
                    "instagram_url": "https://www.instagram.com/officialgrafika/"},
    },
    {
        "id": "floating", "name": "Floating Market Lembang", "image": "floating.jpg",
        "category": "Wisata Kuliner & Keluarga", "zone": "Zona Kuning",
        "ticket": "Rp30.000",
        "evac": {"point": "Area Parkir Depan Danau", "bearing": 250,
                  "dist": "150 m", "time": "≈2–3 mnt",
                  "note": "Jauhi tepi danau saat evakuasi berlangsung. Arahkan pengunjung ke "
                          "area parkir depan yang datar dan jauh dari struktur perahu."},
        "amenities": {
            "resto": [("Perahu kuliner Sunda (lotek, batagor, karedok)", "T · 40 m", "sundaness.jpg"),
                       ("Zona jajanan internasional", "TL · 100 m", None)],
            "mushola": [("Mushola dekat pintu masuk", "B · 90 m")],
            "fasilitas": [("Toilet area playground", "TG · 70 m"),
                           ("Loket & pos informasi", "B · 50 m")],
        },
        "social": {"instagram": "@floating.market.lembang",
                    "instagram_url": "https://www.instagram.com/floating.market.lembang/"},
    },
    {
        "id": "asiaafrika", "name": "The Great Asia Afrika", "image": "asiaafrika.jpg",
        "category": "Wisata Tematik & Kuliner", "zone": "Zona Kuning",
        "ticket": "Rp30.000 – Rp50.000",
        "evac": {"point": "Plaza Terbuka Zona Indonesia", "bearing": 15,
                  "dist": "200 m", "time": "≈3–4 mnt",
                  "note": "Hindari berlindung di dalam replika bangunan negara. Menuju plaza "
                          "terbuka di zona Indonesia yang berjarak paling dekat."},
        "amenities": {
            "resto": [("Kuliner Zona Korea & Jepang", "TL · 120 m"),
                       ("Kuliner Zona Afrika", "T · 160 m")],
            "mushola": [("Mushola dekat Zona Indonesia", "B · 80 m")],
            "fasilitas": [("Toilet Zona India", "TG · 100 m"),
                           ("Pos keamanan pintu masuk", "BD · 60 m")],
        },
        "social": {"instagram": "@thegreatasiaafricalembang",
                    "instagram_url": "https://www.instagram.com/thegreatasiaafricalembang/"},
    },
    {
        "id": "pineforest", "name": "Pine Forest Camp Lembang", "image": "pineforest.jpg",
        "category": "Wisata Camping & Alam", "zone": "Zona Merah",
        "ticket": "Rp20.000 – Rp50.000",
        "evac": {"point": "Area Camping Ground Terbuka", "bearing": 190,
                  "dist": "160 m", "time": "≈3 mnt",
                  "note": "Jauhi tepi jurang dan pohon pinus condong. Area camping ground yang "
                          "lebih datar menjadi titik kumpul sementara."},
        "amenities": {
            "resto": [("Warung makan area camping", "T · 100 m"),
                       ("Kedai kopi & jajanan hangat", "TG · 70 m")],
            "mushola": [("Mushola sederhana dekat gerbang", "BD · 130 m")],
            "fasilitas": [("Toilet & kamar mandi umum", "T · 90 m"),
                           ("Pos ranger / pengelola", "B · 50 m")],
        },
        "social": {"instagram": "@pineforestcamplembang",
                    "instagram_url": "https://www.instagram.com/pineforestcamplembang/"},
    },
    {
        "id": "deranch", "name": "De Ranch Lembang", "image": "deranch.jpg",
        "category": "Wisata Edukasi & Keluarga", "zone": "Zona Kuning",
        "ticket": "Rp30.000",
        "evac": {"point": "Lapangan Rumput Utama", "bearing": 300,
                  "dist": "120 m", "time": "≈2 mnt",
                  "note": "Jauhi kandang hewan dan pagar kayu saat evakuasi. Lapangan rumput "
                          "utama relatif aman dan mudah diakses dari seluruh wahana."},
        "amenities": {
            "resto": [("Kedai susu & jajanan khas peternakan", "T · 60 m"),
                       ("Warung makan area piknik", "TL · 110 m")],
            "mushola": [("Mushola dekat pintu masuk", "B · 70 m")],
            "fasilitas": [("Toilet umum", "TG · 80 m"),
                           ("Pos informasi wahana", "B · 40 m")],
        },
        "social": {"instagram": None, "instagram_url": None},
    },
]
SPOTS_BY_ID = {s["id"]: s for s in SPOTS}

# ------------------------------------------------------------------
# STYLE
# ------------------------------------------------------------------
st.markdown(
    """
    <style>
    #MainMenu, header[data-testid="stHeader"], footer, .stDeployButton { visibility: hidden; height:0; }

    .stApp { background-color: #16241c; color: #eee9dc; }

    .block-container {
        max-width: 460px;
        padding-top: 14px;
        padding-bottom: 60px;
        padding-left: 16px;
        padding-right: 16px;
    }

    h1, h2, h3, h4 { font-family: 'Trebuchet MS', sans-serif; letter-spacing: 0.02em; }

    .ritam-topbar { display:flex; align-items:center; justify-content:space-between; margin-bottom:14px; }
    .ritam-brand { display:flex; align-items:center; gap:8px; }
    .ritam-dot-ring { width:26px; height:26px; border-radius:50%; border:2px solid #f2b544; position:relative; flex-shrink:0; }
    .ritam-dot-ring::after { content:''; position:absolute; inset:0; margin:auto; width:5px; height:5px; border-radius:50%; background:#f2b544; }
    .ritam-brand span { font-family:'Trebuchet MS',sans-serif; font-size:15px; letter-spacing:0.04em; }
    .ritam-status { font-family:monospace; font-size:9.5px; color:#7c8a76; display:flex; align-items:center; gap:5px; }
    .ritam-status-dot { width:7px; height:7px; border-radius:50%; background:#7fae67; box-shadow:0 0 6px #7fae67; }

    .ritam-heading { font-size:13px; color:#b7bfae; margin-bottom:2px; }
    .ritam-heading b { color:#eee9dc; }

    /* kartu foto destinasi ala grid booking */
    .ritam-photo-card {
        position:relative; border-radius:14px; overflow:hidden; height:150px;
        background-size:cover; background-position:center; margin-bottom:6px;
        border:1px solid rgba(238,233,220,0.12);
    }
    .ritam-photo-overlay {
        position:absolute; inset:0;
        background:linear-gradient(180deg, rgba(22,36,28,0) 35%, rgba(22,36,28,0.92) 100%);
        display:flex; flex-direction:column; justify-content:flex-end; padding:10px 12px;
    }
    .ritam-photo-zone {
        position:absolute; top:8px; right:8px; font-family:monospace; font-size:8.5px;
        padding:3px 8px; border-radius:20px; backdrop-filter:blur(2px);
    }
    .ritam-photo-zone.merah { background:rgba(230,87,42,0.85); color:#fff; }
    .ritam-photo-zone.kuning { background:rgba(242,181,68,0.9); color:#412402; }
    .ritam-photo-title { font-size:13.5px; font-weight:600; color:#fff; margin-bottom:2px; line-height:1.25; }
    .ritam-photo-cat { font-size:10px; color:#d8ddd0; }

    div[data-testid="stButton"] > button {
        width:100%; background:#24392c !important; border:1px solid rgba(238,233,220,0.18) !important;
        color:#eee9dc !important; font-size:12px !important; padding:8px !important; margin-bottom:16px;
    }
    div[data-testid="stButton"] > button:hover { border-color:#f2b544 !important; color:#f2b544 !important; }
    .ritam-back button {
        width:auto !important; background:none !important; border:none !important;
        color:#b7bfae !important; font-size:12px !important; padding:0 !important; margin-bottom:10px !important;
    }

    button[data-baseweb="tab"] { font-size: 13px; padding: 10px 6px; }
    div[data-baseweb="tab-list"] { gap: 4px; }
    div[data-baseweb="tab-highlight"] { background-color:#f2b544 !important; }

    .ritam-tag {
        display:inline-block; font-family: monospace; font-size: 10px;
        padding: 3px 9px; border-radius: 20px; border: 1px solid rgba(238,233,220,0.2);
        color:#b7bfae; margin-right:6px; margin-bottom:6px;
    }
    .ritam-tag.zone { color:#e6572a; border-color:rgba(230,87,42,0.4); background:rgba(230,87,42,0.12); }

    .ritam-hero { border-radius:14px; overflow:hidden; height:150px; background-size:cover;
        background-position:center; margin-bottom:14px; border:1px solid rgba(238,233,220,0.12); }

    .ritam-evac {
        background: linear-gradient(160deg, rgba(230,87,42,0.10), transparent 65%);
        border:1px solid rgba(230,87,42,0.35); border-radius:14px; padding:18px; text-align:center;
    }
    .ritam-evac h3 { font-family:'Trebuchet MS',sans-serif; font-size:17px; margin:6px 0 12px; }
    .ritam-eyebrow { font-family:monospace; font-size:10px; letter-spacing:0.1em; color:#e6572a; text-transform:uppercase; }
    .ritam-meta-row { display:flex; justify-content:center; gap:16px; flex-wrap:wrap; margin-bottom:12px; }
    .ritam-meta-row div { font-family:monospace; font-size:10px; color:#b7bfae; }
    .ritam-meta-row b { display:block; font-size:15px; color:#eee9dc; font-family:Georgia,serif; margin-top:2px; }
    .ritam-note { font-size:12.5px; color:#b7bfae; line-height:1.55; text-align:left; border-top:1px solid rgba(230,87,42,0.25); padding-top:10px; }

    .ritam-step { background:#24392c; border:1px solid rgba(238,233,220,0.12); border-radius:10px;
        padding:13px 14px; font-size:13px; color:#cfd6c6; line-height:1.5; display:flex; gap:12px;
        align-items:flex-start; margin-bottom:10px; }
    .ritam-step-num { font-family:monospace; font-size:11px; color:#f2b544; background:rgba(242,181,68,0.12);
        border-radius:50%; width:26px; height:26px; display:flex; align-items:center; justify-content:center;
        flex-shrink:0; margin-top:1px; }

    .ritam-card { background:#24392c; border:1px solid rgba(238,233,220,0.12); border-radius:10px;
        padding:15px; margin-bottom:12px; }
    .ritam-card h4 { font-family:'Trebuchet MS',sans-serif; font-size:12px; letter-spacing:0.04em;
        text-transform:uppercase; margin-bottom:0; }
    .amen-head { display:flex; align-items:center; gap:10px; margin-bottom:12px; }
    .amen-icon-circle { width:32px; height:32px; border-radius:50%; display:flex; align-items:center;
        justify-content:center; flex-shrink:0; }
    .amen-icon-circle.resto { background:rgba(242,181,68,0.15); color:#f2b544; }
    .amen-icon-circle.mushola { background:rgba(127,174,103,0.15); color:#7fae67; }
    .amen-icon-circle.fasilitas { background:rgba(127,177,247,0.15); color:#7fb1f7; }
    .ritam-item { display:flex; justify-content:space-between; align-items:center; padding:9px 0;
        border-top:1px solid rgba(238,233,220,0.10); font-size:12.5px; color:#cfd6c6; gap:10px; }
    .ritam-item:first-of-type { border-top:none; }
    .ritam-item-left { display:flex; align-items:center; gap:8px; }
    .ritam-item-left svg { opacity:0.55; flex-shrink:0; }
    .ritam-item-thumb {
        width:34px; height:34px; border-radius:8px; object-fit:cover; flex-shrink:0;
        border:1px solid rgba(238,233,220,0.15);
    }
    .ritam-item-thumb-empty {
        display:flex; align-items:center; justify-content:center; background:rgba(238,233,220,0.05);
        color:#7c8a76;
    }
    .ritam-dist-pill { font-family:monospace; font-size:9.5px; padding:3px 8px; border-radius:20px;
        white-space:nowrap; flex-shrink:0; }
    .ritam-dist-pill.resto { background:rgba(242,181,68,0.12); color:#f2b544; }
    .ritam-dist-pill.mushola { background:rgba(127,174,103,0.12); color:#7fae67; }
    .ritam-dist-pill.fasilitas { background:rgba(127,177,247,0.12); color:#7fb1f7; }

    .ritam-footer { font-size:10.5px; color:#7c8a76; line-height:1.6; padding-top:10px; }
    .ritam-footer b { color:#f2b544; }

    .ritam-social-sub { font-size:11px; color:#8a9384; margin:-4px 0 12px; line-height:1.4; }
    .ritam-social-row { display:flex; gap:8px; flex-wrap:wrap; }
    .ritam-social-pill {
        flex:1; min-width:96px; text-align:center; padding:10px 6px; border-radius:10px;
        font-size:11px; font-weight:600; text-decoration:none; display:flex; flex-direction:column;
        align-items:center; justify-content:center; gap:4px; border:1px solid; line-height:1.3;
    }
    .ritam-social-pill span.handle { font-size:9px; font-weight:400; opacity:0.85; }
    .ritam-social-pill.ig { background:rgba(214,65,122,0.13); color:#e78bb0; border-color:rgba(214,65,122,0.35); }
    .ritam-social-pill.tiktok { background:rgba(56,209,201,0.10); color:#7ee8e3; border-color:rgba(56,209,201,0.3); }
    .ritam-social-pill.fb { background:rgba(24,119,242,0.12); color:#7fb1f7; border-color:rgba(24,119,242,0.35); }

    .ritam-admin-toggle button {
        background:none !important; border:1px solid rgba(238,233,220,0.15) !important;
        color:#7c8a76 !important; font-size:11px !important; padding:4px 10px !important;
        border-radius:20px !important; width:auto !important; margin-bottom:0 !important;
    }
    .ritam-admin-badge {
        display:inline-flex; align-items:center; gap:5px; font-family:monospace; font-size:9.5px;
        color:#f2b544; background:rgba(242,181,68,0.12); border:1px solid rgba(242,181,68,0.35);
        padding:3px 10px; border-radius:20px; margin-bottom:12px;
    }
    .ritam-login-box {
        background:#1d2f24; border:1px solid rgba(238,233,220,0.15); border-radius:10px;
        padding:14px; margin-bottom:14px;
    }

    /* sejajarkan tombol Admin dengan teks RITAM di top bar */
    div[data-testid="stHorizontalBlock"] { align-items:center; }
    .ritam-brand { margin-bottom:0 !important; }
    div[data-testid="stButton"] { margin-bottom:0 !important; }

    /* paksa top bar tetap sejajar horizontal walau di layar HP sempit
       (Streamlit otomatis menumpuk kolom di viewport sempit secara default) */
    .st-key-ritam_topbar div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        flex-direction: row !important;
        gap: 8px !important;
    }
    .st-key-ritam_topbar div[data-testid="column"] {
        width: auto !important;
        min-width: 0 !important;
        flex: initial !important;
    }
    .st-key-ritam_topbar div[data-testid="column"]:first-child { flex: 1 1 auto !important; }
    .st-key-ritam_topbar div[data-testid="column"]:last-child { flex: 0 0 auto !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------
# TEMA MODE ADMIN — ganti warna aksen jadi ungu supaya beda kelihatan
# jelas dari tampilan wisatawan (amber/hijau), tanpa perlu baca teks.
# --------------------------------------------------------------
if st.session_state.get("is_admin", False):
    st.markdown(
        """
        <style>
        .ritam-dot-ring { border-color:#a78bfa !important; }
        .ritam-dot-ring::after { background:#a78bfa !important; }
        .ritam-admin-badge {
            color:#c4b5fd !important; background:rgba(167,139,250,0.14) !important;
            border-color:rgba(167,139,250,0.4) !important;
        }
        .ritam-step-num { color:#a78bfa !important; background:rgba(167,139,250,0.14) !important; }
        div[data-testid="stButton"] > button:hover { border-color:#a78bfa !important; color:#a78bfa !important; }
        .ritam-admin-banner {
            background:repeating-linear-gradient(135deg, #a78bfa, #a78bfa 10px, #8b6ff0 10px, #8b6ff0 20px);
            color:#1a1230; font-family:'Trebuchet MS',sans-serif; font-size:11px; font-weight:700;
            letter-spacing:0.06em; text-transform:uppercase; text-align:center; padding:6px;
            margin:-14px -16px 14px; border-radius:0 0 8px 8px;
        }
        .ritam-photo-card { position:relative; }
        .ritam-photo-edit-flag {
            position:absolute; top:8px; left:8px; width:26px; height:26px; border-radius:50%;
            background:rgba(167,139,250,0.9); color:#1a1230; display:flex; align-items:center;
            justify-content:center; font-size:12px; z-index:2;
        }
        </style>
        <div class="ritam-admin-banner">⚙️ Mode Admin — tampilan khusus tim pengelola RITAM</div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def image_to_data_uri(filename: str) -> str:
    """Baca file gambar lokal dari folder assets/ dan ubah jadi data URI base64
    supaya bisa ditempel langsung sebagai background-image di kartu HTML."""
    path = os.path.join(ASSETS_DIR, filename)
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    ext = filename.rsplit(".", 1)[-1].lower()
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext
    return f"data:image/{mime};base64,{encoded}"


def bearing_to_label(deg: int) -> str:
    dirs = [("U", 0), ("TL", 45), ("T", 90), ("TG", 135), ("S", 180),
            ("BD", 225), ("B", 270), ("BL", 315)]
    closest = min(dirs, key=lambda d: min(abs(deg - d[1]), 360 - abs(deg - d[1])))
    return DIR_LABEL[closest[0]]


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
        showlegend=False, margin=dict(l=10, r=10, t=10, b=10), height=260,
    )
    return fig


AMENITY_ICONS = {
    "resto": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 3v8a2 2 0 002 2v8M4 3v0M7 3v8M10 3v8m0 0a2 2 0 002-2V3M17 3v18M17 3c-3 0-3 4-3 6s0 4 3 4"/></svg>',
    "mushola": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 2v3M8 8a4 4 0 118 0c0 2-2 3-2 5h-4c0-2-2-3-2-5z"/><path d="M4 22v-6a8 8 0 0116 0v6"/><path d="M4 22h16"/></svg>',
    "fasilitas": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/></svg>',
}
PIN_ICON = ('<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2"><path d="M12 21s7-7.5 7-12a7 7 0 00-14 0c0 4.5 7 12 7 12z"/>'
            '<circle cx="12" cy="9" r="2.5"/></svg>')


def amenity_card(title: str, items: list, kind: str):
    rows = ""
    for item in items:
        name, dist = item[0], item[1]
        photo = item[2] if len(item) > 2 and item[2] else None
        if photo:
            thumb = f'<img class="ritam-item-thumb" src="{image_to_data_uri(photo)}" alt="">'
        else:
            thumb = f'<span class="ritam-item-thumb ritam-item-thumb-empty">{PIN_ICON}</span>'
        rows += (
            f'<div class="ritam-item">'
            f'<span class="ritam-item-left">{thumb}<span>{name}</span></span>'
            f'<span class="ritam-dist-pill {kind}">{dist}</span>'
            f'</div>'
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


def zone_class(zone: str) -> str:
    return "merah" if "Merah" in zone else "kuning"


def social_card(spot: dict):
    """Kartu ajakan follow Instagram resmi lokasi wisata, untuk info promo
    tiket dan destinasi/wahana baru. Hanya Instagram yang ditampilkan karena
    akun TikTok/Facebook resminya belum bisa saya pastikan satu per satu."""
    name_q = urllib.parse.quote(spot["name"])
    ig = spot["social"]["instagram"]
    ig_url = spot["social"]["instagram_url"] or f"https://www.instagram.com/explore/tags/{name_q}/"
    ig_label = ig if ig else "Cari di Instagram"

    st.markdown(
        f"""
        <div class="ritam-card">
          <h4>📣 Info & Promo Terbaru</h4>
          <div class="ritam-social-sub">Follow Instagram resmi untuk update promo tiket dan wahana/destinasi baru di {spot['name']}.</div>
          <a class="ritam-social-pill ig" href="{ig_url}" target="_blank" rel="noopener"
             style="width:100%; flex-direction:row; justify-content:flex-start; gap:10px; padding:12px 14px;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" style="flex-shrink:0">
              <rect x="3" y="3" width="18" height="18" rx="5.5"/>
              <circle cx="12" cy="12" r="4"/>
              <circle cx="17.3" cy="6.7" r="0.6" fill="currentColor" stroke="none"/>
            </svg>
            <span style="display:flex; flex-direction:column; align-items:flex-start; gap:1px;">
              <span style="font-size:12.5px; font-weight:600;">Instagram</span>
              <span class="handle">{ig_label}</span>
            </span>
          </a>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------------
# STATE
# ------------------------------------------------------------------
if "view" not in st.session_state:
    st.session_state.view = "grid"
if "selected" not in st.session_state:
    st.session_state.selected = SPOTS[0]["id"]
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "admin_name" not in st.session_state:
    st.session_state.admin_name = None
if "show_login" not in st.session_state:
    st.session_state.show_login = False
if "spots" not in st.session_state:
    # salinan data yang bisa diubah admin selama sesi berjalan (belum permanen ke file)
    st.session_state.spots = copy.deepcopy(SPOTS)

spots = st.session_state.spots
spots_by_id = {s["id"]: s for s in spots}

# ------------------------------------------------------------------
# TOP BAR (selalu tampil)
# ------------------------------------------------------------------
with st.container(key="ritam_topbar"):
    top_l, top_r = st.columns([3, 1], gap="small")
    with top_l:
        st.markdown(
            """
            <div class="ritam-brand" style="margin-bottom:6px;">
              <div class="ritam-dot-ring"></div><span>RITAM</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with top_r:
        st.markdown('<div class="ritam-admin-toggle" style="text-align:right;">', unsafe_allow_html=True)
        if st.session_state.is_admin:
            if st.button(f"🔓 {st.session_state.admin_name}", key="admin_logout_btn"):
                st.session_state.is_admin = False
                st.session_state.admin_name = None
                st.rerun()
        else:
            if st.button("🔒 Admin", key="admin_login_toggle"):
                st.session_state.show_login = not st.session_state.show_login
        st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.show_login and not st.session_state.is_admin:
    st.markdown('<div class="ritam-login-box">', unsafe_allow_html=True)
    with st.form("admin_login_form", clear_on_submit=True):
        uname = st.text_input("Username", placeholder="Username")
        pw = st.text_input("Password", type="password", placeholder="Password")
        submitted = st.form_submit_button("Masuk")
        if submitted:
            uname_clean = uname.strip().lower()
            if uname_clean in ADMIN_USERS and pw == ADMIN_USERS[uname_clean]:
                st.session_state.is_admin = True
                st.session_state.admin_name = uname_clean
                st.session_state.show_login = False
                st.rerun()
            else:
                st.error("Username atau password salah.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="ritam-status" style="margin:-6px 0 14px;"><span class="ritam-status-dot"></span> NORMAL · DEMO</div>',
    unsafe_allow_html=True,
)
if st.session_state.is_admin:
    st.markdown(
        f'<div class="ritam-admin-badge">⚙️ Mode admin — masuk sebagai <b>{st.session_state.admin_name}</b></div>',
        unsafe_allow_html=True,
    )

# ==================================================================
# VIEW 1 — GRID PEMILIHAN TITIK WISATA (foto asli)
# ==================================================================
if st.session_state.view == "grid":
    st.markdown(
        '<div class="ritam-heading">Kesiapsiagaan Wisata <b>Kawasan Cikole</b> — pilih lokasi kamu</div>',
        unsafe_allow_html=True,
    )
    st.write("")

    cols = st.columns(2)
    for i, spot in enumerate(spots):
        with cols[i % 2]:
            data_uri = image_to_data_uri(spot["image"])
            zc = zone_class(spot["zone"])
            edit_flag = '<div class="ritam-photo-edit-flag">✎</div>' if st.session_state.is_admin else ""
            st.markdown(
                f"""
                <div class="ritam-photo-card" style="background-image:url('{data_uri}')">
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
            btn_label = "✎ Kelola data lokasi" if st.session_state.is_admin else "Lihat arah evakuasi"
            if st.button(btn_label, key=f"btn_{spot['id']}"):
                st.session_state.selected = spot["id"]
                st.session_state.view = "detail"
                st.rerun()

    st.markdown(
        '<div class="ritam-footer">Foto lokasi ditampilkan sebagai identitas visual titik wisata. '
        'Data arah, jarak, dan layanan tetap <b>ilustratif</b> — purwarupa penelitian RITAM '
        '(Tim Kayaraya, OPSI 2026), belum divalidasi survei GPS lapangan.</div>',
        unsafe_allow_html=True,
    )

# ==================================================================
# VIEW 2 — DETAIL EVAKUASI & LAYANAN
# ==================================================================
else:
    spot = spots_by_id[st.session_state.selected]

    st.markdown('<div class="ritam-back">', unsafe_allow_html=True)
    if st.button("← Kembali ke daftar lokasi", key="back_btn"):
        st.session_state.view = "grid"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    data_uri = image_to_data_uri(spot["image"])
    st.markdown(f'<div class="ritam-hero" style="background-image:url(\'{data_uri}\')"></div>', unsafe_allow_html=True)

    st.markdown(f"### {spot['name']}")
    st.markdown(
        f'<span class="ritam-tag">{spot["category"]}</span>'
        f'<span class="ritam-tag zone">{spot["zone"]}</span>'
        f'<span class="ritam-tag">Tiket {spot["ticket"]}</span>',
        unsafe_allow_html=True,
    )
    st.write("")

    if st.session_state.is_admin:
        tab_evac, tab_sop, tab_amen, tab_admin = st.tabs(
            ["🧭 Evakuasi", "✅ SOP", "🍽️ Layanan", "⚙️ Admin"]
        )
    else:
        tab_evac, tab_sop, tab_amen = st.tabs(["🧭 Evakuasi", "✅ SOP", "🍽️ Layanan"])

    with tab_evac:
        dir_label = bearing_to_label(spot["evac"]["bearing"])
        st.markdown('<div class="ritam-evac">', unsafe_allow_html=True)
        st.markdown('<div class="ritam-eyebrow">Arah Evakuasi Terdekat</div>', unsafe_allow_html=True)
        st.plotly_chart(compass_figure(spot["evac"]["bearing"]), use_container_width=True, config={"displayModeBar": False})
        st.markdown(f'<h3>{spot["evac"]["point"]}</h3>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="ritam-meta-row">
              <div>Arah<b>{dir_label} ({spot["evac"]["bearing"]}°)</b></div>
              <div>Jarak<b>{spot["evac"]["dist"]}</b></div>
              <div>Waktu<b>{spot["evac"]["time"]}</b></div>
            </div>
            <div class="ritam-note">{spot["evac"]["note"]}</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_sop:
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

    with tab_amen:
        social_card(spot)
        amenity_card("Resto & Jajanan", spot["amenities"]["resto"], "resto")
        amenity_card("Mushola", spot["amenities"]["mushola"], "mushola")
        amenity_card("Fasilitas Lain", spot["amenities"]["fasilitas"], "fasilitas")

    if st.session_state.is_admin:
        with tab_admin:
            st.caption("Update data arah evakuasi untuk lokasi ini. Perubahan langsung terlihat "
                       "di tab Evakuasi, tapi hanya berlaku selama sesi berjalan.")
            last_edit = spot.get("_last_edit")
            if last_edit:
                st.markdown(
                    f'<div class="ritam-admin-badge">✎ Terakhir diedit oleh <b>{last_edit["by"]}</b> · {last_edit["at"]}</div>',
                    unsafe_allow_html=True,
                )
            with st.form(f"edit_evac_{spot['id']}"):
                point = st.text_input("Nama titik kumpul", value=spot["evac"]["point"])
                bearing = st.slider("Arah (derajat, 0=Utara)", 0, 359, spot["evac"]["bearing"])
                dist = st.text_input("Jarak", value=spot["evac"]["dist"])
                time_ = st.text_input("Estimasi waktu tempuh", value=spot["evac"]["time"])
                note = st.text_area("Catatan bahaya / arahan", value=spot["evac"]["note"], height=100)
                save = st.form_submit_button("💾 Simpan perubahan")
                if save:
                    spot["evac"]["point"] = point
                    spot["evac"]["bearing"] = bearing
                    spot["evac"]["dist"] = dist
                    spot["evac"]["time"] = time_
                    spot["evac"]["note"] = note
                    spot["_last_edit"] = {
                        "by": st.session_state.admin_name,
                        "at": datetime.now().strftime("%d %b %Y, %H:%M"),
                    }
                    st.success("Tersimpan untuk sesi ini. Buka tab Evakuasi untuk melihat hasilnya.")
                    st.rerun()
                    st.divider()

                st.subheader("🎉 Kelola Promo")

            with st.form("promo_form"):

                    judul = st.text_input("Judul Promo")

                    deskripsi = st.text_area("Deskripsi Promo")

                    if st.form_submit_button("➕ Tambah Promo"):

                        spot.setdefault("promos", []).append({
                            "title": judul,
                            "desc": deskripsi
                        })

                        st.success("Promo berhasil ditambahkan")
                        st.rerun()
            st.divider()

            st.subheader("🏞 Tambah Destinasi Baru")

            with st.form("destinasi_form"):

                nama = st.text_input("Nama Destinasi")

                kategori = st.text_input("Kategori")

                zona = st.selectbox(
                        "Zona",
                        ["Zona Merah","Zona Kuning"]
                    )

                tiket = st.text_input("Harga Tiket")

                if st.form_submit_button("➕ Tambah Destinasi"):

                        new_spot = {
                            "id": f"spot_{len(spots)+1}",
                            "name": nama,
                            "category": kategori,
                            "zone": zona,
                            "ticket": tiket,
                            "image": None,
                            "evac": {
                                "point": "",
                                "bearing": 0,
                                "dist": "",
                                "time": "",
                                "note": ""
                            },
                            "amenities": {
                                "resto": [],
                                "mushola": [],
                                "fasilitas": []
                            },
                            "_last_edit": {
                                "by": st.session_state.admin_name,
                                "at": datetime.now().strftime("%d %b %Y, %H:%M"),
                            }
                        }

                        spots.append(new_spot)
                        st.success("Destinasi baru berhasil ditambahkan")
                        st.rerun()

    st.markdown(
        '<div class="ritam-footer">Arah, jarak, waktu tempuh, dan daftar layanan bersifat '
        '<b>ilustratif</b> — purwarupa penelitian RITAM (Tim Kayaraya, OPSI 2026), belum divalidasi '
        'survei GPS lapangan atau koordinasi resmi dengan BPBD/pengelola wisata.</div>',
        unsafe_allow_html=True,
    )
    
