# ⬡ Research Analyst Agent

A production-grade RAG + LangGraph agent that ingests research papers, PDFs, and web content, then streams citation-aware answers directly to your terminal. The stack uses LangGraph for stateful orchestration, Qdrant in local mode for on-disk vector storage, and Groq-hosted `llama-3.3-70b-versatile` for generation.

---

## Overview

Research Analyst Agent is designed as a practical AI research workflow. It combines document ingestion, semantic retrieval, optional live web search, and citation-aware synthesis into a single streamlined pipeline operated from the CLI.

The architecture is optimized for local development on modest hardware. Qdrant runs without a separate server process, sentence-transformers handle embeddings locally at zero API cost, and the agent streams responses token-by-token for immediate output.

---

## Features

- **High-Performance CLI**: Optimized startup through lazy loading of heavy AI dependencies (LangChain, Torch, Transformers).
- **Ingestion pipeline**: Ingest PDF research papers and web pages into a local searchable knowledge base.
- **Streaming Output**: Stream answers token-by-token to the terminal via the `rich` library.
- **Stateful Agent**: A lean LangGraph pipeline: retriever → conditional web search → streaming synthesizer.
- **Dual-query retrieval**: Automatic rephrasing of questions for a second search pass to improve recall.
- **Local Persistence**: Embeddings stored in Qdrant (local on-disk) and metadata in SQLite.
- **Cost-Efficient**: Local `all-MiniLM-L6-v2` embeddings eliminate the need for paid embedding APIs.
- **Smart Web Search**: Automatic triggering of Tavily web search when knowledge base context is insufficient.

---

## Stack

| Layer | Technology |
|---|---|
| LLM | Groq API — `llama-3.3-70b-versatile` (streaming enabled) |
| Embeddings | `all-MiniLM-L6-v2` via sentence-transformers (free, local) |
| Vector store | Qdrant (local on-disk, no server needed) |
| Metadata DB | SQLite via SQLAlchemy |
| Agent | LangGraph (retriever → web search → synthesizer) |
| CLI output | `rich` library (streaming markdown, live panels) |
| Performance | Lazy-loading imports & singleton pattern optimizations |

---

## Project Structure

```
research_agent/
│
├── agent/
│   ├── __init__.py
│   ├── graph.py                 # LangGraph StateGraph (Lazy-loaded)
│   ├── nodes.py                 # retriever, synthesizer nodes (streaming)
│   └── tools.py                 # retrieve_chunks + search_web tools
│
├── ingestion/
│   ├── __init__.py
│   ├── pdf_loader.py            # PyMuPDF → LangChain Documents
│   ├── web_loader.py            # URL scraper → Documents
│   └── pipeline.py              # chunk → embed → store orchestrator (Lazy imports)
│
├── storage/
│   ├── __init__.py
│   ├── database.py              # SQLite models + Lazy session factory
│   └── vector_store.py          # Qdrant wrapper + Cached client & models
│
├── utils/
│   ├── __init__.py
│   └── config.py                # Pydantic settings from .env
│
├── data/                        # gitignored
│   ├── papers/                  # drop PDFs here
│   ├── qdrant_db/               # auto-created on first ingest
│   └── metadata.db              # auto-created on first ingest
│
├── main.py                      # CLI entry point (optimized startup)
├── requirements.txt
├── .env                         # gitignored — your API keys
├── .env.example                 # committed — template
├── .gitignore
└── README.md
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

# List all ingested documents (Optimized: <1.5s)
python main.py list

# Ask a research question (streams answer to terminal)
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
[Retriever]       Searches Qdrant with primary + rephrased query
    │
    ▼
[Web Search]      Triggers automatically if KB context is thin
    │             (or explicitly via --web flag)
    ▼
[Synthesizer]     Streams citation-aware answer token-by-token
    │             directly to the terminal via rich
    ▼
Live streaming output
```

The planner node was removed in v1.1 to reduce latency. Version 1.2 introduces a major performance refactor, reducing CLI latency for metadata operations (like `list`) from 30+ seconds to under 1.5 seconds through aggressive lazy-loading of the AI stack and singleton resource management.

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
- ✅ LangGraph agent (retriever → web search → synthesizer)
- ✅ Token-by-token streaming output via `rich`
- ✅ Dual-query retrieval for improved recall
- ✅ Conditional web search (auto-triggers on thin KB context)
- ✅ **v1.2: Lazy-loading refactor (90%+ reduction in CLI startup latency)**
- ✅ **v1.2: Graceful shutdown handling for local vector store**
- ✅ CLI interface
- ⬜ LangSmith tracing (add keys to `.env` to enable)
- ⬜ Tavily web search (add `TAVILY_API_KEY` to `.env` to enable)

### Version 2 — Planned

- ⬜ Multi-agent architecture — specialized agents coordinated by a LangGraph supervisor
- ⬜ Dedicated agents for retrieval, critique, citation formatting, and summarization
- ⬜ Agent-to-agent communication via LangGraph supervisor pattern
- ⬜ Expanded tool set per agent (code execution, comparison tables, chart generation)

---

## Versioning

| Version | Status | Description |
|---|---|---|
| v1.0 | ✅ Shipped | Single-agent RAG pipeline with CLI |
| v1.1 | ✅ Shipped | Streaming output, planner removed, faster TTFT |
| v1.2 | ✅ Current | Performance refactor, lazy-loading, graceful shutdown |
| v2.0 | 🗓 Planned | Multi-agent system |
