"""
main.py
=======
Entry point aplikasi RITAM — Evakuasi Cikole.

Modul ini HANYA bertanggung jawab atas orkestrasi: inisialisasi
state, alur navigasi antar tampilan, dan memanggil fungsi render
dari `components/ui.py` serta logika geospasial dari
`utils/map_helpers.py`. Tidak ada CSS, markup HTML mentah, atau
logika parsing OSRM di file ini — semua sudah dipisah ke modulnya
masing-masing (lihat README.md untuk peta arsitektur lengkap).

Jalankan dengan:
    streamlit run main.py
"""

import copy
from datetime import datetime

import streamlit as st

import config
from data import SPOTS, SPOTS_BY_ID
from utils.map_helpers import bearing_to_label, compute_bearing, generate_evac_map_and_instructions
from components import ui

# ------------------------------------------------------------------
# 1. PAGE CONFIG — harus jadi perintah Streamlit pertama
# ------------------------------------------------------------------
config.configure_page()


# ------------------------------------------------------------------
# 2. STATE MANAGEMENT
# ------------------------------------------------------------------
def _init_session_state() -> None:
    """
    Inisialisasi state sekali per sesi.

    View & spot terpilih dipulihkan dari query params jika tersedia
    (mis. pengguna me-refresh halaman atau membagikan tautan),
    sehingga navigasi terasa persisten alih-alih selalu kembali ke
    tampilan grid.
    """
    if "view" not in st.session_state:
        qp_view = st.query_params.get("view", "grid")
        qp_spot = st.query_params.get("spot", SPOTS[0]["id"])
        st.session_state.view = qp_view if qp_view in ("grid", "detail") else "grid"
        st.session_state.selected = qp_spot if qp_spot in SPOTS_BY_ID else SPOTS[0]["id"]

    st.session_state.setdefault("is_admin", False)
    st.session_state.setdefault("admin_name", None)
    st.session_state.setdefault("show_login", False)
    st.session_state.setdefault("spots", copy.deepcopy(SPOTS))


def _go_to_detail(spot_id: str) -> None:
    st.session_state.view = "detail"
    st.session_state.selected = spot_id
    st.query_params["view"] = "detail"
    st.query_params["spot"] = spot_id
    st.rerun()


def _go_to_grid() -> None:
    st.session_state.view = "grid"
    st.query_params["view"] = "grid"
    if "spot" in st.query_params:
        del st.query_params["spot"]
    st.rerun()


def _get_user_location() -> list | None:
    """
    Membaca koordinat GPS pengguna dari query params (?lat=..&lon=..)
    yang disisipkan oleh tombol "Gunakan lokasi saya" (lihat
    components/ui.py -> render_locate_me_widget). Mengembalikan None
    dan aman terhadap nilai rusak/tidak valid — tidak pernah melempar
    exception ke pemanggil.
    """
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


def _clear_user_location() -> None:
    for key in ("lat", "lon"):
        if key in st.query_params:
            del st.query_params[key]
    st.rerun()


_init_session_state()
spots = st.session_state.spots
spots_by_id = {s["id"]: s for s in spots}

# ------------------------------------------------------------------
# 3. CSS & TEMA (tema admin di-inject SETELAH CSS global agar variabel
#    warnanya menimpa nilai default, bukan sebaliknya)
# ------------------------------------------------------------------
ui.inject_global_css()
if st.session_state.is_admin:
    ui.inject_admin_theme()

# ------------------------------------------------------------------
# 4. TOPBAR & LOGIN ADMIN
# ------------------------------------------------------------------
topbar_action = ui.render_topbar(st.session_state.is_admin, st.session_state.admin_name)
if topbar_action == "logout":
    st.session_state.is_admin = False
    st.session_state.admin_name = None
    st.rerun()
elif topbar_action == "login_toggle":
    st.session_state.show_login = not st.session_state.show_login

