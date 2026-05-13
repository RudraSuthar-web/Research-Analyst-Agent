"""
agent/nodes.py
Individual LangGraph node functions.
Each node receives the full AgentState and returns a partial update.
"""
import json
from typing import Any

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

from agent.tools import AGENT_TOOLS, retrieve_chunks, search_web
from utils.config import settings

console = Console()

# ── LLM instance (shared across nodes) ──────────────────────────────────────
def get_llm(temperature: float = 0.1) -> ChatGroq:
    return ChatGroq(
        model=settings.GROQ_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=temperature,
        max_tokens=4096,
        streaming=True
    )


# ── SYSTEM PROMPT ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert AI Research Analyst. Your job is to answer research questions accurately using evidence from documents in the knowledge base.

You have access to these tools:
- retrieve_chunks: search the knowledge base of ingested papers and documents
- search_web: search the live web for current or external information

Guidelines:
- Always search the knowledge base first before using web search
- Cite every factual claim with [Source: title, page] format
- If the knowledge base lacks relevant info, say so and use web search
- Be precise, structured, and evidence-based in your answers
- When synthesizing across multiple sources, clearly distinguish each source's contribution
"""


# ── NODE: planner ─────────────────────────────────────────────────────────────
def planner_node(state: dict) -> dict:
    """
    Decides what tools to call and in what order.
    Returns a plan as structured text that guides subsequent nodes.
    """
    console.print("[bold blue]🧠 Planning...[/bold blue]")

    llm = get_llm(temperature=0)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=(
            f"Research question: {state['query']}\n\n"
            "Create a brief retrieval plan: which tool(s) to use and what to search for. "
            "Be concise — 2-3 sentences max."
        ))
    ]
    response = llm.invoke(messages)
    plan = response.content

    console.print(f"[dim]Plan: {plan[:120]}...[/dim]")
    return {"plan": plan, "messages": [HumanMessage(content=state["query"])]}


# ── NODE: retriever ───────────────────────────────────────────────────────────
def retriever_node(state: dict) -> dict:
    """
    Calls retrieve_chunks tool with the original query.
    Also generates sub-queries for better recall.
    """
    console.print("[bold blue]🔍 Retrieving from knowledge base...[/bold blue]")

    query = state["query"]

    # Primary retrieval
    primary_results = retrieve_chunks.invoke({"query": query, "k": 5})

    # Generate a reformulated query for better recall
    llm = get_llm(temperature=0)
    rephrase_msg = llm.invoke([HumanMessage(
        content=f"Rephrase this research question differently to improve search recall "
                f"(one sentence only, no explanation): {query}"
    )])
    alt_query = rephrase_msg.content.strip()
    alt_results = retrieve_chunks.invoke({"query": alt_query, "k": 3})

    combined = f"=== Primary results ===\n{primary_results}\n\n=== Alternative query results ===\n{alt_results}"

    console.print(f"[green]✓ Retrieved chunks[/green]")
    return {"retrieved_context": combined}


# ── NODE: web search (conditional) ───────────────────────────────────────────
def web_search_node(state: dict) -> dict:
    """
    Runs web search if the retrieved context is insufficient.
    """
    context = state.get("retrieved_context", "")
    needs_web = (
        "No relevant documents found" in context
        or len(context) < 300
        or state.get("force_web_search", False)
    )

    if not needs_web:
        return {"web_context": ""}

    console.print("[bold blue]🌐 Searching web...[/bold blue]")
    web_results = search_web.invoke({"query": state["query"]})
    console.print("[green]✓ Web search complete[/green]")
    return {"web_context": web_results}


# ── NODE: synthesizer ─────────────────────────────────────────────────────────
def synthesizer_node(state: dict) -> dict:
    """
    Synthesizes all retrieved context into a coherent answer.
    Streams the output to the console for better user experience.
    """
    console.print("[bold blue]✍️  Synthesizing answer...[/bold blue]")

    retrieved = state.get("retrieved_context", "")
    web       = state.get("web_context", "")

    context_block = ""
    if retrieved and "No relevant documents found" not in retrieved:
        context_block += f"KNOWLEDGE BASE RESULTS:\n{retrieved}\n\n"
    if web:
        context_block += f"WEB SEARCH RESULTS:\n{web}\n\n"

    if not context_block:
        context_block = "No relevant context was found from any source."

    llm = get_llm(temperature=0.2)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=(
            f"Research question: {state['query']}\n\n"
            f"Available evidence:\n{context_block}\n"
            "Write a comprehensive, well-structured answer. "
            "Use [Source: title, page X] inline citations for every factual claim. "
            "End with a 'Sources used' section listing all cited documents."
        ))
    ]
    
    full_response = ""
    console.rule("[dim]Answer[/dim]")
    
    with Live(Markdown(""), auto_refresh=False, console=console) as live:
        for chunk in llm.stream(messages):
            full_response += chunk.content
            live.update(Markdown(full_response), refresh=True)

    console.rule()
    return {"answer": full_response}
