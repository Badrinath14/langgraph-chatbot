# from src.graph.graph_builder import GraphBuilder
# from src.state.state import State
# from src.LLMs.ollama_llm import LlamaOllamaLLM  # or your LLM class

# def run_terminal_chat(usecase="Basic Chatbot"):
#     # 1. Load LLM
#     llm = LlamaOllamaLLM("llama3.2:3b")  # change model if needed

#     # 2. Build graph
#     builder = GraphBuilder(llm)
#     graph = builder.setup_graph(usecase)

#     # 3. Start terminal loop
#     print(f"--- {usecase} is ready! Type 'exit' to quit. ---")
#     state = {"messages": []}  # initial empty conversation state

#     while True:
#         user_input = input("You: ")
#         if user_input.lower() in ["exit", "quit"]:
#             print("Goodbye 👋")
#             break

#         # Update state with user message
#         state["messages"].append({"role": "user", "content": user_input})

#         # Invoke the graph
#         state = graph.invoke(state)

#         # Extract bot response
#         if state["messages"]:
#             last_msg = state["messages"][-1]
#             if isinstance(last_msg, dict):
#                 last_message = last_msg.get("content", "")
#             elif hasattr(last_msg, "content"):
#                 last_message = last_msg.content
#             else:
#                 last_message = str(last_msg)
#             print(f"Bot: {last_message}")

# if __name__ == "__main__":
#     run_terminal_chat("Chatbot With Web")  # or "Basic Chatbot"
