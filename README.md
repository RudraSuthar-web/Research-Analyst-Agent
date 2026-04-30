# AI Research Analyst Agent

A production-grade RAG + LangGraph agent that ingests research papers, PDFs, and web content — then answers questions with citations.

## Stack
- **LLM**: Groq API — `llama-3.3-70b-versatile` (GPT OSS 120B)
- **Embeddings**: `all-MiniLM-L6-v2` via sentence-transformers (free, local)
- **Vector store**: Chroma (local persistent)
- **Metadata DB**: SQLite via SQLAlchemy
- **Agent**: LangGraph (planner → retriever → web_search → synthesizer)
- **Observability**: LangSmith (optional)

---

## Setup

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Open .env and set your GROQ_API_KEY
```

---

## Usage

### Ingest a PDF
```bash
python main.py ingest pdf data/papers/attention.pdf --tags transformers,nlp
```

### Ingest a web page
```bash
python main.py ingest url https://arxiv.org/abs/1706.03762 --tags transformers
```

### List all ingested documents
```bash
python main.py list
```

### Ask a research question
```bash
python main.py ask "What attention mechanism did Vaswani et al. introduce?"

# Force web search in addition to knowledge base
python main.py ask "Latest LLM benchmarks in 2025" --web
```

---

## Project Structure

```
research_agent/
├── main.py                    # CLI entry point
├── requirements.txt
├── .env.example
│
├── ingestion/
│   ├── pdf_loader.py          # PyMuPDF → LangChain Documents
│   ├── web_loader.py          # URL → clean text → Documents
│   └── pipeline.py            # chunk → embed → store (orchestrator)
│
├── storage/
│   ├── database.py            # SQLite models + session factory
│   └── vector_store.py        # Chroma wrapper (local + OpenAI embeddings)
│
├── agent/
│   ├── graph.py               # LangGraph StateGraph definition
│   ├── nodes.py               # planner, retriever, web_search, synthesizer
│   └── tools.py               # retrieve_chunks + search_web tools
│
├── utils/
│   └── config.py              # Pydantic settings from .env
│
└── data/
    ├── papers/                # drop PDFs here
    ├── chroma_db/             # auto-created on first ingest
    └── metadata.db            # auto-created on first ingest
```

---

## Agent flow

```
User query
    │
    ▼
[Planner]        Creates a retrieval plan
    │
    ▼
[Retriever]      Searches Chroma with primary + rephrased query
    │
    ▼
[Web Search]     Runs if KB results are thin (or --web flag)
    │
    ▼
[Synthesizer]    GPT OSS 120B synthesizes answer with inline citations
    │
    ▼
Cited answer (Markdown)
```

---

## Build status
- ✅ Ingestion pipeline (PDF + URL)
- ✅ Chroma vector store + local embeddings
- ✅ SQLite metadata store
- ✅ LangGraph agent (planner → retriever → web search → synthesizer)
- ✅ CLI with ingest / list / ask commands
- ⬜ LangSmith tracing (add keys to .env to enable)
- ⬜ Tavily web search (add TAVILY_API_KEY to .env to enable)
