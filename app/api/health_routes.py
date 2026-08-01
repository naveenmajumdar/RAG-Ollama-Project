from fastapi import APIRouter
from app.vectorstore import chroma_store

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health():
    # Keep liveness checks lightweight to avoid false "API not reachable" states.
    return {"status": "ok"}


@router.get("/stats")
def health_stats():
    return {"documents_indexed": chroma_store.collection_count()}
