from fastapi import APIRouter
from app.vectorstore import chroma_store

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health():
    return {"status": "ok", "documents_indexed": chroma_store.collection_count()}
