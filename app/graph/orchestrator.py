from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict
from typing import List
from app.utils.logger import get_logger

logger = get_logger(__name__)

from app.agents.planner_agent import planner_agent
from app.agents.retriever_agent import retriever_agent
from app.agents.reranker_agent import reranker_agent
from app.agents.summarizer_agent import summarizer_agent
from app.agents.validator_agent import validator_agent


class MekaState(TypedDict):
    query: str
    web_search_enabled: bool
    planner_output: str
    retrieved_docs: List
    reranked_docs: List
    final_answer: str
    validation: str
    reason: str
    reasoning_trace: List[str]


graph = StateGraph(MekaState)

graph.add_node("planner", planner_agent)
graph.add_node("retriever", retriever_agent)
graph.add_node("reranker", reranker_agent)
graph.add_node("summarizer", summarizer_agent)
graph.add_node("validator", validator_agent)

graph.set_entry_point("planner")
graph.add_edge("planner", "retriever")
graph.add_edge("retriever", "reranker")
graph.add_edge("reranker", "summarizer")
graph.add_edge("summarizer", "validator")
graph.set_finish_point("validator")

# Initialize memory checkpointer
memory = MemorySaver()
app = graph.compile(checkpointer=memory)


def run_meka(query: str, web_search: bool = False, thread_id: str = "default_user"):
    config = {"configurable": {"thread_id": thread_id}}
    return app.invoke({
        "query": query, 
        "web_search_enabled": web_search,
        "reasoning_trace": []
    }, config=config)