"""
utils/config.py
Single source of truth for all environment-based settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # LLM — Groq
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"   # GPT OSS 120B on Groq console
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"

    # Embeddings — still OpenAI (Groq doesn't provide embeddings)
    # Use a free alternative: "sentence-transformers" locally, or keep OpenAI
    OPENAI_API_KEY: str = ""                        # optional, only for embeddings
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_PROVIDER: str = "local"              # "openai" | "local"

    # Chroma
    CHROMA_PERSIST_DIR: str = "./data/chroma_db"
    CHROMA_COLLECTION: str = "research_papers"

    # SQLite
    SQLITE_DB_PATH: str = "./data/metadata.db"

    # LangSmith (optional)
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "research-analyst-agent"

    # Tavily web search (optional)
    TAVILY_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
