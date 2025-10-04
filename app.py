# import streamlit as st
# from src.graph.graph_builder import GraphBuilder
# from src.state.state import State
# from src.LLMs.ollama_llm import LlamaOllamaLLM
# from src.LLMs.groq_llm import GroqLLM
# from langgraph.checkpoint.memory import MemorySaver

# # Page configuration
# st.set_page_config(
#     page_title="LangGraph Chatbot",
#     page_icon="🤖",
#     layout="centered"
# )

# # Initialize session state
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# if "graph" not in st.session_state:
#     st.session_state.graph = None

# if "usecase" not in st.session_state:
#     st.session_state.usecase = None

# if "llm_provider" not in st.session_state:
#     st.session_state.llm_provider = "Ollama"

# if "llm_model" not in st.session_state:
#     st.session_state.llm_model = "llama3.2:3b"

# if "groq_api_key" not in st.session_state:
#     st.session_state.groq_api_key = ""

# if "thread_id" not in st.session_state:
#     st.session_state.thread_id = "thread_1"

# if "pending_approval" not in st.session_state:
#     st.session_state.pending_approval = None

# if "checkpointer" not in st.session_state:
#     st.session_state.checkpointer = MemorySaver()

# # Sidebar for configuration
# with st.sidebar:
#     st.title("⚙️ Configuration")
    
#     # LLM Provider selection
#     llm_provider = st.selectbox(
#         "Select LLM Provider",
#         ["Ollama", "Groq"],
#         help="Choose between Ollama (local) or Groq (API)"
#     )
    
#     # Provider-specific configuration
#     if llm_provider == "Ollama":
#         model_name = st.text_input(
#             "Ollama Model Name",
#             value="llama3.2:3b" if llm_provider != st.session_state.llm_provider else st.session_state.llm_model,
#             help="Enter the Ollama model name (e.g., llama3.2:3b, llama3.1:8b)"
#         )
#         groq_api_key = None
#     else:  # Groq
#         groq_api_key = st.text_input(
#             "Groq API Key",
#             value=st.session_state.groq_api_key,
#             type="password",
#             help="Enter your Groq API key from console.groq.com"
#         )
#         model_name = st.selectbox(
#             "Groq Model",
#             ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it","openai/gpt-oss-120b"],
#             help="Select a Groq model"
#         )
    
#     # Use case selection
#     usecase = st.selectbox(
#         "Select Chatbot Mode",
#         ["Basic Chatbot", "Chatbot With Web"],
#         help="Choose between basic chat or web-enabled chatbot"
#     )
    
#     # Initialize button
#     if st.button("Initialize Chatbot", type="primary"):
#         try:
#             if llm_provider == "Groq" and not groq_api_key:
#                 st.error("❌ Please enter your Groq API key")
#             else:
#                 with st.spinner(f"Loading {llm_provider} model and building graph..."):
#                     if llm_provider == "Ollama":
#                         llm = LlamaOllamaLLM(model_name)
#                     else:
#                         llm = GroqLLM(model_name, groq_api_key)
                    
#                     builder = GraphBuilder(llm)
#                     graph = builder.setup_graph(usecase, st.session_state.checkpointer)
                    
#                     st.session_state.graph = graph
#                     st.session_state.usecase = usecase
#                     st.session_state.llm_provider = llm_provider
#                     st.session_state.llm_model = model_name
#                     if groq_api_key:
#                         st.session_state.groq_api_key = groq_api_key
                    
#                     st.success(f"✅ {usecase} initialized successfully with {llm_provider}!")
#         except Exception as e:
#             st.error(f"❌ Error initializing chatbot: {str(e)}")
#             st.exception(e)
    
#     # Display current status
#     st.divider()
#     if st.session_state.graph is not None:
#         st.success(f"**Status:** Active")
#         st.info(f"**Provider:** {st.session_state.llm_provider}")
#         st.info(f"**Mode:** {st.session_state.usecase}")
#         st.info(f"**Model:** {st.session_state.llm_model}")
#     else:
#         st.warning("**Status:** Not initialized")
    
#     # Clear chat button
#     st.divider()
#     if st.button("Clear Chat History"):
#         st.session_state.messages = []
#         st.session_state.pending_approval = None
#         st.rerun()

# # Main chat interface
# st.title("🤖 LangGraph Chatbot with Human-in-the-Loop")
# st.caption("A conversational AI with human approval for sensitive actions")

