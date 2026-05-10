# ⬡ Research Analyst Agent

A production-grade RAG + LangGraph agent that ingests research papers, PDFs, and web content, then answers questions with inline citations. The stack uses LangGraph for stateful orchestration, Qdrant in local mode for on-disk vector storage, and Groq-hosted `llama-3.3-70b-versatile` for generation.

---

## Overview
Research Analyst Agent is designed as a practical AI research workflow rather than a simple “chat with PDF” demo. It combines document ingestion, semantic retrieval, optional live web search, and citation-aware synthesis into a single pipeline that can be used from a CLI.

The architecture is optimized for local development on modest hardware. Qdrant supports local persistence without requiring a separate server process in its local integration mode, while Groq handles the heavy LLM inference remotely.

---

## Features
- Ingest PDF research papers into a local searchable knowledge base.
- Ingest web pages and use them alongside local documents for grounded answers.
- Run a LangGraph workflow with planner, retriever, sufficiency check, optional web search, synthesizer, and verifier stages.
- Store embeddings in Qdrant with local on-disk persistence.
- Store document metadata and library state in SQLite through SQLAlchemy.
- Use local sentence-transformer embeddings with `all-MiniLM-L6-v2` to avoid paid embedding APIs.
- Query the system through CLI.
- Optionally enable LangSmith tracing for observability and debugging.

---

## Stack

| Layer | Technology |
|---|---|
| LLM | Groq API — `llama-3.3-70b-versatile` (GPT OSS 120B) |
| Embeddings | `all-MiniLM-L6-v2` via sentence-transformers (free, local) |
| Vector store | Qdrant (local on-disk, no server needed) |
| Metadata DB | SQLite via SQLAlchemy |
| Agent | LangGraph (planner → retriever → web search → synthesizer) |
| Observability | LangSmith (optional) |

---

## Project Structure

```
research_agent/
│
├── agent/
│   ├── __init__.py
│   ├── graph.py                 # LangGraph StateGraph
│   ├── nodes.py                 # planner, retriever, synthesizer nodes
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
│
├── data/                        # gitignored
│   ├── papers/                  # drop PDFs here
│   ├── qdrant_db/               # auto-created on first ingest
│   └── metadata.db              # auto-created on first ingest
│
├── main.py                      # CLI entry point
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
[Planner]       Creates a retrieval strategy
    │
    ▼
[Retriever]     Searches Qdrant with primary + rephrased query
    │
    ▼
[Web Search]    Runs only if KB results are thin (or --web flag)
    │
    ▼
[Synthesizer]   LLaMA 3.3 70B writes answer with inline citations
    │
    ▼
Cited answer (Markdown)
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
| `TAVILY_API_KEY` | ✅ | Enables live web search tool |

---

## Build Status

- ✅ Ingestion pipeline (PDF + URL)
- ✅ Qdrant vector store (local, lightweight)
- ✅ SQLite metadata store
- ✅ LangGraph agent (planner → retriever → web search → synthesizer)
- ✅ CLI interface
- ⬜ LangSmith tracing (add keys to `.env` to enable)
- ⬜ Tavily web search (add `TAVILY_API_KEY` to `.env` to enable)
