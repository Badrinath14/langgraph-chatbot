from langchain_groq import ChatGroq

class GroqLLM:
    def __init__(self, model_name: str = "llama-3.3-70b-versatile", api_key: str = None):
        """
        Initialize with a Groq model name and API key.
        
        Args:
            model_name: Groq model name (e.g., llama-3.3-70b-versatile, mixtral-8x7b-32768)
            api_key: Groq API key from console.groq.com
        """
        self.model_name = model_name
        self.api_key = api_key
    
    def invoke(self, messages):
        """
        Generate a response from the LLM using the provided messages.
        
        Args:
            messages: List of message objects or dicts with 'role' and 'content'.
        
        Returns:
            Response from the LLM
        """
        llm = self.get_llm_model()
        response = llm.invoke(messages)
        return response

    def get_llm_model(self):
        """
        Returns the ChatGroq model instance.
        
        Returns:
            ChatGroq: Configured Groq model
        
        Raises:
            Exception: If model loading fails
        """
        try:
            return ChatGroq(
                model=self.model_name,
                api_key=self.api_key,
                temperature=0.7,
                max_tokens=1024
            )
        except Exception as e:
            raise Exception(f"Error occurred while loading Groq model '{self.model_name}': {e}")