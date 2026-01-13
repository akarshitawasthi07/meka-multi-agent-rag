from app.llm.groq_llm import get_llm

def planner_agent(state: dict):
    llm = get_llm()
    query = state["query"]
    web_enabled = state.get("web_search_enabled", False)
    
    prompt = f"""
You are a planning agent for a Multi-Agent Expert Knowledge Assistant (MEKA).
Decompose this query into a simple search plan.
Note: Web search is {"ENABLED" if web_enabled else "DISABLED"}.

Query: {query}

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