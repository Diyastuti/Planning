# Panduan Pengembangan (Development Guidelines)
## Project: LERES - Layanan E-Government Rekomendasi dan Edukasi Smart

Panduan ini berisi standar teknis, arsitektur proyek, konfigurasi UI/UX, dan panduan keamanan untuk memandu proses pengembangan aplikasi.

---

## 1. Persiapan Lingkungan (Environment Setup)
Ikuti langkah-langkah berikut untuk memulai lingkungan pengembangan lokal yang bersih dan konsisten:

3. **Instalasi Dependencies:**
   Buat file `requirements.txt` dengan konten berikut untuk mendukung seluruh fitur chatbot LERES (UI, AI, Pemrosesan Data, Visualisasi, dan API):
   ```text
   streamlit>=1.30.0          # Framework UI utama untuk membuat web app interaktif
   google-generativeai>=0.3.0 # SDK resmi Google Gemini API untuk chatbot & analisis
   pandas>=2.0.0              # Pengolahan database bantuan sosial (membaca CSV/Excel)
   openpyxl>=3.1.0            # Engine pembaca file Excel (.xlsx) untuk Pandas jika dataset menggunakan Excel
   matplotlib>=3.7.0          # Pembuatan visualisasi grafik statistik
   seaborn>=0.12.0            # Mempercantik tampilan grafik dengan tema yang lebih modern
   pillow>=10.0.0             # Pemrosesan gambar untuk logo/avatar di antarmuka Streamlit
   numpy>=1.24.0              # Library komputasi numerik pendukung Pandas
   requests>=2.31.0           # Melakukan request data eksternal/API jika diperlukan
   ```
   Lalu jalankan instalasi menggunakan terminal:
   ```bash
   pip install -r requirements.txt
   ```

---

## 2. Struktur Proyek (Directory Structure)
Struktur folder dibuat sesederhana mungkin agar mudah dipahami, dikembangkan, dan dideploy:

```text
├── app.py                # File utama Streamlit (Logika UI, Gemini API, Pandas, & Visualisasi)
├── requirements.txt      # Daftar dependensi library
└── README.md             # Panduan menjalankan aplikasi
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
