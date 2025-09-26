# main.py
import sys
from logger_system import logger
import config
from llm_providers import get_llm_instance 
from agents.orchestrator import create_aist_agent

# Impor semua tools yang akan digunakan
from tools.wireless_breacher import breach_wifi_network_manual
from tools.contextual_auditor import run_contextual_wifi_audit
from tools.network_mapper import map_lan_devices
from tools.iot_controller import control_iot_device
from tools.hidden_network_discoverer import discover_hidden_ssid
from tools.custom_wordlist_generator import generate_custom_wordlist

def main():
    """Fungsi utama untuk menjalankan AIST-IoT."""
    logger.info("==============================================")
    logger.info("        Memulai AIST-IoT Agent                ")
    logger.info("==============================================")

    # 1. Memeriksa Konfigurasi
    if not config.OPENAI_API_KEY:
        logger.critical("FATAL ERROR: OPENAI_API_KEY tidak ditemukan. Pastikan sudah diatur di file .env.")
        sys.exit(1)

    # 2. Menginisialisasi LLM
    try:
        # Untuk pengujian, kita hardcode pilihan modelnya
        llm_selection = "openai:gpt-5-nano"
        logger.info(f"Menggunakan LLM: {llm_selection}")
        llm = get_llm_instance(llm_selection, api_key=config.OPENAI_API_KEY)
    except Exception as e:
        logger.critical(f"Gagal memuat LLM: {e}")
        sys.exit(1)

    # 3. Merakit daftar tools
    all_tools = [
        generate_custom_wordlist,
        discover_hidden_ssid,
        breach_wifi_network_manual,
        run_contextual_wifi_audit,
        map_lan_devices,
        control_iot_device,
    ]
    logger.info(f"Tools yang dimuat: {[tool.name for tool in all_tools]}")

    # 4. Membuat Agent
    aist_agent = create_aist_agent(tools=all_tools, llm=llm, verbose=True)

    # 5. Memulai loop interaktif dengan user
    logger.info("Agent siap menerima perintah. Ketik 'exit' untuk keluar.")
    while True:
        try:
            user_command = input("\nPerintah > ")
            if user_command.lower() == 'exit':
                break
            
            logger.info(f"Mengeksekusi perintah: {user_command}")
            result = aist_agent.invoke({"input": user_command})
            logger.info(f"Hasil akhir dari agent: {result.get('output')}")

        except KeyboardInterrupt:
            print("\nKeluar dari program.")
            break
        except Exception as e:
            logger.error(f"Terjadi error pada main loop: {e}", exc_info=True)

    logger.info("AIST-IoT Agent dihentikan.")

if __name__ == "__main__":
    main()