"""
data.py
=======
Sumber data statis aplikasi: daftar titik wisata (SPOTS) beserta
data evakuasi, koordinat, dan amenitasnya, serta kamus label arah
mata angin.

File ini sengaja tidak memuat logika apa pun — murni data — agar
mudah diaudit, di-diff pada pull request, dan suatu saat dipindah
ke sumber lain (database/CMS/API) tanpa menyentuh kode aplikasi.

CATATAN: seluruh nilai (koordinat, jarak, arah, catatan bahaya)
bersifat ILUSTRATIF untuk keperluan purwarupa penelitian dan belum
divalidasi oleh BPBD.
"""

DIR_LABEL = {
    "U": "Utara", "TL": "Timur Laut", "T": "Timur", "TG": "Tenggara",
    "S": "Selatan", "BD": "Barat Daya", "B": "Barat", "BL": "Barat Laut",
}

SPOTS = [
    {
        "id": "orchid", "name": "Orchid Forest Cikole", "image": "orchid.jpg",
        "category": "Wisata Alam & Outbound", "zone": "Zona Merah",
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
        "category": "Alam, Outbound & Kuliner", "zone": "Zona Merah",
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
        "category": "Wisata Kuliner & Keluarga", "zone": "Zona Kuning",
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
        "category": "Wisata Tematik & Kuliner", "zone": "Zona Kuning",
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
        "category": "Wisata Camping & Alam", "zone": "Zona Merah",
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
        "category": "Wisata Edukasi & Keluarga", "zone": "Zona Kuning",
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
]

SPOTS_BY_ID = {s["id"]: s for s in SPOTS}
