# from src.state.state import State

# class ChatbotWithToolNode:
#     """
#     Chatbot logic enhanced with tool integration.
#     """
#     def __init__(self,model):
#         self.llm = model

#     def process(self, state: State) -> dict:
#         """
#         Processes the input state and generates a response with tool integration.
#         """
#         user_input = state["messages"][-1] if state["messages"] else ""
#         llm_response = self.llm.invoke([{"role": "user", "content": user_input}])

#         # Simulate tool-specific logic
#         # tools_response = f"Tool integration for: '{user_input}'"
#         tools_response = {"role": "tool", "content": f"Tool integration for: '{user_input}'"}

#         return {"messages": [llm_response, tools_response]}
    

#     def create_chatbot(self, tools):
#         """
#         Returns a chatbot node function.
#         """
#         # llm_with_tools = self.llm.bind_tools(tools)
#         llm_with_tools = self.llm.get_llm_model().bind_tools(tools)        

#         def chatbot_node(state: State):
#             """
#             Chatbot logic for processing the input state and returning a response.
#             """
#             return {"messages": [llm_with_tools.invoke(state["messages"])]}

#         return chatbot_node

# File: src/nodes/chatbot_with_tool_node.py

from langchain_core.messages import SystemMessage

class ChatbotWithToolNode:
    def __init__(self, llm):
        self.llm = llm

    def create_chatbot(self, tools):
        """
        Creates a chatbot node with tool-calling capabilities.
        """
        # Bind tools to the LLM
        llm_with_tools = self.llm.get_llm_model().bind_tools(tools)
        
        def chatbot(state):
            """
            Chatbot logic with system message for better tool usage
            """
            messages = state["messages"]
            
            # Create system message to guide the chatbot
            system_message = SystemMessage(content="""You are a helpful assistant with access to tools:

1. **web_search (Tavily)**: Search the web for current information
2. **send_whatsapp_message**: Send WhatsApp messages via Twilio

IMPORTANT INSTRUCTIONS:
- When you use tools, you WILL receive the results
- After receiving tool results, acknowledge them in your response
- If send_whatsapp_message succeeds, tell the user the message was sent
- If web_search returns results, use that information in your answer
- Be conversational and helpful
- Don't say you "can't" do things if you have tools for them

Example flows:
- User: "Send Hi to +91999..." → Use tool → Respond: "I've sent the WhatsApp message successfully!"
- User: "Search weather and send to +91..." → Use web_search → Use send_whatsapp_message → Respond: "I found the weather info and sent it via WhatsApp!"
""")
            
            # Add system message only at the start of conversation
            if len(messages) == 0 or (len(messages) > 0 and not any(
                isinstance(m, SystemMessage) or (isinstance(m, dict) and m.get("role") == "system")
                for m in messages
            )):
                messages = [system_message] + list(messages)
            
            # Invoke LLM with tools
            response = llm_with_tools.invoke(messages)
            
            return {"messages": [response]}
        
        return chatbot