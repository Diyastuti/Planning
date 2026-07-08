# Panduan Pengembangan (Development Guidelines)
## Project: Asisten Pintar Komunitas

Panduan ini berisi standar teknis, arsitektur proyek, konfigurasi UI/UX, dan panduan keamanan untuk memandu proses pengembangan aplikasi.

---

## 1. Persiapan Lingkungan (Environment Setup)
Ikuti langkah-langkah berikut untuk memulai lingkungan pengembangan lokal yang bersih dan konsisten:

1. **Membuat Virtual Environment:**
   ```bash
   python -m venv venv
   ```
2. **Mengaktifkan Virtual Environment:**
   * Windows (PowerShell): `.\venv\Scripts\Activate.ps1`
   * Windows (CMD): `.\venv\Scripts\activate.bat`
   * Linux/macOS: `source venv/bin/activate`
3. **Instalasi Dependencies:**
   Buat file `requirements.txt` dengan konten berikut:
   ```text
   streamlit>=1.30.0
   google-generativeai>=0.3.0
   pandas>=2.0.0
   matplotlib>=3.7.0
   python-dotenv>=1.0.0
   ```
   Lalu jalankan instalasi:
   ```bash
   pip install -r requirements.txt
   ```
4. **Konfigurasi Variabel Lingkungan:**
   Buat file `.env` di root direktori untuk menyimpan API Key:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```
   *Penting: Pastikan file `.env` telah ditambahkan ke `.gitignore` agar tidak terunggah ke repositori publik.*

---

## 2. Struktur Proyek (Directory Structure)
Struktur folder disarankan dibuat modular agar pemisahan logika (data, AI, dan UI) menjadi jelas:

```text
├── .env                  # API Key & konfigurasi rahasia
├── .gitignore            # Mengabaikan venv, .env, __pycache__, dll.
├── app.py                # Titik masuk utama aplikasi Streamlit
├── requirements.txt      # Daftar pustaka dependensi proyek
├── README.md             # Dokumentasi ringkas proyek
├── dataset/              # Folder untuk menyimpan dataset (CSV/JSON)
│   └── bantuan_sosial.csv # Contoh dataset resmi (dari data.go.id / mock)
├── utils/                # Modul utilitas
│   ├── __init__.py
│   ├── ai_helper.py      # Pengolahan LLM Gemini (Prompt, Chat, Verifikasi)
│   └── data_helper.py    # Logika Pandas & Visualisasi Matplotlib
└── config/               # Konfigurasi Streamlit & Tema
    └── config.toml       # Pengaturan tema visual Streamlit
```

---

## 3. Panduan UI/UX Premium (Vibe & Aesthetics)
Untuk memberikan impresi pertama yang memukau bagi pengguna (terutama juri dan warga), kita akan menerapkan desain Streamlit yang modern dan premium:

### A. Konfigurasi Tema (`.streamlit/config.toml`)
Buat file `.streamlit/config.toml` dengan palette warna modern:
```toml
[theme]
primaryColor = "#6366F1"          # Indigo modern
backgroundColor = "#0F172A"      # Slate Dark Mode (Sangat elegan)
secondaryBackgroundColor = "#1E293B" # Card/Sidebar Background
textColor = "#F8FAFC"            # Putih abu-abu untuk pembacaan nyaman
font = "sans serif"
```

### B. Kustomisasi UI Menggunakan CSS
Gunakan `st.markdown(..., unsafe_allow_html=True)` di `app.py` untuk memoles elemen yang kurang fleksibel bawaan Streamlit:
* **Glassmorphism:** Gunakan latar belakang semi-transparan dengan blur untuk container/cards.
* **Badges Status:** Gunakan warna spesifik untuk status verifikasi berita:
  * **VALID:** Hijau Neon (`#10B981`)
  * **HOAKS:** Merah Terang (`#EF4444`)
  * **KLARIFIKASI:** Kuning Amber (`#F59E0B`)
* **Micro-Animations:** Tambahkan efek transisi halus ketika kursor mengarah ke tombol (hover effect).

---

## 4. Standar Pengkodean (Coding Standards)

### A. Python (PEP 8)
* Gunakan penamaan variabel `snake_case` dan nama fungsi yang deskriptif.
* Sertakan type hinting untuk memperjelas tipe parameter input dan output fungsi.
  ```python
  def verify_news_with_gemini(claim_text: str, database_context: str) -> dict:
      # Logika verifikasi
      return {"status": "VALID", "explanation": "..."}
  ```

### B. Pemrosesan Data Pandas
* Hindari manipulasi langsung pada dataframe yang menghasilkan `SettingWithCopyWarning`. Gunakan `.loc` atau `.copy()`.
* Selalu bungkus proses load data dalam cache Streamlit (`@st.cache_data`) agar aplikasi berjalan cepat saat memuat data besar.
  ```python
  @st.cache_data
  def load_data(filepath: str) -> pd.DataFrame:
      return pd.read_csv(filepath)
  ```

---

## 5. Implementasi Responsible AI & Penanganan Error

### A. Pencegahan Halusinasi (Grounding)
* Asisten AI harus dibatasi perilakunya menggunakan *System Prompt* agar hanya merujuk pada dokumen yang di-load oleh Pandas.
* Jika jawaban tidak ditemukan di basis data, asisten wajib menjawab: *"Maaf, informasi program bantuan tersebut tidak ditemukan dalam basis data resmi kami."* jangan mengarang informasi.

### B. Sistem Penanganan Error (Robustness)
* **Koneksi API Gagal:** Jika koneksi API Gemini terputus atau limit kuota tercapai, aplikasi harus mendeteksi error tersebut dengan blok `try-except` dan beralih ke pencarian teks berbasis Pandas biasa (keyword matching) secara otomatis.
* **Dataset Rusak/Kosong:** Lakukan validasi file dataset sebelum aplikasi dimulai. Tampilkan pesan kesalahan yang ramah jika dataset tidak ditemukan.
