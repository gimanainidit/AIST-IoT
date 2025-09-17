# llm_providers/__init__.py

from . import openai_provider

def get_llm_instance(llm_choice: str):
    """
    Factory yang disederhanakan untuk fase pengujian. Hanya mendukung OpenAI.
    Format pilihan: 'openai:model_name'
    Contoh: 'openai:gpt-4o-mini'
    """
    try:
        provider, model_name = llm_choice.lower().split(":", 1)
    except ValueError:
        raise ValueError(f"Format LLM choice tidak valid: '{llm_choice}'. Gunakan format 'provider:model_name'.")

    if provider != "openai":
        raise ValueError(f"Pengujian saat ini hanya mendukung provider 'openai', bukan '{provider}'.")

    # Langsung memanggil provider OpenAI
    return openai_provider.get_provider(model_name)
# # Kode sebelumnya yang mendukung banyak provider telah dikomentari untuk penyederhanaan
# from . import openai_provider, google_provider, anthropic_provider, ollama_provider

# # Mapping dari nama umum ke fungsi provider yang sesuai
# PROVIDER_MAP = {
#     "openai": openai_provider.get_provider,
#     "google": google_provider.get_provider,
#     "anthropic": anthropic_provider.get_provider,
#     "ollama": ollama_provider.get_provider,
# }

# def get_llm_instance(llm_choice: str):
#     """
#     Factory utama untuk mendapatkan instance LLM berdasarkan pilihan.
#     Format pilihan: 'provider:model_name'
#     Contoh: 'openai:gpt-4-turbo', 'ollama:llama3', 'google:gemini-1.5-flash-latest'
#     """
#     try:
#         provider, model_name = llm_choice.lower().split(":", 1)
#     except ValueError:
#         raise ValueError(f"Format LLM choice tidak valid: '{llm_choice}'. Gunakan format 'provider:model_name'.")

#     if provider not in PROVIDER_MAP:
#         raise ValueError(f"Provider '{provider}' tidak dikenal. Pilihan yang tersedia: {list(PROVIDER_MAP.keys())}")

#     # Memanggil fungsi get_provider yang sesuai dari mapping
#     return PROVIDER_MAP[provider](model_name)