# from langgraph.graph import StateGraph
# from src.state.state import State   
# from langgraph.graph import START, END
# from src.nodes.basic_chatbot_node import BasicChatbotNode
# from src.tools.search_tool import get_tools, create_tool_node
# from langgraph.prebuilt import tools_condition
# from src.nodes.chatbot_with_tool_node import ChatbotWithToolNode
# from langgraph.checkpoint.memory import MemorySaver


# class GraphBuilder:
#     def __init__(self, model):
#         self.llm = model
#         self.graph_builder = StateGraph(State)

#     def basic_chatbot_build_graph(self):
#         """
#         Builds a basic chatbot graph using LangGraph.
#         This method initializes a chatbot node using the `BasicChatbotNode` class 
#         and integrates it into the graph. The chatbot node is set as both the 
#         entry and exit point of the graph.
#         """
#         self.basic_chatbot_node = BasicChatbotNode(self.llm)

#         self.graph_builder.add_node("chatbot", self.basic_chatbot_node.process)
#         self.graph_builder.add_edge(START, "chatbot")
#         self.graph_builder.add_edge("chatbot", END)

#     def chatbot_with_tools_build_graph(self):
#         """
#         Builds an advanced chatbot graph with tool integration and human-in-the-loop.
#         This method creates a chatbot graph that includes both a chatbot node 
#         and a tool node with human approval for sensitive actions.
        
#         Flow: START -> chatbot -> (interrupt for approval) -> tools -> chatbot -> END
#         """
#         # Define the tool and tool node
#         tools = get_tools()
#         tool_node = create_tool_node(tools)

#         # Define the LLM
#         llm = self.llm

#         # Define the chatbot node
#         obj_chatbot_with_node = ChatbotWithToolNode(llm)
#         chatbot_node = obj_chatbot_with_node.create_chatbot(tools)
        
#         # Add nodes
#         self.graph_builder.add_node("chatbot", chatbot_node)
#         self.graph_builder.add_node("tools", tool_node)
        
#         # Define edges
#         # Start with chatbot
#         self.graph_builder.add_edge(START, "chatbot")
        
#         # Conditional: if chatbot wants to use tools, go to tools node
#         # This creates an interrupt point for human approval
#         self.graph_builder.add_conditional_edges(
#             "chatbot",
#             tools_condition
#         )
        
#         # After tools execute, go back to chatbot to generate final response
#         self.graph_builder.add_edge("tools", "chatbot")

#     def setup_graph(self, usecase: str, checkpointer=None):
#         """
#         Sets up the graph based on the selected use case with optional checkpointer.
        
#         Args:
#             usecase: The use case to build ("Basic Chatbot" or "Chatbot With Web")
#             checkpointer: Memory checkpointer for human-in-the-loop (default: MemorySaver)
#         """
#         if usecase == "Basic Chatbot":
#             self.basic_chatbot_build_graph()
#             return self.graph_builder.compile()

#         if usecase == "Chatbot With Web":
#             self.chatbot_with_tools_build_graph()
            
#             # Use provided checkpointer or create new one
#             if checkpointer is None:
#                 checkpointer = MemorySaver()
            
#             # Compile with checkpointer and interrupt before tools
#             # This enables human-in-the-loop approval
#             return self.graph_builder.compile(
#                 checkpointer=checkpointer,
#                 interrupt_before=["tools"]  # Interrupt before executing tools
#             )

#         return self.graph_builder.compile()

from langgraph.graph import StateGraph
from src.state.state import State   
from langgraph.graph import START, END
from src.nodes.basic_chatbot_node import BasicChatbotNode
from src.tools.search_tool import get_tools, create_tool_node
from langgraph.prebuilt import tools_condition
from src.nodes.chatbot_with_tool_node import ChatbotWithToolNode
from langgraph.checkpoint.memory import MemorySaver


