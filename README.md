# GoWisata — Sistem Informasi Pemesanan Tiket Wisata Berbasis Web

Aplikasi web ini dibuat berdasarkan dokumen **SRS (Software Requirements
Specification)** dan **Laporan Manajemen Proyek IT** proyek GoWisata —
UAS Rekayasa Perangkat Lunak, D3 Teknik Informatika, Universitas AMIKOM
Yogyakarta.

Sistem sudah lengkap dan **siap pakai**: tinggal jalankan, aplikasi otomatis
membuat database dan mengisi data contoh (destinasi wisata + akun demo untuk
3 peran pengguna), sehingga langsung bisa dipresentasikan.

---

## 1. Cara Menjalankan

Dibutuhkan **Python 3.10+** sudah terpasang di komputer (cek dengan `python3 --version`).

### Mac / Linux
```bash
cd gowisata
./run.sh
```

### Windows
Klik dua kali `run.bat`, atau lewat Command Prompt:
```cmd
cd gowisata
run.bat
```

Script ini otomatis: membuat virtual environment → menginstal semua
dependency di `requirements.txt` → menjalankan server.

Setelah muncul tulisan `GoWisata siap berjalan di http://127.0.0.1:5000`,
buka alamat tersebut di browser (Chrome/Firefox/Edge).

> Jika ingin instal manual tanpa script:
> ```bash
> pip install -r requirements.txt
> python3 app.py
> ```

Database (`gowisata.db`) dan seluruh data contoh dibuat otomatis saat
pertama kali dijalankan — tidak perlu setup MySQL/phpMyAdmin untuk demo.

---

## 2. Menjalankan Lewat VS Code (opsional, lebih praktis)

1. Buka folder `gowisata` di VS Code (**File → Open Folder**).
2. Pastikan extension **Python** sudah terpasang di VS Code.
3. Buka file `app.py`, lalu tekan **F5** (atau klik tombol ▶️ Run di pojok
   kanan atas). Konfigurasi run sudah disiapkan otomatis di `.vscode/launch.json`.
4. Buka terminal bawaan VS Code kalau perlu install dependency dulu:
   ```bash
   pip install -r requirements.txt
   ```
5. Setelah muncul log `Running on http://127.0.0.1:5000`, buka alamat itu
   di browser, atau klik link yang muncul di terminal (Ctrl+Klik).

Tidak perlu install MySQL/database server apa pun — database SQLite
(`gowisata.db`) dibuat otomatis oleh aplikasi saat pertama kali dijalankan.

---

## 3. Deploy ke Internet Lewat GitHub (dapat Link Web publik, gratis)

Supaya aplikasi bisa diakses dari HP/laptop mana saja lewat link (misalnya
untuk dilampirkan di laporan atau dibuka juri kompetisi), pakai **Render.com**
(gratis, otomatis connect ke GitHub):

