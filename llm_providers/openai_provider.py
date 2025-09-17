# llm_providers/openai_provider.py

from langchain_openai import ChatOpenAI

def get_provider(model_name: str):
    """Menyediakan instance LLM dari OpenAI."""
    # Menambahkan 'gpt-4o-mini' ke dalam daftar model yang didukung
    supported_models = ["gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o-mini"]
    
    if model_name not in supported_models:
        raise ValueError(f"Model OpenAI yang didukung adalah {supported_models}")
    
    return ChatOpenAI(model=model_name, temperature=0)