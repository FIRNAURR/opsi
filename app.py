\
from __future__ import annotations

import copy
import re
from datetime import datetime

import streamlit as st

import config
from data import SPOTS, SPOTS_BY_ID, TYPE_LABELS
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
    if "view" not in st.session_state:
        qp_view = st.query_params.get("view", "grid")
        qp_spot = st.query_params.get("spot", SPOTS[0]["id"])
        st.session_state.view = qp_view if qp_view in ("grid", "detail") else "grid"
        st.session_state.selected = qp_spot if qp_spot in SPOTS_BY_ID else SPOTS[0]["id"]

    st.session_state.setdefault("is_admin", False)
    st.session_state.setdefault("admin_name", None)
    st.session_state.setdefault("show_login", False)
    st.session_state.setdefault("spots", copy.deepcopy(SPOTS))
    st.session_state.setdefault("type_filter", "semua")
    st.session_state.setdefault("show_add_spot_form", False)

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

def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "item"

def _unique_id(base_slug: str, existing_ids: set) -> str:
    candidate = base_slug
    i = 2
    while candidate in existing_ids:
        candidate = f"{base_slug}-{i}"
        i += 1
    return candidate

_init_session_state()
spots = st.session_state.spots
spots_by_id = {s["id"]: s for s in spots}

