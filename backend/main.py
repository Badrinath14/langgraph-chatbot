from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
from src.graph.graph_builder import GraphBuilder
from src.LLMs.ollama_llm import LlamaOllamaLLM
from src.LLMs.groq_llm import GroqLLM
from src.checkpoint.redis_checkpoint import RedisCheckpointer

app = FastAPI(title="LangGraph Chatbot API")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for graphs (in production, use proper session management)
graphs = {}
redis_checkpointer = None

# Pydantic models
class InitializeRequest(BaseModel):
    llm_provider: str  # "Ollama" or "Groq"
    model_name: str
    groq_api_key: Optional[str] = None
    usecase: str = "Chatbot With Web"
    thread_id: str = "thread_1"

class ChatRequest(BaseModel):
    message: str
    thread_id: str = "thread_1"

class ApprovalRequest(BaseModel):
    thread_id: str
    approved: bool

class Message(BaseModel):
    role: str
    content: str

class ChatResponse(BaseModel):
    response: str
    pending_approval: Optional[Dict[str, Any]] = None
    messages: List[Message]

@app.on_event("startup")
async def startup_event():
    """Initialize Redis checkpointer on startup"""
    global redis_checkpointer
    redis_checkpointer = RedisCheckpointer().get_checkpointer()
    print("✅ FastAPI server started with Redis checkpointer")

@app.get("/")
async def root():
    return {"message": "LangGraph Chatbot API", "status": "running"}

@app.post("/initialize")
async def initialize_chatbot(request: InitializeRequest):
    """Initialize a chatbot instance with specified configuration"""
    try:
        # Validate Groq API key if needed
        if request.llm_provider == "Groq" and not request.groq_api_key:
            raise HTTPException(status_code=400, detail="Groq API key is required")
        
        # Create LLM instance
        if request.llm_provider == "Ollama":
            llm = LlamaOllamaLLM(request.model_name)
        else:
            llm = GroqLLM(request.model_name, request.groq_api_key)
        
        # Build graph
        builder = GraphBuilder(llm)
        graph = builder.setup_graph(request.usecase, redis_checkpointer)
        
        # Store graph (use thread_id as key)
        graphs[request.thread_id] = {
            "graph": graph,
            "llm_provider": request.llm_provider,
            "model_name": request.model_name,
            "usecase": request.usecase
        }
        
        return {
            "status": "success",
            "message": f"{request.usecase} initialized successfully with {request.llm_provider}",
            "thread_id": request.thread_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing chatbot: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message and get a response"""
    try:
        # Check if graph exists for this thread
        if request.thread_id not in graphs:
            raise HTTPException(status_code=400, detail="Chatbot not initialized. Please initialize first.")
        
        graph_data = graphs[request.thread_id]
        graph = graph_data["graph"]
        
        # Prepare state
        config = {"configurable": {"thread_id": request.thread_id}}
        
        # Get current state to build on existing messages
        try:
            snapshot = graph.get_state(config)
            existing_messages = snapshot.values.get("messages", []) if snapshot.values else []
        except:
            existing_messages = []
        
        # Add user message
        from langchain_core.messages import HumanMessage
        state = {
            "messages": existing_messages + [HumanMessage(content=request.message)]
        }
        
        # Stream through graph
        final_state = None
        for event in graph.stream(state, config, stream_mode="values"):
            final_state = event
        
        # Check for interrupts (human approval needed)
        snapshot = graph.get_state(config)
        
        if snapshot.next and "human_approval" in snapshot.next:
            # Pending approval
            last_message = snapshot.values["messages"][-1]
            
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                tool_call = last_message.tool_calls[0]
                
                return ChatResponse(
                    response="",
                    pending_approval={
                        "tool_call": {
                            "name": tool_call["name"],
                            "args": tool_call["args"]
                        }
                    },
                    messages=convert_messages_to_dict(snapshot.values["messages"])
                )
        
        # Normal completion
        result_state = snapshot.values
        messages = result_state.get("messages", [])
        
        # Extract assistant response
        bot_response = ""
        if messages:
            for msg in reversed(messages):
                if hasattr(msg, "type") and msg.type == "ai":
                    content = msg.content
                    if content and not (hasattr(msg, "tool_calls") and msg.tool_calls and not content):
                        bot_response = content
                        break
        
        return ChatResponse(
            response=bot_response,
            pending_approval=None,
            messages=convert_messages_to_dict(messages)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.post("/approve")
async def approve_action(request: ApprovalRequest):
    """Approve or reject a pending action"""
    try:
        if request.thread_id not in graphs:
            raise HTTPException(status_code=400, detail="Chatbot not initialized")
        
        graph = graphs[request.thread_id]["graph"]
        config = {"configurable": {"thread_id": request.thread_id}}
        
        if request.approved:
            # Continue execution
            for event in graph.stream(None, config, stream_mode="values"):
                pass
            
            snapshot = graph.get_state(config)
            result_state = snapshot.values
            messages = result_state.get("messages", [])
            
            # Extract response
            bot_response = ""
            if messages:
                for msg in reversed(messages):
                    if hasattr(msg, "type") and msg.type == "ai":
                        content = msg.content
                        if content and not (hasattr(msg, "tool_calls") and msg.tool_calls and not content):
                            bot_response = content
                            break
            
            return {
                "status": "approved",
                "response": bot_response,
                "messages": convert_messages_to_dict(messages)
            }
        else:
            # Reject
            from langchain_core.messages import AIMessage
            
            graph.update_state(
                config,
                {"messages": [AIMessage(content="❌ WhatsApp message was not sent (rejected by user). How else can I help you?")]},
                as_node="chatbot"
            )
            
            snapshot = graph.get_state(config)
            messages = snapshot.values.get("messages", [])
            
            return {
                "status": "rejected",
                "response": "❌ WhatsApp message was not sent (rejected by user). How else can I help you?",
                "messages": convert_messages_to_dict(messages)
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing approval: {str(e)}")

@app.get("/history/{thread_id}")
async def get_history(thread_id: str):
    """Get conversation history for a thread"""
    try:
        if thread_id not in graphs:
            return {"messages": []}
        
        graph = graphs[thread_id]["graph"]
        config = {"configurable": {"thread_id": thread_id}}
        
        snapshot = graph.get_state(config)
        messages = snapshot.values.get("messages", []) if snapshot.values else []
        
        return {"messages": convert_messages_to_dict(messages)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")

@app.delete("/history/{thread_id}")
async def clear_history(thread_id: str):
    """Clear conversation history for a thread"""
    try:
        if thread_id not in graphs:
            return {"status": "success", "message": "No history to clear"}
        
        graph = graphs[thread_id]["graph"]
        config = {"configurable": {"thread_id": thread_id}}
        
        graph.update_state(
            config,
            {"messages": []},
            as_node="chatbot"
        )
        
        return {"status": "success", "message": "History cleared"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing history: {str(e)}")

def convert_messages_to_dict(messages):
    """Convert LangChain messages to simple dicts"""
    result = []
    for msg in messages:
        if isinstance(msg, dict):
            role = msg.get("role", "assistant")
            content = msg.get("content", "")
        elif hasattr(msg, "type"):
            role = "user" if msg.type == "human" else "assistant"
            content = msg.content if hasattr(msg, "content") else str(msg)
        else:
            continue
        
        if content and role in ["user", "assistant"]:
            result.append({"role": role, "content": content})
    
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)