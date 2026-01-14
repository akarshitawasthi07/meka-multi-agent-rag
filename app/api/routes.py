from fastapi import APIRouter, HTTPException, BackgroundTasks, Request, WebSocket, WebSocketDisconnect
from sse_starlette.sse import EventSourceResponse
from app.schemas import AskRequest
from app.graph.orchestrator import run_meka, stream_meka
from app.utils.history import add_query_to_history, update_query_status, get_query_by_id, get_all_history, delete_history_item, save_history
from langchain_core.documents import Document
import uuid
import asyncio
import json
import traceback

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

def serialize_docs(obj):
    if isinstance(obj, list):
        return [serialize_docs(item) for item in obj]
    if isinstance(obj, Document):
        return {"page_content": obj.page_content, "metadata": obj.metadata}
    if isinstance(obj, dict):
        return {k: serialize_docs(v) for k, v in obj.items()}
    # Handle LangChain Message objects (HumanMessage, AIMessage, etc)
    if hasattr(obj, 'content'):
        return obj.content
    return obj

router = APIRouter()

@router.websocket("/ws/ask/{thread_id}")
async def websocket_ask(websocket: WebSocket, thread_id: str):
    await websocket.accept()
    logger.info(f"WS: Connection accepted | thread_id={thread_id}")
    
    try:
        # 1. Listen for initial payload
        data = await websocket.receive_json()
        query = data.get("query")
        web_search = data.get("web_search", False)
        
        if not query:
            await websocket.send_json({"event": "error", "error": "No query provided"})
            await websocket.close()
            return

        query_id = str(uuid.uuid4())
        logger.info(f"WS: Processing query | id={query_id} | query={query[:50]}...")
        
        # Save initial history
        add_query_to_history(query_id, {
            "query_id": query_id,
            "query": query,
            "status": "processing",
            "result": "",
            "reasoning_trace": [],
            "thread_id": thread_id
        })

        combined_trace = []
        full_state = {}

        # 2. Stream results
        async for event in stream_meka(query, web_search, thread_id):
            if not isinstance(event, dict): continue
            node_name = list(event.keys())[0]
            state_update = event[node_name]
            full_state.update(state_update)
            
            # Send traces
            if "reasoning_trace" in state_update:
                for t in state_update["reasoning_trace"]:
                    if t not in combined_trace:
                        combined_trace.append(t)
                        await websocket.send_json({"event": "trace", "trace": t})

            # Send answer updates
            if "final_answer" in state_update:
                await websocket.send_json({"event": "answer", "answer": state_update["final_answer"]})

        # 3. Finalize
        update_query_status(query_id, "completed", serialize_docs(full_state))
        
        # Persist final trace to history
        all_h = get_all_history() # Re-fetch to ensure we have latest
        from app.utils.history import save_history, get_history
        hist = get_history()
        if query_id in hist:
            hist[query_id]["reasoning_trace"] = combined_trace
            save_history(hist)

        await websocket.send_json({
            "event": "done",
            "full_result": serialize_docs(full_state),
            "query_id": query_id
        })

    except WebSocketDisconnect:
        logger.info(f"WS: Disconnected | thread_id={thread_id}")
    except Exception as e:
        logger.error(f"WS: Error | thread_id={thread_id} | error={str(e)}")
        traceback.print_exc()
        try:
            await websocket.send_json({"event": "error", "error": str(e)})
        except:
            pass
    finally:
        logger.info(f"WS: Closing socket | thread_id={thread_id}")
        try:
            await websocket.close()
        except:
            pass

@router.post("/query")
async def create_query(req: AskRequest, background_tasks: BackgroundTasks):
    """Asynchronous endpoint for long-running workflows - Required by Assignment."""
    query_id = str(uuid.uuid4())
    add_query_to_history(query_id, {
        "query_id": query_id,
        "query": req.query,
        "web_search": req.web_search,
        "status": "processing",
        "result": "",
        "reasoning_trace": [],
        "thread_id": req.thread_id or "default"
    })
    
    background_tasks.add_task(process_query_task, query_id, req.query, req.web_search, req.thread_id or "default")
    return {"query_id": query_id, "status": "processing"}

async def process_query_task(query_id: str, question: str, web_search: bool, thread_id: str):
    try:
        resultado = run_meka(question, web_search, thread_id)
        # Final formatting/serialization
        resultado = serialize_docs(resultado)
        update_query_status(query_id, "completed", resultado)
    except Exception as e:
        logger.error(f"Async Error | id={query_id} | error={str(e)}")
        update_query_status(query_id, "failed", {"error": str(e)})

@router.get("/status/{query_id}")
def get_status(query_id: str):
    """Poll result of async query - Required by Assignment."""
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
