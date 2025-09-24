#!/bin/bash

# ==============================================================================
# Installer Otomatis untuk Proyek AIST-IoT
# ==============================================================================

# Fungsi untuk mencetak pesan dengan warna
print_info() {
    echo -e "\n\e[34m[INFO]\e[0m $1"
}

print_success() {
    echo -e "\e[32m[SUCCESS]\e[0m $1"
}

print_error() {
    echo -e "\e[31m[ERROR]\e[0m $1"
}

# 1. Memeriksa hak akses root
print_info "Memeriksa hak akses root..."
if [[ $EUID -ne 0 ]]; then
   print_error "Skrip ini harus dijalankan sebagai root. Coba jalankan dengan 'sudo bash install.sh'" 
   exit 1
fi

# 2. Memperbarui sistem dan menginstal dependensi sistem
print_info "Memperbarui paket sistem dan menginstal dependensi (aircrack-ng, nmap, wifite, dll)..."
apt-get update
apt-get install -y git python3-venv aircrack-ng nmap wifite bc build-essential linux-headers-$(uname -r) dkms

# 3. Membuat file .env secara interaktif
print_info "Menyiapkan file konfigurasi .env..."
if [ -f ".env" ]; then
    print_info "File .env sudah ada. Melewati pembuatan."
else
    echo "-------------------------------------------------------------"
    echo "Silakan masukkan kunci API OpenAI Anda."
    echo "Kunci ini tidak akan ditampilkan di layar dan akan disimpan"
    echo "secara lokal di dalam file .env."
    echo "-------------------------------------------------------------"
    read -sp 'Masukkan OPENAI_API_KEY: ' openai_api_key
    echo
    
    # Menulis kunci API ke file .env
    echo "OPENAI_API_KEY=\"$openai_api_key\"" > .env
    print_success "File .env berhasil dibuat."
fi

# 4. Membuat dan mengaktifkan lingkungan virtual Python
print_info "Membuat lingkungan virtual Python di dalam folder 'venv'..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    print_error "Gagal membuat lingkungan virtual Python."
    exit 1
fi

# 5. Menginstal dependensi Python dari requirements.txt
print_info "Menginstal pustaka Python dari requirements.txt ke dalam venv..."
source venv/bin/activate
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    print_error "Gagal menginstal dependensi Python. Periksa file requirements.txt."
    exit 1
fi
deactivate

echo
print_success "======================================================"
print_success "         Instalasi AIST-IoT Selesai!                  "
print_success "======================================================"
echo
print_info "Untuk menjalankan program, gunakan perintah berikut:"
echo "1. Aktifkan lingkungan virtual: source venv/bin/activate"
echo "2. Jalankan skrip utama: sudo $(pwd)/venv/bin/python3 main.py"
echo