class GraphBuilder:
    def __init__(self, model):
        self.llm = model
        self.graph_builder = StateGraph(State)

    def basic_chatbot_build_graph(self):
        """
        Builds a basic chatbot graph using LangGraph.
        This method initializes a chatbot node using the `BasicChatbotNode` class 
        and integrates it into the graph. The chatbot node is set as both the 
        entry and exit point of the graph.
        """
        self.basic_chatbot_node = BasicChatbotNode(self.llm)

        self.graph_builder.add_node("chatbot", self.basic_chatbot_node.process)
        self.graph_builder.add_edge(START, "chatbot")
        self.graph_builder.add_edge("chatbot", END)

    def human_approval_required(self, state: State) -> str:
        """
        Determines if human approval is needed based on the tool being called.
        Returns 'human_approval' for sensitive tools, 'tools' for auto-approved tools.
        """
        messages = state["messages"]
        last_message = messages[-1]
        
        # Check if there are tool calls
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            for tool_call in last_message.tool_calls:
                tool_name = tool_call.get("name", "")
                
                # Only WhatsApp messages require human approval
                if tool_name == "send_whatsapp_message":
                    return "human_approval"
        
        # Auto-approve all other tools (web_search, etc.)
        return "tools"

    def chatbot_with_tools_build_graph(self):
        """
        Builds an advanced chatbot graph with tool integration and selective human-in-the-loop.
        Only WhatsApp messages require human approval. Web searches execute automatically.
        
        Flow: 
        - Web search: START -> chatbot -> tools -> chatbot -> END
        - WhatsApp: START -> chatbot -> human_approval (interrupt) -> tools -> chatbot -> END
        """
        # Define the tool and tool node
        tools = get_tools()
        tool_node = create_tool_node(tools)

        # Define the LLM
        llm = self.llm

        # Define the chatbot node
        obj_chatbot_with_node = ChatbotWithToolNode(llm)
        chatbot_node = obj_chatbot_with_node.create_chatbot(tools)
        
        # Add nodes
        self.graph_builder.add_node("chatbot", chatbot_node)
        self.graph_builder.add_node("tools", tool_node)
        self.graph_builder.add_node("human_approval", tool_node)  # Same as tools, but will interrupt
        
        # Define edges
        # Start with chatbot
        self.graph_builder.add_edge(START, "chatbot")
        
        # Conditional routing based on tool calls
        def route_tools(state: State) -> str:
            """Route to either human approval or direct tool execution"""
            messages = state["messages"]
            last_message = messages[-1]
            
            # Check if chatbot wants to end conversation
            if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
                return END
            
            # Check if approval needed
            for tool_call in last_message.tool_calls:
                tool_name = tool_call.get("name", "")
                if tool_name == "send_whatsapp_message":
                    return "human_approval"
            
            # Auto-approve other tools
            return "tools"
        
        # Add conditional edge from chatbot
        self.graph_builder.add_conditional_edges(
            "chatbot",
            route_tools,
            {
                "human_approval": "human_approval",
                "tools": "tools",
                END: END
            }
        )
        
        # After tools execute, go back to chatbot
        self.graph_builder.add_edge("tools", "chatbot")
        self.graph_builder.add_edge("human_approval", "chatbot")

    def setup_graph(self, usecase: str, checkpointer=None):
        """
        Sets up the graph based on the selected use case with optional checkpointer.
        
        Args:
            usecase: The use case to build ("Basic Chatbot" or "Chatbot With Web")
            checkpointer: Memory checkpointer for human-in-the-loop (default: MemorySaver)
        """
        if usecase == "Basic Chatbot":
            self.basic_chatbot_build_graph()
            return self.graph_builder.compile()

        if usecase == "Chatbot With Web":
            self.chatbot_with_tools_build_graph()
            
            # Use provided checkpointer or create new one
            if checkpointer is None:
                checkpointer = MemorySaver()
            
            # Compile with checkpointer and interrupt only before human_approval node
            # This enables selective human-in-the-loop
            return self.graph_builder.compile(
                checkpointer=checkpointer,
                interrupt_before=["human_approval"]  # Only interrupt for WhatsApp
            )

        return self.graph_builder.compile()