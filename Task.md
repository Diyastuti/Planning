# Task List (Rencana Kerja & Checklist)
## Project: LERES - Layanan E-Government Rekomendasi dan Edukasi Smart

Gunakan checklist ini untuk melacak progres pengembangan aplikasi dari awal hingga selesai. Berikan tanda `[x]` pada tugas yang sudah diselesaikan.

---

## 🚀 FASE 1: Setup Proyek & Persiapan Data
* [ ] **1.1. Inisialisasi Repositori & Berkas**
  * Buat berkas utama proyek di root direktori sesuai [Guideline.md](file:///d:/21_KAMARUL%20ARIFIN%20MUZAFFAR_XI%20TJKT1_PIC/Planning/Guideline.md): `app.py`, `dataset_bantuan.csv`, `requirements.txt`.
  * Buat file `.gitignore` untuk mengecualikan `venv/` dan file cache compiler.
* [ ] **1.2. Konfigurasi Lingkungan & API KEY**
  * Tulis file `requirements.txt` dengan library yang diperlukan (Streamlit, Gemini API, Pandas, Matplotlib, NumPy, Requests, pillow, openpyxl, seaborn).
  * Siapkan daftar 3 API KEY Google AI Studio di dalam kode untuk rotasi cadangan kuota agar tidak mudah terkena limit.
  * Tambahkan juga baris data khusus untuk contoh isu hoaks yang sering beredar beserta penjelasan klarifikasinya untuk pencocokan cepat.

---

## 🧠 FASE 2: Pemrosesan Data & Utilitas AI (Integrasi di `app.py`)
* [ ] **2.1. Pemrosesan Data Pandas**
  * Tulis fungsi `load_dataset()` dengan decorator caching `@st.cache_data` untuk membaca `dataset_bantuan.csv`.
  * Tulis fungsi pencarian berbasis kata kunci (keyword matching) sebagai backup jika API Gemini mengalami kegagalan.
  * Implementasikan pengolahan data menggunakan Pandas untuk menghitung statistik program bantuan (misal: jumlah program per kategori) sebagai bahan visualisasi.
* [ ] **2.2. Integrasi & Rotasi API Gemini**
  * Buat mekanisme inisialisasi SDK `google-generativeai` dengan sistem rotasi 3 API Key (mencoba Key 1, jika limit pindah ke Key 2, dst).
  * Tulis fungsi `get_gemini_response(prompt: str, context: str)` dengan grounding data dari CSV.
  * Tulis fungsi `verify_claim_with_gemini(claim: str, reference_data: str)` untuk proses klasifikasi & analisis hoaks.

---

## 🎨 FASE 3: Pengembangan UI & Fitur Utama (`app.py`)
* [ ] **3.1. Kerangka Halaman & Sidebar**
  * Atur konfigurasi halaman Streamlit (`st.set_page_config`) dengan judul dan ikon yang menarik.
  * Implementasikan sidebar navigasi yang memiliki 4 menu utama:
    1. 💬 **Chatbot Konsultasi**
    2. 🔍 **Verifikasi Hoaks**
    3. 📊 **Visualisasi Data Bantuan**
    4. 📞 **Hubungi Petugas (Eskalasi)**
* [ ] **3.2. Pengembangan Fitur Chatbot Konsultasi (Menu 1)**
  * Tampilan chat bubble yang menarik (menggunakan Streamlit chat input & chat message).
  * Simpan riwayat percakapan menggunakan `st.session_state.messages` agar asisten dapat mengingat konteks chat sebelumnya.
  * Integrasikan chatbot dengan Gemini API dan gunakan dataset sebagai penunjang jawaban (Grounding).
* [ ] **3.3. Pengembangan Fitur Verifikasi Hoaks (Menu 2)**
  * Sediakan kolom teks area bagi pengguna untuk menempelkan berita bantuan.
  * Buat tombol "Verifikasi Sekarang".
  * Tampilkan status verifikasi (VALID/HOAKS) dengan badge visual berwarna mencolok beserta penjelasan analisis AI.
* [ ] **3.4. Pengembangan Dashboard Visualisasi (Menu 3)**
  * Tampilkan rangkuman statistik data bantuan sosial berupa metrik (misal: Total Program Bantuan Aktif, Total Instansi Terlibat).
  * Render grafik diagram menggunakan Matplotlib/Seaborn ke dalam Streamlit menggunakan `st.pyplot()`.
* [ ] **3.5. Pengembangan Fitur Eskalasi (Menu 4)**
  * Sediakan daftar kontak darurat dan instansi penting berdasarkan kategori kebutuhan (Kesehatan, Bencana, Kesejahteraan Sosial).
  * Implementasikan logika otomatis pada Chatbot: jika chatbot mendeteksi pertanyaan bernada darurat atau di luar database, tampilkan card khusus berisi tombol pintas untuk langsung membuka halaman kontak ini.

---

## 🛡️ FASE 4: Responsible AI & Evaluasi
* [ ] **4.1. Pencegahan Halusinasi & Filter Output**
  * Terapkan instruksi ketat pada *System Prompt* agar AI tidak mengarang data di luar file CSV yang disediakan.
  * Tambahkan pesan disclaimer di bagian bawah chat untuk memperingatkan pengguna agar selalu memverifikasi ulang informasi krusial.
* [ ] **4.2. Penanganan Error Batasan API**
  * Implementasikan fallback otomatis: jika API key bermasalah atau kuota habis, sistem beralih menggunakan algoritma keyword-matching Pandas untuk tetap memberikan informasi prasyarat bantuan.
* [ ] **4.3. Uji Coba Keamanan Input**
  * Uji chatbot dengan pertanyaan aneh, ujaran kebencian, atau prompt injection untuk memastikan AI tetap bersikap sopan dan menolak menjawab di luar konteks bantuan sosial.

---

## 🏁 FASE 5: Dokumentasi & Finalisasi
* [ ] **5.1. File README.md**
  * Tulis instruksi instalasi, cara menjalankan aplikasi, dan penjelasan singkat fitur.
* [ ] **5.2. Walkthrough & Presentasi**
  * Siapkan data pengujian (skenario chat sukses, skenario hoaks terdeteksi, dan visualisasi diagram) untuk dipresentasikan saat penilaian.
