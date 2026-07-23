import base64
import copy
import os
import math
import urllib.parse
from datetime import datetime
import streamlit as st
import plotly.graph_objects as go
import folium
from folium import plugins
import requests
import streamlit.components.v1 as components

# ------------------------------------------------------------------
# CONFIG & AUTH
# ------------------------------------------------------------------
st.set_page_config(
    page_title="RITAM — Evakuasi Cikole",
    page_icon="🧭",
    layout="centered",
    initial_sidebar_state="collapsed",
)

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

try:
    ADMIN_USERS = dict(st.secrets.get("admins", {"admin": "kayaraya2026"}))
except Exception:
    ADMIN_USERS = {"admin": "kayaraya2026"}

# ------------------------------------------------------------------
# DATA AWAL (6 Titik Wisata Lengkap dengan Koordinat Presisi)
# ------------------------------------------------------------------
DIR_LABEL = {
    "U": "Utara", "TL": "Timur Laut", "T": "Timur", "TG": "Tenggara",
    "S": "Selatan", "BD": "Barat Daya", "B": "Barat", "BL": "Barat Laut",
}

INITIAL_SPOTS = [
    {
        "id": "orchid", "name": "Orchid Forest Cikole", "image": "orchid.jpg",
        "category": "Wisata Alam & Outbound", "zone": "Zona Merah", "ticket": "Rp40.000 – Rp100.000",
        "evac": {"point": "Area Terbuka / Rest Area Cikole", "bearing": 35, "dist": "1.2 km", "time": "≈15 mnt",
                 "note": "Jauhi jembatan gantung dan area pepohonan tinggi. Menuju rest area yang lebih terbuka."},
        "coords": {"start": [-6.780613, 107.637505], "end": [-6.789125, 107.644133], "safe_name": "Rest Area Cikole"},
        "amenities": {
            "resto": [("Kedai kuliner Rabbit Forest", "T · 90 m", None), ("Golden Pine Cafe", "TL · 140 m", None)],
            "mushola": [("Mushola dekat loket masuk", "B · 60 m", None)],
            "fasilitas": [("Toilet umum area parkir", "B · 70 m", None), ("Pos informasi & P3K", "T · 100 m", None)],
        },
        "social": {"instagram": "@orchidforestcikole", "instagram_url": "https://www.instagram.com/orchidforestcikole/"},
    },
    {
        "id": "grafika", "name": "Terminal Wisata Grafika Cikole", "image": "grafika.jpg",
        "category": "Alam, Outbound & Kuliner", "zone": "Zona Merah", "ticket": "Rp15.000",
        "evac": {"point": "Lapangan Jayagiri Cikole", "bearing": 110, "dist": "900 m", "time": "≈10 mnt",
                 "note": "Segera menjauh dari pohon pinus tinggi. Lapangan Jayagiri menjadi titik kumpul terluas."},
        "coords": {"start": [-6.786551, 107.650482], "end": [-6.793284, 107.647901], "safe_name": "Lapangan Jayagiri Cikole"},
        "amenities": {
            "resto": [("Restoran Sangkuriang", "TG · 130 m", None), ("Saung Pengkolan 2", "T · 80 m", None)],
            "mushola": [("Mushola dekat camping ground", "BD · 150 m", None)],
            "fasilitas": [("Toilet & kamar bilas", "T · 90 m", None), ("Pos keamanan", "BD · 60 m", None)],
        },
        "social": {"instagram": "@officialgrafika", "instagram_url": "https://www.instagram.com/officialgrafika/"},
    },
    {
        "id": "floating", "name": "Floating Market Lembang", "image": "floating.jpg",
        "category": "Wisata Kuliner & Keluarga", "zone": "Zona Kuning", "ticket": "Rp30.000",
        "evac": {"point": "Stadion Bentang", "bearing": 250, "dist": "300 m", "time": "≈4 mnt",
                 "note": "Jauhi tepi danau. Arahkan pengunjung ke Stadion Bentang yang bebas dari struktur perahu."},
        "coords": {"start": [-6.817521, 107.618640], "end": [-6.817183, 107.616553], "safe_name": "Stadion Bentang"},
        "amenities": {
            "resto": [("Perahu kuliner Sunda", "T · 40 m", None), ("Zona jajanan internasional", "TL · 100 m", None)],
            "mushola": [("Mushola dekat pintu masuk", "B · 90 m", None)],
            "fasilitas": [("Toilet area playground", "TG · 70 m", None), ("Loket & pos informasi", "B · 50 m", None)],
        },
        "social": {"instagram": "@floating.market.lembang", "instagram_url": "https://www.instagram.com/floating.market.lembang/"},
    },
    {
        "id": "asiaafrika", "name": "The Great Asia Afrika", "image": "asiaafrika.jpg",
        "category": "Wisata Tematik & Kuliner", "zone": "Zona Kuning", "ticket": "Rp30.000 – Rp50.000",
        "evac": {"point": "Lapangan Terbuka Gudangkahuripan", "bearing": 15, "dist": "450 m", "time": "≈6 mnt",
                 "note": "Hindari berlindung di dalam replika bangunan. Menuju lapangan terbuka yang berjarak paling dekat."},
        "coords": {"start": [-6.833157, 107.602738], "end": [-6.829141, 107.605330], "safe_name": "Lapangan Terbuka Gudangkahuripan"},
        "amenities": {
            "resto": [("Kuliner Zona Korea & Jepang", "TL · 120 m", None), ("Kuliner Zona Afrika", "T · 160 m", None)],
            "mushola": [("Mushola dekat Zona Indonesia", "B · 80 m", None)],
            "fasilitas": [("Toilet Zona India", "TG · 100 m", None), ("Pos keamanan pintu masuk", "BD · 60 m", None)],
        },
        "social": {"instagram": "@thegreatasiaafricalembang", "instagram_url": "https://www.instagram.com/thegreatasiaafricalembang/"},
    },
    {
        "id": "pineforest", "name": "Pine Forest Camp Lembang", "image": "pineforest.jpg",
        "category": "Wisata Camping & Alam", "zone": "Zona Merah", "ticket": "Rp20.000 – Rp50.000",
        "evac": {"point": "Lapangan Desa Cibodas", "bearing": 190, "dist": "1.1 km", "time": "≈15 mnt",
                 "note": "Jauhi tepi jurang dan pohon pinus condong. Bergerak ke arah lapangan desa."},
        "coords": {"start": [-6.819036, 107.665377], "end": [-6.825211, 107.657512], "safe_name": "Lapangan Desa Cibodas"},
        "amenities": {
            "resto": [("Warung makan area camping", "T · 100 m", None), ("Kedai kopi & jajanan", "TG · 70 m", None)],
            "mushola": [("Mushola sederhana dekat gerbang", "BD · 130 m", None)],
            "fasilitas": [("Toilet & kamar mandi umum", "T · 90 m", None), ("Pos ranger / pengelola", "B · 50 m", None)],
        },
        "social": {"instagram": "@pineforestcamplembang", "instagram_url": "https://www.instagram.com/pineforestcamplembang/"},
    },
    {
        "id": "deranch", "name": "De Ranch Lembang", "image": "deranch.jpg",
        "category": "Wisata Edukasi & Keluarga", "zone": "Zona Kuning", "ticket": "Rp30.000",
        "evac": {"point": "Lapangan Terbuka Seskoau", "bearing": 300, "dist": "800 m", "time": "≈10 mnt",
                 "note": "Jauhi kandang hewan dan pagar kayu saat evakuasi. Arahkan ke lapangan rumput asrama Seskoau."},
        "coords": {"start": [-6.813915, 107.621255], "end": [-6.808535, 107.623588], "safe_name": "Lapangan Terbuka Seskoau"},
        "amenities": {
            "resto": [("Kedai susu & jajanan khas", "T · 60 m", None), ("Warung makan area piknik", "TL · 110 m", None)],
            "mushola": [("Mushola dekat pintu masuk", "B · 70 m", None)],
            "fasilitas": [("Toilet umum", "TG · 80 m", None), ("Pos informasi wahana", "B · 40 m", None)],
        },
        "social": {"instagram": "@deranchlembang", "instagram_url": "https://www.instagram.com/deranchlembang/"},
    }
]

