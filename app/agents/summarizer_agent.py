from app.llm.groq_llm import get_llm
from langchain_core.messages import AIMessage

def summarizer_agent(state: dict):
    llm = get_llm()
    query = state["query"]
    docs = state["reranked_docs"]
    messages = state.get("messages", [])

    context = "\n\n".join([doc.page_content for doc in docs])
    
    # Get conversation context
    history_str = ""
    for msg in messages[:-1]:
        role = "User" if hasattr(msg, 'type') and msg.type == 'human' else "Assistant"
        history_str += f"{role}: {msg.content}\n"

    prompt = f"""
You are a synthesis agent for MEKA. Use the provided context AND conversation history to answer the user's latest query accurately.
If the context doesn't contain the answer but the history does, use the history. If both are available, prioritize the latest retrieved context.

**Conversation History:**
{history_str if history_str else "No prior conversation."}

**Retrieved Context:**
{context}

**Current User Query:** {query}

Answer:
"""

    response = llm.invoke(prompt)
    answer = response.content
    
    trace = state.get("reasoning_trace", [])
    trace.append(f"Summarizer: Synthesized final answer using context and history")
    
    return {
        "messages": [AIMessage(content=answer)],
        "final_answer": answer,
        "reasoning_trace": trace
    }