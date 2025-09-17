@tool
def control_iot_device(ip_address: str, vendor: str) -> str:
    """
    Gunakan tool ini untuk mencoba mengambil alih kontrol perangkat IoT yang telah
    teridentifikasi. Berdasarkan vendor, tool ini akan menggunakan library yang sesuai
    (pywizlight untuk Espressif, tinytuya untuk Tuya).
    """
    print(f"--- [Tool Running] control_iot_device ---")
    print(f"Attempting to control {vendor} device at {ip_address}")
    time.sleep(2)
    # --- GANTI BAGIAN INI DENGAN KODE ASLI (pywizlight atau tinytuya) ---
    if vendor == "Espressif Inc.":
        # Simulasi kontrol pywizlight
        print(f"SUCCESS! Controlled Wiz bulb at {ip_address}. Turned it ON (Green) and OFF.")
        return f"Successfully controlled Wiz (Espressif) device at {ip_address}. Proof of Control: Turned ON and OFF."
    elif vendor == "Tuya Smart Inc.":
        # Simulasi tinytuya yang butuh local_key
        print(f"INFO: Tuya device at {ip_address} requires a local_key for control.")
        return f"Identified Tuya device at {ip_address}, but cannot control without a local_key. Manual intervention may be needed."
    else:
        return f"No control module available for vendor '{vendor}' at {ip_address}."
    # --------------------------------------------------------------------# tools/iot_controller.py

