from llm_clients.openai_cliant import OpenAIClient

LLM_PROVIDER = "openai"

def get_llm_client():
    if LLM_PROVIDER == "openai":
        return OpenAIClient()
    # elif LLM_PROVIDER == "other_llm":
    #    return OtherLLMClient()
    else: 
        raise Exception("Unsupported LLM provider")

def extract_menu_from_text(extracted_text):
    client = get_llm_client()
    return client.extract_desired_output(extracted_text)