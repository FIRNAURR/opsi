"""
data.py
=======
Sumber data statis aplikasi: daftar SEMUA titik (wisata, resto,
penginapan) di kawasan Cikole–Lembang, masing-masing dengan data
evakuasi, koordinat, dan amenitasnya sendiri — beserta kamus label
arah mata angin.

DESAIN PENTING: tidak ada pemisahan struktur data antara "titik
wisata" dan "resto/penginapan". Semuanya adalah SPOTS dengan bentuk
data yang identik (coords, evac, amenities, social), dibedakan hanya
lewat field `type` untuk keperluan filter di UI. Ini karena tujuan
aplikasi adalah jalur evakuasi untuk SEMUA titik keramaian di kawasan
ini, bukan cuma tempat wisata — resto dan penginapan sama-sama
berpotensi ramai pengunjung saat kondisi darurat terjadi.

File ini sengaja tidak memuat logika apa pun — murni data — agar
mudah diaudit, di-diff pada pull request, dan suatu saat dipindah
ke sumber lain (database/CMS/API) tanpa menyentuh kode aplikasi.

CATATAN: seluruh nilai (koordinat, jarak, arah, catatan bahaya)
bersifat ILUSTRATIF untuk keperluan purwarupa penelitian dan belum
divalidasi oleh BPBD. Titik-titik yang berasal dari kategori
resto/penginapan (lihat field `type`) memakai koordinat perkiraan
berdasarkan alamat publik yang ditemukan saat data ini disusun —
BUKAN hasil pengukuran GPS langsung — sebaiknya diverifikasi dan
disesuaikan admin lewat panel "Update Informasi Destinasi".
"""

DIR_LABEL = {
    "U": "Utara", "TL": "Timur Laut", "T": "Timur", "TG": "Tenggara",
    "S": "Selatan", "BD": "Barat Daya", "B": "Barat", "BL": "Barat Laut",
}

# Label & ikon per jenis titik — dipakai UI untuk badge/filter.
TYPE_LABELS = {
    "wisata": "🧭 Wisata",
    "resto": "🍽️ Resto",
    "penginapan": "🛏️ Penginapan",
    "resto_penginapan": "🍽️🛏️ Resto & Penginapan",
}

