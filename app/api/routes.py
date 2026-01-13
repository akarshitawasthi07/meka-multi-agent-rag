from fastapi import APIRouter
from app.llm.groq_llm import get_llm
from app.schemas import AskRequest
from app.graph.orchestrator import run_meka
from langchain_community.vectorstores import Chroma

router = APIRouter()

@router.post("/ask")
def ask(req: AskRequest):
    return {"answer": run_meka(req.question)}
