import base64
import os
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
            "resto": [("Kedai kuliner Rabbit Forest", "T · 90 m"),
                       ("Warung kopi Orchid House", "TL · 140 m")],
            "mushola": [("Mushola dekat loket masuk", "B · 60 m")],
            "fasilitas": [("Toilet umum area parkir", "B · 70 m"),
                           ("Pos informasi & P3K", "T · 100 m")],
        },
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
            "resto": [("Saung makan area vintage", "TG · 130 m"),
                       ("Kedai jajanan pinggir taman", "T · 80 m")],
            "mushola": [("Mushola dekat area camping ground", "BD · 150 m")],
            "fasilitas": [("Toilet & kamar bilas", "T · 90 m"),
                           ("Pos keamanan", "BD · 60 m")],
        },
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
            "resto": [("Perahu kuliner Sunda", "T · 40 m"),
                       ("Zona jajanan internasional", "TL · 100 m")],
            "mushola": [("Mushola dekat pintu masuk", "B · 90 m")],
            "fasilitas": [("Toilet area playground", "TG · 70 m"),
                           ("Loket & pos informasi", "B · 50 m")],
        },
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
        text-transform:uppercase; margin-bottom:10px; }
    .ritam-item { display:flex; justify-content:space-between; align-items:center; padding:8px 0;
        border-top:1px solid rgba(238,233,220,0.10); font-size:12.5px; color:#cfd6c6; gap:8px; }
    .ritam-item:first-of-type { border-top:none; }
    .ritam-dir { font-family:monospace; font-size:10px; color:#7c8a76; white-space:nowrap; }

    .ritam-footer { font-size:10.5px; color:#7c8a76; line-height:1.6; padding-top:10px; }
    .ritam-footer b { color:#f2b544; }
    </style>
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


def amenity_card(title: str, items: list, icon: str):
    rows = "".join(
        f'<div class="ritam-item">{name}<span class="ritam-dir">{dist}</span></div>'
        for name, dist in items
    )
    st.markdown(f'<div class="ritam-card"><h4>{icon} {title}</h4>{rows}</div>', unsafe_allow_html=True)


def zone_class(zone: str) -> str:
    return "merah" if "Merah" in zone else "kuning"


# ------------------------------------------------------------------
# STATE
# ------------------------------------------------------------------
if "view" not in st.session_state:
    st.session_state.view = "grid"
if "selected" not in st.session_state:
    st.session_state.selected = SPOTS[0]["id"]

# ------------------------------------------------------------------
# TOP BAR (selalu tampil)
# ------------------------------------------------------------------
st.markdown(
    """
    <div class="ritam-topbar">
      <div class="ritam-brand"><div class="ritam-dot-ring"></div><span>RITAM</span></div>
      <div class="ritam-status"><span class="ritam-status-dot"></span> NORMAL · DEMO</div>
    </div>
    """,
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
    for i, spot in enumerate(SPOTS):
        with cols[i % 2]:
            data_uri = image_to_data_uri(spot["image"])
            zc = zone_class(spot["zone"])
            st.markdown(
                f"""
                <div class="ritam-photo-card" style="background-image:url('{data_uri}')">
                  <div class="ritam-photo-zone {zc}">{spot['zone']}</div>
                  <div class="ritam-photo-overlay">
                    <div class="ritam-photo-title">{spot['name']}</div>
                    <div class="ritam-photo-cat">{spot['category']}</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Lihat arah evakuasi", key=f"btn_{spot['id']}"):
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
    spot = SPOTS_BY_ID[st.session_state.selected]

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
        amenity_card("Resto & Jajanan", spot["amenities"]["resto"], "🍽️")
        amenity_card("Mushola", spot["amenities"]["mushola"], "🕌")
        amenity_card("Fasilitas Lain", spot["amenities"]["fasilitas"], "🚻")

    st.markdown(
        '<div class="ritam-footer">Arah, jarak, waktu tempuh, dan daftar layanan bersifat '
        '<b>ilustratif</b> — purwarupa penelitian RITAM (Tim Kayaraya, OPSI 2026), belum divalidasi '
        'survei GPS lapangan atau koordinasi resmi dengan BPBD/pengelola wisata.</div>',
        unsafe_allow_html=True,
    )