# ------------------------------------------------------------------
# 3. CSS & TEMA
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
# VIEW 1 — MENU UTAMA
# ==================================================================
if st.session_state.view == "grid":
    st.markdown(
        '<div class="ritam-heading">Kesiapsiagaan <b>Kawasan Cikole–Lembang</b> — pilih lokasi kamu</div>',
        unsafe_allow_html=True,
    )

    wisata_n = sum(1 for s in spots if s["type"] == "wisata")
    resto_n = sum(1 for s in spots if s["type"] in ("resto", "resto_penginapan"))
    penginapan_n = sum(1 for s in spots if s["type"] in ("penginapan", "resto_penginapan"))
    ui.render_stat_row(wisata_n, resto_n, penginapan_n)
    ui.render_zone_legend()
    st.write("")

    if st.session_state.is_admin:
        with st.expander("➕ Tambah Titik Baru (Wisata/Resto/Penginapan)", expanded=st.session_state.show_add_spot_form):
            with st.form("add_spot_form", clear_on_submit=True):
                new_type = st.selectbox(
                    "Jenis titik", ["wisata", "resto", "penginapan", "resto_penginapan"],
                    format_func=lambda k: TYPE_LABELS[k],
                )
                c1, c2 = st.columns(2)
                with c1:
                    new_name = st.text_input("Nama tempat")
                    new_category = st.text_input("Kategori", placeholder="mis. Wisata Alam & Outbound / Kuliner Sunda")
                    new_ticket = st.text_input("Harga tiket / tarif", placeholder="mis. Rp20.000 atau Sesuai pesanan")
                with c2:
                    new_zone = st.selectbox("Zona risiko", ["Zona Merah", "Zona Kuning"])
                    new_image = st.text_input("URL foto (opsional)", placeholder="https://...")
                new_point = st.text_input("Nama titik kumpul evakuasi", placeholder="mis. Halaman Parkir Depan")
                c3, c4 = st.columns(2)
                with c3:
                    new_start_lat = st.number_input("Latitude lokasi", value=-6.800000, format="%.6f")
                    new_end_lat = st.number_input("Latitude titik kumpul", value=-6.800000, format="%.6f")
                with c4:
                    new_start_lon = st.number_input("Longitude lokasi", value=107.630000, format="%.6f")
                    new_end_lon = st.number_input("Longitude titik kumpul", value=107.630000, format="%.6f")
                new_note = st.text_area("Catatan bahaya / arahan evakuasi", height=90,
                                         placeholder="mis. Jauhi pohon tinggi dan tebing, menuju area terbuka...")
                submitted_new_spot = st.form_submit_button("➕ Tambah Titik")
                if submitted_new_spot:
                    if not new_name.strip():
                        st.error("Nama tempat wajib diisi.")
                    else:
                        new_id = _unique_id(_slugify(new_name), set(spots_by_id.keys()))
                        start_coords_new = [new_start_lat, new_start_lon]
                        end_coords_new = [new_end_lat, new_end_lon]
                        new_spot = {
                            "id": new_id,
                            "name": new_name.strip(),
                            "image": new_image.strip() or None,
                            "type": new_type,
                            "category": new_category.strip() or TYPE_LABELS[new_type],
                            "zone": new_zone,
                            "ticket": new_ticket.strip() or "-",
                            "evac": {
                                "point": new_point.strip() or "Titik Kumpul",
                                "bearing": compute_bearing(start_coords_new, end_coords_new),
                                "dist": "-", "time": "-",
                                "note": new_note.strip() or "Catatan evakuasi belum diisi.",
                            },
                            "coords": {
                                "start": start_coords_new, "end": end_coords_new,
                                "safe_name": new_point.strip() or "Titik Kumpul",
                            },
                            "amenities": {"resto": [], "mushola": [], "fasilitas": []},
                            "social": {"instagram": None, "instagram_url": None},
                            "_last_edit": {
                                "by": st.session_state.admin_name,
                                "at": datetime.now().strftime("%d %b %Y, %H:%M"),
                            },
                        }
                        spots.append(new_spot)
                        st.session_state.show_add_spot_form = False
                        st.toast(f'"{new_spot["name"]}" berhasil ditambahkan.', icon="✅")
                        st.rerun()

    filter_counts = {
        "semua": len(spots),
        "wisata": wisata_n,
        "resto": sum(1 for s in spots if s["type"] in ("resto", "resto_penginapan")),
        "penginapan": sum(1 for s in spots if s["type"] in ("penginapan", "resto_penginapan")),
    }
    filter_clicked = ui.render_type_filter(st.session_state.type_filter, filter_counts)
    if filter_clicked:
        st.session_state.type_filter = filter_clicked
        st.rerun()

    active_filter = st.session_state.type_filter
    if active_filter == "semua":
        visible_spots = spots
    elif active_filter == "resto":
        visible_spots = [s for s in spots if s["type"] in ("resto", "resto_penginapan")]
    elif active_filter == "penginapan":
        visible_spots = [s for s in spots if s["type"] in ("penginapan", "resto_penginapan")]
    else:
        visible_spots = [s for s in spots if s["type"] == active_filter]

    clicked_id = ui.render_spot_grid(visible_spots, st.session_state.is_admin)
    if clicked_id:
        _go_to_detail(clicked_id)

    ui.render_footer(
        "Semua titik — wisata, resto, dan penginapan — punya jalur evakuasi masing-masing. "
        "Data arah, jarak, dan layanan tetap <b>ilustratif</b> — purwarupa penelitian RITAM."
    )