# ------------------------------------------------------------------
# INISIALISASI STATE & URL PARAMS
# ------------------------------------------------------------------
if "view" not in st.session_state:
    qp_view = st.query_params.get("view", "grid")
    qp_spot = st.query_params.get("spot", INITIAL_SPOTS[0]["id"])
    st.session_state.view = qp_view if qp_view in ("grid", "detail") else "grid"
    st.session_state.selected = qp_spot

if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "admin_name" not in st.session_state: st.session_state.admin_name = None
if "show_login" not in st.session_state: st.session_state.show_login = False
if "spots" not in st.session_state: st.session_state.spots = copy.deepcopy(INITIAL_SPOTS)
if "trigger_locate" not in st.session_state: st.session_state.trigger_locate = False

spots = st.session_state.spots
spots_by_id = {s["id"]: s for s in spots}

def _get_user_location() -> list | None:
    lat_raw = st.query_params.get("lat")
    lon_raw = st.query_params.get("lon")
    if lat_raw is None or lon_raw is None:
        return None
    try:
        lat, lon = float(lat_raw), float(lon_raw)
    except (TypeError, ValueError):
        return None
    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        return None
    return [lat, lon]

def _clear_user_location():
    if "lat" in st.query_params: del st.query_params["lat"]
    if "lon" in st.query_params: del st.query_params["lon"]
    st.session_state.trigger_locate = False
    st.rerun()

