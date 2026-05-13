"""
agent/graph.py
Defines the LangGraph StateGraph for the Research Analyst Agent.

Flow:
  planner → retriever → web_search → synthesizer → END
                              ↑
                    (conditional: only if context is thin)
"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

from agent.nodes import (
    retriever_node,
    web_search_node,
    synthesizer_node,
)


# ── Agent state schema ────────────────────────────────────────────────────────
class AgentState(TypedDict):
    query:             str
    messages:          list
    retrieved_context: Optional[str]
    web_context:       Optional[str]
    answer:            Optional[str]
    force_web_search:  bool


# ── Build the graph ───────────────────────────────────────────────────────────
def build_graph():
    graph = StateGraph(AgentState)

    # Register nodes
    graph.add_node("retriever",  retriever_node)
    graph.add_node("web_search", web_search_node)
    graph.add_node("synthesizer",synthesizer_node)

    # Entry point
    graph.set_entry_point("retriever")

    # Edges
    graph.add_edge("retriever",  "web_search")
    graph.add_edge("web_search", "synthesizer")
    graph.add_edge("synthesizer", END)

    return graph.compile()


# Module-level compiled graph (import and call directly)
agent_graph = build_graph()


def run_agent(query: str, force_web_search: bool = False) -> str:
    """
    Run the full research agent pipeline for a query.

    Args:
        query:            The research question.
        force_web_search: Always include web search even if KB has results.

    Returns:
        The synthesized answer string with inline citations.
    """
    initial_state: AgentState = {
        "query":             query,
        "messages":          [HumanMessage(content=query)],
        "retrieved_context": None,
        "web_context":       None,
        "answer":            None,
        "force_web_search":  force_web_search,
    }

    final_state = agent_graph.invoke(initial_state)
    return final_state.get("answer", "Agent produced no answer.")
