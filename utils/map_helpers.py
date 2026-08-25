"""
utils/map_helpers.py
=====================
Logika geospasial aplikasi: pembuatan peta Folium, pemanggilan API
OSRM untuk rute pejalan kaki, parsing instruksi navigasi, dan arah kompas.
"""

import math
import folium
import requests
import streamlit as st
from folium import plugins

from config import MAP_CACHE_TTL_SECONDS, OSRM_BASE_URL, OSRM_TIMEOUT_SECONDS
from data import DIR_LABEL

def bearing_to_label(deg: int) -> str:
    dirs = [("U", 0), ("TL", 45), ("T", 90), ("TG", 135), ("S", 180),
            ("BD", 225), ("B", 270), ("BL", 315)]
    closest = min(dirs, key=lambda d: min(abs(deg - d[1]), 360 - abs(deg - d[1])))
    return DIR_LABEL[closest[0]]

def compute_bearing(start_coords: list, end_coords: list) -> int:
    lat1, lon1 = math.radians(start_coords[0]), math.radians(start_coords[1])
    lat2, lon2 = math.radians(end_coords[0]), math.radians(end_coords[1])
    dlon = lon2 - lon1

    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    bearing = math.degrees(math.atan2(x, y))
    return round((bearing + 360) % 360)

def parse_directions(steps: list) -> list:
    instructions = []
    for step in steps:
        dist = round(step.get("distance", 0))
        maneuver = step.get("maneuver", {})
        m_type = maneuver.get("type", "")
        m_mod = maneuver.get("modifier", "lurus")
        name = step.get("name", "")

        street = name if name != "" else "jalan setapak/gang"
        arah = (
            m_mod.replace("sharp", "tajam")
            .replace("slight", "sedikit")
            .replace("straight", "lurus")
            .replace("uturn", "putar balik")
            .replace("left", "kiri")
            .replace("right", "kanan")
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
    """Peta dasar dengan tema OpenStreetMap (Klasik berwarna seperti Google Maps)."""
    m = folium.Map(
        location=[
            (start_coords[0] + end_coords[0]) / 2,
            (start_coords[1] + end_coords[1]) / 2,
        ],
        zoom_start=16, 
        tiles="OpenStreetMap", # <--- TEMA KLASIK (Jalanan kuning/putih, taman hijau, dll)
    )
    
    # Marker Titik Awal (Lokasi Wisata / User)
    folium.CircleMarker(
        location=start_coords, radius=7, color="white", weight=2, fill=True,
        fill_color="#e6572a", fill_opacity=1, tooltip=f"Lokasi: {spot_name}",
    ).add_to(m)
    
    # Zona Titik Kumpul
    folium.Circle(
        location=end_coords, radius=50, color="#7fae67", weight=2, fill=True,
        fill_color="#7fae67", fill_opacity=0.4, tooltip=f"Area Aman: {safe_name}",
    ).add_to(m)
    
    # Marker Titik Kumpul (Hijau)
    folium.CircleMarker(
        location=end_coords, radius=8, color="white", weight=2, fill=True,
        fill_color="#2c7a3f", fill_opacity=1,
    ).add_to(m)
    
    return m

def _draw_fallback_route(m: folium.Map, start_coords, end_coords) -> None:
    # Garis putus-putus jika OSRM gagal
    folium.PolyLine(
        locations=[start_coords, end_coords],
        color="#1A73E8", weight=5, opacity=0.8, dash_array="8, 12",
    ).add_to(m)
    m.fit_bounds([start_coords, end_coords])

@st.cache_data(show_spinner="🗺️ Menghitung rute evakuasi teraman...", ttl=MAP_CACHE_TTL_SECONDS)
def generate_evac_map_and_instructions(spot_name: str, start_coords: list, end_coords: list, safe_name: str):
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

        # TITIK-TITIK RUTE (Animasi Berjalan)
        plugins.AntPath(
            locations=route_lat_lon, 
            dash_array=[15, 30], 
            delay=1000,          
            color="#1A73E8",     # Warna biru persis seperti jalur Google Maps
            pulse_color="#FFFFFF", 
            weight=6,            # Sedikit lebih tebal agar jelas di atas peta warna-warni
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
                f"<li style='margin-bottom: 8px; font-size: 13px; "
                f"color:var(--ritam-text-muted); line-height:1.5;'>{text}</li>"
            )
        html_output += "</ul>"

    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.RequestException, ValueError, KeyError, IndexError, Exception) as e:
        status = "fallback" if not isinstance(e, (ValueError, KeyError, IndexError)) else "no_route"
        _draw_fallback_route(m, start_coords, end_coords)
        pesan = "⚠️ Terjadi kendala memuat rute."
        if status == "fallback": pesan = "📡 Server navigasi sedang sibuk. Menampilkan panduan arah lurus."
        elif status == "no_route": pesan = "🧭 Rute jalan kaki otomatis tidak ditemukan."
        html_output += f"<p style='color:var(--ritam-accent); font-size:12px; margin:0;'>{pesan}</p>"

    html_output += "</div>"
    map_html = m._repr_html_()
    return map_html, html_output, status
