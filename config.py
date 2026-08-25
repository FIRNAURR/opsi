"""
config.py
=========
Konfigurasi terpusat untuk aplikasi RITAM — Evakuasi Cikole.

Bertanggung jawab atas:
  - Page config Streamlit (dipanggil sekali dari main.py)
  - Path direktori aset
  - Parameter jaringan/cache untuk pemanggilan OSRM
  - Pemuatan kredensial admin murni dari st.secrets (TIDAK ADA
    kredensial hardcoded di source code — lihat pilar Keamanan)
"""

import os
import streamlit as st

# ------------------------------------------------------------------
# PATH & DIREKTORI
# ------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# ------------------------------------------------------------------
# PENGATURAN HALAMAN
# ------------------------------------------------------------------
PAGE_CONFIG = dict(
    page_title="RITAM — Evakuasi Cikole",
    page_icon="🧭",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def configure_page() -> None:
    """Harus dipanggil satu kali sebagai perintah Streamlit paling awal di main.py."""
    st.set_page_config(**PAGE_CONFIG)


# ------------------------------------------------------------------
# JARINGAN & CACHE (OSRM)
# ------------------------------------------------------------------
OSRM_BASE_URL = "http://router.project-osrm.org/route/v1/foot"
OSRM_TIMEOUT_SECONDS = 6
MAP_CACHE_TTL_SECONDS = 3600  # koordinat statis -> aman di-cache 1 jam per sesi


# ------------------------------------------------------------------
# KREDENSIAL ADMIN — MURNI DARI st.secrets, TANPA FALLBACK HARDCODED
# ------------------------------------------------------------------
# Format yang diharapkan pada .streamlit/secrets.toml:
#
#   [admins]
#   admin = "password-super-rahasia"
#   pengelola_cikole = "password_lain"
#
# Lihat .streamlit/secrets.toml.example sebagai template.

@st.cache_resource(show_spinner=False)
def load_admin_users() -> dict:
    """
    Memuat kredensial admin dari secrets.toml.

    Mengembalikan dict kosong (bukan None) apabila secrets belum
    dikonfigurasi, agar seluruh pemanggil cukup melakukan pengecekan
    `if not users` tanpa perlu try/except berulang. Ketersediaan
    autentikasi admin sebaiknya dicek lewat admin_auth_available().
    """
    try:
        admins_section = st.secrets["admins"]
        parsed = dict(admins_section)
        return parsed
    except Exception:
        # Mencakup: file secrets.toml tidak ada, section [admins] tidak
        # ada, atau st.secrets tidak dapat diparse. Sengaja "fail closed"
        # -> login admin otomatis nonaktif, bukan crash aplikasi.
        return {}


def admin_auth_available() -> bool:
    """True apabila secrets.toml sudah berisi minimal satu akun admin."""
    return len(load_admin_users()) > 0


def verify_admin(username: str, password: str) -> bool:
    """Verifikasi kredensial. Selalu False apabila secrets belum dikonfigurasi."""
    users = load_admin_users()
    if not users:
        return False
    uname_clean = (username or "").strip().lower()
    return uname_clean in users and password == users[uname_clean]


# ------------------------------------------------------------------
# KOMPATIBILITAS LINTAS VERSI STREAMLIT
# ------------------------------------------------------------------
# `st.html` dan `st.iframe` baru resmi ada mulai Streamlit 1.56 (Maret
# 2026). Jika requirements.txt sudah pernah terpasang sebelumnya dengan
# versi lebih lama (mis. venv lama yang belum di-upgrade), memanggil
# st.html/st.iframe langsung akan menghasilkan AttributeError dan
# aplikasi gagal start. Tiga fungsi di bawah ini mendeteksi ketersediaan
# API baru tsb saat runtime dan otomatis jatuh ke API lama yang setara
# (st.components.v1.html/.iframe, use_container_width) bila belum ada —
# jadi aplikasi tetap jalan di kedua rentang versi tanpa memaksa upgrade.
def render_html(content: str, *, allow_js: bool = False) -> None:
    """Pengganti aman untuk st.html() — fallback ke st.markdown bila belum tersedia."""
    if hasattr(st, "html"):
        if allow_js:
            st.html(content, unsafe_allow_javascript=True)
        else:
            st.html(content)
    else:
        st.markdown(content, unsafe_allow_html=True)


def render_iframe(content: str, *, height: int = 350) -> None:
    """Pengganti aman untuk st.iframe() — fallback ke st.components.v1.html bila belum tersedia."""
    if hasattr(st, "iframe"):
        st.iframe(content, height=height)
    else:
        import streamlit.components.v1 as components
        components.html(content, height=height)


def render_plotly(fig, **kwargs) -> None:
    """Pengganti aman untuk st.plotly_chart(..., width='stretch') di versi Streamlit
    yang belum mengenal parameter `width` (masih memakai use_container_width)."""
    try:
        st.plotly_chart(fig, width="stretch", **kwargs)
    except TypeError:
        st.plotly_chart(fig, use_container_width=True, **kwargs)
