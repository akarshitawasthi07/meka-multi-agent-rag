from langgraph.graph import StateGraph
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
    planner_output: str
    retrieved_docs: List
    reranked_docs: List
    final_answer: str
    validation: str
    reason: str


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

app = graph.compile()


def run_meka(query: str):
    return app.invoke({"query": query})