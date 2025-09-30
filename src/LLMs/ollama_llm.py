# from langchain_ollama import ChatOllama

# class LlamaOllamaLLM:
#     def __init__(self, model_name: str = "llama3.1:8b"):
#         """
#         Initialize with a model name. Default is 'llama3'.
#         Make sure you have pulled the model with `ollama pull llama3`.
#         """
#         self.model_name = model_name    
#     def invoke(self, messages):
#         """
#         Generate a response from the LLM using the provided messages.
#         messages: List of dicts with 'role' and 'content'.
#         """
#         llm = self.get_llm_model()
#         # Convert messages to the format expected by ChatOllama
#         # If ChatOllama expects a string, use the last user message
#         if isinstance(messages, list) and messages:
#             last_msg = messages[-1]
#             if isinstance(last_msg, dict):
#                 prompt = last_msg.get("content", "")
#             elif hasattr(last_msg, "content"):
#                 prompt = last_msg.content
#             else:
#                 prompt = str(last_msg)
#         else:
#             prompt = ""
#         response = llm.invoke(prompt)
#         return response


#     def get_llm_model(self):
#         try:
#             return ChatOllama(model=self.model_name)
#         except Exception as e:
#             raise Exception(f"Error occurred while loading Ollama model '{self.model_name}': {e}")
        
# # if __name__ == "__main__":
# #     ollama_llm = LlamaOllamaLLM(model_name="llama3.1:8b")
# #     llm_model = ollama_llm.get_llm_model()
# #     print(f"Ollama model '{ollama_llm.model_name}' loaded successfully.")
# from langchain_ollama import ChatOllama
# from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# class LlamaOllamaLLM:
#     def __init__(self, model_name: str = "llama3.2:3b"):
#         self.model_name = model_name
    
#     def invoke(self, messages):
#         """
#         Generate a response from the LLM using the provided messages.
#         messages: List of dicts with 'role' and 'content'.
#         """
#         llm = self.get_llm_model()
        
#         # Convert messages to LangChain message format
#         lc_messages = []
#         for msg in messages:
#             if isinstance(msg, dict):
#                 role = msg.get("role", "")
#                 content = msg.get("content", "")
#                 if role == "user":
#                     lc_messages.append(HumanMessage(content=content))
#                 elif role == "assistant":
#                     lc_messages.append(AIMessage(content=content))
#                 elif role == "system":
#                     lc_messages.append(SystemMessage(content=content))
#             else:
#                 # If it's already a LangChain message type
#                 lc_messages.append(msg)
        
#         response = llm.invoke(lc_messages)
#         return response

#     def get_llm_model(self):
#         try:
#             return ChatOllama(
#                 model=self.model_name,
#                 temperature=0.7,
#                 # stream=True  # Enable streaming for better UX
#             )
#         except Exception as e:
#             raise Exception(f"Error occurred while loading Ollama model '{self.model_name}': {e}")


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