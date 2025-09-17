from langchain_anthropic import ChatAnthropic

def get_provider(model_name: str):
    """Menyediakan instance LLM dari Anthropic."""
    # Contoh: "claude-3-haiku-20240307"
    return ChatAnthropic(model=model_name, temperature=0)