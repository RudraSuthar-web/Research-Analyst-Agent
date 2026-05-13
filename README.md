# ⬡ Research Analyst Agent

A production-grade RAG + LangGraph agent that ingests research papers, PDFs, and web content, then streams citation-aware answers directly to your terminal. The stack uses LangGraph for stateful orchestration, Qdrant in local mode for on-disk vector storage, and Groq-hosted `llama-3.3-70b-versatile` for generation.

---

## Overview

Research Analyst Agent is designed as a practical AI research workflow rather than a simple "chat with PDF" demo. It combines document ingestion, semantic retrieval, optional live web search, and citation-aware synthesis into a single streamlined pipeline operated from the CLI.

The architecture is optimized for local development on modest hardware. Qdrant runs without a separate server process, sentence-transformers handle embeddings locally at zero API cost, and the agent streams responses token-by-token so you see output immediately rather than waiting for full generation.

---

## Features

- Ingest PDF research papers into a local searchable knowledge base.
- Ingest web pages and use them alongside local documents for grounded answers.
- **Real-time Streaming:** Answers stream token-by-token to the terminal via the `rich` library.
- **Optimized LangGraph Pipeline:** Lean retriever → conditional web search → streaming synthesizer flow.
- **Dual-Query Retrieval:** Rephrases questions for a second search pass to improve recall.
- **Local Embeddings:** Uses `all-MiniLM-L6-v2` via sentence-transformers (zero cost, local).
- **On-Disk Vector Store:** Qdrant in local mode (no Docker or server needed).
- **Metadata Management:** SQLite + SQLAlchemy for tracking documents and tags.
- **Conditional Web Search:** Automatically triggers Tavily when local context is thin.

---

## Stack

| Layer | Technology |
|---|---|
| LLM | Groq API — `llama-3.3-70b-versatile` (Streaming) |
| Embeddings | `all-MiniLM-L6-v2` (Local) |
| Vector store | Qdrant (Local on-disk) |
| Metadata DB | SQLite via SQLAlchemy |
| Agent | LangGraph (Optimized StateGraph) |
| UI/UX | Rich (Streaming Markdown) |

---

## Project Structure

```
research_agent/
│
├── agent/
│   ├── __init__.py
│   ├── graph.py                 # LangGraph StateGraph (Optimized)
│   ├── nodes.py                 # retriever, synthesizer (streaming) nodes
│   └── tools.py                 # retrieve_chunks + search_web tools
│
├── ingestion/
│   ├── __init__.py
│   ├── pdf_loader.py            # PyMuPDF → LangChain Documents
│   ├── web_loader.py            # URL scraper → Documents
│   └── pipeline.py              # chunk → embed → store orchestrator
│
├── storage/
│   ├── __init__.py
│   ├── database.py              # SQLite models + session factory
│   └── vector_store.py          # Qdrant wrapper + similarity search
│
├── utils/
│   ├── __init__.py
│   └── config.py                # Pydantic settings from .env
...
```

---

## Setup

```bash
# 1. Clone and enter the project
cd research_analyst_agent

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Open .env and set your GROQ_API_KEY
```

---

## Usage

```bash
# Ingest a PDF
python main.py ingest pdf "data/papers/llama2.pdf" --tags "llama,meta,llm"

# Ingest a web page
python main.py ingest url https://arxiv.org/abs/2307.09288 --tags "llama,meta"

# List all ingested documents
python main.py list

# Ask a research question
python main.py ask "How did Meta approach RLHF in LLaMA 2?"

# Force web search alongside KB lookup
python main.py ask "Latest LLM benchmarks" --web
```

---

## Agent Flow

```
User query
    │
    ▼
[Retriever]     Searches Qdrant with primary + rephrased query
    │
    ▼
[Web Search]    Runs only if KB results are thin (or --web flag)
    │
    ▼
[Synthesizer]   LLaMA 3.3 70B streams answer with inline citations
    │
    ▼
Real-time Streaming Answer (Markdown)
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | ✅ | Your Groq API key (console.groq.com) |
| `GROQ_MODEL` | optional | Default: `llama-3.3-70b-versatile` |
| `EMBEDDING_PROVIDER` | optional | `local` (default) or `openai` |
| `LANGCHAIN_TRACING_V2` | optional | Set `true` to enable LangSmith tracing |
| `LANGCHAIN_API_KEY` | optional | LangSmith API key |
| `TAVILY_API_KEY` | optional | Enables live web search tool |

---

## Build Status

### Version 1 — Current
- ✅ Ingestion pipeline (PDF + URL)
- ✅ Qdrant vector store (local, lightweight)
- ✅ SQLite metadata store
- ✅ Optimized LangGraph (Low-latency flow)
- ✅ Token-by-token Streaming
- ✅ CLI interface with `rich` formatting
- ⬜ LangSmith tracing (add keys to `.env` to enable)
- ⬜ Tavily web search (add `TAVILY_API_KEY` to `.env` to enable)

### Version 2 — Planned
- ⬜ Multi-agent architecture — specialized agents working in parallel (e.g. retrieval agent, critique agent, citation agent, summarization agent)
- ⬜ Agent-to-agent communication
- ⬜ Each agent independently callable or composable into larger workflows
- ⬜ Expanded tool set per agent (code execution, chart generation, comparison tables)

---

## Versioning

| Version | Status | Description |
|---|---|---|
| v1.0 | ✅ Current | Single-agent RAG pipeline with CLI |
| v2.0 | 🗓 Planned | Multi-agent system with specialized roles and supervisor orchestration |
