# config.py
import os
from dotenv import load_dotenv

# Memuat variabel dari file .env
load_dotenv()

# Mengambil kunci API dari environment
# Jika tidak ditemukan, akan bernilai None
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Konfigurasi lain bisa ditambahkan di sini
# Contoh:
DEFAULT_INTERFACE = "wlan0"
DEFAULT_WORDLIST_PATH = "/usr/share/wordlists/rockyou.txt"