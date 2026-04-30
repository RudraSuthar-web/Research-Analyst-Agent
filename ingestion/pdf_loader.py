"""
ingestion/pdf_loader.py
Parse PDFs → extract text + metadata → return LangChain Documents.
"""
import hashlib
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF
from langchain_core.documents import Document


def _sha256(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def load_pdf(file_path: str, tags: Optional[list[str]] = None) -> tuple[str, list[Document]]:
    """
    Parse a PDF file into LangChain Document chunks (one per page).

    Returns:
        doc_id   — sha256 of the full text (used as DB primary key)
        pages    — list of Documents, one per page, with metadata
    """
    path = Path(file_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    pdf = fitz.open(str(path))
    pages: list[Document] = []
    full_text_parts = []

    # Extract title from PDF metadata or fall back to filename
    pdf_meta = pdf.metadata or {}
    title = pdf_meta.get("title") or path.stem
    authors_raw = pdf_meta.get("author") or ""
    authors = [a.strip() for a in authors_raw.split(";") if a.strip()]

    for page_num, page in enumerate(pdf, start=1):
        text = page.get_text("text").strip()
        if not text:
            continue  # skip blank pages

        full_text_parts.append(text)

        pages.append(Document(
            page_content=text,
            metadata={
                "source_path": str(path),
                "source_type": "pdf",
                "title":       title,
                "authors":     ", ".join(authors) if authors else "Unknown",
                "tags":        ", ".join(tags) if tags else "",
                "page_number": page_num,
                "total_pages": len(pdf),
            }
        ))

    pdf.close()

    doc_id = _sha256("\n".join(full_text_parts))
    return doc_id, pages, title, authors