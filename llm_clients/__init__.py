from abc import ABC,abstractmethod

class BaseLLMClient(ABC):
    @abstractmethod
    def generateJ_text(self,prompt: str,**kwargs) -> str:
        """
        Given a prompt, call the LLM and return generated text.
        Additional kwargs can be model-specific options.
        """
        pass