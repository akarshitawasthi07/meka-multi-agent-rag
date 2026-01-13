from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.schemas import AskRequest
from app.graph.orchestrator import run_meka
from app.utils.history import add_query_to_history, update_query_status, get_query_by_id, get_all_history, delete_history_item
import uuid
import traceback

router = APIRouter()

@router.post("/ask")
def ask(req: AskRequest):
    """Synchronous endpoint for immediate answers."""
    try:
        resultado = run_meka(req.question, req.web_search, req.thread_id)
        
        # Serialize LangChain Documents for JSON compatibility
        if "retrieved_docs" in resultado:
            resultado["retrieved_docs"] = [
                {"page_content": d.page_content, "metadata": d.metadata} 
                for d in resultado["retrieved_docs"]
            ]
        if "reranked_docs" in resultado:
            resultado["reranked_docs"] = [
                {"page_content": d.page_content, "metadata": d.metadata} 
                for d in resultado["reranked_docs"]
            ]
            
        # Store in history 
        query_id = str(uuid.uuid4())
        add_query_to_history(query_id, {
            "query_id": query_id,
            "question": req.question,
            "web_search": req.web_search,
            "status": "COMPLETED",
            "result": resultado
        })
        return {"answer": resultado, "query_id": query_id}
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}, 500

@router.post("/query")
async def create_query(req: AskRequest, background_tasks: BackgroundTasks):
    """Asynchronous endpoint for long-running workflows."""
    query_id = str(uuid.uuid4())
    add_query_to_history(query_id, {
        "query_id": query_id,
        "question": req.question,
        "web_search": req.web_search,
        "status": "IN_PROGRESS"
    })
    
    background_tasks.add_task(process_query_task, query_id, req.question, req.web_search, req.thread_id)
    return {"query_id": query_id, "status": "IN_PROGRESS"}

async def process_query_task(query_id: str, question: str, web_search: bool, thread_id: str):
    try:
        resultado = run_meka(question, web_search, thread_id)
        
        # Serialize 
        if "retrieved_docs" in resultado:
            resultado["retrieved_docs"] = [
                {"page_content": d.page_content, "metadata": d.metadata} 
                for d in resultado["retrieved_docs"]
            ]
        if "reranked_docs" in resultado:
            resultado["reranked_docs"] = [
                {"page_content": d.page_content, "metadata": d.metadata} 
                for d in resultado["reranked_docs"]
            ]
            
        update_query_status(query_id, "COMPLETED", resultado)
    except Exception as e:
        traceback.print_exc()
        update_query_status(query_id, "FAILED", {"error": str(e)})

@router.get("/status/{query_id}")
def get_status(query_id: str):
    query = get_query_by_id(query_id)
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    return query

@router.get("/history")
def list_history():
    return get_all_history()

@router.delete("/history/{query_id}")
def delete_item(query_id: str):
    if delete_history_item(query_id):
        return {"status": "DELETED"}
    raise HTTPException(status_code=404, detail="Item not found")