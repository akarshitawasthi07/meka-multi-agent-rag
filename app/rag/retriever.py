from langchain_community.retrievers import BM25Retriever
from langchain_tavily import TavilySearch
from langchain_core.documents import Document
from app.rag.vector_db import get_vector_store
from app.rag.ingest import load_documents
import os

# Global BM25 retriever to prevent recalculating index on every query
_cached_bm25 = None

def get_bm25_retriever():
    global _cached_bm25
    if _cached_bm25 is None:
        documents = load_documents()
        if documents:
            print("Initializing BM25 Retriever...")
            _cached_bm25 = BM25Retriever.from_documents(documents)
            _cached_bm25.k = 5
    return _cached_bm25

def web_search_docs(query: str):
    """
    Performs a web search using Tavily and returns results as LangChain Documents.
    """
    if not os.getenv("TAVILY_API_KEY"):
        return []

    try:
        search = TavilySearch(max_results=3)
        response = search.invoke(query)
        
        # Handle both dict with 'results' and direct list response
        if isinstance(response, dict):
            results_list = response.get("results", [])
        elif isinstance(response, list):
            results_list = response
        else:
            return []

        docs = []
        for res in results_list:
            content = res.get("content", "")
            url = res.get("url", "unknown")
            docs.append(Document(
                page_content=content,
                metadata={"source": url, "type": "web"}
            ))
        return docs
    except Exception as e:
        print(f"Web search error: {e}")
        return []

def retrieve_docs(query: str, use_web: bool = False):
    """
    Hybrid retriever that combines Vector search and Keyword (BM25) search.
    """
    # 1. Vector Search
    vector_store = get_vector_store()
    vector_retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    local_docs = vector_retriever.invoke(query)
    
    # 2. BM25 Keyword Search
    bm25 = get_bm25_retriever()
    if bm25:
        bm25_docs = bm25.invoke(query)
        # Manual merge to avoid 'langchain_classic' extension issues
        seen_content = {d.page_content for d in local_docs}
        for d in bm25_docs:
            if d.page_content not in seen_content:
                local_docs.append(d)
                seen_content.add(d.page_content)

    # 3. Supplemental Web Search
    if use_web:
        web_docs = web_search_docs(query)
        local_docs.extend(web_docs)
        
    return local_docs