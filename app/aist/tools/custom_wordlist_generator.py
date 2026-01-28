# tools/custom_wordlist_generator.py

import os
import re
import itertools
from logger_system import logger
from langchain.agents import tool
import PyPDF2
import docx

# --- Helper Functions for File Reading ---

def _read_txt(file_path):
    logger.info(f"Membaca file teks: {file_path}")
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def _read_pdf(file_path):
    logger.info(f"Membaca file PDF: {file_path}")
    text = ""
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        logger.error(f"Gagal membaca PDF {file_path}: {e}")
    return text

def _read_docx(file_path):
    logger.info(f"Membaca file DOCX: {file_path}")
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        logger.error(f"Gagal membaca DOCX {file_path}: {e}")
    return text

# --- Helper Function for Leet Speak Generation ---

LEET_MAP = {
    'a': ['a', '4', '@'],
    'e': ['e', '3'],
    'i': ['i', '1', '!'],
    'o': ['o', '0'],
    's': ['s', '5', '$'],
    't': ['t', '7']
}

def _generate_leet_variations(word):
    """Menghasilkan semua variasi leet-speak dari sebuah kata."""
    # Membuat daftar pilihan untuk setiap karakter dalam kata
    options = []
    for char in word:
        # Jika karakter ada di map, gunakan variasinya. Jika tidak, gunakan karakter aslinya.
        options.append(LEET_MAP.get(char.lower(), [char]))
    
    # Menghasilkan semua kombinasi produk kartesius dari pilihan
    variations = []
    for combo in itertools.product(*options):
        variations.append("".join(combo))
    return variations

# --- Main Tool Function ---

@tool
def generate_custom_wordlist(output_filename: str) -> str:
    """
    Membuat wordlist kustom dari file (.txt, .pdf, .docx) di dalam folder 'INPUT/'.
    Tool ini mengekstrak kata-kata unik, menghasilkan variasi leet-speak,
    dan menyimpannya ke file output yang ditentukan.
    Gunakan tool ini sebelum menjalankan serangan kamus untuk membuat wordlist yang ditargetkan.
    """
    logger.info(f"--- Memulai Pembuatan Wordlist Kustom -> {output_filename} ---")
    input_dir = "INPUT"
    
    if not os.path.isdir(input_dir):
        msg = f"Folder '{input_dir}' tidak ditemukan. Harap buat folder tersebut dan letakkan file sumber di dalamnya."
        logger.error(msg)
        return f"FAILURE: {msg}"
        
    all_text = ""
    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)
        if filename.endswith(".txt"):
            all_text += _read_txt(file_path) + "\n"
        elif filename.endswith(".pdf"):
            all_text += _read_pdf(file_path) + "\n"
        elif filename.endswith(".docx"):
            all_text += _read_docx(file_path) + "\n"
    
    # Ekstrak kata-kata unik (minimal 4 karakter, hanya alfabet)
    words = re.findall(r'\b[a-zA-Z]{4,12}\b', all_text.lower())
    unique_words = sorted(list(set(words)))
    
    if not unique_words:
        msg = "Tidak ada kata-kata valid yang dapat diekstrak dari file di folder INPUT/."
        logger.warning(msg)
        return f"WARNING: {msg}"

    logger.info(f"Ditemukan {len(unique_words)} kata unik untuk diproses.")
    
    final_wordlist = set()
    for word in unique_words:
        # Menambahkan kata asli dan variasinya
        final_wordlist.add(word)
        final_wordlist.add(word.capitalize())
        variations = _generate_leet_variations(word)
        final_wordlist.update(variations)

    logger.info(f"Menghasilkan total {len(final_wordlist)} kandidat kata sandi.")
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        for item in sorted(list(final_wordlist)):
            f.write(f"{item}\n")
            
    msg = f"Wordlist kustom berhasil dibuat. {len(final_wordlist)} kata sandi disimpan di '{output_filename}'."
    logger.info(msg)
    return f"SUCCESS: {msg}"