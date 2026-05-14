"""
ingestion/pipeline.py
Orchestrates the full ingestion flow:
  load → chunk → embed → store in Qdrant + SQLite
"""
from typing import Optional

from rich.console import Console

from ingestion.pdf_loader import load_pdf
from ingestion.web_loader import load_url
from storage.vector_store import get_vector_store
from storage.database import get_session, Document as DBDocument

console = Console()

_SPLITTER = None

def get_splitter():
    global _SPLITTER
    if _SPLITTER is None:
        # Move heavy import inside the function to speed up script startup
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        _SPLITTER = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
    return _SPLITTER


def _already_ingested(doc_id: str) -> bool:
    with get_session() as session:
        return session.get(DBDocument, doc_id) is not None


def _save_metadata(doc_id: str, title: str, source_type: str,
                   source_path: str, authors: list, tags: list,
                   chunk_count: int) -> None:
    with get_session() as session:
        record = DBDocument(
            id=doc_id,
            title=title,
            source_type=source_type,
            source_path=source_path,
            authors=authors,
            tags=tags,
            chunk_count=chunk_count,
        )
        session.merge(record)   # upsert
        session.commit()


def ingest_pdf(file_path: str, tags: Optional[list[str]] = None) -> dict:
    """Ingest a PDF. Returns a summary dict."""
    doc_id, pages, title, authors = load_pdf(file_path, tags)

    if _already_ingested(doc_id):
        console.print(f"[yellow]⚠ Already ingested:[/yellow] {title}")
        return {"status": "skipped", "doc_id": doc_id, "title": title}

    chunks = get_splitter().split_documents(pages)
    # Tag each chunk with the stable doc_id for later filtering
    for chunk in chunks:
        chunk.metadata["doc_id"] = doc_id

    store = get_vector_store()
    store.add_documents(chunks)

    _save_metadata(doc_id, title, "pdf", file_path,
                   authors, tags or [], len(chunks))

    console.print(f"[green]✓ Ingested PDF:[/green] {title} "
                  f"([cyan]{len(chunks)} chunks[/cyan])")
    return {"status": "ok", "doc_id": doc_id, "title": title,
            "chunks": len(chunks)}


def ingest_url(url: str, tags: Optional[list[str]] = None) -> dict:
    """Ingest a web page. Returns a summary dict."""
    doc_id, docs, title = load_url(url, tags)

    if _already_ingested(doc_id):
        console.print(f"[yellow]⚠ Already ingested:[/yellow] {title}")
        return {"status": "skipped", "doc_id": doc_id, "title": title}

    chunks = get_splitter().split_documents(docs)
    for chunk in chunks:
        chunk.metadata["doc_id"] = doc_id

    store = get_vector_store()
    store.add_documents(chunks)

    _save_metadata(doc_id, title, "url", url,
                   [], tags or [], len(chunks))

    console.print(f"[green]✓ Ingested URL:[/green] {title} "
                  f"([cyan]{len(chunks)} chunks[/cyan])")
    return {"status": "ok", "doc_id": doc_id, "title": title,
            "chunks": len(chunks)}
