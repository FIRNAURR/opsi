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
- pal16.jpg

Jika sebuah file belum tersedia, aplikasi tidak akan error — kartu
terkait otomatis menampilkan latar polos (`utils/asset_helpers.py`
menangani `FileNotFoundError` secara aman dan mengembalikan string
kosong).

**Destinasi/layanan yang ditambahkan lewat panel Admin** tidak perlu
file lokal di sini — cukup isi kolom "URL foto" pada form dengan tautan
gambar (mis. hasil upload ke Imgur/Google Drive publik/dsb).
