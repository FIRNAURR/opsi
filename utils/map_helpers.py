"""
utils/map_helpers.py
=====================
Logika geospasial aplikasi: pembuatan peta Folium, pemanggilan API
OSRM untuk rute pejalan kaki, parsing instruksi navigasi ke Bahasa
Indonesia, dan util arah mata angin.

RESILIENCY
----------
OSRM adalah layanan pihak ketiga publik yang bisa timeout, down,
atau tidak menemukan rute. Modul ini didesain agar kegagalan
tersebut TIDAK PERNAH membuat aplikasi crash atau menampilkan
traceback ke pengguna:

  1. Setiap kegagalan jaringan ditangkap secara spesifik
     (Timeout, ConnectionError, RequestException) maupun umum.
  2. Ketika OSRM gagal, peta tetap dirender dengan fallback berupa
     garis lurus antara lokasi wisata dan titik kumpul, dilabeli
     jelas sebagai estimasi.
  3. Fungsi mengembalikan `status` eksplisit ("ok" / "fallback" /
     "no_route") agar lapisan UI (main.py) bisa menampilkan
     st.toast/pesan yang sesuai tanpa perlu mem-parsing HTML.
"""

import folium
import requests
import streamlit as st
from folium import plugins

from config import MAP_CACHE_TTL_SECONDS, OSRM_BASE_URL, OSRM_TIMEOUT_SECONDS
from data import DIR_LABEL


def bearing_to_label(deg: int) -> str:
    """Mengubah derajat kompas (0-359) menjadi label arah mata angin Indonesia."""
    dirs = [("U", 0), ("TL", 45), ("T", 90), ("TG", 135), ("S", 180),
            ("BD", 225), ("B", 270), ("BL", 315)]
    closest = min(dirs, key=lambda d: min(abs(deg - d[1]), 360 - abs(deg - d[1])))
    return DIR_LABEL[closest[0]]


def parse_directions(steps: list) -> list:
    """Mengubah langkah mentah (steps) dari respons OSRM menjadi kalimat instruksi."""
    instructions = []
    for step in steps:
        dist = round(step.get("distance", 0))
        maneuver = step.get("maneuver", {})
        m_type = maneuver.get("type", "")
        m_mod = maneuver.get("modifier", "lurus")
        name = step.get("name", "")

        street = name if name != "" else "jalan setapak/gang"
        arah = (
            m_mod.replace("left", "kiri")
            .replace("right", "kanan")
            .replace("straight", "lurus")
            .replace("slight", "sedikit")
        )

        if m_type == "depart":
            txt = f"🚶 <b>Mulai:</b> Jalan sejauh {dist}m menuju {street}."
        elif m_type == "arrive":
            txt = "🏁 <b>SELESAI:</b> Anda telah tiba di titik kumpul."
        else:
            txt = (
                f"↪️ Belok <b>{arah}</b> ke {street}, lanjut {dist}m."
                if dist > 0
                else f"↪️ Belok <b>{arah}</b> ke {street}."
            )

        if dist > 0 or m_type == "arrive":
            instructions.append(txt)
    return instructions


def _build_base_map(start_coords, end_coords, spot_name, safe_name):
    """Peta dasar bertema gelap beserta marker lokasi wisata & titik kumpul."""
    m = folium.Map(
        location=[
            (start_coords[0] + end_coords[0]) / 2,
            (start_coords[1] + end_coords[1]) / 2,
        ],
        zoom_start=15,
        tiles="CartoDB dark_matter",
    )
    folium.CircleMarker(
        location=start_coords, radius=6, color="white", weight=1.5, fill=True,
        fill_color="#e6572a", fill_opacity=1, tooltip=f"Lokasi: {spot_name}",
    ).add_to(m)
    folium.Circle(
        location=end_coords, radius=60, color="#7fae67", weight=1, fill=True,
        fill_color="#7fae67", fill_opacity=0.3, tooltip=f"Area Aman: {safe_name}",
    ).add_to(m)
    folium.CircleMarker(
        location=end_coords, radius=8, color="white", weight=2, fill=True,
        fill_color="#2c7a3f", fill_opacity=1,
    ).add_to(m)
    return m


def _draw_fallback_route(m: folium.Map, start_coords, end_coords) -> None:
    """Fallback saat OSRM tidak tersedia: garis lurus putus-putus + fit bounds."""
    folium.PolyLine(
        locations=[start_coords, end_coords],
        color="#f2b544", weight=3, opacity=0.75, dash_array="6, 10",
    ).add_to(m)
    m.fit_bounds([start_coords, end_coords])


