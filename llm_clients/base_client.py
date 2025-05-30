from abc import ABC ,abstractmethod

class BaseLLMClient(ABC):
    @abstractmethod
    def process_menu_text(ABC):
        
       """
        Send the extracted menu text to the LLM, get structured info back.
        Return a dict representing the structured menu data, e.g. list of items with name, quantity, price, group etc.
        """
    pass 