### Langkah 1 — Upload ke GitHub
1. Buat akun di [github.com](https://github.com) kalau belum punya.
2. Buat repository baru (mis. nama `gowisata`), pilih **Public**.
3. Di folder project, jalankan di terminal:
   ```bash
   git init
   git add .
   git commit -m "GoWisata - sistem pemesanan tiket wisata"
   git branch -M main
   git remote add origin https://github.com/USERNAME/gowisata.git
   git push -u origin main
   ```
   (Ganti `USERNAME` dengan username GitHub Anda. Bisa juga upload lewat
   tombol "Add file → Upload files" di web GitHub tanpa terminal.)

### Langkah 2 — Deploy di Render
1. Buka [render.com](https://render.com) → **Sign up** pakai akun GitHub.
2. Klik **New → Web Service**.
3. Pilih repository `gowisata` yang tadi di-push.
4. Render otomatis mendeteksi `render.yaml` — biarkan pengaturan default
   (Build command: `pip install -r requirements.txt`, Start command:
   `gunicorn app:app`), plan **Free**.
5. Klik **Create Web Service**, tunggu proses build (±2–3 menit).
6. Setelah selesai, Render memberi link publik seperti:
   `https://gowisata.onrender.com` — inilah link web yang bisa dibuka
   siapa saja, dari HP maupun laptop.

> Catatan: paket gratis Render akan "tidur" jika 15 menit tidak diakses,
> dan butuh ±30 detik untuk bangun lagi saat pertama dibuka — normal untuk
> demo/kompetisi. Alternatif lain dengan cara serupa: Railway.app atau
> PythonAnywhere.

---

## 4. Akun Demo (Login)

| Peran | Email | Password | Akses |
|---|---|---|---|
| Wisatawan | `budi@gowisata.id` | `user123` | Cari & pesan tiket, dashboard riwayat |
| Admin / Pengelola Wisata | `admin@gowisata.id` | `admin123` | Kelola destinasi, verifikasi QR, laporan transaksi |
| Owner / Dinas Pariwisata | `owner@gowisata.id` | `owner123` | Statistik pendapatan & kunjungan |

Atau daftar akun wisatawan baru sendiri lewat halaman **Daftar**.

---

## 5. Alur Demo yang Disarankan (untuk presentasi/juri)

1. **Beranda** → tampilkan hero, pencarian, dan destinasi unggulan.
2. **Cari destinasi** → filter kategori (Pegunungan/Budaya/Petualangan).
3. Buka **detail destinasi** → tunjukkan peta lokasi (Google Maps).
4. **Login sebagai wisatawan** → pesan tiket (pilih tanggal & jumlah).
5. **Bayar (simulasi)** → e-tiket berisi **QR Code** langsung terbit.
6. **Logout → login sebagai Admin** → buka menu **Verifikasi Tiket**,
   masukkan kode tiket (mis. `GW-XXXXXX` dari e-tiket tadi) → status
   berubah menjadi tervalidasi/terpakai.
7. Tunjukkan **Kelola Destinasi** (tambah/edit/hapus) dan **Laporan Transaksi**.
8. **Logout → login sebagai Owner** → tunjukkan grafik pendapatan &
   kunjungan bulanan serta ranking destinasi terpopuler.

---

## 6. Fitur yang Tersedia (sesuai SRS & Laporan Proyek)

- ✅ Registrasi & login pengguna (role: wisatawan, admin, owner)
- ✅ Pencarian & filter destinasi wisata
- ✅ Detail destinasi + peta lokasi (Google Maps embed)
- ✅ Pemesanan tiket (tanggal kunjungan & jumlah tiket)
- ✅ Simulasi pembayaran tiket
- ✅ Generate & verifikasi tiket dengan QR Code
- ✅ Dashboard wisatawan (riwayat pemesanan & status tiket)
- ✅ Dashboard admin (CRUD destinasi, verifikasi QR, laporan transaksi)
- ✅ Dashboard owner (statistik kunjungan, grafik pendapatan, destinasi terpopuler)
- ✅ Desain UI/UX profesional & responsif (desktop & mobile)

---

## 7. Struktur Teknis

```
gowisata/
├── app.py                  # Aplikasi Flask (model, route, logika bisnis)
├── generate_images.py      # Skrip pembuat ilustrasi destinasi (opsional, sudah dijalankan)
├── requirements.txt        # Daftar dependency Python
├── run.sh / run.bat        # Skrip menjalankan aplikasi otomatis
├── Procfile                # Perintah start untuk hosting (Render/Railway)
├── render.yaml             # Konfigurasi deploy otomatis ke Render.com
├── .gitignore              # File yang tidak perlu diupload ke GitHub
├── .vscode/                # Konfigurasi run otomatis (tekan F5) di VS Code
├── static/
│   ├── css/style.css       # Desain visual (tema lereng Merapi & batik Sleman)
│   ├── img/                # Logo & ilustrasi destinasi
│   └── qrcodes/            # QR Code e-tiket yang ter-generate otomatis
└── templates/               # Halaman HTML (Jinja2)
```

**Teknologi** (sesuai kebutuhan sistem di SRS bab 6 & Laporan bab 4.2):
Python (Flask), HTML/CSS/JavaScript, database **SQLite** (tanpa perlu
instalasi MySQL/database server terpisah — otomatis dibuat sebagai satu
file `gowisata.db`), QR Code generation, Google Maps embed. Tampilan sudah
responsif untuk desktop maupun HP (mobile-friendly, ada menu hamburger).

---

## 8. Tentang Foto/Gambar Destinasi

Ilustrasi destinasi pada aplikasi ini adalah **artwork bergaya flat-design**
yang dibuat khusus untuk proyek ini (bukan foto asli), karena lingkungan
pembuatan aplikasi ini tidak memiliki akses internet untuk mengunduh foto
berlisensi/berhak cipta. Tampilannya tetap profesional dan konsisten untuk
kebutuhan demo maupun laporan.

**Untuk hasil terbaik saat presentasi/kompetisi**, disarankan mengganti
gambar di `static/img/destinations/` dengan foto asli destinasi (nama file
sudah disesuaikan, misalnya `kaliurang.png`, `prambanan.png`, dsb — cukup
timpa file dengan nama yang sama, ukuran disarankan rasio 3:2).

Folder `screenshots_demo/` berisi tangkapan layar seluruh halaman aplikasi,
dipisah dalam dua subfolder — `desktop/` dan `mobile/` (tampilan HP) — untuk
beranda, pencarian, detail destinasi, e-tiket QR, dashboard admin & owner,
dsb. Bisa langsung dipakai untuk laporan atau slide presentasi/kompetisi.

---

## 9. Catatan Pengembangan Lanjutan (sesuai rekomendasi Laporan Proyek bab 11.2)

Fitur yang secara sengaja **belum** diimplementasikan karena di luar ruang
lingkup SRS (bab 1.3) — cocok disebut sebagai "pengembangan selanjutnya"
saat presentasi:
- Payment gateway asli (saat ini masih simulasi)
- Aplikasi mobile Android/iOS
- Notifikasi otomatis email/WhatsApp
- Fitur ulasan & rating wisata

---

Dibuat untuk keperluan tugas akademik (UAS Rekayasa Perangkat Lunak) dan
demo kompetisi. Selamat presentasi! 🌋
