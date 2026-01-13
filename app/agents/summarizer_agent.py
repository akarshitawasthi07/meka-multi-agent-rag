from app.llm.groq_llm import get_llm
from langchain_core.prompts import PromptTemplate

def summarizer_agent(state: dict):
    llm = get_llm()
    query = state["query"]
    docs = state["reranked_docs"]

    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""
Use the context to answer the question below. Be thorough and provide a traceable answer.

Context:
{context}

Question: {query}
Answer:
"""

    response = llm.invoke(prompt)
    answer = response.content
    
    trace = state.get("reasoning_trace", [])
    trace.append(f"Summarizer: Synthesized final answer from reranked context")
    
    return {
        "final_answer": answer,
        "reasoning_trace": trace
    }