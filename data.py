DIR_LABEL = {
    "U": "Utara", "TL": "Timur Laut", "T": "Timur", "TG": "Tenggara",
    "S": "Selatan", "BD": "Barat Daya", "B": "Barat", "BL": "Barat Laut",
}

TYPE_LABELS = {
    "wisata": "🧭 Wisata",
    "resto": "🍽️ Resto",
    "penginapan": "🛏️ Penginapan",
    "resto_penginapan": "🍽️🛏️ Resto & Penginapan",
}

SPOTS = [
    # ---------------------------------------------------------- WISATA
    {
        "id": "orchid", 
        "name": "Orchid Forest Cikole", 
        "image": "orchid.jpg",
        "site_map": "peta_wisata_orchid.jpg",  # Peta internal lokasi
        "type": "wisata", 
        "category": "Wisata Alam & Outbound", 
        "zone": "Zona Merah",
        "ticket": "Rp40.000 – Rp100.000",
        "evac": {
            "point": "Area Terbuka / Rest Area Cikole", "bearing": 35,
            "dist": "180 m", "time": "≈3 mnt",
            "note": "Jauhi jembatan gantung (Wood Bridge) dan area pepohonan tinggi. Menuju lapangan parkir yang lebih terbuka dan jauh dari tebing."
        },
        "coords": {"start": [-6.780613, 107.637505], "end": [-6.780110, 107.634944], "safe_name": "Area Parkir Utama (Plaza Luar)"},
        "amenities": {
            "resto": [
                ("Golden Pine Cafe", "TL · 140 m", "golden_pine.jpg"),
                ("Aspasia Coffee", "B · 100 m", None),
                ("Pine Kitchen", "B · 150 m", None),
                ("Food Court & Food Corner", "T · 500 m", None)
            ],
            "layanan": [
                ("Shuttle Car", "B · 50 m"),
                ("Teras Paphio", "T · 120 m"),
                ("Orchid House & Greenhouse", "B · 250 m"),
                ("Bazaar Anggrek", "T · 300 m"),
                ("Garden of Light", "B · 350 m"),
                ("Putt Putt Golf", "T · 400 m"),
                ("Rabbit Forest & Pet Venture", "B · 450 m"),
                ("Wood Bridge & Flying Fox", "B · 550 m"),
                ("Orchid Castle", "T · 600 m"),
                ("Camping Ground", "B · 650 m"),
                ("Horse Ranch", "T · 800 m")
            ],
            "mushola": [("Mushola dekat Entrance Gate", "B · 60 m")],
            "fasilitas": [
                ("Toilet umum (Area Parkir A & B)", "B · 70 m"),
                ("Souvenir Shop", "T · 110 m"),
                ("Pos Informasi & P3K", "T · 100 m")
            ],
        },
        "contact": {
            "phone": "0811 222 1284",
            "WA": "wa.me/68112221284",
            "email": "orchidforestcikole.ofc@gmail.com",
            "facebook": "Orchid Forest Cikole",
            "facebook_url": "https://www.facebook.com/orchidforestcikole",
            "instagram": "@orchidforestcikole",
            "instagram_url": "https://www.instagram.com/orchidforestcikole/"
        },
    },
    {
        "id": "grafika", 
        "name": "Terminal Wisata Grafika Cikole", 
        "image": "grafika.jpg",
        "site_map": None,
        "type": "wisata", 
        "category": "Alam, Outbound & Kuliner", 
        "zone": "Zona Merah",
        "ticket": "Rp15.000",
        "evac": {
            "point": "Lapangan Jayagiri Cikole", "bearing": 110,
            "dist": "220 m", "time": "≈4 mnt",
            "note": "Segera menjauh dari pohon pinus tinggi dan bangunan kayu vintage. Lapangan api unggun menjadi titik kumpul terluas di kawasan ini."
        },
        "coords": {"start": [-6.783374405338507, 107.65176797972961], "end": [-6.784854, 107.651587], "safe_name": "Lapangan Outbound / Area Parkir Depan"},
        "amenities": {
            "resto": [
                ("Restoran Sangkuriang", "TG · 130 m", "sangkuriang.jpg"),
                ("Saung Pengkolan 2", "T · 80 m", "saung_pengkolan2.jpg")
            ],
            "layanan": [
                ("Area Outbound & Flying Fox", "U · 100 m"),
                ("Camping Ground & Resto Sunda", "S · 120 m")
            ],
            "mushola": [("Mushola dekat area camping ground", "BD · 150 m")],
            "fasilitas": [
                ("Toilet & kamar bilas", "T · 90 m"),
                ("Pos keamanan & informasi", "BD · 60 m")
            ],
        },
        "contact": {
            "phone": "+62 22 82782515",
            "email": "info@grafikacikole.com",
            "facebook": "Terminal Wisata Grafika Cikole",
            "facebook_url": None,
            "instagram": "@officialgrafika",
            "instagram_url": "https://www.instagram.com/officialgrafika/"
        },
    },
    {
        "id": "floating", 
        "name": "Floating Market Lembang", 
        "image": "floating.jpg",
        "site_map": None,
        "type": "wisata", 
        "category": "Wisata Kuliner & Keluarga", 
        "zone": "Zona Kuning",
        "ticket": "Rp30.000",
        "evac": {
            "point": "Stadion Bentang", "bearing": 250,
            "dist": "150 m", "time": "≈2–3 mnt",
            "note": "Jauhi tepi danau saat evakuasi berlangsung. Arahkan pengunjung ke area parkir depan yang datar dan jauh dari struktur perahu."
        },
        "coords": {"start": [-6.817521, 107.618640], "end": [-6.817276, 107.618820], "safe_name": "Lapangan Parkir Depan Utama"},
        "amenities": {
            "resto": [
                ("Perahu Kuliner Sunda", "T · 40 m", "sundaness.jpg"),
                ("Zona Jajanan Internasional", "TL · 100 m", None)
            ],
            "layanan": [
                ("Sewa Kostum Kyotoku", "U · 80 m"),
                ("Kota Mini & Rainbow Slide", "TG · 120 m"),
                ("Sewa Perahu Air", "T · 50 m")
            ],
            "mushola": [("Mushola dekat pintu masuk", "B · 90 m")],
            "fasilitas": [
                ("Toilet area playground", "TG · 70 m"),
                ("Loket & pos informasi", "B · 50 m")
            ],
        },
        "contact": {
            "phone": "+62 22 2787766",
            "email": "floatingmarketlembang@gmail.com",
            "facebook": "Floating Market Lembang",
            "facebook_url": None,
            "instagram": "@floating.market.lembang",
            "instagram_url": "https://www.instagram.com/floating.market.lembang/"
        },
    },
    {
        "id": "asiaafrika", 
        "name": "The Great Asia Afrika", 
        "image": "asiaafrika.jpg",
        "site_map": None,
        "type": "wisata", 
        "category": "Wisata Tematik & Kuliner", 
        "zone": "Zona Kuning",
        "ticket": "Rp30.000 – Rp50.000",
        "evac": {
            "point": "Lapangan Terbuka Gudangkahuripan", "bearing": 15,
            "dist": "200 m", "time": "≈3–4 mnt",
            "note": "Hindari berlindung di dalam replika bangunan negara. Menuju plaza terbuka di zona Indonesia yang berjarak paling dekat."
        },
        "coords": {"start": [-6.832594844649511, 107.60476229517006], "end": [-6.8324, 107.6038], "safe_name": "Plaza Pintu Masuk / Parkir Atas"},
        "amenities": {
            "resto": [
                ("Kuliner Zona Korea & Jepang", "TL · 120 m", None),
                ("Kuliner Zona Afrika", "T · 160 m", None)
            ],
            "layanan": [
                ("Sewa Hanbok & Kimono", "TL · 110 m"),
                ("Lift Khusus Disabilitas/Lansia", "B · 40 m"),
                ("Spot Foto 7 Negara", "U · 150 m")
            ],
            "mushola": [("Mushola dekat Zona Indonesia", "B · 80 m")],
            "fasilitas": [
                ("Toilet Zona India", "TG · 100 m"),
                ("Pos keamanan pintu masuk", "BD · 60 m")
            ],
        },
        "contact": {
            "phone": "+62 811-2166-000",
            "email": "thegreatasiaafrica@gmail.com",
            "facebook": "The Great Asia Afrika",
            "facebook_url": None,
            "instagram": "@thegreatasiaafricalembang",
            "instagram_url": "https://www.instagram.com/thegreatasiaafricalembang/"
        },
    },
    {
        "id": "pineforest", 
        "name": "Pine Forest Camp Lembang", 
        "image": "pineforest.jpg",
        "site_map": None,
        "type": "wisata", 
        "category": "Wisata Camping & Alam", 
        "zone": "Zona Merah",
        "ticket": "Rp20.000 – Rp50.000",
        "evac": {
            "point": "Lapangan Heli", "bearing": 190,
            "dist": "160 m", "time": "≈3 mnt",
            "note": "Jauhi tepi jurang dan pohon pinus condong. Area camping ground yang lebih datar menjadi titik kumpul sementara."
        },
        "coords": {"start": [-6.815396647755517, 107.69403000790399], "end": [-6.815861, 107.694844], "safe_name": "Lapangan Heli / Area Camping Ground Terbuka"},
        "amenities": {
            "resto": [
                ("Warung makan area camping", "T · 100 m", None),
                ("Kedai kopi & jajanan hangat", "TG · 70 m", None)
            ],
            "layanan": [
                ("Sewa Tenda & Alat Camp", "B · 50 m"),
                ("Jalur Offroad & High Rope", "U · 120 m")
            ],
            "mushola": [("Mushola sederhana dekat gerbang", "BD · 130 m")],
            "fasilitas": [
                ("Toilet & kamar mandi umum", "T · 90 m"),
                ("Pos ranger / pengelola", "B · 50 m")
            ],
        },
        "contact": {
            "phone": "+62 811-2237-700",
            "email": "info@pineforestcamp.com",
            "facebook": None,
            "facebook_url": None,
            "instagram": "@pineforestcamplembang",
            "instagram_url": "https://www.instagram.com/pineforestcamplembang/"
        },
    },
    {
        "id": "deranch", 
        "name": "De Ranch Lembang", 
        "image": "deranch.jpg",
        "site_map": None,
        "type": "wisata", 
        "category": "Wisata Edukasi & Keluarga", 
        "zone": "Zona Kuning",
        "ticket": "Rp30.000",
        "evac": {
            "point": "Alun Alun Lembang", "bearing": 300,
            "dist": "120 m", "time": "≈2 mnt",
            "note": "Jauhi kandang hewan dan pagar kayu saat evakuasi. Lapangan rumput utama relatif aman dan mudah diakses dari seluruh wahana."
        },
        "coords": {"start": [-6.813915, 107.621255], "end": [-6.8142, 107.6262], "safe_name": "Lapangan Pacuan / Padang Rumput Terbuka"},
        "amenities": {
            "resto": [
                ("Kedai susu & jajanan khas peternakan", "T · 60 m", None),
                ("Warung makan area piknik", "TL · 110 m", None)
            ],
            "layanan": [
                ("Sewa Kuda & Kostum Cowboy", "U · 50 m"),
                ("Panahan & Delman", "S · 80 m")
            ],
            "mushola": [("Mushola dekat pintu masuk", "B · 70 m")],
            "fasilitas": [
                ("Toilet umum", "TG · 80 m"),
                ("Pos informasi wahana", "B · 40 m")
            ],
        },
        "contact": {
            "phone": "+62 22 2785865",
            "email": "info@deranchlembang.com",
            "facebook": "De Ranch Lembang",
            "facebook_url": None,
            "instagram": "@deranchlembang",
            "instagram_url": "https://www.instagram.com/deranchlembang/"
        },
    },
    {
        "id": "pal16", 
        "name": "Hutan Pinus Cikole (Pal 16)", 
        "image": "pal16.jpg",
        "site_map": None,
        "type": "wisata", 
        "category": "Wisata Alam & Piknik", 
        "zone": "Zona Merah",
        "ticket": "Rp10.000",
        "evac": {
            "point": "Area Parkir Utama Pal 16", "bearing": 208,
            "dist": "160 m", "time": "≈3 mnt",
            "note": "Jauhi hammock, gazebo kayu, dan barisan pohon pinus tinggi di tepi jalan. Menuju area parkir utama yang lebih terbuka dan datar."
        },
        "coords": {"start": [-6.789200, 107.654100], "end": [-6.790500, 107.653400], "safe_name": "Area Parkir Utama Pal 16"},
        "amenities": {
            "resto": [("Warung jajanan & kopi tepi hutan pinus", "T · 60 m", None)],
            "layanan": [
                ("Sewa Hammock & Gazebo", "U · 30 m"),
                ("Spot Foto Pinus", "S · 50 m")
            ],
            "mushola": [("Mushola dekat gerbang masuk", "B · 80 m")],
            "fasilitas": [
                ("Toilet umum", "B · 70 m"),
                ("Pos tiket & informasi", "T · 40 m")
            ],
        },
        "contact": {
            "phone": "+62 821-1234-5678",
            "email": "pal16cikole@gmail.com",
            "facebook": None,
            "facebook_url": None,
            "instagram": "@pal16cikole",
            "instagram_url": "https://www.instagram.com/pal16cikole/"
        },
    },

    # ---------------------------------------------------- RESTO & PENGINAPAN
    {
        "id": "sindang-reret", 
        "name": "Sindang Reret Cikole", 
        "image": "sindang_reret.jpg",
        "site_map": None,
        "type": "resto_penginapan", 
        "category": "🍽️🛏️ Resto & Penginapan Sunda", 
        "zone": "Zona Kuning",
        "ticket": "Sesuai pesanan / tarif kamar",
        "evac": {
            "point": "Area Parkir Depan Sindang Reret", "bearing": 319,
            "dist": "100 m", "time": "≈2 mnt",
            "note": "Jauhi bangunan utama restoran, dapur, dan ballroom tertutup. Menuju halaman parkir depan yang lebih terbuka."
        },
        "coords": {"start": [-6.775000, 107.665000], "end": [-6.7875, 107.6383], "safe_name": "Halaman Parkir Bus & Mobil Depan"},
        "amenities": {
            "resto": [("Restoran Utama Khas Sunda", "Utama", None)],
            "layanan": [
                ("Cottage & Cottage Suite", "Area Penginapan"),
                ("Ruang Rapat & Ballroom", "Lantai 2")
            ],
            "mushola": [("Mushola dalam area hotel", "Lantai Dasar")],
            "fasilitas": [
                ("Resepsionis 24 jam", "Lobby Utama"),
                ("Toilet & kamar mandi tamu", "Samping Resto")
            ],
        },
        "contact": {
            "phone": "+62 22 2786500",
            "email": "info@sindangreret.co.id",
            "facebook": "Sindang Reret Hotel & Restaurant",
            "facebook_url": None,
            "instagram": "@sindangreretlembang",
            "instagram_url": "https://www.instagram.com/sindangreretlembang/"
        },
    },
    {
        "id": "sate-maranggi-hj-ita", 
        "name": "Warung Nasi Sunda Sate Maranggi Hj Ita", 
        "image": "sate_maranggi.jpg",
        "site_map": None,
        "type": "resto", 
        "category": "🍽️ Kuliner Sunda & Sate Maranggi", 
        "zone": "Zona Kuning",
        "ticket": "Sesuai pesanan",
        "evac": {
            "point": "Halaman Parkir Warung", "bearing": 53,
            "dist": "60 m", "time": "≈1–2 mnt",
            "note": "Jauhi area pembakaran sate/tungku arang. Menuju halaman parkir depan yang lebih terbuka."
        },
        "coords": {"start": [-6.787000, 107.648000], "end": [-6.786700, 107.648400], "safe_name": "Halaman Parkir Terbuka Depan Restoran"},
        "amenities": {
            "resto": [("Dapur Sate Maranggi & Masakan Sunda", "Utama", None)],
            "layanan": [("Lesehan & Meja Makan", "Area Resto")],
            "mushola": [("Mushola Kecil Resto", "B · 20 m")],
            "fasilitas": [("Toilet umum", "Samping Resto")],
        },
        "contact": {
            "phone": "+62 813-2000-1234",
            "email": None,
            "facebook": None,
            "facebook_url": None,
            "instagram": None,
            "instagram_url": None
        },
    },
    {
        "id": "bobocabin-cikole", 
        "name": "Bobocabin Cikole", 
        "image": "bobocabin.jpg",
        "site_map": None,
        "type": "penginapan", 
        "category": "🛏️ Glamping & Penginapan", 
        "zone": "Zona Merah",
        "ticket": "Sesuai tarif kabin",
        "evac": {
            "point": "Area Api Unggun Bersama", "bearing": 140,
            "dist": "80 m", "time": "≈2 mnt",
            "note": "Jauhi kabin kayu dan barisan pohon pinus tinggi di sekitar area menginap. Menuju area api unggun bersama yang lebih terbuka."
        },
        "coords": {"start": [-6.784000, 107.641000], "end": [-6.7818, 107.6335], "safe_name": "Pelataran Lobby / Parkir Atas"},
        "amenities": {
            "resto": [("Shared Kitchen & Pop-up Cafe", "Area Komunal", None)],
            "layanan": [
                ("Sewa Kabin Pintar (Smart Cabin)", "Seluruh Area"),
                ("Layanan Host 24 Jam", "Lobby")
            ],
            "mushola": [("Mushola Komunal", "T · 30 m")],
            "fasilitas": [
                ("BBQ Grill Bersama", "Tengah Kabin"),
                ("Toilet & Kamar Mandi Air Panas", "Di dalam Kabin")
            ],
        },
        "contact": {
            "phone": "+62 811-2110-111",
            "email": "help@bobobox.com",
            "facebook": "Bobobox Indonesia",
            "facebook_url": None,
            "instagram": "@bobocabin",
            "instagram_url": "https://www.instagram.com/bobocabin/"
        },
    },
    {
        "id": "puteri-gunung-hotel", 
        "name": "Puteri Gunung Hotel", 
        "image": "puteri-gunung.jpg",
        "site_map": None,
        "type": "penginapan", 
        "category": "🏨 Penginapan & Resort", 
        "zone": "Zona Kuning",
        "ticket": "Sesuai tarif kamar",
        "evac": {
            "point": "Halaman Depan Hotel", "bearing": 50,
            "dist": "80 m", "time": "≈2 mnt",
            "note": "Jauhi gedung bertingkat dan area kolam renang. Ikuti tangga darurat menuju halaman depan yang terbuka."
        },
        "coords": {"start": [-6.788000, 107.652000], "end": [-6.8122, 107.6258], "safe_name": "Taman & Lapangan Rumput Tengah Hotel"},
        "amenities": {
            "resto": [("Cikole Restaurant", "Lantai 1", None)],
            "layanan": [
                ("Layanan Kamar / Room Service", "Seluruh Kamar"),
                ("Ruang Rapat & Meeting Room", "Lobby Level")
            ],
            "mushola": [("Mushola Hotel", "Lantai Dasar")],
            "fasilitas": [
                ("Kolam renang outdoor", "Taman Tengah"),
                ("Resepsionis 24 jam", "Lobby Utama")
            ],
        },
        "contact": {
            "phone": "+62 22 2786650",
            "email": "reservation@puterigunung.com",
            "facebook": "Puteri Gunung Hotel Lembang",
            "facebook_url": None,
            "instagram": "@puterigununghotel",
            "instagram_url": "https://www.instagram.com/puterigununghotel/"
        },
    },
    {
        "id": "nirwana-lembang", 
        "name": "Nirwana Hotel & Villa Lembang", 
        "image": "nirwana_lembang.jpg",
        "site_map": None,
        "type": "penginapan", 
        "category": "🏨 Penginapan Keluarga", 
        "zone": "Zona Kuning",
        "ticket": "Sesuai tarif kamar/villa",
        "evac": {
            "point": "Area Kolam Renang Terbuka", "bearing": 54,
            "dist": "80 m", "time": "≈2 mnt",
            "note": "Jauhi bangunan villa dan pagar kayu. Menuju area kolam renang yang lebih terbuka dan luas."
        },
        "coords": {"start": [-6.796000, 107.628000], "end": [-6.7815, 107.6360], "safe_name": "Pelataran Parkir Depan Villa / Lapangan Utama"},
        "amenities": {
            "resto": [("Dapur / Cafe Hotel", "Area Utama", None)],
            "layanan": [("Sewa Villa & Room Stay", "Seluruh Kompleks")],
            "mushola": [("Mushola Hotel", "Samping Lobby")],
            "fasilitas": [
                ("Kolam renang", "Area Luar"),
                ("Area parkir luas", "Depan Villa")
            ],
        },
        "contact": {
            "phone": "+62 22 2786123",
            "email": "nirwanalembang@gmail.com",
            "facebook": None,
            "facebook_url": None,
            "instagram": "@nirwana_lembang",
            "instagram_url": "https://www.instagram.com/nirwana_lembang/"
        },
    },
]

SPOTS_BY_ID = {s["id"]: s for s in SPOTS}