# # Check if graph is initialized
# if st.session_state.graph is None:
#     st.info("👈 Please initialize the chatbot using the sidebar configuration.")
# else:
#     # Display pending approval UI
#     if st.session_state.pending_approval is not None:
#         st.warning("⏸️ **Action Pending Approval**")
        
#         approval_data = st.session_state.pending_approval
        
#         with st.container():
#             st.markdown("### 📋 Requested Action")
#             st.json(approval_data["tool_call"])
            
#             col1, col2 = st.columns(2)
            
#             with col1:
#                 if st.button("✅ Approve", type="primary", use_container_width=True):
#                     try:
#                         # Continue the graph with approval
#                         config = {"configurable": {"thread_id": st.session_state.thread_id}}
                        
#                         # Update state to continue
#                         result_state = st.session_state.graph.invoke(None, config)
                        
#                         # Extract response
#                         if result_state["messages"]:
#                             assistant_messages = [
#                                 msg for msg in result_state["messages"] 
#                                 if (isinstance(msg, dict) and msg.get("role") == "assistant") or 
#                                    (hasattr(msg, "type") and msg.type == "ai")
#                             ]
                            
#                             if assistant_messages:
#                                 last_msg = assistant_messages[-1]
                                
#                                 if isinstance(last_msg, dict):
#                                     bot_response = last_msg.get("content", "")
#                                 elif hasattr(last_msg, "content"):
#                                     bot_response = last_msg.content
#                                 else:
#                                     bot_response = str(last_msg)
                                
#                                 st.session_state.messages.append({
#                                     "role": "assistant",
#                                     "content": bot_response
#                                 })
                        
#                         st.session_state.pending_approval = None
#                         st.rerun()
                        
#                     except Exception as e:
#                         st.error(f"Error executing approved action: {str(e)}")
            
#             with col2:
#                 if st.button("❌ Reject", type="secondary", use_container_width=True):
#                     # Update state to reject
#                     config = {"configurable": {"thread_id": st.session_state.thread_id}}
                    
#                     # Update graph with rejection
#                     st.session_state.graph.update_state(
#                         config,
#                         {"messages": [{"role": "assistant", "content": "Action was rejected by user."}]}
#                     )
                    
#                     st.session_state.messages.append({
#                         "role": "assistant",
#                         "content": "❌ Action rejected. How else can I help you?"
#                     })
                    
#                     st.session_state.pending_approval = None
#                     st.rerun()
    
#     # Display chat messages
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])
    
#     # Chat input (disabled if pending approval)
#     if prompt := st.chat_input(
#         "Type your message here...",
#         disabled=st.session_state.pending_approval is not None
#     ):
#         st.session_state.messages.append({"role": "user", "content": prompt})
        
#         with st.chat_message("user"):
#             st.markdown(prompt)
        
#         with st.chat_message("assistant"):
#             message_placeholder = st.empty()
            
#             try:
#                 with st.spinner("Thinking..."):
#                     state = {"messages": st.session_state.messages.copy()}
#                     config = {"configurable": {"thread_id": st.session_state.thread_id}}
                    
#                     # Stream through the graph
#                     for event in st.session_state.graph.stream(state, config, stream_mode="values"):
#                         pass
                    
#                     # Check if we hit an interrupt (human-in-the-loop)
#                     snapshot = st.session_state.graph.get_state(config)
                    
#                     if snapshot.next:  # There are pending nodes
#                         # Check if it's waiting for approval
#                         last_message = snapshot.values["messages"][-1]
                        
#                         if hasattr(last_message, "tool_calls") and last_message.tool_calls:
#                             # Store pending approval
#                             st.session_state.pending_approval = {
#                                 "tool_call": {
#                                     "name": last_message.tool_calls[0]["name"],
#                                     "args": last_message.tool_calls[0]["args"]
#                                 }
#                             }
#                             message_placeholder.info("⏸️ Action requires approval. Please review above.")
#                             st.rerun()
#                         else:
#                             # Normal completion
#                             result_state = snapshot.values
                            
#                             if result_state["messages"]:
#                                 assistant_messages = [
#                                     msg for msg in result_state["messages"] 
#                                     if (isinstance(msg, dict) and msg.get("role") == "assistant") or 
#                                        (hasattr(msg, "type") and msg.type == "ai")
#                                 ]
                                