# ==================================================================
# VIEW 2 — DETAIL EVAKUASI & LAYANAN
# ==================================================================
else:
    spot = spots_by_id.get(st.session_state.selected)
    if spot is None:
        st.warning("Lokasi tidak ditemukan. Kembali ke daftar lokasi.")
        _go_to_grid()
        st.stop()

    st.markdown('<div class="ritam-back">', unsafe_allow_html=True)
    if st.button("← Kembali ke daftar lokasi", key="back_btn"):
        _go_to_grid()
    st.markdown("</div>", unsafe_allow_html=True)

    ui.render_detail_header(spot)
    st.write("")

    if spot.get("name") == "Orchid Forest Cikole":
        ui.render_map_card(
            image_path="assets\\peta_wisata_orchid.jpg", 
            title="Peta Wisata Orchid Forest",
            desc="Lihat titik kumpul, fasilitas, dan rute di dalam area Orchid Forest. (Klik gambar untuk memperbesar)"
    )

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
        
        # KOMPAS DIHAPUS DARI SINI
        
        st.markdown(f'<h3 style="margin-top: 10px;">{spot["coords"]["safe_name"]}</h3>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="ritam-meta-row">
              <div>Arah <b>{dir_label} ({bearing}°)</b></div>
            </div>
            <div class="ritam-note">{spot["evac"]["note"]}</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

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

        map_html, instructions_html, status = generate_evac_map_and_instructions(
            spot["name"], start_coords, spot["coords"]["end"], spot["coords"]["safe_name"]
        )
        if status == "fallback":
            st.toast("Server navigasi sedang bermasalah — memakai estimasi arah garis lurus.", icon="📡")
        elif status == "no_route":
            st.toast("Rute pejalan kaki otomatis tidak ditemukan untuk lokasi ini.", icon="🧭")

        config.render_iframe(map_html, height=350)
        config.render_html(instructions_html)

    # ---------------- TAB: SOP ----------------
    with tab_sop:
        ui.render_sop_steps()

    # ---------------- TAB: LAYANAN ----------------
    with tab_amen:
        ui.render_social_card(spot)
        ui.render_amenity_card("Resto & Jajanan", spot["amenities"]["resto"], "resto")
        ui.render_amenity_card("Mushola", spot["amenities"]["mushola"], "mushola")
        ui.render_amenity_card("Fasilitas Lain", spot["amenities"]["fasilitas"], "fasilitas")

    # ---------------- TAB: ADMIN ----------------
    if st.session_state.is_admin:
        with tab_admin:
            last_edit = spot.get("_last_edit")
            if last_edit:
                st.markdown(
                    f'<div class="ritam-admin-badge">✎ Terakhir diedit oleh '
                    f'<b>{last_edit["by"]}</b> · {last_edit["at"]}</div>',
                    unsafe_allow_html=True,
                )

            st.markdown("#### ✏️ Update Informasi Destinasi")
            st.caption(f"ID internal: `{spot['id']}` · Perubahan berlaku selama sesi berjalan.")
            with st.form(f"edit_spot_{spot['id']}"):
                type_in = st.selectbox(
                    "Jenis titik", ["wisata", "resto", "penginapan", "resto_penginapan"],
                    index=["wisata", "resto", "penginapan", "resto_penginapan"].index(spot.get("type", "wisata")),
                    format_func=lambda k: TYPE_LABELS[k],
                )
                c1, c2 = st.columns(2)
                with c1:
                    name_in = st.text_input("Nama destinasi", value=spot["name"])
                    category_in = st.text_input("Kategori", value=spot["category"])
                    ticket_in = st.text_input("Harga tiket", value=spot["ticket"])
                with c2:
                    zone_in = st.selectbox(
                        "Zona risiko", ["Zona Merah", "Zona Kuning"],
                        index=0 if spot["zone"] == "Zona Merah" else 1,
                    )
                    image_in = st.text_input("URL/nama file foto", value=spot.get("image") or "")
                point_in = st.text_input("Nama titik kumpul evakuasi", value=spot["coords"]["safe_name"])
                c3, c4 = st.columns(2)
                with c3:
                    start_lat_in = st.number_input("Latitude lokasi wisata", value=float(spot["coords"]["start"][0]), format="%.6f")
                    end_lat_in = st.number_input("Latitude titik kumpul", value=float(spot["coords"]["end"][0]), format="%.6f")
                with c4:
                    start_lon_in = st.number_input("Longitude lokasi wisata", value=float(spot["coords"]["start"][1]), format="%.6f")
                    end_lon_in = st.number_input("Longitude titik kumpul", value=float(spot["coords"]["end"][1]), format="%.6f")
                note_in = st.text_area("Catatan bahaya / arahan", value=spot["evac"]["note"], height=100)
                save = st.form_submit_button("💾 Simpan perubahan")
                if save:
                    if not name_in.strip():
                        st.error("Nama destinasi wajib diisi.")
                    else:
                        spot["type"] = type_in
                        spot["name"] = name_in.strip()
                        spot["category"] = category_in.strip()
                        spot["ticket"] = ticket_in.strip()
                        spot["zone"] = zone_in
                        spot["image"] = image_in.strip() or None
                        spot["coords"]["safe_name"] = point_in.strip()
                        spot["coords"]["start"] = [start_lat_in, start_lon_in]
                        spot["coords"]["end"] = [end_lat_in, end_lon_in]
                        spot["evac"]["note"] = note_in.strip()
                        spot["evac"]["bearing"] = compute_bearing(spot["coords"]["start"], spot["coords"]["end"])
                        spot["_last_edit"] = {
                            "by": st.session_state.admin_name,
                            "at": datetime.now().strftime("%d %b %Y, %H:%M"),
                        }
                        st.toast("Perubahan tersimpan untuk sesi ini.", icon="💾")
                        st.rerun()

            st.divider()

            st.markdown("#### 🍴 Kelola Layanan (Resto, Mushola, Fasilitas)")
            _kind_labels = {"resto": "Resto & Jajanan", "mushola": "Mushola", "fasilitas": "Fasilitas Lain"}
            for kind, kind_label in _kind_labels.items():
                st.markdown(f"**{kind_label}**")
                items = spot["amenities"][kind]
                if not items:
                    st.caption("Belum ada data.")
                for idx, item in enumerate(items):
                    item_name, item_dist = item[0], item[1]
                    ic1, ic2 = st.columns([5, 1])
                    with ic1:
                        st.write(f"{item_name} · {item_dist}")
                    with ic2:
                        if st.button("🗑️", key=f"del_amen_{spot['id']}_{kind}_{idx}"):
                            items.pop(idx)
                            st.toast(f"{kind_label} dihapus.", icon="🗑️")
                            st.rerun()
                with st.form(f"add_amen_{spot['id']}_{kind}", clear_on_submit=True):
                    ac1, ac2 = st.columns(2)
                    with ac1:
                        amen_name = st.text_input("Nama layanan", key=f"amen_name_{spot['id']}_{kind}")
                    with ac2:
                        amen_dist = st.text_input("Jarak (mis. 'T · 90 m')", key=f"amen_dist_{spot['id']}_{kind}")
                    amen_photo = st.text_input("URL foto (opsional)", key=f"amen_photo_{spot['id']}_{kind}")
                    if st.form_submit_button(f"➕ Tambah {kind_label}"):
                        if amen_name.strip():
                            items.append((amen_name.strip(), amen_dist.strip() or "-", amen_photo.strip() or None))
                            st.toast(f"{kind_label} ditambahkan.", icon="✅")
                            st.rerun()
                        else:
                            st.error("Nama layanan wajib diisi.")
                st.markdown("---")

            st.markdown("#### 🗑️ Hapus Destinasi")
            confirm_key = f"confirm_del_{spot['id']}"
            if not st.session_state.get(confirm_key):
                if st.button("🗑️ Hapus destinasi ini", key=f"del_btn_{spot['id']}"):
                    st.session_state[confirm_key] = True
                    st.rerun()
            else:
                st.warning(f'Yakin ingin menghapus **"{spot["name"]}"**? Tindakan ini tidak bisa dibatalkan untuk sesi ini.')
                dc1, dc2 = st.columns(2)
                with dc1:
                    if st.button("Ya, hapus", key=f"del_confirm_{spot['id']}"):
                        st.session_state.spots = [s for s in spots if s["id"] != spot["id"]]
                        st.session_state.pop(confirm_key, None)
                        st.toast(f'"{spot["name"]}" dihapus.', icon="🗑️")
                        _go_to_grid()
                with dc2:
                    if st.button("Batal", key=f"del_cancel_{spot['id']}"):
                        st.session_state.pop(confirm_key, None)
                        st.rerun()

    ui.render_footer("Arah, rute, dan layanan bersifat <b>ilustratif</b> — belum divalidasi BPBD.")
