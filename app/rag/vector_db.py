from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from app.rag.ingest import load_documents, get_chunks
import os
import shutil

CHROMA_PATH = "chroma_db"

def get_vector_store():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # If the database doesn't exist, create it by ingesting documents
    if not os.path.exists(CHROMA_PATH) or not os.listdir(CHROMA_PATH):
        sync_vector_store()

    vectordb = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )

    return vectordb

def sync_vector_store():
    """
    Clears the existing vector store and rebuilds it from the data directory.
    """
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
    
    print("Synchronizing Vector DB...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    documents = load_documents()
    chunks = get_chunks(documents)
    
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    print(f"Ingested {len(chunks)} chunks from {len(documents)} documents.")