#                                 if assistant_messages:
#                                     last_msg = assistant_messages[-1]
                                    
#                                     if isinstance(last_msg, dict):
#                                         bot_response = last_msg.get("content", "")
#                                     elif hasattr(last_msg, "content"):
#                                         bot_response = last_msg.content
#                                     else:
#                                         bot_response = str(last_msg)
                                    
#                                     message_placeholder.markdown(bot_response)
                                    
#                                     st.session_state.messages.append({
#                                         "role": "assistant",
#                                         "content": bot_response
#                                     })
#                     else:
#                         # Graph completed normally
#                         result_state = snapshot.values
                        
#                         if result_state["messages"]:
#                             assistant_messages = [
#                                 msg for msg in result_state["messages"] 
#                                 if (isinstance(msg, dict) and msg.get("role") == "assistant") or 
#                                    (hasattr(msg, "type") and msg.type == "ai")
#                             ]
                            
#                             if assistant_messages:
#                                 last_msg = assistant_messages[-1]
                                
#                                 if isinstance(last_msg, dict):
#                                     bot_response = last_msg.get("content", "")
#                                 elif hasattr(last_msg, "content"):
#                                     bot_response = last_msg.content
#                                 else:
#                                     bot_response = str(last_msg)
                                
#                                 message_placeholder.markdown(bot_response)
                                
#                                 st.session_state.messages.append({
#                                     "role": "assistant",
#                                     "content": bot_response
#                                 })
                    
#             except Exception as e:
#                 message_placeholder.error(f"Error: {str(e)}")
#                 st.exception(e)

# st.divider()
# st.caption("Built with Streamlit, LangGraph, Ollama, and Groq | Human-in-the-Loop Enabled")
# import streamlit as st
# from src.graph.graph_builder import GraphBuilder
# from src.state.state import State
# from src.LLMs.ollama_llm import LlamaOllamaLLM
# from src.LLMs.groq_llm import GroqLLM
# from langgraph.checkpoint.memory import MemorySaver

# # Page configuration
# st.set_page_config(
#     page_title="LangGraph Chatbot",
#     page_icon="🤖",
#     layout="centered"
# )

# # Initialize session state
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# if "graph" not in st.session_state:
#     st.session_state.graph = None

# if "usecase" not in st.session_state:
#     st.session_state.usecase = None

# if "llm_provider" not in st.session_state:
#     st.session_state.llm_provider = "Ollama"

# if "llm_model" not in st.session_state:
#     st.session_state.llm_model = "llama3.2:3b"

# if "groq_api_key" not in st.session_state:
#     st.session_state.groq_api_key = ""

# if "thread_id" not in st.session_state:
#     st.session_state.thread_id = "thread_1"

# if "pending_approval" not in st.session_state:
#     st.session_state.pending_approval = None

# if "checkpointer" not in st.session_state:
#     st.session_state.checkpointer = MemorySaver()

# # Sidebar for configuration
# with st.sidebar:
#     st.title("⚙️ Configuration")
    
#     # LLM Provider selection
#     llm_provider = st.selectbox(
#         "Select LLM Provider",
#         ["Ollama", "Groq"],
#         help="Choose between Ollama (local) or Groq (API)"
#     )
    
#     # Provider-specific configuration
#     if llm_provider == "Ollama":
#         model_name = st.text_input(
#             "Ollama Model Name",
#             value="llama3.2:3b" if llm_provider != st.session_state.llm_provider else st.session_state.llm_model,
#             help="Enter the Ollama model name (e.g., llama3.2:3b, llama3.1:8b)"
#         )
#         groq_api_key = None
#     else:  # Groq
#         groq_api_key = st.text_input(
#             "Groq API Key",
#             value=st.session_state.groq_api_key,
#             type="password",
#             help="Enter your Groq API key from console.groq.com"
#         )
#         model_name = st.selectbox(
#             "Groq Model",
#             ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it","openai/gpt-oss-120b"],
#             help="Select a Groq model"
#         )
    
#     # Use case selection
#     usecase = st.selectbox(
#         "Select Chatbot Mode",
#         ["Basic Chatbot", "Chatbot With Web"],
#         help="Choose between basic chat or web-enabled chatbot"
#     )
    
