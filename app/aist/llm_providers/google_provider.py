from langchain_google_genai import ChatGoogleGenerativeAI

def get_provider(model_name: str):
    """Menyediakan instance LLM dari Google."""
    # Contoh: "gemini-1.5-flash-latest"
    return ChatGoogleGenerativeAI(model=model_name, temperature=0)