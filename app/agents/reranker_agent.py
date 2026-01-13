from sentence_transformers import CrossEncoder

def reranker_agent(state: dict):
    query = state["query"]
    retrieved_docs = state["retrieved_docs"]
    
    if not retrieved_docs:
        return {"reranked_docs": []}

    # Load CrossEncoder model (this will download if not present)
    model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    
    # Prepare pairs for reranking
    pairs = [[query, doc.page_content] for doc in retrieved_docs]
    
    # Compute scores
    scores = model.predict(pairs)
    
    # Attach scores and sort
    for i, doc in enumerate(retrieved_docs):
        doc.metadata["rerank_score"] = float(scores[i])
    
    reranked = sorted(retrieved_docs, key=lambda x: x.metadata["rerank_score"], reverse=True)
    
    # Keep top 5
    return {"reranked_docs": reranked[:5]}