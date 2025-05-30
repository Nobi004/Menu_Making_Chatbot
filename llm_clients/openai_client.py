import os 
from openai import OpenAI , OpenAIError

class OpenAIClient:
    from typing import Optional

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("API")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def generate_text(self,prompt:str, **kwargs) ->str:
        try: 
            response = self.client.chat.completions.create(
                model=kwargs.get("model", "gpt-4"),
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return response.choices[0].message.content.strip()
        except OpenAIError as e :
            raise RuntimeError(f"OpenAI API error: {e}")
        
        
    
        