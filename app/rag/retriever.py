from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.documents import Document
from app.rag.vector_db import get_vector_store
from app.rag.ingest import load_documents
import os

def web_search_docs(query: str):
    """
    Performs a web search using Tavily and returns results as LangChain Documents.
    """
    try:
        search = TavilySearchResults(max_results=3)
        results = search.invoke(query)
        docs = []
        for res in results:
            docs.append(Document(
                page_content=res["content"],
                metadata={"source": res["url"], "type": "web"}
            ))
        return docs
    except Exception as e:
        print(f"Web search error: {e}")
        return []

def retrieve_docs(query: str, use_web: bool = False):
    # 1. Vector Store Retriever
    vector_store = get_vector_store()
    vector_retriever = vector_store.as_retriever(search_kwargs={"k": 5})

    # 2. BM25 Retriever (Keyword search)
    # We need some documents to initialize BM25
    documents = load_documents()
    if documents:
        bm25_retriever = BM25Retriever.from_documents(documents)
        bm25_retriever.k = 5
        
        # 3. Hybrid Ensemble Retriever
        ensemble_retriever = EnsembleRetriever(
            retrievers=[vector_retriever, bm25_retriever],
            weights=[0.5, 0.5]
        )
        local_docs = ensemble_retriever.invoke(query)
    else:
        # Fallback to just vector if no docs found for BM25
        local_docs = vector_retriever.invoke(query)

    if use_web:
        web_docs = web_search_docs(query)
        return local_docs + web_docs
        
    return local_docs