# File: src/LLMs/ollama_llm.py

from langchain_ollama import ChatOllama

class LlamaOllamaLLM:
    def __init__(self, model_name: str = "llama3.1:8b"):
        """
        Initialize with a model name. Default is 'llama3.1:8b'.
        Make sure you have pulled the model with `ollama pull llama3`.
        """
        self.model_name = model_name    
    
    def invoke(self, messages):
        """
        Generate a response from the LLM using the provided messages.
        messages: List of message objects or dicts with 'role' and 'content'.
        """
        llm = self.get_llm_model()
        
        # ChatOllama can handle message lists directly
        # Just pass the messages as-is
        response = llm.invoke(messages)
        return response

    def get_llm_model(self):
        try:
            return ChatOllama(model=self.model_name)
        except Exception as e:
            raise Exception(f"Error occurred while loading Ollama model '{self.model_name}': {e}")