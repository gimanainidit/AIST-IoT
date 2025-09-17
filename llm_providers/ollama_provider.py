from langchain_community.chat_models import ChatOllama

def get_provider(model_name: str):
    """Menyediakan instance LLM lokal via Ollama."""
    # Pastikan Ollama server sudah berjalan
    # Contoh model_name: "llama3", "mistral"
    return ChatOllama(model=model_name, temperature=0)