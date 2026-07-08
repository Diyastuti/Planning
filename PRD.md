# Product Requirement Document (PRD)
## Project: Asisten Pintar Komunitas (Penyedia Informasi Layanan Publik & Bantuan Valid)

---

## 1. Pendahuluan & Latar Belakang
Banyak warga masyarakat, khususnya di tingkat komunitas lokal, mengalami kesulitan dalam mengakses informasi bantuan sosial, layanan kesehatan, penanggulangan bencana, dan perlindungan anak. Masalah utama meliputi:
* **Informasi Tersebar:** Informasi resmi tersebar di berbagai situs kementerian, portal pemerintah daerah, dan media sosial, tanpa ada satu pintu akses yang terpusat.
* **Prosedur yang Rumit:** Dokumen persyaratan dan alur birokrasi sulit dipahami oleh masyarakat umum, khususnya orang tua dan masyarakat dengan literasi digital rendah.
* **Maraknya Hoaks:** Beredarnya informasi palsu (hoaks) mengenai bantuan sosial di grup chat (seperti WhatsApp) yang menimbulkan kebingungan dan kekhawatiran.

Untuk mengatasi tantangan ini, proyek ini membangun sebuah **Asisten Pintar Komunitas** berbasis AI. Aplikasi ini bertindak sebagai chatbot satu pintu yang mengintegrasikan data resmi dari pemerintah (seperti `data.go.id`) dan database lokal untuk memberikan jawaban valid, merangkum persyaratan dengan bahasa sederhana, memverifikasi berita hoaks, dan memitigasi risiko disinformasi melalui prinsip Responsible AI.

---

## 2. Tujuan Produk (Product Goals)
1. **Pemusatan Informasi:** Menyajikan informasi bantuan sosial dan layanan publik terintegrasi dalam satu antarmuka percakapan (chat interface) yang ramah pengguna.
2. **Penyederhanaan Prosedur:** Menggunakan Large Language Model (Gemini API) untuk menerjemahkan bahasa hukum/birokrasi yang rumit menjadi langkah-langkah praktis dan mudah dipahami dengan bahasa sehari-hari.
3. **Verifikasi Hoaks:** Menyediakan modul verifikasi cepat bagi warga untuk memeriksa kebenaran isu bantuan sosial yang beredar di komunitas.
4. **Kepercayaan & Keamanan (Responsible AI):** Menjamin jawaban AI dapat dipertanggungjawabkan dengan menyertakan tautan sumber asli dan menyediakan opsi eskalasi langsung ke petugas manusia jika tingkat keyakinan (confidence score) AI rendah.

---

## 3. Profil Pengguna (User Persona)
1. **Gen-Z (Pelajar/Mahasiswa):**
   * Karakter: Menginginkan akses informasi instan, tidak menyukai birokrasi berbelit-belit, terbiasa dengan antarmuka chat/pencarian cepat.
2. **Masyarakat Umum & Orang Tua:**
   * Karakter: Kesulitan membaca dokumen PDF pemerintah yang panjang, rentan terpapar hoaks di grup WhatsApp, membutuhkan bahasa yang sederhana dan petunjuk langkah-demi-langkah (step-by-step).
3. **Petugas Komunitas (RT/RW/Relawan Sosial):**
   * Karakter: Membutuhkan data valid dengan cepat untuk membantu warganya yang sedang kesulitan.

---

## 4. Ruang Lingkup Fitur (Feature Scope)

### Fitur Utama (Functional Requirements)
1. **Portal Chatbot Konsultasi Bantuan (Bahasa Sehari-hari)**
   * Pengguna dapat menginput keluhan menggunakan bahasa sehari-hari (contoh: *"Saya kehilangan pekerjaan dan anak saya mau masuk sekolah, ada bantuan apa ya?"*).
   * AI akan mendeteksi kebutuhan pengguna, mencari data yang relevan dari dataset bantuan sosial, dan membalas dengan format terstruktur:
     * **Nama Bantuan** yang cocok.
     * **Syarat & Dokumen** yang diperlukan.
     * **Prosedur/Alur** pengajuan.
     * **Instansi Terkait** yang harus dihubungi.
   * AI wajib menyertakan **tautan/sumber referensi asli** dari dataset resmi.

