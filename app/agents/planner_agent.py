from app.llm.groq_llm import get_llm

def planner_agent(state: dict):
    llm = get_llm()
    query = state["query"]
    web_enabled = state.get("web_search_enabled", False)
    messages = state.get("messages", [])
    
    # Get last few messages for context
    history_str = ""
    for msg in messages[:-1]: # exclude the latest human query already in state["query"]
        role = "User" if hasattr(msg, 'type') and msg.type == 'human' else "Assistant"
        history_str += f"{role}: {msg.content}\n"

    prompt = f"""
You are a planning agent for a Multi-Agent Expert Knowledge Assistant (MEKA).
Your task is to decompose the user's current query into a simple search plan.
If the query is a follow-up (e.g., "tell me more", "explain that part"), use the conversation history to disambiguate what the user is referring to.

**Conversation History:**
{history_str if history_str else "No prior conversation."}

**Current User Query:** {query}

**Contextual Awareness:**
- If the query is a continuation, make the plan relevant to the previous topic.
- If it's a new topic, create a fresh plan.
- Web search is {"ENABLED" if web_enabled else "DISABLED"}.

Plan:
"""
    response = llm.invoke(prompt)
    plan = response.content.strip()
    
    trace = state.get("reasoning_trace", [])
    trace.append(f"Planner: Created extraction plan - {plan}")
    
    return {
        "planner_output": plan,
        "reasoning_trace": trace
    }