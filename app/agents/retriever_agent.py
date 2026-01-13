from app.rag.retriever import retrieve_docs

def retriever_agent(state: dict):
    query = state["query"]
    docs = retrieve_docs(query)
    return {"retrieved_docs": docs}