# ------------------------------------------------------------------
# STYLE CSS (Global & Admin)
# ------------------------------------------------------------------
st.markdown("""
<style>
#MainMenu, header[data-testid="stHeader"], footer, .stDeployButton { visibility: hidden; height:0; }
.stApp { background-color: #16241c; color: #eee9dc; }
.block-container { max-width: 460px; padding-top: 14px; padding-bottom: 60px; padding-left: 16px; padding-right: 16px; }
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
.ritam-photo-card { position:relative; border-radius:14px; overflow:hidden; height:150px; background-size:cover; background-position:center; margin-bottom:6px; border:1px solid rgba(238,233,220,0.12); background-color: #24392c; }
.ritam-photo-overlay { position:absolute; inset:0; background:linear-gradient(180deg, rgba(22,36,28,0) 35%, rgba(22,36,28,0.92) 100%); display:flex; flex-direction:column; justify-content:flex-end; padding:10px 12px; }
.ritam-photo-zone { position:absolute; top:8px; right:8px; font-family:monospace; font-size:8.5px; padding:3px 8px; border-radius:20px; backdrop-filter:blur(2px); }
.ritam-photo-zone.merah { background:rgba(230,87,42,0.85); color:#fff; }
.ritam-photo-zone.kuning { background:rgba(242,181,68,0.9); color:#412402; }
.ritam-photo-title { font-size:13.5px; font-weight:600; color:#fff; margin-bottom:2px; line-height:1.25; }
.ritam-photo-cat { font-size:10px; color:#d8ddd0; }
div[data-testid="stButton"] > button { width:100%; background:#24392c !important; border:1px solid rgba(238,233,220,0.18) !important; color:#eee9dc !important; font-size:12px !important; padding:8px !important; margin-bottom:16px; }
div[data-testid="stButton"] > button:hover { border-color:#f2b544 !important; color:#f2b544 !important; }
.ritam-back button { width:auto !important; background:none !important; border:none !important; color:#b7bfae !important; font-size:12px !important; padding:0 !important; margin-bottom:10px !important; }
button[data-baseweb="tab"] { font-size: 13px; padding: 10px 6px; }
div[data-baseweb="tab-list"] { gap: 4px; }
div[data-baseweb="tab-highlight"] { background-color:#f2b544 !important; }
.ritam-tag { display:inline-block; font-family: monospace; font-size: 10px; padding: 3px 9px; border-radius: 20px; border: 1px solid rgba(238,233,220,0.2); color:#b7bfae; margin-right:6px; margin-bottom:6px; }
.ritam-tag.zone { color:#e6572a; border-color:rgba(230,87,42,0.4); background:rgba(230,87,42,0.12); }
.ritam-hero { border-radius:14px; overflow:hidden; height:150px; background-size:cover; background-position:center; margin-bottom:14px; border:1px solid rgba(238,233,220,0.12); background-color: #24392c; }
.ritam-evac { background: linear-gradient(160deg, rgba(230,87,42,0.10), transparent 65%); border:1px solid rgba(230,87,42,0.35); border-radius:14px; padding:18px; text-align:center; }
.ritam-evac h3 { font-family:'Trebuchet MS',sans-serif; font-size:17px; margin:6px 0 12px; }
.ritam-eyebrow { font-family:monospace; font-size:10px; letter-spacing:0.1em; color:#e6572a; text-transform:uppercase; margin-bottom: 8px;}
.ritam-meta-row { display:flex; justify-content:center; gap:16px; flex-wrap:wrap; margin-bottom:12px; }
.ritam-meta-row div { font-family:monospace; font-size:10px; color:#b7bfae; }
.ritam-meta-row b { display:block; font-size:15px; color:#eee9dc; font-family:Georgia,serif; margin-top:2px; }
.ritam-note { font-size:12.5px; color:#b7bfae; line-height:1.55; text-align:left; border-top:1px solid rgba(230,87,42,0.25); padding-top:10px; }
.ritam-step { background:#24392c; border:1px solid rgba(238,233,220,0.12); border-radius:10px; padding:13px 14px; font-size:13px; color:#cfd6c6; line-height:1.5; display:flex; gap:12px; align-items:flex-start; margin-bottom:10px; }
.ritam-step-num { font-family:monospace; font-size:11px; color:#f2b544; background:rgba(242,181,68,0.12); border-radius:50%; width:26px; height:26px; display:flex; align-items:center; justify-content:center; flex-shrink:0; margin-top:1px; }
.ritam-card { background:#24392c; border:1px solid rgba(238,233,220,0.12); border-radius:10px; padding:15px; margin-bottom:12px; }
.ritam-card h4 { font-family:'Trebuchet MS',sans-serif; font-size:12px; letter-spacing:0.04em; text-transform:uppercase; margin-bottom:0; }
.amen-head { display:flex; align-items:center; gap:10px; margin-bottom:12px; }
.amen-icon-circle { width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.amen-icon-circle.resto { background:rgba(242,181,68,0.15); color:#f2b544; }
.amen-icon-circle.mushola { background:rgba(127,174,103,0.15); color:#7fae67; }
.amen-icon-circle.fasilitas { background:rgba(127,177,247,0.15); color:#7fb1f7; }
.ritam-item { display:flex; justify-content:space-between; align-items:center; padding:9px 0; border-top:1px solid rgba(238,233,220,0.10); font-size:12.5px; color:#cfd6c6; gap:10px; }
.ritam-dist-pill { font-family:monospace; font-size:9.5px; padding:3px 8px; border-radius:20px; white-space:nowrap; flex-shrink:0; }
.ritam-dist-pill.resto { background:rgba(242,181,68,0.12); color:#f2b544; }
.ritam-dist-pill.mushola { background:rgba(127,174,103,0.12); color:#7fae67; }
.ritam-dist-pill.fasilitas { background:rgba(127,177,247,0.12); color:#7fb1f7; }
.ritam-admin-toggle button { background:none !important; border:1px solid rgba(238,233,220,0.15) !important; color:#7c8a76 !important; font-size:11px !important; padding:4px 10px !important; border-radius:20px !important; width:auto !important; margin-bottom:0 !important; }
.ritam-admin-badge { display:inline-flex; align-items:center; gap:5px; font-family:monospace; font-size:9.5px; color:#f2b544; background:rgba(242,181,68,0.12); border:1px solid rgba(242,181,68,0.35); padding:3px 10px; border-radius:20px; margin-bottom:12px; }
.ritam-login-box { background:#1d2f24; border:1px solid rgba(238,233,220,0.15); border-radius:10px; padding:14px; margin-bottom:14px; }
.st-key-ritam_topbar div[data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; flex-direction: row !important; gap: 8px !important; }
</style>
""", unsafe_allow_html=True)

