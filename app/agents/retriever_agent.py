from app.rag.retriever import retrieve_docs

def retriever_agent(state: dict):
    query = state["query"]
    web_enabled = state.get("web_search_enabled", False)
    
    docs = retrieve_docs(query, use_web=web_enabled)
    
    trace = state.get("reasoning_trace", [])
    trace.append(f"Retriever: Fetched {len(docs)} segments from {'Local + Web' if web_enabled else 'Local Hybrid'}")
    
    return {
        "retrieved_docs": docs,
        "reasoning_trace": trace
    }