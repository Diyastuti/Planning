# LERES - Layanan E-Government Rekomendasi & Edukasi Smart

Aplikasi chatbot asisten pintar satu pintu berbasis AI (`gemini-3.5-flash` / `gemini-1.5-flash`) yang dirancang untuk menjawab kesulitan masyarakat dalam mengakses informasi bantuan sosial resmi yang valid dan mendeteksi/memverifikasi isu berita hoaks di tingkat komunitas.

Aplikasi ini dilengkapi dengan **CKAN API Harvester** untuk memanen dataset langsung dari portal data pemerintahan resmi secara *real-time*.

## Fitur Utama

1. **💬 Chatbot LERES**: Fitur tanya-jawab interaktif menggunakan bahasa sehari-hari. Chatbot secara otomatis memindai database lokal hasil unduhan, mencari dataset relevan menggunakan Pandas, dan menggunakannya sebagai konteks pembatasan (*grounding*) model AI untuk memitigasi halusinasi.
2. **🔍 Verifikasi Hoaks**: Modul penentu fakta untuk memeriksa kebenaran klaim berita bansos yang beredar di grup chat. Hasil verifikasi menampilkan status **VALID**, **HOAKS**, atau **BUTUH KLARIFIKASI** disertai persentase tingkat keyakinan dan analisis detail.
3. **🔄 Sinkronisasi Portal Data (Harvester)**: Antarmuka pemanen data CKAN API langsung dari:
   * Nasional: `data.go.id`
   * Jawa Tengah: `data.jatengprov.go.id`
   * Jawa Barat: `data.jabarprov.go.id`
   * DKI Jakarta: `data.jakarta.go.id`
4. **📊 Dashboard & Visualizer Dinamis**: Dashboard interaktif untuk mengeksplorasi berkas CSV yang diunduh secara lokal. Pengguna dapat menghasilkan visualisasi grafik (Bar Plot, Line Plot, Scatter Plot) secara dinamis dengan memilih sumbu X dan Y.
5. **📞 Kontak Instansi & Eskalasi**: Sistem rujukan kontak telepon dan situs resmi kementerian jika AI mendeteksi kondisi darurat atau membutuhkan intervensi petugas manusia langsung.

## Teknologi & Dependensi

* **Python 3.10+**
* **Streamlit**: Framework UI Antarmuka Web
* **Google Generative AI SDK**: Integrasi model LLM Gemini
* **Pandas & NumPy**: Pengolahan dan indeksing berkas dataset
* **Matplotlib & Seaborn**: Render bagan visualisasi data secara dinamis
* **Requests & Urllib3**: Penarikan data dari CKAN API daerah (disertai bypass peringatan SSL)

---

## Petunjuk Instalasi & Cara Menjalankan

### 1. Buka Direktori Proyek
Buka terminal Anda dan pastikan berada di folder direktori `Planning`:
```bash
cd D:\21_KAMARUL ARIFIN MUZAFFAR_XI TJKT1_PIC\Planning
```

### 2. Aktifkan Virtual Environment
* **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
* **Windows (CMD):**
  ```cmd
  python -m venv venv
  .\venv\Scripts\activate.bat
  ```

### 3. Instal Dependensi Library
```bash
pip install -r requirements.txt
```

### 4. Konfigurasi API Key Gemini
Untuk mengaktifkan model AI:
1. Buka file [app.py](file:///d:/21_KAMARUL%20ARIFIN%20MUZAFFAR_XI%20TJKT1_PIC/Planning/app.py) di editor Anda.
2. Cari variabel array `API_KEYS` di bagian atas kode (baris 21).
3. Ganti `"YOUR_GEMINI_API_KEY_1"`, dll. dengan API Key Google AI Studio Anda yang valid:
   ```python
   API_KEYS = [
       "AIzaSy...", 
       "AIzaSy...",
       "AIzaSy..."
   ]
   ```
   *Catatan: Anda juga dapat memasukkan API Key secara langsung melalui antarmuka web LERES pada menu sidebar **🔑 Advanced API Configuration** saat aplikasi berjalan.*

### 5. Jalankan Aplikasi
Jalankan perintah berikut pada terminal:
```bash
streamlit run app.py
```
Aplikasi secara otomatis akan terbuka di browser Anda pada alamat `http://localhost:8501`.

### 6. Pemanenan Data Pertama Kali
Setelah aplikasi terbuka:
1. Pilih menu **🔄 Sinkronisasi Portal Data** di menu sebelah kiri.
2. Atur jumlah paket data yang ingin diambil menggunakan slider.
3. Klik tombol **Mulai Sinkronisasi Sekarang** untuk mengunduh dataset resmi langsung dari server pemerintahan ke folder `database_chatbot/`.
4. Setelah selesai, chatbot LERES dan Dashboard Visualisasi siap digunakan sepenuhnya dengan data dinamis.
