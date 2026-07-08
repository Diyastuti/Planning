# Task List (Rencana Kerja & Checklist)
## Project: Asisten Pintar Komunitas

Gunakan checklist ini untuk melacak progres pengembangan aplikasi dari awal hingga selesai. Berikan tanda `[x]` pada tugas yang sudah diselesaikan.

---

## 🚀 FASE 1: Setup Proyek & Persiapan Data
* [ ] **1.1. Inisialisasi Repositori & Folder**
  * Buat struktur folder sesuai dengan [Guideline.md](file:///d:/21_KAMARUL%20ARIFIN%20MUZAFFAR_XI%20TJKT1_PIC/Planning/Guideline.md) (`dataset/`, `utils/`, `config/`).
  * Buat file `.gitignore` untuk mengecualikan `.env`, `venv/`, dan cache file.
* [ ] **1.2. Konfigurasi Lingkungan & Library**
  * Buat virtual environment (venv) dan aktifkan.
  * Tulis file `requirements.txt` dan instal semua dependensi.
  * Buat file `.env` dan masukkan API Key Gemini yang valid.
* [ ] **1.3. Penyiapan Dataset Layanan Publik**
  * Unduh atau buat mock dataset berupa file `dataset/bantuan_sosial.csv` yang berisi kolom: `id`, `nama_bantuan`, `kategori`, `deskripsi`, `persyaratan`, `prosedur_klaim`, `instansi_terkait`, `kontak_resmi`, `tautan_sumber`.
  * Buat file `dataset/hoaks_db.csv` yang berisi daftar berita hoaks yang sering beredar beserta penjelasannya untuk pencocokan cepat.

---

## 🧠 FASE 2: Modul Data & Utilitas AI
* [ ] **2.1. Helper Pemrosesan Data (`utils/data_helper.py`)**
  * Tulis fungsi `load_dataset()` dengan decorator caching dari Streamlit.
  * Tulis fungsi pencarian berbasis kata kunci (keyword matching) sebagai backup jika API Gemini mengalami kegagalan.
  * Implementasikan fungsi pengolahan data untuk statistik bantuan (misal: menghitung jumlah bantuan per kategori).
* [ ] **2.2. Helper Integrasi Gemini AI (`utils/ai_helper.py`)**
  * Setup inisialisasi SDK `google-generativeai` dengan API Key dari variabel lingkungan.
  * Buat fungsi `get_gemini_response(prompt: str, context: str)` untuk memproses chatbot dengan grounding data.
  * Buat fungsi `verify_claim_with_gemini(claim: str, reference_data: str)` untuk proses cek hoaks.

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
