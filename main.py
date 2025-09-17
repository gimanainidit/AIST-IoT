import os
from dotenv import load_dotenv
import json
import locale

# Import factory, not a specific provider
from llm_providers import get_llm_instance 

# 1. Impor tools diperbarui: tool manual diganti nama, tool auditor ditambahkan
from tools.wireless_breacher import breach_wifi_network as breach_wifi_network_manual
from tools.wireless_auditor import audit_wifi_with_wifite
from tools.network_mapper import map_lan_devices
from tools.iot_controller import control_iot_device
from agents.orchestrator import create_aist_agent # Import agent creation function

def run():
    """Fungsi utama untuk menjalankan AIST-IoT."""
    load_dotenv()

    # --- LANGKAH 1: Pemilihan Model Secara Interaktif ---
    # Baca pilihan model dari environment variable.
    # ENV: AIST_LLM_PROVIDER, format: "<provider>:<model>", e.g., "openai:gpt-4-turbo"
    # Default ke "openai:gpt-4-turbo" jika tidak diset untuk tahapan initial dev dengan penalaran terbaik.
    llm_selection = os.getenv("AIST_LLM_PROVIDER", "openai:gpt-4-turbo")
    print(f"🧠 Using LLM: {llm_selection}")

    try:
        # Panggil factory untuk mendapatkan instance LLM yang benar
        llm = get_llm_instance(llm_selection)
    except (ValueError, ImportError) as e:
        print("Make sure you have installed the appropriate library for your selected provider (e.g., 'pip install langchain-openai', 'langchain-google-genai', etc.).")
        print("Make sure you have installed the appropriate library, e.g.: pip install langchain-google-genai")
        return

    # --- LANGKAH 2: Merakit Agent dengan Daftar Tool yang Lengkap ---
    all_tools = [
        breach_wifi_network_manual, # Nama baru yang lebih deskriptif
        audit_wifi_with_wifite,     # Tool baru ditambahkan
        map_lan_devices,
        control_iot_device,
    ]
    
    aist_agent = create_aist_agent(tools=all_tools, llm=llm)
    
    # --- LANGKAH 3: Menyiapkan Perintah Pengguna (Localization) ---
    # Load localization file based on system locale
    lang_tuple = locale.getlocale()
    if not lang_tuple or not lang_tuple[0]:
        lang_tuple = locale.getdefaultlocale()
    lang = lang_tuple[0] if lang_tuple and lang_tuple[0] else None
    try:
        with open(f"locales/{lang_code}.json", "r", encoding="utf-8") as f:
            messages = json.load(f)
    except FileNotFoundError:
        # Fallback to English if locale file not found
        try:
            with open("locales/en.json", "r", encoding="utf-8") as f:
                messages = json.load(f)
        except FileNotFoundError:
            print("❌ Error: No localization files found. Please ensure at least 'locales/en.json' exists.")
            return
        with open("locales/en.json", "r", encoding="utf-8") as f:
            messages = json.load(f)

    # Dapatkan perintah dari file localization
    user_command = messages.get(
        "user_command",
        "Perform a full security test on the SSID 'WifiAdit' using the wordlist '/usr/share/wordlists/rockyou.txt'."
    )
    
    # --- LANGKAH 4: Menjalankan Agent dan Menampilkan Hasil ---
    result = aist_agent.invoke({"input": user_command})

    # Hasilnya ditampilkan SETELAH agent selesai bekerja
    print("\n✅ Test run complete. Final Result:")
    if isinstance(result, dict):
        print(result.get('output', 'No output received from agent.'))
    elif result is None:
        print('No output received from agent (None returned).')
    else:
        print(f'Agent returned unexpected result: {result}')

    # Hasilnya ditampilkan SETELAH agent selesai bekerja
    print("\n✅ Test run complete. Final Result:")
    print(result.get('output', 'No output received from agent.'))


if __name__ == "__main__":
    run()