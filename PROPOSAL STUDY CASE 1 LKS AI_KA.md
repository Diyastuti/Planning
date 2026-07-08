TEAM …  
SMK TUNAS HARAPAN PATI

Anggota team : 1,2,3

Study case — KOMUNITAS: Kesulitan Mengakses Informasi yang Valid 

STUDY CASE 1

1. LATAR BELAKANG  
   Banyak warga kesulitan mengakses bantuan yang sebenarnya tersedia karena informasinya membingungkan, tersebar di banyak tempat, atau sulit diverifikasi kebenarannya. Ketika seseorang sedang menghadapi situasi sulit — misalnya bencana, kebutuhan layanan kesehatan, perlindungan anak, atau bantuan sosial — mereka sering tidak tahu harus mulai dari mana, dokumen apa yang diperlukan, atau lembaga mana yang tepat untuk dihubungi. Beredarnya informasi keliru (hoaks) di komunitas juga membuat orang ragu dan kehilangan kesempatan memperoleh bantuan tepat waktu.   
     
2. RUMUSAN MASALAH  
1. Informasi layanan publik tersebar di berbagai sumber sehingga sulit diakses oleh masyarakat.  
2. Masyarakat mengalami kesulitan dalam memahami persyaratan dan prosedur yang sesuai dengan kondisi yang dihadapi.  
3. Sulitnya memastikan kebenaran informasi bantuan yang beredar.  
4. Keterbatasan akses terhadap informasi bantuan yang tersusun dalam satu tempat dan mudah dipahami.

   

3. IDE SOLUSI BERBASIS AI  
   Aplikasi ini adalah chatbot asisten pintar satu pintu yang menjawab 4 rumusan masalah melalui fitur berikut:

   A. Menyatukan seluruh data bantuan yang tersebar di portal data.go.id ke dalam satu ruang chat agar mudah diakses.  
   B. Warga cukup cerita pakai bahasa sehari-hari saat kesulitan (misal: "Saya sakit"), lalu AI langsung menunjukkan syarat dan instansi yang tepat.  
   C. Memverifikasi berita bantuan yang beredar di komunitas dengan data resmi pemerintah agar warga merasa tenang dan tidak ragu.  
   D. Warga tidak perlu lagi pusing mencari ke sana kemari. Cukup di satu tempat ini, AI merangkum semua info bantuan dengan bahasa yang mudah dipahami  
     
4. TARGET PENGGUNA  
1. Gen-Z (Anak muda yang ingin akses cepat tanpa ribet)  
2. Masyarakat umum.   
3. Pelajar dan mahasiswa.   
4. Orang tua. 

   

5. PENDEKATAN TEKNIS DAN TOOLS  
1. API Key Gemini  
2. Streamlit  
3. Pandas  
4. Python  
5. Matplotlib  
     
     
6. RENCANA SUMBER DATA  
1. [data.go.id](http://data.go.id)  
2. Database sendiri

   

7. PERNYATAAN RESPONSIBLE AI

   Risiko: 

1. Chatbot mengalami hallucination (halusinasi) dan memberikan prosedur atau syarat klaim bantuan sosial yang keliru/hoaks kepada warga.

   Strategi Mitigasi:

   1. Membatasi basis pengetahuan AI (Knowledge Base) hanya mengambil data dari portal resmi pemerintah (seperti data.go.id).

      2. Menyertakan tautan sumber asli pada setiap jawaban chatbot agar pengguna dapat memverifikasi ulang kebenaran informasinya.

      3. Penilaian: Menyediakan tombol "Hubungi Petugas" atau fitur ke petugas instansi terkait jika AI mendeteksi pertanyaan yang sensitif atau memiliki tingkat keyakinan (confidence score) yang rendah.