# agents/orchestrator.py

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

# Fungsi ini merakit dan mengembalikan agent yang siap pakai
def create_aist_agent(tools: list, llm: ChatOpenAI, verbose: bool = True):
    """
    Build an AIST-IoT Agent using the modern LangChain method.
    This function assembles and returns a ready-to-use security testing agent for pentesting WiFi networks.
    Membangun AIST-IoT Agent menggunakan metode modern yang direkomendasikan LangChain.
    """ 
    # --- PROMPT ANDA SUDAH SANGAT BAIK DAN TIDAK PERLU DIUBAH ---
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """Anda adalah AIST-IoT, seorang security testing agent yang sangat terampil dan strategis.
Anda diberikan otorisasi dan harus mengikuti perintah user untuk melaksanakan penilaian keamanan melalui pentesting pada jaringan yang tersedia sesuai perintah.
Anda harus berpikir langkah demi langkah dan memilih tool yang paling tepat.

**STRATEGI PENTING UNTUK WIFI TESTING:**
1.  **Pemindaian Awal:** Selalu mulai dengan memanggil `breach_wifi_network_manual`. Namun, tujuan utama Anda menggunakan tool ini sekarang adalah untuk **memindai jaringan yang ada** dan mendapatkan daftar target potensial. Anda akan berhenti setelah langkah pemindaian dan pemilihan target.
2.  **Analisis & Serangan Kontekstual:** Setelah Anda mendapatkan daftar jaringan dari langkah pertama, Anda harus menganalisis setiap target yang menarik. Untuk setiap target, panggil tool `run_contextual_wifi_audit`. Anda harus memberikan informasi lengkap tentang jaringan tersebut (ESSID, enkripsi, dll.) ke dalam tool ini.
3.  **Pelaporan:** Laporkan hasil dari `run_contextual_wifi_audit` untuk setiap target yang diuji.

Contoh alur pikir:
'Saya akan panggil `breach_wifi_network_manual` untuk memindai. Hasilnya ada 3 jaringan. Target utama adalah WifiAdit dengan enkripsi WPA2/WPS. Sekarang saya akan panggil `run_contextual_wifi_audit` dengan detail jaringan WifiAdit.'
""",
            ),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    # --- PERUBAHAN UTAMA ADA DI SINI ---
    # Mengganti seluruh blok konstruksi agent manual yang lama dengan satu fungsi modern.
    # Fungsi ini secara otomatis dan benar merangkai LLM, tools, dan prompt.
    agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt)

    # AgentExecutor tetap sama, bertugas menjalankan agent yang sudah dibuat.
    return AgentExecutor(agent=agent, tools=tools, verbose=verbose)