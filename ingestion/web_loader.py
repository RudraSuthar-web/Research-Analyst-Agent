"""
ingestion/web_loader.py
Fetch a URL → extract clean text → return LangChain Documents.
"""
import hashlib
from typing import Optional

import requests
from bs4 import BeautifulSoup
from langchain_core.documents import Document


def _sha256(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def _clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # Remove boilerplate tags
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)


def load_url(url: str, tags: Optional[list[str]] = None) -> tuple[str, list[Document], str]:
    """
    Fetch a URL and return ingestion-ready Documents.

    Returns:
        doc_id  — sha256 of page text
        docs    — list with a single Document (entire page as one chunk pre-split)
        title   — page <title> or URL
    """
    headers = {"User-Agent": "Mozilla/5.0 (research-agent/1.0)"}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else url

    text = _clean_html(resp.text)
    if not text.strip():
        raise ValueError(f"No extractable text at: {url}")

    doc_id = _sha256(text)

    doc = Document(
        page_content=text,
        metadata={
            "source_path": url,
            "source_type": "url",
            "title":       title,
            "authors":     "",
            "tags":        ", ".join(tags) if tags else "",
            "page_number": 1,
            "total_pages": 1,
        }
    )
    return doc_id, [doc], title