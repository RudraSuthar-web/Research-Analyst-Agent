"""
agent/tools.py
LangChain tools the agent can call:
  - retrieve_chunks  : semantic search over ingested documents
  - search_web       : live web search via Tavily (optional)
"""
from typing import Optional
from langchain_core.tools import tool
from storage.vector_store import similarity_search
from utils.config import settings


@tool
def retrieve_chunks(query: str, k: int = 5) -> str:
    """
    Search the research knowledge base for chunks relevant to the query.
    Returns formatted text with source citations.
    Use this for questions about ingested papers and documents.
    """
    results = similarity_search(query, k=k)

    if not results:
        return "No relevant documents found in the knowledge base."

    formatted = []
    for i, (doc, score) in enumerate(results, start=1):
        meta = doc.metadata
        title  = meta.get("title", "Unknown")
        source = meta.get("source_path", "")
        page   = meta.get("page_number", "")
        relevance = round((1 - score) * 100, 1)   # convert distance → %

        formatted.append(
            f"[{i}] Source: {title}"
            + (f", p.{page}" if page else "")
            + f" (relevance: {relevance}%)\n"
            + f"    Path: {source}\n"
            + f"    Content: {doc.page_content[:600]}\n"
        )

    return "\n".join(formatted)


@tool
def search_web(query: str) -> str:
    """
    Search the live web for current information not in the knowledge base.
    Use this when the question requires up-to-date or external information.
    Requires TAVILY_API_KEY to be set in .env.
    """
    if not settings.TAVILY_API_KEY:
        return (
            "Web search is not configured. "
            "Add TAVILY_API_KEY to .env to enable live web search."
        )

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        results = client.search(query, max_results=4)

        formatted = []
        for r in results.get("results", []):
            formatted.append(
                f"Title: {r.get('title', 'N/A')}\n"
                f"URL: {r.get('url', '')}\n"
                f"Summary: {r.get('content', '')[:400]}\n"
            )
        return "\n---\n".join(formatted) or "No web results found."

    except Exception as e:
        return f"Web search failed: {e}"


# Exported tool list — passed to the agent
AGENT_TOOLS = [retrieve_chunks, search_web]
