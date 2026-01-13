from sentence_transformers import CrossEncoder

def reranker_agent(state: dict):
    query = state["query"]
    retrieved_docs = state["retrieved_docs"]
    
    if not retrieved_docs:
        return {"reranked_docs": [], "reasoning_trace": state.get("reasoning_trace", []) + ["Reranker: No docs to rerank"]}

    # Load CrossEncoder model
    model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    
    pairs = [[query, doc.page_content] for doc in retrieved_docs]
    scores = model.predict(pairs)
    
    for i, doc in enumerate(retrieved_docs):
        doc.metadata["rerank_score"] = float(scores[i])
    
    reranked = sorted(retrieved_docs, key=lambda x: x.metadata["rerank_score"], reverse=True)
    top_docs = reranked[:5]
    
    trace = state.get("reasoning_trace", [])
    trace.append(f"Reranker: Re-scored {len(retrieved_docs)} segments, optimized to top {len(top_docs)}")
    
    return {
        "reranked_docs": top_docs,
        "reasoning_trace": trace
    }