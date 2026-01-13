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
    return {"final_answer": response.content}