from .openai_client import OpenAIClient
from .others_llm_client import OtherLLMClient
from typing import Optional

def get_llm_client(provider: str = "openai", api_key: Optional[str] = None):
    if provider == "openai":
        return OpenAIClient(api_key=api_key)
    elif provider == "other":
        return OtherLLMClient(api_key=api_key)
    else: 
        raise ValueError(f"Unsupported LLM provider:{provider}")