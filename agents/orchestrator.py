# agents/orchestrator.py "Otak" utama dari AIST-IoT, berisi definisi dan prompt untuk LangChain agent.
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from logger_system import logger

def create_aist_agent(tools: list, llm: ChatOpenAI, verbose: bool = True):
    """
    Membangun AIST-IoT Agent menggunakan metode modern LangChain.
    """ 
    logger.info("Membangun agent dengan prompt dan tools yang disediakan...")
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system",
                """Anda adalah AIST-IoT, seorang security testing agent yang sangat terampil dan strategis.
Anda diberikan otorisasi dan harus mengikuti perintah user untuk melaksanakan penilaian keamanan melalui pentesting pada jaringan yang tersedia sesuai perintah.
Anda harus berpikir langkah demi langkah dan memilih tool yang paling tepat.

**STRATEGI UTAMA WIFI TESTING:**
1.  **Pembuatan Wordlist (Opsional):** Jika diperlukan, pertama-tama panggil tool `generate_custom_wordlist` untuk membuat daftar kata sandi yang ditargetkan dari dokumen di folder /INPUT. Beri nama file outputnya, misalnya 'custom_list.txt'.
2.  **Identifikasi Jaringan Tersembunyi:** Adanya jaringan dengan ESSID tersembunyi (hidden atau <length: 0>), maka gunakan tool `discover_hidden_ssid` untuk mencoba menemukan SSID name. Tool ini akan meminta Anda untuk memasukkan informasi MAC Address dari WIFI AP dan path wordlist. Anda dapat menggunakan wordlist kustom yang sudah dibuat di step 1 jika relevan.
3.  **Pemindaian (Reconnaissance):** Jika sudah melakukan identifikasi Hidden SSID, maka tools melanjutkan dengan memanggil tool `breach_wifi_network_manual` untuk mendapatkan daftar jaringan di sekitar dan informasi detailnya. Anda dapat menggunakan wordlist kustom di step 1 jika relevan.
4.  **Analisis & Serangan (Attack):** Setelah nama jaringan diketahui, panggil tool `run_contextual_wifi_audit` dengan memberikan informasi lengkap dari jaringan target untuk melancarkan serangan otomatis yang paling sesuai.
5.  **Enumerasi Jaringan (Post-Exploitation):** Jika berhasil mendapatkan akses ke sebuah jaringan, gunakan `map_lan_devices` untuk memetakan semua perangkat yang terhubung.
6.  **Kontrol Perangkat (IoT Interaction):** Berdasarkan hasil pemetaan, gunakan `control_iot_device` untuk mencoba berinteraksi atau mengontrol perangkat IoT yang teridentifikasi.
7.  **Pelaporan:** Laporkan setiap temuan dan hasil dari setiap langkah dengan jelas.

Contoh alur pikir:
'Saya akan panggil `breach_wifi_network_manual` untuk memindai. Hasilnya ada 3 jaringan. Target utama adalah WifiAdit dengan enkripsi WPA2/WPS. Sekarang saya akan panggil `run_contextual_wifi_audit` dengan detail jaringan WifiAdit.'
"""),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    agent = create_openai_tools_agent(llm, tools, prompt)
    logger.info("Agent berhasil dibuat.")
    
    return AgentExecutor(agent=agent, tools=tools, verbose=verbose)