SPOTS = [
    # ---------------------------------------------------------- WISATA
    {
        "id": "orchid", "name": "Orchid Forest Cikole", "image": "orchid.jpg",
        "type": "wisata", "category": "Wisata Alam & Outbound", "zone": "Zona Merah",
        "ticket": "Rp40.000 – Rp100.000",
        "evac": {"point": "Area Terbuka / Rest Area Cikole", "bearing": 35,
                 "dist": "180 m", "time": "≈3 mnt",
                 "note": "Jauhi jembatan gantung (Wood Bridge) dan area pepohonan tinggi. "
                         "Menuju lapangan parkir yang lebih terbuka dan jauh dari tebing."},
        "coords": {"start": [-6.780613, 107.637505], "end": [-6.789125, 107.644133], "safe_name": "Area Terbuka / Rest Area Cikole"},
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
        "type": "wisata", "category": "Alam, Outbound & Kuliner", "zone": "Zona Merah",
        "ticket": "Rp15.000",
        "evac": {"point": "Lapangan Jayagiri Cikole", "bearing": 110,
                 "dist": "220 m", "time": "≈4 mnt",
                 "note": "Segera menjauh dari pohon pinus tinggi dan bangunan kayu vintage. "
                         "Lapangan api unggun menjadi titik kumpul terluas di kawasan ini."},
        "coords": {"start": [-6.786551, 107.650482], "end": [-6.793284, 107.647901], "safe_name": "Lapangan Jayagiri Cikole"},
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
        "type": "wisata", "category": "Wisata Kuliner & Keluarga", "zone": "Zona Kuning",
        "ticket": "Rp30.000",
        "evac": {"point": "Stadion Bentang", "bearing": 250,
                 "dist": "150 m", "time": "≈2–3 mnt",
                 "note": "Jauhi tepi danau saat evakuasi berlangsung. Arahkan pengunjung ke "
                         "area parkir depan yang datar dan jauh dari struktur perahu."},
        "coords": {"start": [-6.817521, 107.618640], "end": [-6.8171828196150726, 107.61655355104207], "safe_name": "Stadion Bentang"},
        "amenities": {
            "resto": [("Perahu kuliner Sunda", "T · 40 m", "sundaness.jpg"),
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
        "type": "wisata", "category": "Wisata Tematik & Kuliner", "zone": "Zona Kuning",
        "ticket": "Rp30.000 – Rp50.000",
        "evac": {"point": "Lapangan Terbuka Gudangkahuripan", "bearing": 15,
                 "dist": "200 m", "time": "≈3–4 mnt",
                 "note": "Hindari berlindung di dalam replika bangunan negara. Menuju plaza "
                         "terbuka di zona Indonesia yang berjarak paling dekat."},
        "coords": {"start": [-6.832594844649511, 107.60476229517006], "end": [-6.829141, 107.605330], "safe_name": "Lapangan Terbuka Gudangkahuripan"},
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
        "type": "wisata", "category": "Wisata Camping & Alam", "zone": "Zona Merah",
        "ticket": "Rp20.000 – Rp50.000",
        "evac": {"point": "Lapangan Heli", "bearing": 190,
                 "dist": "160 m", "time": "≈3 mnt",
                 "note": "Jauhi tepi jurang dan pohon pinus condong. Area camping ground yang "
                         "lebih datar menjadi titik kumpul sementara."},
        "coords": {"start": [-6.815396647755517, 107.69403000790399], "end": [-6.815922, 107.694905], "safe_name": "Lapangan Heli"},
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
        "type": "wisata", "category": "Wisata Edukasi & Keluarga", "zone": "Zona Kuning",
        "ticket": "Rp30.000",
        "evac": {"point": "Alun Alun Lembang", "bearing": 300,
                 "dist": "120 m", "time": "≈2 mnt",
                 "note": "Jauhi kandang hewan dan pagar kayu saat evakuasi. Lapangan rumput "
                         "utama relatif aman dan mudah diakses dari seluruh wahana."},
        "coords": {"start": [-6.813915, 107.621255], "end": [-6.812107496782993, 107.6187219088518], "safe_name": "Alun Alun Lembang"},
        "amenities": {
            "resto": [("Kedai susu & jajanan khas peternakan", "T · 60 m"),
                       ("Warung makan area piknik", "TL · 110 m")],
            "mushola": [("Mushola dekat pintu masuk", "B · 70 m")],
            "fasilitas": [("Toilet umum", "TG · 80 m"),
                           ("Pos informasi wahana", "B · 40 m")],
        },
        "social": {"instagram": None, "instagram_url": None},
    },
    {
        "id": "pal16", "name": "Hutan Pinus Cikole (Pal 16)", "image": "pal16.jpg",
        "type": "wisata", "category": "Wisata Alam & Piknik", "zone": "Zona Merah",
        "ticket": "Rp10.000",
        "evac": {"point": "Area Parkir Utama Pal 16", "bearing": 208,
                 "dist": "160 m", "time": "≈3 mnt",
                 "note": "Jauhi hammock, gazebo kayu, dan barisan pohon pinus tinggi di tepi "
                         "jalan. Menuju area parkir utama yang lebih terbuka dan datar."},
        "coords": {"start": [-6.789200, 107.654100], "end": [-6.790500, 107.653400], "safe_name": "Area Parkir Utama Pal 16"},
        "amenities": {
            "resto": [("Warung jajanan & kopi tepi hutan pinus", "T · 60 m", None)],
            "mushola": [("Mushola dekat gerbang masuk", "B · 80 m")],
            "fasilitas": [("Toilet umum", "B · 70 m"),
                           ("Pos tiket & informasi", "T · 40 m")],
        },
        "social": {"instagram": "@pal16cikole", "instagram_url": None},
    },

    # ---------------------------------------------------- RESTO & PENGINAPAN
    # Koordinat entri di bawah ini adalah PERKIRAAN berdasarkan alamat publik
    # (lihat catatan berkas). Sebaiknya disesuaikan admin via panel edit
    # begitu koordinat presisi lapangan tersedia.
    {
        "id": "sindang-reret", "name": "Sindang Reret Cikole", "image": None,
        "type": "resto_penginapan", "category": "🍽️🛏️ Resto & Penginapan Sunda", "zone": "Zona Kuning",
        "ticket": "Sesuai pesanan / tarif kamar",
        "evac": {"point": "Area Parkir Depan Sindang Reret", "bearing": 319,
                 "dist": "100 m", "time": "≈2 mnt",
                 "note": "Jauhi bangunan utama restoran, dapur, dan ballroom tertutup. Menuju "
                         "halaman parkir depan yang lebih terbuka."},
        "coords": {"start": [-6.775000, 107.665000], "end": [-6.774200, 107.664300], "safe_name": "Area Parkir Depan Sindang Reret"},
        "amenities": {
            "resto": [],
            "mushola": [("Mushola dalam area hotel", "-")],
            "fasilitas": [("Resepsionis 24 jam", "-"), ("Toilet & kamar mandi tamu", "-")],
        },
        "social": {"instagram": "@sindangreretlembang", "instagram_url": None},
    },
    {
        "id": "sate-maranggi-hj-ita", "name": "Warung Nasi Sunda Sate Maranggi Hj Ita", "image": None,
        "type": "resto", "category": "🍽️ Kuliner Sunda & Sate Maranggi", "zone": "Zona Kuning",
        "ticket": "Sesuai pesanan",
        "evac": {"point": "Halaman Parkir Warung", "bearing": 53,
                 "dist": "60 m", "time": "≈1–2 mnt",
                 "note": "Jauhi area pembakaran sate/tungku arang. Menuju halaman parkir depan "
                         "yang lebih terbuka."},
        "coords": {"start": [-6.787000, 107.648000], "end": [-6.786700, 107.648400], "safe_name": "Halaman Parkir Warung"},
        "amenities": {
            "resto": [],
            "mushola": [],
            "fasilitas": [("Toilet umum", "-")],
        },
        "social": {"instagram": None, "instagram_url": None},
    },
    {
        "id": "bobocabin-cikole", "name": "Bobocabin Cikole", "image": None,
        "type": "penginapan", "category": "🛏️ Glamping & Penginapan", "zone": "Zona Merah",
        "ticket": "Sesuai tarif kabin",
        "evac": {"point": "Area Api Unggun Bersama", "bearing": 140,
                 "dist": "80 m", "time": "≈2 mnt",
                 "note": "Jauhi kabin kayu dan barisan pohon pinus tinggi di sekitar area "
                         "menginap. Menuju area api unggun bersama yang lebih terbuka."},
        "coords": {"start": [-6.784000, 107.641000], "end": [-6.784600, 107.641500], "safe_name": "Area Api Unggun Bersama"},
        "amenities": {
            "resto": [],
            "mushola": [],
            "fasilitas": [("BBQ grill bersama", "-"), ("Toilet & kamar mandi air panas", "-")],
        },
        "social": {"instagram": "@bobocabin", "instagram_url": None},
    },
    {
        "id": "puteri-gunung-hotel", "name": "Puteri Gunung Hotel", "image": None,
        "type": "penginapan", "category": "🏨 Penginapan & Resort", "zone": "Zona Kuning",
        "ticket": "Sesuai tarif kamar",
        "evac": {"point": "Halaman Depan Hotel", "bearing": 50,
                 "dist": "80 m", "time": "≈2 mnt",
                 "note": "Jauhi gedung bertingkat dan area kolam renang. Ikuti tangga darurat "
                         "menuju halaman depan yang terbuka."},
        "coords": {"start": [-6.788000, 107.652000], "end": [-6.787500, 107.652600], "safe_name": "Halaman Depan Hotel"},
        "amenities": {
            "resto": [],
            "mushola": [],
            "fasilitas": [("Kolam renang outdoor", "-"), ("Resepsionis 24 jam", "-")],
        },
        "social": {"instagram": None, "instagram_url": None},
    },
    {
        "id": "nirwana-lembang", "name": "Nirwana Hotel & Villa Lembang", "image": None,
        "type": "penginapan", "category": "🏨 Penginapan Keluarga", "zone": "Zona Kuning",
        "ticket": "Sesuai tarif kamar/villa",
        "evac": {"point": "Area Kolam Renang Terbuka", "bearing": 54,
                 "dist": "80 m", "time": "≈2 mnt",
                 "note": "Jauhi bangunan villa dan pagar kayu. Menuju area kolam renang yang "
                         "lebih terbuka dan luas."},
        "coords": {"start": [-6.796000, 107.628000], "end": [-6.795500, 107.628700], "safe_name": "Area Kolam Renang Terbuka"},
        "amenities": {
            "resto": [],
            "mushola": [],
            "fasilitas": [("Kolam renang", "-"), ("Area parkir luas", "-")],
        },
        "social": {"instagram": "@nirwana_lembang", "instagram_url": None},
    },
]

SPOTS_BY_ID = {s["id"]: s for s in SPOTS}
