from os import getenv

from dotenv import load_dotenv

# Import the factory, not a specific provider
from llm_providers import get_llm_instance 
# Import tools from their respective modules
from tools.wireless_breacher import breach_wifi_network
from tools.network_mapper import map_lan_devices
from tools.iot_controller import control_iot_device
from agents.orchestrator import create_aist_agent # Import agent creation function

import json
import locale

def run():
    """Fungsi utama untuk menjalankan AIST-IoT."""
    load_dotenv()

    # --- LANGKAH 1: Pemilihan Model Secara Interaktif ---
    # Baca pilihan model dari environment variable.
    # Default ke gpt-4-turbo jika tidak diset untuk tahapan initial dev dengan penalaran terbaik.
    llm_selection = getenv("AIST_LLM_PROVIDER", "openai:gpt-4-turbo")
    print(f"🧠 Using LLM: {llm_selection}")

    try:
        # Call factory to get the correct LLM instance
        llm = get_llm_instance(llm_selection)
    except (ValueError, ImportError) as e:
        print(f"Error: Unable to load LLM. {e}")
        print("Make sure you have installed the appropriate library, e.g.: pip install langchain-google-genai")
        return

    # --- LANGKAH 2: Merakit dan Menjalankan Agent---
    all_tools = [
        breach_wifi_network,
        map_lan_devices,
        control_iot_device,
    ]
    
    aist_agent = create_aist_agent(tools=all_tools, llm=llm)
    # Load localization file based on system locale
    lang_tuple = locale.getlocale()
    lang = lang_tuple[0] if lang_tuple and lang_tuple[0] else None
    lang_code = lang.split('_')[0] if lang else 'en'
    try:
        with open(f"locales/{lang_code}.json", "r", encoding="utf-8") as f:
            messages = json.load(f)
    except FileNotFoundError:
        with open("locales/en.json", "r", encoding="utf-8") as f:
            messages = json.load(f)
            messages = json.load(f)

    user_command = messages.get(
        "user_command",
        "Perform a security test without causing destructive impact and try to connect to available SSIDs..."
    )
    
    print("\n✅ Test run complete. Final Result:")
    print(result.get('output', ''))
    print(result['output'])

if __name__ == "__main__":
    run()