# logger_system.py Modul terpusat untuk mengelola logging di seluruh aplikasi.
import logging
import sys

def setup_logger():
    """Mengkonfigurasi dan mengembalikan instance logger."""
    # Membuat logger utama
    logger = logging.getLogger('AIST_Logger')
    logger.setLevel(logging.INFO)

    # Mencegah duplikasi handler jika fungsi ini dipanggil berkali-kali
    if logger.hasHandlers():
        logger.handlers.clear()

    # Formatter untuk log
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(module)s] - %(message)s')

    # Handler untuk menyimpan log ke file
    file_handler = logging.FileHandler('aist_audit.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler untuk menampilkan log di console (terminal)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# Membuat satu instance logger untuk diimpor oleh modul lain
logger = setup_logger()