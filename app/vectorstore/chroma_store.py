from __future__ import annotations

from typing import Optional

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.schema import Document
from app.utils.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_store: Optional[Chroma] = None


def _embeddings() -> OllamaEmbeddings:
    return OllamaEmbeddings(
        model=settings.ollama_embed_model,
        base_url=settings.ollama_base_url,
    )


def get_store() -> Chroma:
    global _store
    if _store is None:
        _store = Chroma(
            persist_directory=settings.chroma_persist_dir,
            embedding_function=_embeddings(),
        )
    return _store


def add_documents(docs: list[Document]) -> int:
    store = get_store()
    store.add_documents(docs)
    logger.info("Added %d documents to vector store", len(docs))
    return len(docs)


def similarity_search(query: str) -> list[Document]:
    return get_store().similarity_search(query, k=settings.top_k_retrieval)


def collection_count() -> int:
    try:
        return get_store()._collection.count()
    except Exception:
        return 0