if st.session_state.show_login and not st.session_state.is_admin:
    login_result = ui.render_admin_login_form(config.admin_auth_available())
    if login_result is not None:
        uname, pw = login_result
        if config.verify_admin(uname, pw):
            st.session_state.is_admin = True
            st.session_state.admin_name = uname.strip().lower()
            st.session_state.show_login = False
            st.toast(f"Berhasil masuk sebagai {st.session_state.admin_name}", icon="✅")
            st.rerun()
        else:
            st.error("Username atau password salah.")

ui.render_status_bar(st.session_state.is_admin, st.session_state.admin_name)

# ==================================================================
# VIEW 1 — GRID PEMILIHAN TITIK WISATA
# ==================================================================
if st.session_state.view == "grid":
    st.markdown(
        '<div class="ritam-heading">Kesiapsiagaan Wisata <b>Kawasan Cikole</b> — pilih lokasi kamu</div>',
        unsafe_allow_html=True,
    )
    st.write("")

    clicked_id = ui.render_spot_grid(spots, st.session_state.is_admin)
    if clicked_id:
        _go_to_detail(clicked_id)

    ui.render_footer(
        "Data arah, jarak, dan layanan tetap <b>ilustratif</b> — purwarupa penelitian RITAM."
    )

# ==================================================================
# VIEW 2 — DETAIL EVAKUASI & LAYANAN
# ==================================================================
else:
    spot = spots_by_id.get(st.session_state.selected)
    if spot is None:
        # Guard: id pada query params tidak valid -> kembali ke grid alih-alih crash
        st.warning("Lokasi tidak ditemukan. Kembali ke daftar lokasi.")
        _go_to_grid()
        st.stop()

    st.markdown('<div class="ritam-back">', unsafe_allow_html=True)
    if st.button("← Kembali ke daftar lokasi", key="back_btn"):
        _go_to_grid()
    st.markdown("</div>", unsafe_allow_html=True)

    ui.render_detail_header(spot)
    st.write("")

    if st.session_state.is_admin:
        tab_evac, tab_sop, tab_amen, tab_admin = st.tabs(["🧭 Evakuasi", "✅ SOP", "🍽️ Layanan", "⚙️ Admin"])
    else:
        tab_evac, tab_sop, tab_amen = st.tabs(["🧭 Evakuasi", "✅ SOP", "🍽️ Layanan"])

    # ---------------- TAB: EVAKUASI ----------------
    with tab_evac:
        user_location = _get_user_location()
        using_live_location = user_location is not None
        start_coords = user_location if using_live_location else spot["coords"]["start"]
        bearing = (
            compute_bearing(start_coords, spot["coords"]["end"])
            if using_live_location
            else spot["evac"]["bearing"]
        )
        dir_label = bearing_to_label(bearing)

        st.markdown('<div class="ritam-evac">', unsafe_allow_html=True)
        eyebrow = "Arah Evakuasi dari Lokasi Anda" if using_live_location else "Arah Evakuasi Terdekat"
        st.markdown(f'<div class="ritam-eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
        st.plotly_chart(
            ui.compass_figure(bearing),
            width="stretch",
            config={"displayModeBar": False},
        )
        st.markdown(f'<h3>{spot["coords"]["safe_name"]}</h3>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="ritam-meta-row">
              <div>Arah<b>{dir_label} ({bearing}°)</b></div>
            </div>
            <div class="ritam-note">{spot["evac"]["note"]}</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # ---- Titik awal: lokasi GPS pengguna (mode "Google Maps") vs
        #      titik acuan statis lokasi wisata (mode ilustratif bawaan) ----
        if using_live_location:
            st.markdown(
                '<div class="ritam-admin-badge" style="color:var(--ritam-success);'
                'border-color:rgba(var(--ritam-success-rgb),0.4);'
                'background:rgba(var(--ritam-success-rgb),0.12);">'
                '📍 Rute &amp; arah dihitung dari lokasi Anda saat ini</div>',
                unsafe_allow_html=True,
            )
            if st.button("↺ Pakai titik acuan bawaan lokasi wisata", key="reset_geo_location"):
                _clear_user_location()
        else:
            st.caption(
                "Arah di atas adalah estimasi dari titik acuan resmi lokasi wisata. "
                "Aktifkan lokasi Anda untuk arah & rute real-time dari posisi Anda sekarang."
            )
            ui.render_locate_me_widget()

        st.markdown('<div class="ritam-eyebrow" style="margin-bottom:8px;">Peta Rute Evakuasi</div>', unsafe_allow_html=True)

        # generate_evac_map_and_instructions sudah menangani seluruh
        # kegagalan OSRM secara internal (lihat utils/map_helpers.py) dan
        # tidak pernah melempar exception ke sini. `status` dipakai murni
        # untuk memberi tahu pengguna lewat toast, bukan untuk logika alur.
        # Saat mode lokasi live aktif, start_coords adalah GPS pengguna —
        # sehingga cache rute otomatis unik per koordinat, bukan per spot.
        map_html, instructions_html, status = generate_evac_map_and_instructions(
            spot["name"], start_coords, spot["coords"]["end"], spot["coords"]["safe_name"]
        )
        if status == "fallback":
            st.toast("Server navigasi sedang bermasalah — memakai estimasi arah garis lurus.", icon="📡")
        elif status == "no_route":
            st.toast("Rute pejalan kaki otomatis tidak ditemukan untuk lokasi ini.", icon="🧭")

        # map_html & instructions_html dibangkitkan sepenuhnya dari data
        # internal (koordinat + respons OSRM), bukan input mentah dari
        # pengguna, sehingga aman dirender lewat st.iframe/st.html.
        # st.html dipakai (bukan st.markdown) agar markup panjang & indentasi
        # tidak pernah salah ditafsir sebagai blok kode oleh parser Markdown.
        st.iframe(map_html, height=350)
        st.html(instructions_html)

    # ---------------- TAB: SOP ----------------
    with tab_sop:
        ui.render_sop_steps()

    # ---------------- TAB: LAYANAN ----------------
    with tab_amen:
        ui.render_social_card(spot)
        ui.render_amenity_card("Resto & Jajanan", spot["amenities"]["resto"], "resto")
        ui.render_amenity_card("Mushola", spot["amenities"]["mushola"], "mushola")
        ui.render_amenity_card("Fasilitas Lain", spot["amenities"]["fasilitas"], "fasilitas")

    # ---------------- TAB: ADMIN (hanya muncul jika login) ----------------
    if st.session_state.is_admin:
        with tab_admin:
            st.caption(
                "Update data arah evakuasi untuk lokasi ini. Perubahan langsung terlihat "
                "di tab Evakuasi (berlaku selama sesi berjalan — lihat catatan produksi di README.md)."
            )
            last_edit = spot.get("_last_edit")
            if last_edit:
                st.markdown(
                    f'<div class="ritam-admin-badge">✎ Terakhir diedit oleh '
                    f'<b>{last_edit["by"]}</b> · {last_edit["at"]}</div>',
                    unsafe_allow_html=True,
                )
            with st.form(f"edit_evac_{spot['id']}"):
                point = st.text_input("Nama titik kumpul", value=spot["coords"]["safe_name"])
                bearing = st.slider("Arah (derajat, 0=Utara)", 0, 359, spot["evac"]["bearing"])
                note = st.text_area("Catatan bahaya / arahan", value=spot["evac"]["note"], height=100)
                save = st.form_submit_button("💾 Simpan perubahan")
                if save:
                    spot["coords"]["safe_name"] = point
                    spot["evac"]["bearing"] = bearing
                    spot["evac"]["note"] = note
                    spot["_last_edit"] = {
                        "by": st.session_state.admin_name,
                        "at": datetime.now().strftime("%d %b %Y, %H:%M"),
                    }
                    # Data rute meng-cache berdasarkan argumen fungsi (nama,
                    # koordinat, safe_name) — mengubah safe_name otomatis
                    # membuat cache lama tidak terpakai lagi tanpa perlu
                    # invalidasi manual.
                    st.toast("Perubahan tersimpan untuk sesi ini.", icon="💾")
                    st.rerun()

    ui.render_footer("Arah, rute, dan layanan bersifat <b>ilustratif</b> — belum divalidasi BPBD.")