2. **Modul Cek & Verifikasi Hoaks**
   * Halaman khusus atau mode chat khusus di mana pengguna dapat menempelkan (paste) teks berita atau pesan berantai mengenai program bantuan sosial.
   * AI akan mencocokkan klaim tersebut dengan basis data resmi (`data.go.id` atau database lokal) dan mengeluarkan status verifikasi:
     * **[VALID]**: Jika informasi sesuai dengan program resmi yang sedang berjalan.
     * **[HOAKS / TIDAK VALID]**: Jika informasi tidak ditemukan atau bertentangan dengan data resmi.
     * **[BUTUH VERIFIKASI LANJUTAN]**: Jika data tidak cukup meyakinkan.
   * Menyertakan penjelasan logis mengapa informasi tersebut valid/hoaks.

3. **Dashboard Visualisasi Distribusi Bantuan (Matplotlib)**
   * Menampilkan wawasan data (data insights) grafis berupa diagram batang/lingkaran yang menggambarkan:
     * Distribusi jenis bantuan di berbagai sektor (Kesehatan, Pendidikan, Bencana, Sosial).
     * Jumlah penerima bantuan per wilayah atau statistik anggaran program bantuan aktif.
   * Membantu pengguna visual (terutama petugas) melihat tren penyebaran program bantuan secara transparan.

4. **Sistem Eskalasi & Responsible AI (Hubungi Petugas)**
   * Chatbot dilengkapi dengan detektor confidence score (skor keyakinan). Jika pertanyaan berada di luar basis data resmi atau sangat sensitif (misalnya kasus kekerasan anak, kondisi medis darurat), AI akan menampilkan tombol **"Hubungi Petugas"**.
   * Menampilkan kontak telepon, alamat kantor, atau WhatsApp resmi instansi terkait berdasarkan kategori masalah (misal: Dinas Sosial, BNPB, KPAI, atau Puskesmas setempat).

---

## 5. Spesifikasi Teknis & Non-Fungsional

### Stack Teknologi
* **Bahasa Pemrograman:** Python 3.10+
* **Framework Web & UI:** Streamlit (untuk pembuatan antarmuka web interaktif dengan cepat).
* **Pemrosesan Data:** Pandas (untuk membaca, menyaring, dan memproses file dataset CSV/JSON dari `data.go.id` atau DB lokal).
* **Visualisasi Grafik:** Matplotlib / Seaborn (untuk plotting diagram statistik).
* **Model AI:** Google Gemini API (`gemini-1.5-flash` atau `gemini-1.5-pro` via SDK `google-generativeai`) untuk penalaran (reasoning), klasifikasi keluhan, penyederhanaan teks, dan verifikasi hoaks.
* **Manajemen Environment:** `python-dotenv` untuk mengamankan API key di file `.env`.

### Kebutuhan Non-Fungsional (Non-Functional Requirements)
1. **Keamanan Data (Security):** API Key Gemini tidak boleh ditulis langsung di kode sumber (*hardcoded*) dan harus dimuat melalui variabel lingkungan.
2. **Kinerja (Performance):** Respon chatbot rata-rata harus selesai dalam waktu kurang dari 5 detik.
3. **Desain Antarmuka (UI/UX):** Mengikuti prinsip responsif, ramah seluler, menggunakan tipografi yang jelas (Inter/Roboto), kontras warna yang baik (aksesibilitas), serta navigasi sidebar yang intuitif.
4. **Akurasi & Grounding (Fidelity):** Sistem harus mengutamakan data dari file lokal/dataset resmi (`data.go.id`) dan menghindari halusinasi dengan menolak menjawab jika topik di luar cakupan informasi layanan publik/bantuan sosial yang valid.
