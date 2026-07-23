"""
utils/asset_helpers.py
=======================
Util pemuatan aset statis (gambar) menjadi data URI base64, dengan
cache agar file tidak dibaca ulang dari disk pada setiap rerun
Streamlit (lihat pilar Optimasi Performa).
"""

import base64
import os

import streamlit as st

from config import ASSETS_DIR


@st.cache_data(show_spinner=False)
def image_to_data_uri(filename: str) -> str:
    """
    Mengonversi file gambar di ASSETS_DIR menjadi data URI base64.

    Mengembalikan string kosong secara aman apabila nama file kosong
    atau file tidak ditemukan/tidak dapat dibaca, sehingga pemanggil
    cukup melakukan `if data_uri else <placeholder>` tanpa perlu
    try/except berulang di banyak tempat.
    """
    if not filename:
        return ""
    try:
        path = os.path.join(ASSETS_DIR, filename)
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        ext = filename.rsplit(".", 1)[-1].lower()
        mime = "jpeg" if ext in ("jpg", "jpeg") else ext
        return f"data:image/{mime};base64,{encoded}"
    except (FileNotFoundError, OSError, ValueError):
        return ""