@st.cache_data(show_spinner="🗺️ Menghitung rute evakuasi teraman...", ttl=MAP_CACHE_TTL_SECONDS)
def generate_evac_map_and_instructions(spot_name: str, start_coords: list, end_coords: list, safe_name: str):
    """
    Menghasilkan peta evakuasi beserta instruksi jalan kaki.

    Returns
    -------
    map_html : str
        HTML peta Folium siap dirender lewat st.components.v1.html.
    instructions_html : str
        Blok HTML kartu berisi estimasi jarak/waktu dan daftar instruksi.
    status : str
        "ok"        -> rute OSRM berhasil dimuat.
        "fallback"  -> OSRM gagal dihubungi, memakai estimasi garis lurus.
        "no_route"  -> OSRM terhubung tapi tidak menemukan rute pejalan kaki.

    Fungsi ini TIDAK PERNAH melempar exception ke pemanggil — setiap
    kegagalan ditangani secara internal dengan fallback yang aman.
    """
    m = _build_base_map(start_coords, end_coords, spot_name, safe_name)

    lon_s, lat_s = start_coords[1], start_coords[0]
    lon_e, lat_e = end_coords[1], end_coords[0]
    url = f"{OSRM_BASE_URL}/{lon_s},{lat_s};{lon_e},{lat_e}?overview=full&geometries=geojson&steps=true"

    html_output = """
    <div class="ritam-card" style="margin-top: 14px;">
        <h4 style="color:var(--ritam-danger); margin-bottom:8px;">Jalur Navigasi Darat</h4>
    """
    status = "ok"

    try:
        resp = requests.get(url, timeout=OSRM_TIMEOUT_SECONDS)
        resp.raise_for_status()
        payload = resp.json()

        if not payload.get("routes"):
            raise ValueError("OSRM tidak mengembalikan rute pejalan kaki untuk koordinat ini.")

        route_data = payload["routes"][0]
        coords = route_data["geometry"]["coordinates"]
        route_lat_lon = [[lat, lon] for lon, lat in coords]

        plugins.AntPath(
            locations=route_lat_lon, dash_array=[10, 20], delay=800,
            color="#1f472a", pulse_color="#f2b544", weight=4,
        ).add_to(m)
        m.fit_bounds(route_lat_lon)

        total_dist = round(route_data["distance"])
        total_time = round(route_data["duration"] / 60)

        html_output += f"""
        <div style="font-family:monospace; font-size:11.5px; color:var(--ritam-text-muted); margin-bottom:12px; padding-bottom:8px; border-bottom:1px solid rgba(var(--ritam-line-rgb),0.1);">
            Estimasi: <b style="color:var(--ritam-accent);">{total_dist}m</b> • <b style="color:var(--ritam-accent);">{total_time} mnt</b> jalan kaki
        </div>
        <ul style='list-style-type: none; padding-left: 0; margin:0;'>
        """
        steps = route_data["legs"][0]["steps"]
        for text in parse_directions(steps):
            html_output += (
                f"<li style='margin-bottom: 8px; font-size: 12.5px; "
                f"color:var(--ritam-text-muted); line-height:1.5;'>{text}</li>"
            )
        html_output += "</ul>"

    except requests.exceptions.Timeout:
        status = "fallback"
        _draw_fallback_route(m, start_coords, end_coords)
        html_output += (
            "<p style='color:var(--ritam-accent); font-size:12px; margin:0;'>"
            "⏱️ Server navigasi tidak merespons tepat waktu. Peta menampilkan estimasi "
            "arah garis lurus — ikuti jalur fisik terdekat menuju titik kumpul.</p>"
        )

    except (requests.exceptions.ConnectionError, requests.exceptions.RequestException):
        status = "fallback"
        _draw_fallback_route(m, start_coords, end_coords)
        html_output += (
            "<p style='color:var(--ritam-accent); font-size:12px; margin:0;'>"
            "📡 Tidak dapat terhubung ke server navigasi saat ini. Peta menampilkan "
            "estimasi arah garis lurus sebagai panduan sementara.</p>"
        )

    except (ValueError, KeyError, IndexError):
        status = "no_route"
        _draw_fallback_route(m, start_coords, end_coords)
        html_output += (
            "<p style='color:var(--ritam-accent); font-size:12px; margin:0;'>"
            "🧭 Rute pejalan kaki otomatis tidak ditemukan untuk lokasi ini. Peta "
            "menampilkan estimasi arah garis lurus menuju titik kumpul.</p>"
        )

    except Exception:
        # Jaring pengaman terakhir — apa pun yang tidak terduga tetap
        # menghasilkan tampilan yang aman, bukan traceback di layar pengguna.
        status = "fallback"
        _draw_fallback_route(m, start_coords, end_coords)
        html_output += (
            "<p style='color:var(--ritam-accent); font-size:12px; margin:0;'>"
            "⚠️ Terjadi kendala saat memuat rute. Peta menampilkan estimasi arah "
            "garis lurus sebagai panduan sementara.</p>"
        )

    html_output += "</div>"
    map_html = m._repr_html_()
    return map_html, html_output, status
