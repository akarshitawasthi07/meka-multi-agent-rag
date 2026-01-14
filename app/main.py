import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
logger = logging.getLogger("MEKA")

load_dotenv()

# Import RAG components to trigger eager model loading
from app.rag.vector_db import get_embeddings, get_vector_store
from app.rag.retriever import get_bm25_retriever
from app.api.routes import router

app = FastAPI(title="Multi-Agent RAG API | MEKA")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("--- MEKA Backend Initializing ---")
    # Eagerly load AI models during startup to prevent request timeouts
    try:
        logger.info("Pre-loading Embeddings (HuggingFace)...")
        get_embeddings()
        logger.info("Pre-loading Vector Store (Chroma)...")
        get_vector_store()
        logger.info("Pre-loading BM25 Index...")
        get_bm25_retriever()
        logger.info("--- Initialization Complete ---")
    except Exception as e:
        logger.warning(f"Initialization Warning: {e}")

app.include_router(router)

@app.get("/")
def root():
    return {"status": "API is running", "version": "1.0.0"}