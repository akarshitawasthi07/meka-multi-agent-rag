from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from app.rag.vector_db import get_vector_store
from app.rag.ingest import load_documents
import os

def retrieve_docs(query: str):
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
        return ensemble_retriever.invoke(query)
    else:
        # Fallback to just vector if no docs found for BM25
        return vector_retriever.invoke(query)