#     # Initialize button
#     if st.button("Initialize Chatbot", type="primary"):
#         try:
#             if llm_provider == "Groq" and not groq_api_key:
#                 st.error("❌ Please enter your Groq API key")
#             else:
#                 with st.spinner(f"Loading {llm_provider} model and building graph..."):
#                     if llm_provider == "Ollama":
#                         llm = LlamaOllamaLLM(model_name)
#                     else:
#                         llm = GroqLLM(model_name, groq_api_key)
                    
#                     builder = GraphBuilder(llm)
#                     graph = builder.setup_graph(usecase, st.session_state.checkpointer)
                    
#                     st.session_state.graph = graph
#                     st.session_state.usecase = usecase
#                     st.session_state.llm_provider = llm_provider
#                     st.session_state.llm_model = model_name
#                     if groq_api_key:
#                         st.session_state.groq_api_key = groq_api_key
                    
#                     st.success(f"✅ {usecase} initialized successfully with {llm_provider}!")
#         except Exception as e:
#             st.error(f"❌ Error initializing chatbot: {str(e)}")
#             st.exception(e)
    
#     # Display current status
#     st.divider()
#     if st.session_state.graph is not None:
#         st.success(f"**Status:** Active")
#         st.info(f"**Provider:** {st.session_state.llm_provider}")
#         st.info(f"**Mode:** {st.session_state.usecase}")
#         st.info(f"**Model:** {st.session_state.llm_model}")
#     else:
#         st.warning("**Status:** Not initialized")
    
#     # Clear chat button
#     st.divider()
#     if st.button("Clear Chat History"):
#         st.session_state.messages = []
#         st.session_state.pending_approval = None
#         st.rerun()

# # Main chat interface
# st.title("🤖 LangGraph Chatbot with Selective HITL")
# st.caption("WhatsApp messages require approval • Web searches auto-execute")

# # Check if graph is initialized
# if st.session_state.graph is None:
#     st.info("👈 Please initialize the chatbot using the sidebar configuration.")
# else:
#     # Display pending approval UI
#     if st.session_state.pending_approval is not None:
#         st.warning("⏸️ **WhatsApp Message Pending Approval**")
        
#         approval_data = st.session_state.pending_approval
        
#         with st.container():
#             st.markdown("### 📱 WhatsApp Message Details")
#             st.json(approval_data["tool_call"])
            
#             col1, col2 = st.columns(2)
            
#             with col1:
#                 if st.button("✅ Approve & Send", type="primary", use_container_width=True):
#                     try:
#                         config = {"configurable": {"thread_id": st.session_state.thread_id}}
                        
#                         # Continue the graph execution (will execute the tool)
#                         for event in st.session_state.graph.stream(None, config, stream_mode="values"):
#                             pass
                        
#                         # Get final state
#                         snapshot = st.session_state.graph.get_state(config)
#                         result_state = snapshot.values
                        
#                         # Extract the final assistant response
#                         if result_state["messages"]:
#                             assistant_messages = [
#                                 msg for msg in result_state["messages"] 
#                                 if (isinstance(msg, dict) and msg.get("role") == "assistant") or 
#                                    (hasattr(msg, "type") and msg.type == "ai")
#                             ]
                            
#                             if assistant_messages:
#                                 # Get the last message that's not a tool call
#                                 for msg in reversed(assistant_messages):
#                                     if isinstance(msg, dict):
#                                         content = msg.get("content", "")
#                                     elif hasattr(msg, "content"):
#                                         content = msg.content
#                                     else:
#                                         content = str(msg)
                                    
#                                     # Skip empty or tool-only messages
#                                     if content and not (hasattr(msg, "tool_calls") and msg.tool_calls and not content):
#                                         st.session_state.messages.append({
#                                             "role": "assistant",
#                                             "content": content
#                                         })
#                                         break
                        
#                         st.session_state.pending_approval = None
#                         st.success("✅ Message sent successfully!")
#                         st.rerun()
                        
#                     except Exception as e:
#                         st.error(f"Error executing approved action: {str(e)}")
#                         st.exception(e)
            
#             with col2:
#                 if st.button("❌ Reject", type="secondary", use_container_width=True):
#                     try:
#                         config = {"configurable": {"thread_id": st.session_state.thread_id}}
                        
#                         # Update state to indicate rejection
#                         from langchain_core.messages import AIMessage
                        
#                         st.session_state.graph.update_state(
#                             config,
#                             {"messages": [AIMessage(content="❌ WhatsApp message was not sent (rejected by user). How else can I help you?")]},
#                             as_node="chatbot"
#                         )
                        
