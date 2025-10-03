import streamlit as st
from src.graph.graph_builder import GraphBuilder
from src.state.state import State
from src.LLMs.ollama_llm import LlamaOllamaLLM
from src.LLMs.groq_llm import GroqLLM

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
            ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"],
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
            # Validate Groq API key if Groq is selected
            if llm_provider == "Groq" and not groq_api_key:
                st.error("❌ Please enter your Groq API key")
            else:
                with st.spinner(f"Loading {llm_provider} model and building graph..."):
                    # Load LLM based on provider
                    if llm_provider == "Ollama":
                        llm = LlamaOllamaLLM(model_name)
                    else:  # Groq
                        llm = GroqLLM(model_name, groq_api_key)
                    
                    # Build graph
                    builder = GraphBuilder(llm)
                    graph = builder.setup_graph(usecase)
                    
                    # Store in session state
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
        st.rerun()

# Main chat interface
st.title("🤖 LangGraph Chatbot")
st.caption("A conversational AI powered by LangGraph and Ollama/Groq")

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
                st.exception(e)

# Footer
st.divider()
st.caption("Built with Streamlit, LangGraph, Ollama, and Groq")