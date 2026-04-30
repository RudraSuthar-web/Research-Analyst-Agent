"""
storage/vector_store.py
Qdrant vector store — lighter alternative to Chroma.
Runs fully in-memory or on-disk (local mode, no server needed).
"""
from typing import Optional
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from utils.config import settings


VECTOR_SIZE = 384   # all-MiniLM-L6-v2 output dimension


def _get_embeddings():
    if settings.EMBEDDING_PROVIDER == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
        )
    else:
        from langchain_huggingface import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )


def _get_client() -> QdrantClient:
    """
    Local on-disk Qdrant client — no server, no Docker needed.
    Data persists at QDRANT_PATH between runs.
    """
    import os
    path = os.path.join(settings.CHROMA_PERSIST_DIR.replace("chroma_db", "qdrant_db"))
    os.makedirs(path, exist_ok=True)
    return QdrantClient(path=path)


def _ensure_collection(client: QdrantClient):
    """Create collection if it doesn't exist yet."""
    collections = [c.name for c in client.get_collections().collections]
    if settings.CHROMA_COLLECTION not in collections:
        client.create_collection(
            collection_name=settings.CHROMA_COLLECTION,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )


def get_vector_store() -> QdrantVectorStore:
    client = _get_client()
    _ensure_collection(client)
    embeddings = _get_embeddings()
    return QdrantVectorStore(
        client=client,
        collection_name=settings.CHROMA_COLLECTION,
        embedding=embeddings,
    )


def similarity_search(query: str, k: int = 5, filter_dict: Optional[dict] = None):
    """
    Search Qdrant and return top-k chunks with scores.
    filter_dict support is basic — Qdrant uses its own filter format,
    so we ignore it here and filter post-retrieval if needed.
    """
    store = get_vector_store()
    return store.similarity_search_with_score(query, k=k)