# tools/hidden_network_discoverer.py

import subprocess
import re
import os
from logger_system import logger
from langchain.agents import tool

def _run_mdk4_command(command: list, timeout: int = 60) -> str:
    """Menjalankan command mdk4, menangani output, dan timeout."""
    logger.info(f"Executing command: {' '.join(command)}")
    try:
        # mdk4 terus berjalan, jadi kita gunakan Popen dengan timeout
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(timeout=timeout)
        logger.info(f"mdk4 finished or timed out. STDOUT: {stdout.strip()}")
        if stderr:
            logger.warning(f"mdk4 STDERR: {stderr.strip()}")
        return stdout
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, _ = process.communicate()
        logger.warning(f"mdk4 command timed out after {timeout} seconds. Process killed.")
        return stdout
    except FileNotFoundError:
        logger.error("Command 'mdk4' not found. Please install it using 'sudo apt install mdk4'")
        raise
    except Exception as e:
        logger.error(f"An exception occurred while running mdk4: {e}")
        raise

@tool
def discover_hidden_ssid(interface: str) -> str:
    """
    Mengidentifikasi ESSID dari jaringan tersembunyi (hidden network) menggunakan
    serangan kamus probe request mdk4. Tool ini akan meminta BSSID target
    dan path ke file wordlist secara interaktif.
    """
    logger.info("--- Memulai Tool Penemuan SSID Tersembunyi ---")
    
    # --- Langkah 1: Input Interaktif dari User ---
    print("\n--- [INTERACTIVE STEP] Input untuk Penemuan SSID Tersembunyi ---")
    try:
        target_bssid = input("Masukkan BSSID (MAC Address) dari AP target: ").strip()
        # Validasi sederhana untuk format BSSID
        if not re.match(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$", target_bssid):
            logger.error(f"Format BSSID tidak valid: {target_bssid}")
            return "Aksi dibatalkan: Format BSSID tidak valid."

        wordlist_path = input("Masukkan path lengkap ke file wordlist (e.g., /usr/share/wordlists/rockyou.txt): ").strip()
        if not os.path.exists(wordlist_path):
            logger.error(f"File wordlist tidak ditemukan di: {wordlist_path}")
            return f"Aksi dibatalkan: File wordlist tidak ditemukan di {wordlist_path}."

    except (ValueError, IndexError):
        logger.error("Input tidak valid.")
        return "Aksi dibatalkan: Input tidak valid."

    logger.info(f"Target BSSID: {target_bssid}, Wordlist: {wordlist_path}")

    # --- Langkah 2: Menjalankan Serangan mdk4 ---
    command = ["sudo", "mdk4", interface, "p", "-t", target_bssid, "-f", wordlist_path]
    output = _run_mdk4_command(command)

    # --- Langkah 3: Menganalisis Hasil ---
    # mdk4 biasanya mencetak "SSID Found: 'NAMA_SSID'" saat berhasil
    match = re.search(r"SSID Found: SSID '(.*?)'", output, re.IGNORECASE)
    
    if match:
        found_ssid = match.group(1)
        logger.info(f"SUCCESS! SSID ditemukan: '{found_ssid}'")
        return f"SUCCESS! SSID untuk BSSID {target_bssid} berhasil diidentifikasi: '{found_ssid}'"
    else:
        logger.warning("SSID tidak ditemukan menggunakan wordlist yang diberikan.")
        return f"FAILURE. SSID untuk BSSID {target_bssid} tidak dapat ditemukan dengan wordlist tersebut."