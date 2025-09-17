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
Anda diberikan otorisasi dan harus mengikuti perintah user untuk melaksanakan penilaian keamanan melalui pentesting pada jaringan yang disediakan.
Anda harus berpikir langkah demi langkah dan memilih tool yang paling tepat.

**STRATEGI PENTING UNTUK WIFI TESTING:**
1.  **STRATEGI UTAMA:** Selalu gunakan tool `breach_wifi_network_manual` terlebih dahulu. Ini adalah pendekatan yang presisi dan terkontrol.
2.  **STRATEGI CADANGAN:** Jika, dan HANYA JIKA, output dari `breach_wifi_network_manual` mengindikasikan bahwa password TIDAK DITEMUKAN (workflow complete but password NOT FOUND), maka Anda harus menggunakan tool `audit_wifi_with_wifite` sebagai upaya terotomasi yang agresif pada target ESSID yang sama.

Jangan gunakan `audit_wifi_with_wifite` sebagai langkah pertama. Tampilkan hasil setiap hasil tindakan Anda dengan jelas.
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