#                         st.session_state.messages.append({
#                             "role": "assistant",
#                             "content": "❌ WhatsApp message was not sent (rejected by user). How else can I help you?"
#                         })
                        
#                         st.session_state.pending_approval = None
#                         st.rerun()
                        
#                     except Exception as e:
#                         st.error(f"Error rejecting action: {str(e)}")
#                         st.exception(e)
    
#     # Display chat messages
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])
    
#     # Chat input (disabled if pending approval)
#     if prompt := st.chat_input(
#         "Type your message here...",
#         disabled=st.session_state.pending_approval is not None
#     ):
#         st.session_state.messages.append({"role": "user", "content": prompt})
        
#         with st.chat_message("user"):
#             st.markdown(prompt)
        
#         with st.chat_message("assistant"):
#             message_placeholder = st.empty()
            
#             try:
#                 with st.spinner("Thinking..."):
#                     state = {"messages": st.session_state.messages.copy()}
#                     config = {"configurable": {"thread_id": st.session_state.thread_id}}
                    
#                     # Stream through the graph
#                     final_state = None
#                     for event in st.session_state.graph.stream(state, config, stream_mode="values"):
#                         final_state = event
                    
#                     # Check if we hit an interrupt (human-in-the-loop)
#                     snapshot = st.session_state.graph.get_state(config)
                    
#                     # Check if graph is waiting at human_approval node
#                     if snapshot.next and "human_approval" in snapshot.next:
#                         # Extract tool call details from the last message
#                         last_message = snapshot.values["messages"][-1]
                        
#                         if hasattr(last_message, "tool_calls") and last_message.tool_calls:
#                             tool_call = last_message.tool_calls[0]
                            
#                             # Store pending approval
#                             st.session_state.pending_approval = {
#                                 "tool_call": {
#                                     "name": tool_call["name"],
#                                     "args": tool_call["args"]
#                                 }
#                             }
#                             message_placeholder.info("⏸️ WhatsApp message requires approval. Please review above.")
#                             st.rerun()
#                     else:
#                         # Graph completed normally (no interrupt)
#                         result_state = snapshot.values
                        
#                         if result_state["messages"]:
#                             assistant_messages = [
#                                 msg for msg in result_state["messages"] 
#                                 if (isinstance(msg, dict) and msg.get("role") == "assistant") or 
#                                    (hasattr(msg, "type") and msg.type == "ai")
#                             ]
                            
#                             if assistant_messages:
#                                 # Get the last meaningful message
#                                 for msg in reversed(assistant_messages):
#                                     if isinstance(msg, dict):
#                                         bot_response = msg.get("content", "")
#                                     elif hasattr(msg, "content"):
#                                         bot_response = msg.content
#                                     else:
#                                         bot_response = str(msg)
                                    
#                                     # Skip empty messages or messages with only tool calls
#                                     if bot_response and not (hasattr(msg, "tool_calls") and msg.tool_calls and not bot_response):
#                                         message_placeholder.markdown(bot_response)
                                        
#                                         st.session_state.messages.append({
#                                             "role": "assistant",
#                                             "content": bot_response
#                                         })
#                                         break
#                             else:
#                                 message_placeholder.info("Processing...")
#                         else:
#                             message_placeholder.error("No response generated.")
                    
#             except Exception as e:
#                 message_placeholder.error(f"Error: {str(e)}")
#                 st.exception(e)

# st.divider()
# st.caption("Built with Streamlit, LangGraph, Ollama, and Groq | Selective HITL Enabled 🔒")

import streamlit as st
from src.graph.graph_builder import GraphBuilder
from src.state.state import State
from src.LLMs.ollama_llm import LlamaOllamaLLM
from src.LLMs.groq_llm import GroqLLM
from langgraph.checkpoint.memory import MemorySaver

