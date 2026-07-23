# Direktori assets/

Letakkan file gambar berikut di direktori ini (nama harus persis sama,
sesuai referensi pada `data.py`):

- orchid.jpg
- golden_pine.jpg
- grafika.jpg
- sangkuriang.jpg
- saung_pengkolan2.jpg
- floating.jpg
- sundaness.jpg
- asiaafrika.jpg
- pineforest.jpg
- deranch.jpg

Jika sebuah file belum tersedia, aplikasi tidak akan error — kartu
terkait otomatis menampilkan latar polos (`utils/asset_helpers.py`
menangani `FileNotFoundError` secara aman dan mengembalikan string
kosong).
