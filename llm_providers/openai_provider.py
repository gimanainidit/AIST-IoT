# llm_providers/openai_provider.py Logika spesifik untuk menginisialisasi model dari OpenAI
from langchain_openai import ChatOpenAI
from logger_system import logger

def get_provider(model_name: str, api_key: str):
    """Menyediakan instance LLM dari OpenAI."""
    logger.info(f"Menginisialisasi model OpenAI: {model_name}")
    supported_models = ["gpt-5-nano", "gpt-4.1-mini", "gpt-4o-mini","o3"]
    if model_name not in supported_models:
        logger.error(f"Model OpenAI '{model_name}' tidak didukung.")
        raise ValueError(f"Model OpenAI yang didukung adalah {supported_models}")
    
    return ChatOpenAI(model=model_name, temperature=0, api_key=api_key)