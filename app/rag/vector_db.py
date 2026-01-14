from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from app.rag.ingest import load_documents, get_chunks
import os
import shutil

CHROMA_PATH = "chroma_db"

# Global Singletons to prevent reloading models on every request
_embeddings = None
_vector_store = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        print("Loading HuggingFace Embeddings...")
        _embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return _embeddings

def get_vector_store():
    global _vector_store
    if _vector_store is None:
        embeddings = get_embeddings()
        
        # If the database doesn't exist, create it by ingesting documents
        if not os.path.exists(CHROMA_PATH) or not os.listdir(CHROMA_PATH):
            sync_vector_store()
            
        _vector_store = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=embeddings
        )
    return _vector_store

def sync_vector_store():
    """
    Clears the existing vector store and rebuilds it from the data directory.
    """
    global _vector_store
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
    
    print("Synchronizing Vector DB...")
    embeddings = get_embeddings()
    documents = load_documents()
    chunks = get_chunks(documents)
    
    if chunks:
        _vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=CHROMA_PATH
        )
        print(f"Ingested {len(chunks)} chunks from {len(documents)} documents.")
    else:
        print("No documents found to ingest.")