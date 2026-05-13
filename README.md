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
- Stream answers token-by-token to the terminal via the `rich` library — no waiting for full generation.
- Run a lean LangGraph pipeline: retriever → conditional web search → streaming synthesizer.
- Dual-query retrieval — rephrases your question for a second search pass to improve recall.
- Store embeddings in Qdrant with local on-disk persistence.
- Store document metadata and library state in SQLite through SQLAlchemy.
- Use local sentence-transformer embeddings with `all-MiniLM-L6-v2` to avoid paid embedding APIs.
- Automatically trigger Tavily web search only when the knowledge base lacks sufficient context.
- Optionally enable LangSmith tracing for observability and debugging.

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
| Observability | LangSmith (optional) |

---

## Project Structure

```
research_agent/
│
├── agent/
│   ├── __init__.py
│   ├── graph.py                 # LangGraph StateGraph
│   ├── nodes.py                 # retriever, synthesizer nodes (streaming)
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

The planner node was removed in v1.1 — it added several seconds of latency with no meaningful improvement in answer quality for the current single-agent architecture. The pipeline now goes straight from query to retrieval, reducing time-to-first-token by roughly 60–70%.

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
- ✅ CLI interface
- ⬜ LangSmith tracing (add keys to `.env` to enable)
- ⬜ Tavily web search (add `TAVILY_API_KEY` to `.env` to enable)

### Version 2 — Planned

- ⬜ Multi-agent architecture — specialized agents coordinated by a LangGraph supervisor
- ⬜ Dedicated agents for retrieval, critique, citation formatting, and summarization
- ⬜ Gemma 3 2B (local via Ollama) for lightweight preprocessing — query rephrasing, relevance scoring, tag extraction
- ⬜ Groq LLaMA 70B reserved for heavy reasoning — planning and synthesis only
- ⬜ Agent-to-agent communication via LangGraph supervisor pattern
- ⬜ Expanded tool set per agent (code execution, comparison tables, chart generation)
- ⬜ Persistent memory across sessions

---

## Versioning

| Version | Status | Description |
|---|---|---|
| v1.0 | ✅ Shipped | Single-agent RAG pipeline with CLI |
| v1.1 | ✅ Current | Streaming output, planner removed, 60–70% faster TTFT |
| v2.0 | 🗓 Planned | Multi-agent system with Gemma 3 2B + LLaMA 70B hybrid |
