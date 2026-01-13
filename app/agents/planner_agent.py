from app.llm.groq_llm import get_llm

def planner_agent(state: dict):
    llm = get_llm()
    query = state["query"]
    
    prompt = f"""
You are a planning agent for a Multi-Agent Expert Knowledge Assistant (MEKA).
Your goal is to decompose a complex query into a simple search plan.

Query: {query}

Provide a concise plan (1-2 sentences) of what needs to be retrieved to answer this query.
Plan:
"""
    response = llm.invoke(prompt)
    plan = response.content.strip()
    
    return {"planner_output": plan}