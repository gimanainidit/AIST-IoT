# agents/orchestrator.py
from langchain.agents import AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.agents.format_scratchpad.openai_functions import format_to_openai_function_messages
from langchain.agents.output_parsers.openai_functions import OpenAIFunctionsAgentOutputParser

# Fungsi ini merakit dan mengembalikan agent yang siap pakai
def create_aist_agent(tools: list, llm):
    """Membangun AIST-IoT Agent dari tools dan LLM yang diberikan."""
    
    llm_with_tools = llm.bind_functions(tools)

    # --- PERUBAHAN PENTING DI SINI ---
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

Jangan gunakan `audit_wifi_with_wifite` sebagai langkah pertama. Tampilkan hasil setiap hasil tindakan Anda dengan jelas.
Contoh alur pikir:
'Saya akan panggil `breach_wifi_network_manual` untuk memindai. Hasilnya ada 3 jaringan. Target utama adalah WifiAdit dengan enkripsi WPA2/WPS. Sekarang saya akan panggil `run_contextual_wifi_audit` dengan detail jaringan WifiAdit.'
""",
            ),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    # ------------------------------------
    agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_function_messages(x["intermediate_steps"]),
        }
        | prompt
        | llm_with_tools
        | OpenAIFunctionsAgentOutputParser()
    )

    return AgentExecutor(agent=agent, tools=tools, verbose=True)