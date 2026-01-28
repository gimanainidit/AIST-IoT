# AIST-IoT: Pengujian Keamanan IoT Berbasis Agen
AIST-IoT (Agentic AI Security Tester for IoT) adalah sistem yang dirancang untuk melakukan pengujian keamanan otomatis pada jaringan IoT (Internet of Things). Sistem ini menggunakan agen (agentic AI) yang didukung oleh model bahasa besar (LLM) untuk mengidentifikasi potensi kerentanan sistem mulai dari jaringan nirkabel sampai dengan perangkat cerdas (IoT) yang terhubung ke jaringan publik/rumah/kantor/perkotaan.

## Cara Kerja

Sistem ini bekerja melalui beberapa langkah utama:

1.  **Pemilihan Model Bahasa (LLM):**
    *   Sistem memilih model bahasa yang akan digunakan. Secara default, sistem akan mencoba menggunakan `gpt-4o-mini` (model yang lebih kecil dan cepat untuk pengujian). Anda dapat mengubah model ini melalui *environment variable* `AIST_LLM_PROVIDER`.
    *   Contoh: `AIST_LLM_PROVIDER=openai:gpt-4` (untuk menggunakan GPT-4).
2.  **Perakitan Agen Cerdas:**
    *   Agen cerdas dibuat dengan menggabungkan berbagai *tools* keamanan. *Tools* ini mencakup:
        *   `breach_wifi_network_manual`: Melakukan percobaan pembobolan jaringan Wi-Fi secara manual.
        *   `audit_wifi_with_wifite`: Melakukan audit jaringan Wi-Fi menggunakan alat Wifite.
        *   `run_contextual_wifi_audit`: Melakukan audit jaringan Wi-Fi yang lebih cerdas dan kontekstual.
        *   `map_lan_devices`: Memetakan perangkat yang terhubung ke jaringan lokal (LAN).
        *   `control_iot_device`: Mengontrol perangkat IoT (misalnya, mematikan atau menghidupkan).
    *   Agen ini menggunakan LLM yang dipilih untuk memahami perintah pengguna dan menentukan *tool* mana yang perlu dijalankan.
3.  **Penyiapan Perintah Pengguna (Lokalisasi):**
    *   Sistem membaca perintah pengguna dari file lokalisasi (`locales/*.json`). Ini memungkinkan sistem untuk mendukung berbagai bahasa.
    *   Jika file lokalisasi untuk bahasa sistem tidak ditemukan, sistem akan menggunakan bahasa Inggris sebagai *fallback*.
    *   Anda dapat menyesuaikan perintah pengguna dengan mengubah nilai `user_command` di file JSON lokalisasi.
4.  **Menjalankan Agen dan Menampilkan Hasil:**
    *   Agen cerdas menjalankan perintah pengguna menggunakan *tools* yang sesuai.
    *   Hasil dari setiap *tool* dikumpulkan dan dianalisis oleh agen.
    *   Hasil akhir ditampilkan kepada pengguna setelah semua *tools* selesai dijalankan.

## Cara Penggunaan

1.  **Instalasi *Dependencies*:**
    *   Pastikan Anda telah menginstal semua *dependencies* yang diperlukan. Anda dapat menggunakan `pip` untuk menginstal *dependencies* dari file `requirements.txt` (jika ada).
2.  **Konfigurasi *Environment Variables*:**
    *   Buat file `.env` di direktori proyek Anda.
    *   Tambahkan *environment variable* `AIST_LLM_PROVIDER` untuk menentukan model bahasa yang ingin Anda gunakan.
    *   Contoh:

        ```
        AIST_LLM_PROVIDER=openai:gpt-4
        ```
3.  **Menjalankan Sistem:**
    *   Jalankan file `main.py` menggunakan perintah:

        ```bash
        python main.py
        ```

## Struktur Kode

*   `main.py`: File utama yang menjalankan sistem.
*   `llm_providers/`: Direktori yang berisi kode untuk memuat dan mengkonfigurasi model bahasa.
*   `tools/`: Direktori yang berisi *tools* keamanan yang digunakan oleh agen.
*   `agents/`: Direktori yang berisi kode untuk membuat dan mengkonfigurasi agen cerdas.
*   `locales/`: Direktori yang berisi file lokalisasi untuk berbagai bahasa.

## Keterangan Tambahan

*   Pastikan Anda memiliki kunci API yang valid untuk model bahasa yang Anda gunakan. Anda dapat mengatur kunci API ini sebagai *environment variable*.
*   Sistem ini masih dalam pengembangan dan mungkin memiliki beberapa keterbatasan.
*   Gunakan sistem ini dengan hati-hati dan hanya pada jaringan yang Anda miliki izin untuk melakukan pengujian keamanan.

Semoga dokumentasi ini membantu Anda memahami cara kerja AIST-IoT!
