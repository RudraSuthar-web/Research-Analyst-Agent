# Research Analyst Agent

A production-grade RAG + LangGraph agent that ingests research papers, PDFs, and web content, then answers questions with inline citations. The stack uses LangGraph for stateful orchestration, Qdrant in local mode for on-disk vector storage, and Groq-hosted `llama-3.3-70b-versatile` for generation.

## Overview

Research Analyst Agent is designed as a practical AI research workflow rather than a simple “chat with PDF” demo. It combines document ingestion, semantic retrieval, optional live web search, and citation-aware synthesis into a single pipeline that can be used from either a Streamlit UI or a CLI.

The architecture is optimized for local development on modest hardware. Qdrant supports local persistence without requiring a separate server process in its local integration mode, while Groq handles the heavy LLM inference remotely.

## Features

- Ingest PDF research papers into a local searchable knowledge base.
- Ingest web pages and use them alongside local documents for grounded answers.
- Run a LangGraph workflow with planner, retriever, sufficiency check, optional web search, synthesizer, and verifier stages.
- Store embeddings in Qdrant with local on-disk persistence.
- Store document metadata and library state in SQLite through SQLAlchemy.
- Use local sentence-transformer embeddings with `all-MiniLM-L6-v2` to avoid paid embedding APIs.
- Query the system through Streamlit or CLI.
- Optionally enable LangSmith tracing for observability and debugging.

## Architecture

The agent follows a retrieval-first workflow so that answers stay grounded in ingested material whenever possible. Web search is used only when the local knowledge base is insufficient or when the user explicitly requests live search.

```text
User query
   ↓
[Planner]
   ↓
[Retriever]
   ↓
[Sufficiency Check]
   ├── enough evidence ──→ [Synthesizer]
   └── weak evidence ────→ [Web Search]
                              ↓
                          [Synthesizer]
                              ↓
                     [Verifier / Citation Check]
                              ↓
                     Final cited markdown answer
```

This graph structure fits LangGraph well because LangGraph is designed for stateful, node-based workflows where conditional routing is part of the core execution model.

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq API — `llama-3.3-70b-versatile` |
| Embeddings | `all-MiniLM-L6-v2` via sentence-transformers |
| Vector Store | Qdrant local mode with on-disk persistence |
| Metadata DB | SQLite via SQLAlchemy |
| Agent Runtime | LangGraph StateGraph |
| UI | Streamlit |
| Observability | LangSmith (optional) |
| Optional Search | Tavily or another web-search provider |

## Project Structure

```text
research_agent/
│
├── .streamlit/
│   └── config.toml
│
├── agent/
│   ├── __init__.py
│   ├── graph.py
│   ├── nodes.py
│   └── tools.py
│
├── ingestion/
│   ├── __init__.py
│   ├── pdf_loader.py
│   ├── web_loader.py
│   └── pipeline.py
│
├── storage/
│   ├── __init__.py
│   ├── database.py
│   └── vector_store.py
│
├── utils/
│   ├── __init__.py
│   └── config.py
│
├── data/
│   ├── papers/
│   ├── qdrant_db/
│   └── metadata.db
│
├── app.py
├── main.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
└── README.md
```

## Setup

### 1. Clone and enter the project

```bash
cd research_analyst_agent
```

### 2. Create data directories

```bash
mkdir -p data/papers
```

This directory is gitignored and stores uploaded PDFs, vector data, and metadata.

### 3. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

For Windows:

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

```bash
cp .env.example .env
```

Then open `.env` and add the required API keys.

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Groq API key for the main LLM. [cite:171] |
| `GROQ_MODEL` | No | Defaults to `llama-3.3-70b-versatile`. [cite:171] |
| `EMBEDDING_PROVIDER` | No | `local` by default; can be extended later. |
| `LANGCHAIN_TRACING_V2` | No | Set to `true` to enable LangSmith tracing. [cite:169] |
| `LANGCHAIN_API_KEY` | No | LangSmith API key. |
| `TAVILY_API_KEY` | No | Enables live web search in the graph. |

## Usage

### Streamlit UI

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501` and can be organized into three views:

- **Chat** — ask questions and receive cited answers.
- **Ingest** — upload PDFs or submit URLs for indexing.
- **Library** — browse, filter, and remove ingested sources.

### CLI

Ingest a PDF:

```bash
python main.py ingest pdf data/papers/llama2.pdf --tags "llama,meta,llm"
```

Ingest a web page:

```bash
python main.py ingest url https://arxiv.org/abs/2307.09288 --tags "llama,meta"
```

List ingested documents:

```bash
python main.py list
```

Ask a question:

```bash
python main.py ask "How did Meta approach RLHF in LLaMA 2?"
```

Force web search:

```bash
python main.py ask "Latest LLM benchmarks" --web
```

## Ingestion Pipeline

The ingestion flow should convert raw inputs into normalized LangChain-style documents, split them into chunks, generate embeddings, and write both vectors and metadata to local storage. This separation keeps indexing work outside the interactive question-answering path, which improves responsiveness and makes the project more production-like.

Typical flow:

1. Load PDF or web content.
2. Clean and normalize text.
3. Chunk text with overlap.
4. Generate embeddings.
5. Store vectors in Qdrant.
6. Store source metadata in SQLite.

## Why Qdrant

Qdrant was chosen over Chroma because it provides a cleaner path from local development to a more production-oriented vector database setup. LangChain documents direct Qdrant integration, including local persistence modes that work well for lightweight projects.

This is especially useful for machines with limited resources, since the architecture can stay local for development while still resembling a production RAG stack.

## Why LangGraph

LangGraph is a strong fit for this project because the workflow is not a single prompt call. It includes conditional routing, retrieval, optional search, synthesis, and verification, which are exactly the kinds of stateful graph patterns LangGraph is meant to handle.

Using LangGraph also makes the system easier to extend with additional nodes later, such as contradiction detection, research-gap analysis, paper clustering, or methodology review.

## Future Improvements

- Add reranking before synthesis to improve chunk selection quality.
- Add paper comparison tables and evidence matrices.
- Add contradiction detection across sources.
- Add research-gap identification for differentiated research analysis workflows.
- Add user feedback logging and answer evaluation.
- Add export to Markdown or PDF reports.
- Add background ingestion jobs for large batches of papers.

## Notes

This project is intentionally designed to be feasible on older hardware by keeping embeddings local and sending only the reasoning/generation step to the Groq API. For best results, ingest documents in small batches and avoid indexing very large paper collections all at once.

