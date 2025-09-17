from langchain_openai import ChatOpenAI

def get_provider(model_name: str):
    """Menyediakan instance LLM dari OpenAI."""
    if model_name not in ["gpt-4-turbo", "gpt-3.5-turbo"]:
        raise ValueError("Model OpenAI yang didukung adalah 'gpt-4-turbo' atau 'gpt-3.5-turbo'")
    
    return ChatOpenAI(model=model_name, temperature=0)