# Page configuration
st.set_page_config(
    page_title="LangGraph Chatbot",
    page_icon="🤖",
    layout="centered"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "graph" not in st.session_state:
    st.session_state.graph = None

if "usecase" not in st.session_state:
    st.session_state.usecase = None

if "llm_provider" not in st.session_state:
    st.session_state.llm_provider = "Ollama"

if "llm_model" not in st.session_state:
    st.session_state.llm_model = "llama3.2:3b"

if "groq_api_key" not in st.session_state:
    st.session_state.groq_api_key = ""

if "thread_id" not in st.session_state:
    st.session_state.thread_id = "thread_1"

if "pending_approval" not in st.session_state:
    st.session_state.pending_approval = None

if "checkpointer" not in st.session_state:
    st.session_state.checkpointer = MemorySaver()

# Sidebar for configuration
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # LLM Provider selection
    llm_provider = st.selectbox(
        "Select LLM Provider",
        ["Ollama", "Groq"],
        help="Choose between Ollama (local) or Groq (API)"
    )
    
    # Provider-specific configuration
    if llm_provider == "Ollama":
        model_name = st.text_input(
            "Ollama Model Name",
            value="llama3.2:3b" if llm_provider != st.session_state.llm_provider else st.session_state.llm_model,
            help="Enter the Ollama model name (e.g., llama3.2:3b, llama3.1:8b)"
        )
        groq_api_key = None
    else:  # Groq
        groq_api_key = st.text_input(
            "Groq API Key",
            value=st.session_state.groq_api_key,
            type="password",
            help="Enter your Groq API key from console.groq.com"
        )
        model_name = st.selectbox(
            "Groq Model",
            ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it","openai/gpt-oss-120b","openai/gpt-oss-20b"],
            help="Select a Groq model"
        )
    
    # Use case selection
    usecase = st.selectbox(
        "Select Chatbot Mode",
        ["Basic Chatbot", "Chatbot With Web"],
        help="Choose between basic chat or web-enabled chatbot"
    )
    
    # Initialize button
    if st.button("Initialize Chatbot", type="primary"):
        try:
            if llm_provider == "Groq" and not groq_api_key:
                st.error("❌ Please enter your Groq API key")
            else:
                with st.spinner(f"Loading {llm_provider} model and building graph..."):
                    if llm_provider == "Ollama":
                        llm = LlamaOllamaLLM(model_name)
                    else:
                        llm = GroqLLM(model_name, groq_api_key)
                    
                    builder = GraphBuilder(llm)
                    graph = builder.setup_graph(usecase, st.session_state.checkpointer)
                    
                    st.session_state.graph = graph
                    st.session_state.usecase = usecase
                    st.session_state.llm_provider = llm_provider
                    st.session_state.llm_model = model_name
                    if groq_api_key:
                        st.session_state.groq_api_key = groq_api_key
                    
                    st.success(f"✅ {usecase} initialized successfully with {llm_provider}!")
        except Exception as e:
            st.error(f"❌ Error initializing chatbot: {str(e)}")
            st.exception(e)
    
    # Display current status
    st.divider()
    if st.session_state.graph is not None:
        st.success(f"**Status:** Active")
        st.info(f"**Provider:** {st.session_state.llm_provider}")
        st.info(f"**Mode:** {st.session_state.usecase}")
        st.info(f"**Model:** {st.session_state.llm_model}")
    else:
        st.warning("**Status:** Not initialized")
    
    # Clear chat button
    st.divider()
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.pending_approval = None
        st.rerun()

# Main chat interface
st.title("🤖 LangGraph Chatbot with Selective HITL")
st.caption("WhatsApp messages require approval • Web searches auto-execute")

# Check if graph is initialized
if st.session_state.graph is None:
    st.info("👈 Please initialize the chatbot using the sidebar configuration.")
else:
    # Display chat messages
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
        
        # Show approval UI right after the user message that triggered it
        if (st.session_state.pending_approval is not None and 
            message["role"] == "user" and 
            idx == len(st.session_state.messages) - 1):
            
            approval_data = st.session_state.pending_approval
            
            # Display approval prompt in assistant's chat bubble
            with st.chat_message("assistant"):
                st.warning("⏸️ **WhatsApp Message Pending Approval**")
                
                st.markdown("### 📱 Message Details")
                st.json(approval_data["tool_call"])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✅ Approve & Send", type="primary", use_container_width=True, key="approve_btn"):
                        try:
                            config = {"configurable": {"thread_id": st.session_state.thread_id}}
                            
                            # Continue the graph execution (will execute the tool)
                            for event in st.session_state.graph.stream(None, config, stream_mode="values"):
                                pass
                            
                            # Get final state
                            snapshot = st.session_state.graph.get_state(config)
                            result_state = snapshot.values
                            
                            # Extract the final assistant response
                            if result_state["messages"]:
                                assistant_messages = [
                                    msg for msg in result_state["messages"] 
                                    if (isinstance(msg, dict) and msg.get("role") == "assistant") or 
                                       (hasattr(msg, "type") and msg.type == "ai")
                                ]
                                
                                if assistant_messages:
                                    # Get the last message that's not a tool call
                                    for msg in reversed(assistant_messages):
                                        if isinstance(msg, dict):
                                            content = msg.get("content", "")
                                        elif hasattr(msg, "content"):
                                            content = msg.content
                                        else:
                                            content = str(msg)
                                        
                                        # Skip empty or tool-only messages
                                        if content and not (hasattr(msg, "tool_calls") and msg.tool_calls and not content):
                                            st.session_state.messages.append({
                                                "role": "assistant",
                                                "content": content
                                            })
                                            break
                            
                            st.session_state.pending_approval = None
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error executing approved action: {str(e)}")
                            st.exception(e)
                
                with col2:
                    if st.button("❌ Reject", type="secondary", use_container_width=True, key="reject_btn"):
                        try:
                            config = {"configurable": {"thread_id": st.session_state.thread_id}}
                            
                            # Update state to indicate rejection
                            from langchain_core.messages import AIMessage
                            
                            st.session_state.graph.update_state(
                                config,
                                {"messages": [AIMessage(content="❌ WhatsApp message was not sent (rejected by user). How else can I help you?")]},
                                as_node="chatbot"
                            )
                            
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": "❌ WhatsApp message was not sent (rejected by user). How else can I help you?"
                            })
                            
                            st.session_state.pending_approval = None
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error rejecting action: {str(e)}")
                            st.exception(e)
    
    # Chat input (disabled if pending approval)
    if prompt := st.chat_input(
        "Type your message here..." if st.session_state.pending_approval is None else "⏸️ Please approve or reject the pending action first",
        disabled=st.session_state.pending_approval is not None
    ):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            try:
                with st.spinner("Thinking..."):
                    state = {"messages": st.session_state.messages.copy()}
                    config = {"configurable": {"thread_id": st.session_state.thread_id}}
                    
                    # Stream through the graph
                    final_state = None
                    for event in st.session_state.graph.stream(state, config, stream_mode="values"):
                        final_state = event
                    
                    # Check if we hit an interrupt (human-in-the-loop)
                    snapshot = st.session_state.graph.get_state(config)
                    
                    # Check if graph is waiting at human_approval node
                    if snapshot.next and "human_approval" in snapshot.next:
                        # Extract tool call details from the last message
                        last_message = snapshot.values["messages"][-1]
                        
                        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                            tool_call = last_message.tool_calls[0]
                            
                            # Store pending approval
                            st.session_state.pending_approval = {
                                "tool_call": {
                                    "name": tool_call["name"],
                                    "args": tool_call["args"]
                                }
                            }
                            message_placeholder.empty()  # Clear the placeholder
                            st.rerun()
                    else:
                        # Graph completed normally (no interrupt)
                        result_state = snapshot.values
                        
                        if result_state["messages"]:
                            assistant_messages = [
                                msg for msg in result_state["messages"] 
                                if (isinstance(msg, dict) and msg.get("role") == "assistant") or 
                                   (hasattr(msg, "type") and msg.type == "ai")
                            ]
                            
                            if assistant_messages:
                                # Get the last meaningful message
                                for msg in reversed(assistant_messages):
                                    if isinstance(msg, dict):
                                        bot_response = msg.get("content", "")
                                    elif hasattr(msg, "content"):
                                        bot_response = msg.content
                                    else:
                                        bot_response = str(msg)
                                    
                                    # Skip empty messages or messages with only tool calls
                                    if bot_response and not (hasattr(msg, "tool_calls") and msg.tool_calls and not bot_response):
                                        message_placeholder.markdown(bot_response)
                                        
                                        st.session_state.messages.append({
                                            "role": "assistant",
                                            "content": bot_response
                                        })
                                        break
                            else:
                                message_placeholder.info("Processing...")
                        else:
                            message_placeholder.error("No response generated.")
                    
            except Exception as e:
                message_placeholder.error(f"Error: {str(e)}")
                st.exception(e)

st.divider()
st.caption("Built with Streamlit, LangGraph, Ollama, and Groq | Selective HITL Enabled 🔒")