if st.session_state.is_admin:
    st.markdown("""
    <style>
    .ritam-dot-ring { border-color:#a78bfa !important; }
    .ritam-dot-ring::after { background:#a78bfa !important; }
    .ritam-admin-badge { color:#c4b5fd !important; background:rgba(167,139,250,0.14) !important; border-color:rgba(167,139,250,0.4) !important; }
    .ritam-step-num { color:#a78bfa !important; background:rgba(167,139,250,0.14) !important; }
    div[data-testid="stButton"] > button:hover { border-color:#a78bfa !important; color:#a78bfa !important; }
    .ritam-admin-banner { background:repeating-linear-gradient(135deg, #a78bfa, #a78bfa 10px, #8b6ff0 10px, #8b6ff0 20px); color:#1a1230; font-family:'Trebuchet MS',sans-serif; font-size:11px; font-weight:700; letter-spacing:0.06em; text-transform:uppercase; text-align:center; padding:6px; margin:-14px -16px 14px; border-radius:0 0 8px 8px; }
    .ritam-photo-edit-flag { position:absolute; top:8px; left:8px; width:26px; height:26px; border-radius:50%; background:rgba(167,139,250,0.9); color:#1a1230; display:flex; align-items:center; justify-content:center; font-size:12px; z-index:2; }
    </style>
    <div class="ritam-admin-banner">⚙️ Mode Admin — KELOLA DATA RITAM</div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------
# HELPER FUNCTIONS (Termasuk Rumus Bearing & GPS)
# ------------------------------------------------------------------
def image_to_data_uri(filename: str) -> str:
    if not filename: return ""
    path = os.path.join(ASSETS_DIR, filename)
    if not os.path.exists(path): return ""
    with open(path, "rb") as f: encoded = base64.b64encode(f.read()).decode()
    ext = filename.rsplit(".", 1)[-1].lower()
    return f"data:image/{'jpeg' if ext in ('jpg', 'jpeg') else ext};base64,{encoded}"

def compute_bearing(coord1, coord2):
    """Menghitung sudut (derajat) antara koordinat awal (GPS user) dan koordinat tujuan"""
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    dLon = lon2 - lon1
    y = math.sin(dLon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dLon)
    brng = math.degrees(math.atan2(y, x))
    return round((brng + 360) % 360)

def bearing_to_label(deg: int) -> str:
    dirs = [("U", 0), ("TL", 45), ("T", 90), ("TG", 135), ("S", 180), ("BD", 225), ("B", 270), ("BL", 315)]
    return min(dirs, key=lambda d: min(abs(deg - d[1]), 360 - abs(deg - d[1])))[0]

def compass_figure(bearing: int) -> go.Figure:
    fig = go.Figure()
    theta_ring = list(range(0, 361, 5))
    fig.add_trace(go.Scatterpolar(r=[1]*len(theta_ring), theta=theta_ring, mode="lines", line=dict(color="rgba(238,233,220,0.15)", width=1), showlegend=False, hoverinfo="skip"))
    polar_theta = (90 - bearing) % 360
    fig.add_trace(go.Scatterpolar(r=[0, 1], theta=[polar_theta, polar_theta], mode="lines", line=dict(color="#e6572a", width=6), showlegend=False, hoverinfo="skip"))
    fig.update_layout(
        polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=False, range=[-1, 1]), angularaxis=dict(tickmode="array", tickvals=[90, 0, 270, 180], ticktext=["U", "T", "S", "B"], tickfont=dict(color="#7c8a76", size=13, family="monospace"), showline=False, gridcolor="rgba(0,0,0,0)")),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False, margin=dict(l=10, r=10, t=10, b=10), height=260,
    )
    return fig

AMENITY_ICONS = {"resto": "🍽️", "mushola": "🕌", "fasilitas": "🚻"}

def amenity_card(title: str, items: list, kind: str):
    rows = ""
    for idx, item in enumerate(items):
        name, dist = item[0], item[1]
        btn_delete = ""
        if st.session_state.is_admin:
            btn_delete = f"""
            <form action="?delete_amenity={kind}_{idx}" method="post" style="display:inline;">
               <button style="background:transparent; border:none; color:#e6572a; cursor:pointer;" title="Hapus">✖</button>
            </form>
            """
        rows += f'<div class="ritam-item"><span>{name} {btn_delete}</span><span class="ritam-dist-pill {kind}">{dist}</span></div>'
    st.markdown(f"""
        <div class="ritam-card">
          <div class="amen-head"><div class="amen-icon-circle {kind}">{AMENITY_ICONS[kind]}</div><h4>{title}</h4></div>
          {rows if rows else "<div style='font-size:12px; color:#7c8a76;'>Belum ada data.</div>"}
        </div>
    """, unsafe_allow_html=True)

def parse_directions(steps):
    instructions = []
    for step in steps:
        dist = round(step.get('distance', 0))
        maneuver = step.get('maneuver', {})
        m_type = maneuver.get('type', '')
        m_mod = maneuver.get('modifier', 'lurus')
        street = step.get('name', '') if step.get('name', '') != '' else "jalan setapak/gang"
        arah = m_mod.replace('left', 'kiri').replace('right', 'kanan').replace('straight', 'lurus').replace('slight', 'sedikit')
        
        if m_type == 'depart': txt = f"🚶 <b>Mulai:</b> Jalan {dist}m menuju {street}."
        elif m_type == 'arrive': txt = f"🏁 <b>Tiba</b> di area aman."
        else: txt = f"↪️ Belok <b>{arah}</b> ke {street}, lanjut {dist}m." if dist > 0 else f"↪️ Belok <b>{arah}</b> ke {street}."
        if dist > 0 or m_type == 'arrive': instructions.append(txt)
    return instructions

def render_map_and_directions(start_coords, end_coords, safe_name, is_live_location=False):
    lon_s, lat_s = start_coords[1], start_coords[0]
    lon_e, lat_e = end_coords[1], end_coords[0]
    
    m = folium.Map(location=[(lat_s+lat_e)/2, (lon_s+lon_e)/2], zoom_start=15, tiles='OpenStreetMap')
    # Jika pakai Live Location, marker start bernama "Lokasi Anda (GPS)"
    start_label = "Lokasi Anda (GPS)" if is_live_location else "Titik Acuan Wisata"
    folium.CircleMarker(start_coords, radius=6, color='white', fill_color='#e6572a', fill_opacity=1, tooltip=start_label).add_to(m)
    
    folium.CircleMarker(end_coords, radius=8, color='white', fill_color='#2c7a3f', fill_opacity=1, popup=safe_name, tooltip="Titik Kumpul").add_to(m)
    folium.Circle(end_coords, radius=60, color='#7fae67', fill_color='#7fae67', fill_opacity=0.3).add_to(m)
    
    url = f"http://router.project-osrm.org/route/v1/foot/{lon_s},{lat_s};{lon_e},{lat_e}?overview=full&geometries=geojson&steps=true"
    html_inst = ""
    try:
        resp = requests.get(url, timeout=5).json()
        if resp.get("routes"):
            route = resp["routes"][0]
            r_coords = route["geometry"]["coordinates"]
            plugins.AntPath([[lat, lon] for lon, lat in r_coords], dash_array=[10, 20], delay=800, color='#1f472a', pulse_color='#f2b544', weight=4).add_to(m)
            
            dist_m = round(route["distance"])
            time_m = round(route["duration"] / 60)
            html_inst += f"<div style='background:#1d2f24; padding:10px; border-radius:8px; border:1px solid #7fae67; margin-top:10px;'><b style='color:#7fae67;'>Total Jarak:</b> {dist_m} meter <br><b style='color:#7fae67;'>Estimasi:</b> {time_m} menit jalan kaki</div>"
            html_inst += "<ul style='font-size:13px; color:#cfd6c6; margin-top:10px; padding-left:20px;'>"
            for inst in parse_directions(route["legs"][0]["steps"]): html_inst += f"<li style='margin-bottom:5px;'>{inst}</li>"
            html_inst += "</ul>"
        else: html_inst = "<p style='color:#e6572a; font-size:12px;'>Rute jalan kaki otomatis tidak ditemukan.</p>"
    except Exception: html_inst = "<p style='color:#e6572a; font-size:12px;'>Gagal mengambil rute dari satelit.</p>"
    
    m.fit_bounds([start_coords, end_coords])
    return m._repr_html_(), html_inst

# ------------------------------------------------------------------
# TOP BAR
# ------------------------------------------------------------------
with st.container(key="ritam_topbar"):
    top_l, top_r = st.columns([3, 1], gap="small")
    with top_l: st.markdown('<div class="ritam-brand" style="margin-bottom:6px;"><div class="ritam-dot-ring"></div><span>RITAM</span></div>', unsafe_allow_html=True)
    with top_r:
        st.markdown('<div class="ritam-admin-toggle" style="text-align:right;">', unsafe_allow_html=True)
        if st.session_state.is_admin:
            if st.button(f"🔓 Keluar", key="admin_logout_btn"):
                st.session_state.is_admin, st.session_state.admin_name = False, None
                st.rerun()
        else:
            if st.button("🔒 Admin", key="admin_login_toggle"): st.session_state.show_login = not st.session_state.show_login
        st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.show_login and not st.session_state.is_admin:
    st.markdown('<div class="ritam-login-box">', unsafe_allow_html=True)
    with st.form("admin_login_form", clear_on_submit=True):
        uname = st.text_input("Username", placeholder="Username")
        pw = st.text_input("Password", type="password", placeholder="Password")
        if st.form_submit_button("Masuk"):
            uc = uname.strip().lower()
            if uc in ADMIN_USERS and pw == ADMIN_USERS[uc]:
                st.session_state.is_admin, st.session_state.admin_name, st.session_state.show_login = True, uc, False
                st.rerun()
            else: st.error("Username atau password salah.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="ritam-status" style="margin:-6px 0 14px;"><span class="ritam-status-dot"></span> NORMAL · DEMO</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------
# VIEW 1: GRID UTAMA & CRUD TAMBAH WISATA
# ------------------------------------------------------------------
if st.session_state.view == "grid":
    st.markdown('<div class="ritam-heading">Kesiapsiagaan Wisata <b>Kawasan Cikole</b> — pilih lokasi kamu</div>', unsafe_allow_html=True)
    st.write("")
    
    # Hapus URL query param jika di menu grid
    if "spot" in st.query_params: del st.query_params["spot"]
    if "view" in st.query_params: del st.query_params["view"]

    cols = st.columns(2)
    for i, spot in enumerate(spots):
        with cols[i % 2]:
            data_uri = image_to_data_uri(spot.get("image", ""))
            bg_style = f"background-image:url('{data_uri}');" if data_uri else "background-color: #24392c;"
            zc = "merah" if "Merah" in spot["zone"] else "kuning"
            edit_flag = '<div class="ritam-photo-edit-flag">✎</div>' if st.session_state.is_admin else ""
            st.markdown(f"""
                <div class="ritam-photo-card" style="{bg_style}">
                  {edit_flag}
                  <div class="ritam-photo-zone {zc}">{spot['zone']}</div>
                  <div class="ritam-photo-overlay">
                    <div class="ritam-photo-title">{spot['name']}</div>
                    <div class="ritam-photo-cat">{spot['category']}</div>
                  </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("✎ Kelola" if st.session_state.is_admin else "Lihat Evakuasi", key=f"btn_{spot['id']}"):
                st.session_state.selected = spot["id"]
                st.session_state.view = "detail"
                st.query_params["view"] = "detail"
                st.query_params["spot"] = spot["id"]
                st.rerun()

    # CRUD ADMIN: Tambah Wisata Baru
    if st.session_state.is_admin:
        st.divider()
        with st.expander("➕ Tambah Destinasi Wisata Baru"):
            with st.form("add_spot_form"):
                n_name = st.text_input("Nama Destinasi")
                n_cat = st.text_input("Kategori", "Wisata Alam")
                n_zone = st.selectbox("Zona Kerentanan", ["Zona Merah", "Zona Kuning"])
                col1, col2 = st.columns(2)
                lat_s = col1.number_input("Latitude (Lokasi)", value=-6.8000, format="%.6f")
                lon_s = col2.number_input("Longitude (Lokasi)", value=107.6300, format="%.6f")
                lat_e = col1.number_input("Latitude (Titik Aman)", value=-6.8050, format="%.6f")
                lon_e = col2.number_input("Longitude (Titik Aman)", value=107.6350, format="%.6f")
                n_safe = st.text_input("Nama Titik Aman")
                
                if st.form_submit_button("Simpan Destinasi"):
                    new_spot = {
                        "id": f"spot_{len(spots)+1}", "name": n_name, "image": "", "category": n_cat, "zone": n_zone, "ticket": "-",
                        "evac": {"point": n_safe, "bearing": 0, "dist": "-", "time": "-", "note": "Panduan belum ditambahkan."},
                        "coords": {"start": [lat_s, lon_s], "end": [lat_e, lon_e], "safe_name": n_safe},
                        "amenities": {"resto": [], "mushola": [], "fasilitas": []}, "social": {"instagram": "", "instagram_url": ""}
                    }
                    st.session_state.spots.append(new_spot)
                    st.success(f"{n_name} berhasil ditambahkan!")
                    st.rerun()

# ------------------------------------------------------------------
# VIEW 2: DETAIL EVAKUASI & PELACAKAN LOKASI (GPS)
# ------------------------------------------------------------------
else:
    spot = spots_by_id.get(st.session_state.selected, spots[0])
    st.markdown('<div class="ritam-back">', unsafe_allow_html=True)
    if st.button("← Kembali ke daftar", key="back_btn"):
        st.session_state.view = "grid"
        _clear_user_location() # bersihkan koordinat gps saat kembali
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    data_uri = image_to_data_uri(spot.get("image", ""))
    bg_style = f"background-image:url('{data_uri}');" if data_uri else "background-color: #24392c;"
    st.markdown(f'<div class="ritam-hero" style="{bg_style}"></div>', unsafe_allow_html=True)

    st.markdown(f"### {spot['name']}")
    st.markdown(f'<span class="ritam-tag">{spot["category"]}</span><span class="ritam-tag zone">{spot["zone"]}</span>', unsafe_allow_html=True)
    st.write("")

    tabs = st.tabs(["🧭 Evakuasi", "✅ SOP", "🍽️ Layanan", "⚙️ Admin"] if st.session_state.is_admin else ["🧭 Evakuasi", "✅ SOP", "🍽️ Layanan"])

    # TAB 1: EVAKUASI (Dengan Real-Time GPS Tracker)
    with tabs[0]:
        user_loc = _get_user_location()
        is_live = user_loc is not None
        
        # Logika: Jika user share location, kalkulasi ulang rute dan bearing kompas
        start_coords = user_loc if is_live else spot["coords"]["start"]
        dynamic_bearing = compute_bearing(start_coords, spot["coords"]["end"]) if is_live else spot["evac"]["bearing"]
        dir_label = bearing_to_label(dynamic_bearing)

        # 1. UI Kompas (Otomatis memutar ke arah GPS terbaru jika is_live)
        st.markdown('<div class="ritam-evac">', unsafe_allow_html=True)
        st.markdown(f'<div class="ritam-eyebrow">{"Arah Evakuasi dari GPS Anda" if is_live else "Arah Evakuasi (Titik Acuan Wisata)"}</div>', unsafe_allow_html=True)
        st.plotly_chart(compass_figure(dynamic_bearing), use_container_width=True, config={"displayModeBar": False})
        st.markdown(f'<h3>{spot["coords"]["safe_name"]}</h3>', unsafe_allow_html=True)
        st.markdown(f"""
            <div class="ritam-meta-row">
              <div>Arah<b>{dir_label} ({dynamic_bearing}°)</b></div>
            </div>
            <div class="ritam-note">{spot["evac"]["note"]}</div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 2. Tombol Deteksi Lokasi
        st.write("")
        if is_live:
            st.markdown('<div class="ritam-admin-badge" style="color:#7fae67; border-color:#7fae67; background:rgba(127,174,103,0.12);">📍 Rute dihitung dari lokasi GPS Anda saat ini</div>', unsafe_allow_html=True)
            if st.button("↺ Matikan Lokasi Saya"):
                _clear_user_location()
        else:
            # Inject Script untuk meminta izin GPS HP
            if st.button("📍 Gunakan lokasi GPS saya"):
                st.session_state.trigger_locate = True

            if st.session_state.trigger_locate:
                # Script HTML & JS untuk fetch Geolocation lalu lempar ke URL Parameter Streamlit
                st.components.v1.html("""
                    <script>
                    if (navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition(function(position) {
                            var lat = position.coords.latitude;
                            var lon = position.coords.longitude;
                            var url = new URL(window.parent.location.href);
                            url.searchParams.set('lat', lat);
                            url.searchParams.set('lon', lon);
                            window.parent.location.href = url.href;
                        }, function(error) {
                            alert("Akses lokasi ditolak atau gagal. Pastikan GPS HP Anda menyala.");
                        });
                    } else {
                        alert("Browser Anda tidak mendukung Geolocation.");
                    }
                    </script>
                """, height=0)

        # 3. Peta Navigasi OpenStreetMap
        st.markdown('<div class="ritam-eyebrow" style="margin-top:15px;">Peta Navigasi Otomatis (OSRM)</div>', unsafe_allow_html=True)
        map_html, inst_html = render_map_and_directions(start_coords, spot["coords"]["end"], spot["coords"]["safe_name"], is_live)
        components.html(map_html, height=350)
        st.markdown(inst_html, unsafe_allow_html=True)

    # TAB 2: SOP
    with tabs[1]:
        steps = [
            ("Lindungi diri", "Jauhi kaca dan tebing tinggi. Lindungi kepala."),
            ("Tetap tenang", "Ikuti arah petunjuk staf & peta RITAM."),
            ("Menuju titik kumpul", "Gunakan jalur jalan kaki (GPS) untuk menghindari macet kendaraan."),
            ("Tunggu instruksi", "Tetap di titik aman hingga instruksi dari BPBD."),
        ]
        for i, (l, t) in enumerate(steps, start=1):
            st.markdown(f'<div class="ritam-step"><span class="ritam-step-num">{i}</span><div><b>{l}</b><br>{t}</div></div>', unsafe_allow_html=True)

    # TAB 3: LAYANAN (AMENITIES)
    with tabs[2]:
        amenity_card("Resto & Jajanan", spot["amenities"]["resto"], "resto")
        amenity_card("Mushola", spot["amenities"]["mushola"], "mushola")
        amenity_card("Fasilitas Lain", spot["amenities"]["fasilitas"], "fasilitas")

    # TAB 4: ADMIN CRUD (LAYANAN & EDIT DATA)
    if st.session_state.is_admin:
        with tabs[3]:
            st.subheader("🍽️ Tambah Layanan Baru")
            with st.form(f"add_amenity_{spot['id']}"):
                a_type = st.selectbox("Kategori Layanan", ["resto", "mushola", "fasilitas"])
                a_name = st.text_input("Nama Tempat")
                a_dist = st.text_input("Informasi Jarak (cth: T · 50 m)")
                if st.form_submit_button("➕ Tambah"):
                    if a_name:
                        spot["amenities"][a_type].append((a_name, a_dist, None))
                        st.success(f"{a_name} berhasil ditambahkan.")
                        st.rerun()

            st.divider()
            st.subheader("🧭 Edit Info Evakuasi (Acuan)")
            with st.form(f"edit_evac_{spot['id']}"):
                n_safe = st.text_input("Nama titik kumpul", value=spot["coords"]["safe_name"])
                n_bearing = st.slider("Arah Kompas Bawaan (Derajat)", 0, 359, spot["evac"]["bearing"])
                n_note = st.text_area("Catatan / Arahan", value=spot["evac"]["note"])
                if st.form_submit_button("💾 Simpan Perubahan"):
                    spot["coords"]["safe_name"] = n_safe
                    spot["evac"]["point"] = n_safe
                    spot["evac"]["bearing"] = n_bearing
                    spot["evac"]["note"] = n_note
                    st.success("Tersimpan!")
                    st.rerun()
