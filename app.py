# import streamlit as st
# from src.graph.graph_builder import GraphBuilder
# from src.state.state import State
# from src.LLMs.ollama_llm import LlamaOllamaLLM

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

# if "llm_model" not in st.session_state:
#     st.session_state.llm_model = "llama3.2:3b"

# # Sidebar for configuration
# with st.sidebar:
#     st.title("⚙️ Configuration")
    
#     # Model selection
#     model_name = st.text_input(
#         "Ollama Model Name",
#         value=st.session_state.llm_model,
#         help="Enter the Ollama model name (e.g., llama3.2:3b, llama3.1:8b)"
#     )
    
#     # Use case selection
#     usecase = st.selectbox(
#         "Select Chatbot Mode",
#         ["Basic Chatbot", "Chatbot With Web"],
#         help="Choose between basic chat or web-enabled chatbot"
#     )
    
#     # Initialize button
#     if st.button("Initialize Chatbot", type="primary"):
#         try:
#             with st.spinner("Loading model and building graph..."):
#                 # Load LLM
#                 llm = LlamaOllamaLLM(model_name)
                
#                 # Build graph
#                 builder = GraphBuilder(llm)
#                 graph = builder.setup_graph(usecase)
                
#                 # Store in session state
#                 st.session_state.graph = graph
#                 st.session_state.usecase = usecase
#                 st.session_state.llm_model = model_name
                
#                 st.success(f"✅ {usecase} initialized successfully!")
#         except Exception as e:
#             st.error(f"❌ Error initializing chatbot: {str(e)}")
    
#     # Display current status
#     st.divider()
#     if st.session_state.graph is not None:
#         st.success(f"**Status:** Active")
#         st.info(f"**Mode:** {st.session_state.usecase}")
#         st.info(f"**Model:** {st.session_state.llm_model}")
#     else:
#         st.warning("**Status:** Not initialized")
    
#     # Clear chat button
#     st.divider()
#     if st.button("Clear Chat History"):
#         st.session_state.messages = []
#         st.rerun()

# # Main chat interface
# st.title("🤖 LangGraph Chatbot")
# st.caption("A conversational AI powered by LangGraph and Ollama")

# # Check if graph is initialized
# if st.session_state.graph is None:
#     st.info("👈 Please initialize the chatbot using the sidebar configuration.")
# else:
#     # Display chat messages
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])
    
#     # Chat input
#     if prompt := st.chat_input("Type your message here..."):
#         # Add user message to chat history
#         st.session_state.messages.append({"role": "user", "content": prompt})
        
#         # Display user message
#         with st.chat_message("user"):
#             st.markdown(prompt)
        
#         # Generate bot response
#         with st.chat_message("assistant"):
#             with st.spinner("Thinking..."):
#                 try:
#                     # Prepare state for graph
#                     state = {"messages": st.session_state.messages.copy()}
                    
#                     # Invoke the graph
#                     result_state = st.session_state.graph.invoke(state)
                    
#                     # Extract bot response
#                     if result_state["messages"]:
#                         last_msg = result_state["messages"][-1]
                        
#                         if isinstance(last_msg, dict):
#                             bot_response = last_msg.get("content", "")
#                         elif hasattr(last_msg, "content"):
#                             bot_response = last_msg.content
#                         else:
#                             bot_response = str(last_msg)
                        
#                         # Display bot response
#                         st.markdown(bot_response)
                        
#                         # Add bot response to chat history
#                         st.session_state.messages.append({
#                             "role": "assistant",
#                             "content": bot_response
#                         })
#                     else:
#                         st.error("No response generated.")
                        
#                 except Exception as e:
#                     st.error(f"Error generating response: {str(e)}")

# # Footer
# st.divider()
# st.caption("Built with Streamlit, LangGraph, and Ollama")

import streamlit as st
from src.graph.graph_builder import GraphBuilder
from src.state.state import State
from src.LLMs.ollama_llm import LlamaOllamaLLM

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

if "llm_model" not in st.session_state:
    st.session_state.llm_model = "llama3.2:3b"

# Sidebar for configuration
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # Model selection
    model_name = st.text_input(
        "Ollama Model Name",
        value=st.session_state.llm_model,
        help="Enter the Ollama model name (e.g., llama3.2:3b, llama3.1:8b)"
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
            with st.spinner("Loading model and building graph..."):
                # Load LLM
                llm = LlamaOllamaLLM(model_name)
                
                # Build graph
                builder = GraphBuilder(llm)
                graph = builder.setup_graph(usecase)
                
                # Store in session state
                st.session_state.graph = graph
                st.session_state.usecase = usecase
                st.session_state.llm_model = model_name
                
                st.success(f"✅ {usecase} initialized successfully!")
        except Exception as e:
            st.error(f"❌ Error initializing chatbot: {str(e)}")
    
    # Display current status
    st.divider()
    if st.session_state.graph is not None:
        st.success(f"**Status:** Active")
        st.info(f"**Mode:** {st.session_state.usecase}")
        st.info(f"**Model:** {st.session_state.llm_model}")
    else:
        st.warning("**Status:** Not initialized")
    
    # Clear chat button
    st.divider()
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Main chat interface
st.title("🤖 LangGraph Chatbot")
st.caption("A conversational AI powered by LangGraph and Ollama")

# Check if graph is initialized
if st.session_state.graph is None:
    st.info("👈 Please initialize the chatbot using the sidebar configuration.")
else:
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate bot response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            try:
                # Show thinking status
                with st.spinner("Thinking..."):
                    # Prepare state for graph
                    state = {"messages": st.session_state.messages.copy()}
                    
                    # Invoke the graph (this will handle all tool calls automatically)
                    result_state = st.session_state.graph.invoke(state)
                
                # Extract all messages from result
                if result_state["messages"]:
                    # Get the last assistant message
                    assistant_messages = [
                        msg for msg in result_state["messages"] 
                        if (isinstance(msg, dict) and msg.get("role") == "assistant") or 
                           (hasattr(msg, "type") and msg.type == "ai")
                    ]
                    
                    if assistant_messages:
                        last_msg = assistant_messages[-1]
                        
                        if isinstance(last_msg, dict):
                            bot_response = last_msg.get("content", "")
                        elif hasattr(last_msg, "content"):
                            bot_response = last_msg.content
                        else:
                            bot_response = str(last_msg)
                        
                        # Display bot response
                        message_placeholder.markdown(bot_response)
                        
                        # Add bot response to chat history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": bot_response
                        })
                    else:
                        message_placeholder.error("No assistant response found.")
                else:
                    message_placeholder.error("No response generated.")
                    
            except Exception as e:
                message_placeholder.error(f"Error generating response: {str(e)}")
                st.exception(e)  # Show full traceback for debugging

# Footer
st.divider()
st.caption("Built with Streamlit, LangGraph, and Ollama")