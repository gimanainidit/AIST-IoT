# tools/contextual_auditor.py

import subprocess
import logging
from logger_system import logger
import json
import os
from langchain.agents import tool

logger = logging.getLogger('AIST_Logger')

# Helper functions _run_command dan _parse_wifite_cracked_file bisa di-copy dari wireless_auditor.py
# atau lebih baik lagi, dibuat menjadi modul utilitas bersama.
# Untuk kesederhanaan, kita asumsikan fungsinya tersedia di sini.

def _run_command(command: list, timeout: int) -> subprocess.CompletedProcess:
    """Menjalankan command di shell dengan logging dan timeout."""
    logger.info(f"Executing command: {' '.join(command)}")
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(timeout=timeout)
        logger.info(f"Command finished. RC: {process.returncode}, STDOUT: {stdout.strip()}, STDERR: {stderr.strip()}")
        return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
    except subprocess.TimeoutExpired:
        process.kill()
        logger.warning(f"Command timed out after {timeout} seconds. Process killed.")
        raise
    except Exception as e:
        logger.error(f"An exception occurred: {e}")
        raise

def _parse_wifite_cracked_file(essid: str) -> str | None:
    """Membaca file cracked.json dari wifite dan mencari password."""
    cracked_file = "hs/cracked.json"
    if not os.path.exists(cracked_file): return None
    with open(cracked_file, 'r') as f: data = json.load(f)
    for network in data:
        if network.get('essid') == essid:
            password = network.get('password')
            logger.info(f"Password found for '{essid}' in wifite results: '{password}'")
            return password
    return None

@tool
def run_contextual_wifi_audit(network_info: dict, wordlist_path: str) -> str:
    """
    Menganalisis properti jaringan yang terdeteksi dan secara otomatis memilih
    serta menjalankan serangan wifite2 yang paling sesuai.
    Tool ini harus dipanggil setelah pemindaian awal dilakukan.
    Input 'network_info' adalah dictionary yang berisi detail satu jaringan
    dari hasil pemindaian, termasuk 'essid', 'encryption', dll.
    """
    essid = network_info.get("essid")
    encryption_details = network_info.get("encryption", "").upper()
    
    logger.info(f"Memulai audit kontekstual pada target: {essid}")
    
    # Hapus file cracked.json lama untuk memastikan hasil yang bersih
    if os.path.exists("hs/cracked.json"): os.remove("hs/cracked.json")

    command = ["sudo", "wifite", "--kill", "--essid", essid]
    attack_type = "Unknown"
    timeout = 300 # Default timeout 5 menit

    # --- Logika Pemilihan Serangan ---
    if "WPA" in encryption_details and "WPS" in encryption_details:
        attack_type = "WPS"
        logger.info(f"Target '{essid}' supports WPS. Prioritizing WPS attacks (Pixie-Dust, PIN).")
        command.extend(["--wps", "--wps-time", "300"]) # Fokus pada WPS selama 5 menit
        timeout = 360

    elif "WPA" in encryption_details:
        attack_type = "WPA Handshake/PMKID"
        logger.info(f"Target '{essid}' is WPA/WPA2. Launching Handshake/PMKID capture.")
        command.extend(["--dict", wordlist_path, "--no-wps", "--cracked"])
        timeout = 300

    elif "WEP" in encryption_details:
        logger.critical(f"WEP network '{essid}' detected. This is a critical vulnerability.")
        return f"AUDIT HALT: Network '{essid}' uses WEP, which is a broken protocol. No cracking attempt is needed. The presence of WEP itself is a critical finding. Recommended action: Decommission or upgrade the network immediately."

    else:
        return f"AUDIT INFO: Network '{essid}' uses an unsupported encryption type for this tool: {encryption_details}"

    # --- Eksekusi Serangan ---
    try:
        _run_command(command, timeout=timeout)
    except subprocess.TimeoutExpired:
        logger.warning(f"Wifite run for {attack_type} attack timed out. Checking for partial results...")
    except Exception as e:
        return f"Wifite run failed for {attack_type} attack with a critical error: {e}"

    # --- Cek Hasil ---
    password = _parse_wifite_cracked_file(essid)
    if password:
        return f"SUCCESS! Contextual audit on '{essid}' ({attack_type} Attack) found the key: '{password}'"
    else:
        return f"FAILURE. Contextual audit on '{essid}' ({attack_type} Attack) completed, but the key was NOT FOUND."