import os 
import openai

class OpenAIClient:
    def __init__(self,api_key=None):
        self.api_key = os.getenv("API")
        openai.api_key = self.api_key
    
    def extract_desired_output(self,extracted_text):
        pass
    
        